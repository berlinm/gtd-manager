from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.capture.models import InboxItem
from apps.gtd.models import NextAction, Project, SomedayMaybe, WaitingFor


class ClarifyViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.item = InboxItem.objects.create(title='Buy milk')

    # --- access control ---

    def test_get_shows_item_title(self):
        response = self.client.get(
            reverse('capture:clarify', kwargs={'pk': self.item.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buy milk')

    def test_already_processed_item_returns_404(self):
        self.item.processed_at = timezone.now()
        self.item.save()
        response = self.client.get(
            reverse('capture:clarify', kwargs={'pk': self.item.pk})
        )
        self.assertEqual(response.status_code, 404)

    # --- trash ---

    def test_trash_marks_item_processed(self):
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        response = self.client.post(url, {'disposition': 'trashed'})
        self.assertRedirects(response, reverse('capture:inbox'))
        self.item.refresh_from_db()
        self.assertIsNotNone(self.item.processed_at)
        self.assertEqual(self.item.disposition, InboxItem.Disposition.TRASHED)

    # --- done immediately ---

    def test_done_immediately_marks_item_processed(self):
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        self.client.post(url, {'disposition': 'done_immediately'})
        self.item.refresh_from_db()
        self.assertEqual(self.item.disposition, InboxItem.Disposition.DONE_IMMEDIATELY)
        self.assertIsNotNone(self.item.processed_at)

    # --- delegate ---

    def test_delegate_without_person_name_shows_error(self):
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        response = self.client.post(url, {'disposition': 'delegate', 'person_name': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter the name')
        self.item.refresh_from_db()
        self.assertIsNone(self.item.processed_at)  # not processed

    def test_delegate_creates_waiting_for_and_redirects(self):
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        response = self.client.post(
            url, {'disposition': 'delegate', 'person_name': 'Alice'}
        )
        self.assertRedirects(response, reverse('gtd:waiting_for_list'))
        self.item.refresh_from_db()
        self.assertIsNotNone(self.item.processed_at)
        self.assertEqual(self.item.disposition, InboxItem.Disposition.DELEGATED)
        wf = WaitingFor.objects.get()
        self.assertEqual(wf.title, 'Buy milk')
        self.assertEqual(wf.person.name, 'Alice')
        self.assertEqual(wf.status, WaitingFor.Status.WAITING)

    def test_delegate_reuses_existing_person(self):
        from apps.gtd.models import Person
        existing = Person.objects.create(name='Alice')
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        self.client.post(url, {'disposition': 'delegate', 'person_name': 'Alice'})
        # Should not have created a duplicate Person
        self.assertEqual(Person.objects.filter(name='Alice').count(), 1)

    # --- action ---

    def test_action_creates_next_action_and_redirects(self):
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        response = self.client.post(
            url, {'disposition': 'action', 'action_title': 'Go to the shop'}
        )
        self.assertRedirects(response, reverse('gtd:next_actions'))
        action = NextAction.objects.get()
        self.assertEqual(action.title, 'Go to the shop')
        self.assertEqual(action.status, NextAction.Status.ACTIVE)
        self.item.refresh_from_db()
        self.assertEqual(self.item.disposition, InboxItem.Disposition.ACTION_CREATED)

    def test_action_falls_back_to_item_title_when_action_title_empty(self):
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        self.client.post(url, {'disposition': 'action', 'action_title': ''})
        self.assertEqual(NextAction.objects.get().title, 'Buy milk')

    # --- project ---

    def test_project_creates_project_first_action_and_redirects(self):
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        response = self.client.post(url, {
            'disposition': 'project',
            'project_title': 'Stock the kitchen',
            'desired_outcome': 'Kitchen is fully stocked',
            'first_action_title': 'Write a shopping list',
        })
        project = Project.objects.get()
        self.assertRedirects(
            response,
            reverse('gtd:project_detail', kwargs={'pk': project.pk}),
        )
        self.assertEqual(project.title, 'Stock the kitchen')
        self.assertEqual(project.desired_outcome, 'Kitchen is fully stocked')
        action = NextAction.objects.get(project=project)
        self.assertEqual(action.title, 'Write a shopping list')

    def test_project_without_first_action_creates_project_only(self):
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        self.client.post(url, {
            'disposition': 'project',
            'project_title': 'Stock the kitchen',
            'first_action_title': '',
        })
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(NextAction.objects.count(), 0)

    # --- someday ---

    def test_someday_creates_someday_item(self):
        url = reverse('capture:clarify', kwargs={'pk': self.item.pk})
        response = self.client.post(url, {'disposition': 'someday'})
        self.assertRedirects(response, reverse('capture:inbox'))
        someday = SomedayMaybe.objects.get()
        self.assertEqual(someday.title, 'Buy milk')
        self.item.refresh_from_db()
        self.assertEqual(self.item.disposition, InboxItem.Disposition.SOMEDAY_CREATED)
