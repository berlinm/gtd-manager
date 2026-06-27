from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.gtd.models import NextAction, Person, Project, SomedayMaybe, WaitingFor


class NextActionWorkflowTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)

    def test_list_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('gtd:next_actions'))
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_list_hides_deferred_actions(self):
        from datetime import timedelta
        NextAction.objects.create(title='Available now')
        NextAction.objects.create(
            title='Deferred',
            defer_until=date.today() + timedelta(days=3),
        )
        response = self.client.get(reverse('gtd:next_actions'))
        self.assertContains(response, 'Available now')
        self.assertNotContains(response, 'Deferred')

    def test_done_marks_action_complete(self):
        action = NextAction.objects.create(title='Do something')
        self.client.post(reverse('gtd:action_done', kwargs={'pk': action.pk}))
        action.refresh_from_db()
        self.assertEqual(action.status, NextAction.Status.DONE)
        self.assertIsNotNone(action.completed_at)

    def test_cancel_marks_action_cancelled(self):
        action = NextAction.objects.create(title='Do something')
        self.client.post(reverse('gtd:action_cancel', kwargs={'pk': action.pk}))
        action.refresh_from_db()
        self.assertEqual(action.status, NextAction.Status.CANCELLED)
        self.assertIsNotNone(action.completed_at)

    def test_delegate_cancels_action_and_creates_waiting_for(self):
        action = NextAction.objects.create(title='Write the report')
        person = Person.objects.create(name='Charlie')
        self.client.post(
            reverse('gtd:action_delegate', kwargs={'pk': action.pk}),
            {
                'title': 'Write the report',
                'person': person.pk,
                'delegated_at': date.today().isoformat(),
            },
        )
        action.refresh_from_db()
        self.assertEqual(action.status, NextAction.Status.CANCELLED)
        wf = WaitingFor.objects.get()
        self.assertEqual(wf.person, person)
        self.assertEqual(wf.status, WaitingFor.Status.WAITING)

    def test_delegate_cannot_act_on_done_action(self):
        action = NextAction.objects.create(
            title='Already done',
            status=NextAction.Status.DONE,
            completed_at=timezone.now(),
        )
        response = self.client.get(
            reverse('gtd:action_delegate', kwargs={'pk': action.pk})
        )
        self.assertEqual(response.status_code, 404)


class WaitingForWorkflowTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.person = Person.objects.create(name='Dave')

    def test_list_only_shows_waiting_items(self):
        WaitingFor.objects.create(title='Active item', person=self.person)
        WaitingFor.objects.create(
            title='Received item',
            person=self.person,
            status=WaitingFor.Status.RECEIVED,
            completed_at=timezone.now(),
        )
        response = self.client.get(reverse('gtd:waiting_for_list'))
        self.assertContains(response, 'Active item')
        self.assertNotContains(response, 'Received item')

    def test_receive_marks_item_received(self):
        wf = WaitingFor.objects.create(title='Report from Dave', person=self.person)
        self.client.post(
            reverse('gtd:waiting_for_receive', kwargs={'pk': wf.pk}),
            {'result_notes': 'Got it, looks good.'},
        )
        wf.refresh_from_db()
        self.assertEqual(wf.status, WaitingFor.Status.RECEIVED)
        self.assertIsNotNone(wf.completed_at)
        self.assertEqual(wf.result_notes, 'Got it, looks good.')

    def test_cancel_marks_item_cancelled(self):
        wf = WaitingFor.objects.create(title='Report from Dave', person=self.person)
        self.client.post(reverse('gtd:waiting_for_cancel', kwargs={'pk': wf.pk}))
        wf.refresh_from_db()
        self.assertEqual(wf.status, WaitingFor.Status.CANCELLED)
        self.assertIsNotNone(wf.completed_at)

    def test_receive_already_received_item_returns_404(self):
        wf = WaitingFor.objects.create(
            title='Already received',
            person=self.person,
            status=WaitingFor.Status.RECEIVED,
            completed_at=timezone.now(),
        )
        response = self.client.get(
            reverse('gtd:waiting_for_receive', kwargs={'pk': wf.pk})
        )
        self.assertEqual(response.status_code, 404)


class SomedayPromoteTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)

    def test_promote_creates_project_and_marks_item_promoted(self):
        item = SomedayMaybe.objects.create(title='Learn woodworking')
        self.client.post(
            reverse('gtd:someday_promote', kwargs={'pk': item.pk}),
            {
                'project_title': 'Learn woodworking',
                'desired_outcome': 'Build a bookshelf',
                'first_action_title': 'Buy a saw',
            },
        )
        item.refresh_from_db()
        self.assertIsNotNone(item.promoted_at)
        self.assertIsNotNone(item.promoted_to_project)
        project = item.promoted_to_project
        self.assertEqual(project.title, 'Learn woodworking')
        self.assertEqual(NextAction.objects.filter(project=project).count(), 1)
        self.assertEqual(NextAction.objects.get(project=project).title, 'Buy a saw')

    def test_promoted_item_not_in_someday_list(self):
        item = SomedayMaybe.objects.create(title='Learn woodworking')
        self.client.post(
            reverse('gtd:someday_promote', kwargs={'pk': item.pk}),
            {'project_title': 'Learn woodworking'},
        )
        response = self.client.get(reverse('gtd:someday_list'))
        self.assertNotContains(response, 'Learn woodworking')

    def test_promote_already_promoted_item_returns_404(self):
        project = Project.objects.create(title='Already a project')
        item = SomedayMaybe.objects.create(
            title='Learn woodworking',
            promoted_at=timezone.now(),
            promoted_to_project=project,
        )
        response = self.client.get(
            reverse('gtd:someday_promote', kwargs={'pk': item.pk})
        )
        self.assertEqual(response.status_code, 404)
