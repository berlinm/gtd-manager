import shutil
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


def run_backup():
    db_path = Path(settings.DATABASES['default']['NAME'])
    backup_dir = getattr(settings, 'BACKUP_DIR', settings.BASE_DIR / 'backups')
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    dest = backup_dir / f'gtd-{timestamp}.db'
    shutil.copy2(db_path, dest)
    return dest


class Command(BaseCommand):
    help = 'Copy the SQLite database to the backups directory with a timestamp.'

    def handle(self, *args, **options):
        dest = run_backup()
        self.stdout.write(self.style.SUCCESS(f'Backup written to {dest}'))
