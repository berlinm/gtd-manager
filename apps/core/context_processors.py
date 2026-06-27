from django.db import OperationalError, ProgrammingError


def inbox_count(request):
    if not request.user.is_authenticated:
        return {'inbox_count': 0}
    try:
        from apps.capture.models import InboxItem
        return {'inbox_count': InboxItem.objects.filter(processed_at__isnull=True).count()}
    except (OperationalError, ProgrammingError):
        # Table may not exist before the first migration run.
        return {'inbox_count': 0}
