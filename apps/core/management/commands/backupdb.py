import sqlite3
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


def run_backup():
    """Write a complete backup to BACKUP_DIR as a single timestamped .zip.

    Contains a consistent SQLite snapshot (via the online Backup API — safe while
    the app is running) as ``db.sqlite3`` plus the whole ``media/`` tree (reference
    attachments). Restore by unzipping and putting ``db.sqlite3`` and ``media/``
    back in the project root. Returns the path to the .zip.
    """
    db_name = str(settings.DATABASES['default']['NAME'])
    backup_dir = getattr(settings, 'BACKUP_DIR', settings.BASE_DIR / 'backups')
    backup_dir.mkdir(parents=True, exist_ok=True)
    media_root = Path(getattr(settings, 'MEDIA_ROOT', settings.BASE_DIR / 'media'))
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    dest = backup_dir / f'gtd-{timestamp}.zip'

    with tempfile.TemporaryDirectory() as tmp:
        snapshot = Path(tmp) / 'db.sqlite3'
        # A fresh read-only-ish connection to the database file; the online
        # Backup API yields a consistent snapshot without locking out the app.
        source = sqlite3.connect(db_name, uri=db_name.startswith('file:'))
        try:
            target = sqlite3.connect(str(snapshot))
            try:
                source.backup(target)
            finally:
                target.close()
        finally:
            source.close()

        with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(snapshot, 'db.sqlite3')
            if media_root.exists():
                for path in sorted(media_root.rglob('*')):
                    if path.is_file():
                        arcname = Path('media') / path.relative_to(media_root)
                        zf.write(path, str(arcname))
    return dest


class Command(BaseCommand):
    help = 'Write a complete backup (database + media) to the backups directory as a timestamped .zip.'

    def handle(self, *args, **options):
        dest = run_backup()
        self.stdout.write(self.style.SUCCESS(f'Backup written to {dest}'))
