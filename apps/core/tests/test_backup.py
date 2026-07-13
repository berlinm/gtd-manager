import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.management.commands.backupdb import run_backup
from apps.gtd.models import Reference, ReferenceAttachment


class BackupTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self.backup_dir = Path(self._tmp) / 'backups'
        self.media_root = Path(self._tmp) / 'media'
        self.media_root.mkdir(parents=True, exist_ok=True)
        # run_backup() reads settings.DATABASES['default']['NAME'] and opens its
        # own connection. Point it at a real temp file — the default test DB is
        # an in-memory shared-cache DB, and backing that up from a second
        # connection deadlocks against the test's open transaction. This only
        # affects tests; production uses a plain on-disk sqlite file.
        self.source_db = Path(self._tmp) / 'source.sqlite3'
        sqlite3.connect(str(self.source_db)).close()
        self.override = override_settings(
            BACKUP_DIR=self.backup_dir, MEDIA_ROOT=self.media_root
        )
        self.override.enable()
        # Patch only the DB NAME value (via patch.dict, not override_settings) so
        # run_backup targets a real file without triggering Django to reset the
        # live connection — which would destroy the in-memory test database.
        self.db_patch = mock.patch.dict(
            settings.DATABASES['default'], {'NAME': str(self.source_db)}
        )
        self.db_patch.start()

    def tearDown(self):
        self.db_patch.stop()
        self.override.disable()
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _attachment(self, name='notes.txt', content=b'payload'):
        ref = Reference.objects.create(title='Docs')
        att = ReferenceAttachment(reference=ref, original_name=name)
        att.file.save(name, ContentFile(content), save=True)
        return att

    def test_backup_is_a_zip_with_db_and_media(self):
        self._attachment()
        dest = run_backup()
        self.assertTrue(dest.name.endswith('.zip'))
        self.assertTrue(dest.exists())
        with zipfile.ZipFile(dest) as zf:
            names = zf.namelist()
        self.assertIn('db.sqlite3', names)
        # the uploaded attachment file is included under media/
        media_entries = [n for n in names if n.startswith('media/')]
        self.assertTrue(any(n.endswith('notes.txt') for n in media_entries),
                        f'attachment not in backup: {names}')

    def test_backup_db_snapshot_captures_real_content(self):
        # Confirm the snapshot in the zip is a faithful copy of the source DB
        # (same table, same rows) — exercises the SQLite Backup API path.
        conn = sqlite3.connect(str(self.source_db))
        conn.execute('CREATE TABLE note (id INTEGER PRIMARY KEY, body TEXT)')
        conn.execute("INSERT INTO note (body) VALUES ('remember the milk')")
        conn.commit()
        conn.close()

        dest = run_backup()

        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(dest) as zf:
                zf.extract('db.sqlite3', tmp)
            snap = sqlite3.connect(str(Path(tmp) / 'db.sqlite3'))
            try:
                rows = [r[0] for r in snap.execute('SELECT body FROM note')]
            finally:
                snap.close()
        self.assertEqual(rows, ['remember the milk'])

    def test_backup_without_media_still_succeeds(self):
        # no attachments, media dir empty
        dest = run_backup()
        with zipfile.ZipFile(dest) as zf:
            self.assertIn('db.sqlite3', zf.namelist())

    def test_management_command_runs(self):
        call_command('backupdb')
        self.assertTrue(list(self.backup_dir.glob('gtd-*.zip')))

    def test_settings_lists_zip_backup(self):
        user = User.objects.create_user(username='t', password='p')
        self.client.force_login(user)
        dest = run_backup()
        response = self.client.get(reverse('core:settings'))
        self.assertContains(response, dest.name)
