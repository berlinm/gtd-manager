from django.db import OperationalError, ProgrammingError


def preferences(request):
    from apps.core.models import Preferences
    try:
        prefs = Preferences.load()
    except (OperationalError, ProgrammingError):
        prefs = Preferences()  # unsaved defaults if the table is not migrated yet
    return {'prefs': prefs}


def inbox_count(request):
    if not request.user.is_authenticated:
        return {'inbox_count': 0, 'pending_notes_count': 0}
    try:
        from apps.capture.models import InboxItem
        inbox = InboxItem.objects.filter(processed_at__isnull=True).count()
    except (OperationalError, ProgrammingError):
        inbox = 0
    try:
        from apps.meetings.models import MeetingNote
        pending_notes = MeetingNote.objects.filter(
            processed_at__isnull=True,
            session__closed_at__isnull=False,
        ).count()
    except (OperationalError, ProgrammingError):
        pending_notes = 0
    focus_pks = request.session.get('gtd_focus_pks', [])
    return {
        'inbox_count': inbox,
        'pending_notes_count': pending_notes,
        'focus_count': len(focus_pks),
    }
