from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.gtd.models import AgendaItem, Meeting, NextAction, Project, SomedayMaybe, WaitingFor
from apps.meetings.models import MeetingNote, MeetingSession


class MeetingListViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('meetings:meeting_list'))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_meetings(self):
        Meeting.objects.create(title='Weekly standup')
        response = self.client.get(reverse('meetings:meeting_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Weekly standup')

    def test_list_shows_pending_count_when_notes_pending(self):
        meeting = Meeting.objects.create(title='Standup')
        session = MeetingSession.objects.create(
            meeting=meeting,
            occurred_on='2026-01-01',
            closed_at=timezone.now(),
        )
        MeetingNote.objects.create(session=session, title='A note')
        response = self.client.get(reverse('meetings:meeting_list'))
        self.assertContains(response, '1 note')


class MeetingCreateViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)

    def test_create_meeting(self):
        response = self.client.post(
            reverse('meetings:meeting_create'),
            {'title': '1:1 with manager', 'active': True},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Meeting.objects.filter(title='1:1 with manager').exists())

    def test_create_redirects_to_detail(self):
        response = self.client.post(
            reverse('meetings:meeting_create'),
            {'title': 'New meeting', 'active': True},
        )
        meeting = Meeting.objects.get(title='New meeting')
        self.assertRedirects(response, f'/meetings/{meeting.pk}/')


class MeetingDetailViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.meeting = Meeting.objects.create(title='Retrospective')

    def test_detail_shows_meeting(self):
        response = self.client.get(
            reverse('meetings:meeting_detail', kwargs={'pk': self.meeting.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Retrospective')

    def test_detail_shows_sessions(self):
        MeetingSession.objects.create(meeting=self.meeting, occurred_on='2026-03-01')
        response = self.client.get(
            reverse('meetings:meeting_detail', kwargs={'pk': self.meeting.pk})
        )
        self.assertContains(response, 'March 1, 2026')

    def test_detail_shows_unprocessed_count(self):
        session = MeetingSession.objects.create(
            meeting=self.meeting,
            occurred_on='2026-03-01',
            closed_at=timezone.now(),
        )
        MeetingNote.objects.create(session=session, title='Unprocessed note')
        response = self.client.get(
            reverse('meetings:meeting_detail', kwargs={'pk': self.meeting.pk})
        )
        self.assertContains(response, '1')

    def test_detail_shows_agenda_items(self):
        AgendaItem.objects.create(title='Discuss roadmap', meeting=self.meeting)
        response = self.client.get(
            reverse('meetings:meeting_detail', kwargs={'pk': self.meeting.pk})
        )
        self.assertContains(response, 'Discuss roadmap')


class SessionCreateViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.meeting = Meeting.objects.create(title='Standup')

    def test_get_shows_form(self):
        response = self.client.get(
            reverse('meetings:session_create', kwargs={'pk': self.meeting.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Standup')

    def test_post_creates_session(self):
        response = self.client.post(
            reverse('meetings:session_create', kwargs={'pk': self.meeting.pk}),
            {'occurred_on': '2026-06-26'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MeetingSession.objects.filter(meeting=self.meeting).exists())

    def test_post_redirects_to_session_detail(self):
        response = self.client.post(
            reverse('meetings:session_create', kwargs={'pk': self.meeting.pk}),
            {'occurred_on': '2026-06-26'},
        )
        session = MeetingSession.objects.get(meeting=self.meeting)
        self.assertRedirects(response, reverse('meetings:session_detail', kwargs={'pk': session.pk}))


class SessionDetailViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.meeting = Meeting.objects.create(title='Standup')
        self.session = MeetingSession.objects.create(
            meeting=self.meeting,
            occurred_on='2026-06-26',
        )

    def test_open_session_shows_capture_form(self):
        response = self.client.get(
            reverse('meetings:session_detail', kwargs={'pk': self.session.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Capture notes')

    def test_open_session_shows_agenda_items(self):
        AgendaItem.objects.create(title='Review sprint', meeting=self.meeting)
        response = self.client.get(
            reverse('meetings:session_detail', kwargs={'pk': self.session.pk})
        )
        self.assertContains(response, 'Review sprint')

    def test_closed_session_shows_process_queue(self):
        self.session.closed_at = timezone.now()
        self.session.save()
        MeetingNote.objects.create(session=self.session, title='Decision made')
        response = self.client.get(
            reverse('meetings:session_detail', kwargs={'pk': self.session.pk})
        )
        self.assertContains(response, 'Notes to process')
        self.assertContains(response, 'Decision made')

    def test_closed_session_shows_all_processed_when_done(self):
        self.session.closed_at = timezone.now()
        self.session.save()
        MeetingNote.objects.create(
            session=self.session,
            title='Done note',
            processed_at=timezone.now(),
            disposition=MeetingNote.Disposition.TRASHED,
        )
        response = self.client.get(
            reverse('meetings:session_detail', kwargs={'pk': self.session.pk})
        )
        self.assertContains(response, 'All notes processed')


class SessionCloseViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.meeting = Meeting.objects.create(title='Standup')
        self.session = MeetingSession.objects.create(
            meeting=self.meeting,
            occurred_on='2026-06-26',
        )

    def test_close_sets_closed_at(self):
        self.client.post(
            reverse('meetings:session_close', kwargs={'pk': self.session.pk})
        )
        self.session.refresh_from_db()
        self.assertIsNotNone(self.session.closed_at)

    def test_close_redirects_to_session_detail(self):
        response = self.client.post(
            reverse('meetings:session_close', kwargs={'pk': self.session.pk})
        )
        self.assertRedirects(response, reverse('meetings:session_detail', kwargs={'pk': self.session.pk}))

    def test_closing_already_closed_session_is_idempotent(self):
        original_time = timezone.now()
        self.session.closed_at = original_time
        self.session.save()
        self.client.post(
            reverse('meetings:session_close', kwargs={'pk': self.session.pk})
        )
        self.session.refresh_from_db()
        self.assertEqual(self.session.closed_at, original_time)


class QuickNoteViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.meeting = Meeting.objects.create(title='Standup')
        self.session = MeetingSession.objects.create(
            meeting=self.meeting,
            occurred_on='2026-06-26',
        )

    def test_quick_note_creates_note(self):
        self.client.post(
            reverse('meetings:quick_note', kwargs={'pk': self.session.pk}),
            {'title': 'Deploy by Friday'},
        )
        self.assertTrue(
            MeetingNote.objects.filter(session=self.session, title='Deploy by Friday').exists()
        )

    def test_quick_note_returns_html_partial(self):
        response = self.client.post(
            reverse('meetings:quick_note', kwargs={'pk': self.session.pk}),
            {'title': 'Action item'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Action item')

    def test_quick_note_does_not_create_on_closed_session(self):
        self.session.closed_at = timezone.now()
        self.session.save()
        self.client.post(
            reverse('meetings:quick_note', kwargs={'pk': self.session.pk}),
            {'title': 'Should not appear'},
        )
        self.assertFalse(MeetingNote.objects.filter(title='Should not appear').exists())

    def test_quick_note_ignores_blank_title(self):
        self.client.post(
            reverse('meetings:quick_note', kwargs={'pk': self.session.pk}),
            {'title': ''},
        )
        self.assertEqual(MeetingNote.objects.filter(session=self.session).count(), 0)


class NoteClarifyViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.meeting = Meeting.objects.create(title='Standup')
        self.session = MeetingSession.objects.create(
            meeting=self.meeting,
            occurred_on='2026-06-26',
            closed_at=timezone.now(),
        )
        self.note = MeetingNote.objects.create(session=self.session, title='Fix auth bug')

    def test_get_shows_note_title(self):
        response = self.client.get(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fix auth bug')

    def test_already_processed_returns_404(self):
        self.note.processed_at = timezone.now()
        self.note.save()
        response = self.client.get(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_trash_marks_processed(self):
        self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'trashed'},
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.disposition, MeetingNote.Disposition.TRASHED)
        self.assertIsNotNone(self.note.processed_at)

    def test_done_immediately_marks_processed(self):
        self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'done_immediately'},
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.disposition, MeetingNote.Disposition.DONE_IMMEDIATELY)

    def test_action_creates_next_action(self):
        self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'action', 'action_title': 'Fix auth bug'},
        )
        self.assertTrue(NextAction.objects.filter(title='Fix auth bug').exists())
        self.note.refresh_from_db()
        self.assertEqual(self.note.disposition, MeetingNote.Disposition.ACTION_CREATED)

    def test_someday_creates_someday_maybe(self):
        self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'someday'},
        )
        self.assertTrue(SomedayMaybe.objects.filter(title='Fix auth bug').exists())

    def test_delegate_requires_person_name(self):
        response = self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'delegate', 'person_name': ''},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter the name')

    def test_delegate_creates_waiting_for(self):
        self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'delegate', 'person_name': 'Alice'},
        )
        self.assertTrue(WaitingFor.objects.filter(title='Fix auth bug').exists())

    def test_add_to_project_creates_action_in_project(self):
        project = Project.objects.create(title='Auth overhaul', status=Project.Status.ACTIVE)
        self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'add_to_project', 'add_project_id': project.pk,
             'add_project_action_title': 'Fix auth bug'},
        )
        self.assertTrue(NextAction.objects.filter(title='Fix auth bug', project=project).exists())

    def test_project_creates_project(self):
        self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'project', 'project_title': 'Auth overhaul',
             'first_action_title': 'Audit existing code'},
        )
        self.assertTrue(Project.objects.filter(title='Auth overhaul').exists())
        self.assertTrue(NextAction.objects.filter(title='Audit existing code').exists())

    def test_redirect_to_session_after_processing(self):
        response = self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'trashed'},
        )
        self.assertRedirects(
            response,
            reverse('meetings:session_detail', kwargs={'pk': self.session.pk}),
        )

    def test_redirect_to_project_detail_when_project_created(self):
        response = self.client.post(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk}),
            {'disposition': 'project', 'project_title': 'New project', 'first_action_title': ''},
        )
        project = Project.objects.get(title='New project')
        self.assertRedirects(response, reverse('gtd:project_detail', kwargs={'pk': project.pk}))

    def test_context_includes_active_projects(self):
        Project.objects.create(title='Active proj', status=Project.Status.ACTIVE)
        response = self.client.get(
            reverse('meetings:note_clarify', kwargs={'pk': self.note.pk})
        )
        self.assertContains(response, 'Active proj')


class PendingNotesCountTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)

    def test_pending_notes_count_in_nav(self):
        meeting = Meeting.objects.create(title='Standup')
        session = MeetingSession.objects.create(
            meeting=meeting,
            occurred_on='2026-06-26',
            closed_at=timezone.now(),
        )
        MeetingNote.objects.create(session=session, title='Process me')
        response = self.client.get(reverse('meetings:meeting_list'))
        self.assertContains(response, 'nav-notes-count')

    def test_no_badge_when_no_pending_notes(self):
        response = self.client.get(reverse('meetings:meeting_list'))
        self.assertNotContains(response, 'nav-notes-count')
