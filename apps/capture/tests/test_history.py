from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.capture.models import InboxItem
from apps.gtd.models import NextAction, Project


class InboxHistoryViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)

    def test_empty_history_shows_message(self):
        response = self.client.get(reverse('capture:history'))
        self.assertContains(response, 'No processed items')

    def test_unprocessed_items_not_shown(self):
        InboxItem.objects.create(title='Still in inbox')
        response = self.client.get(reverse('capture:history'))
        self.assertNotContains(response, 'Still in inbox')

    def test_processed_item_appears_with_disposition(self):
        item = InboxItem.objects.create(
            title='Old thought',
            processed_at=timezone.now(),
            disposition=InboxItem.Disposition.TRASHED,
        )
        response = self.client.get(reverse('capture:history'))
        self.assertContains(response, 'Old thought')
        self.assertContains(response, 'Trashed')

    def test_action_link_shown_for_action_created(self):
        action = NextAction.objects.create(title='Do the thing')
        item = InboxItem.objects.create(title='Do the thing', processed_at=timezone.now())
        from django.contrib.contenttypes.models import ContentType
        item.content_type = ContentType.objects.get_for_model(action)
        item.object_id = action.pk
        item.disposition = InboxItem.Disposition.ACTION_CREATED
        item.save()
        response = self.client.get(reverse('capture:history'))
        self.assertContains(response, reverse('gtd:action_edit', kwargs={'pk': action.pk}))

    def test_project_link_shown_for_project_created(self):
        project = Project.objects.create(title='Big plan')
        item = InboxItem.objects.create(title='Big plan', processed_at=timezone.now())
        from django.contrib.contenttypes.models import ContentType
        item.content_type = ContentType.objects.get_for_model(project)
        item.object_id = project.pk
        item.disposition = InboxItem.Disposition.PROJECT_CREATED
        item.save()
        response = self.client.get(reverse('capture:history'))
        self.assertContains(response, reverse('gtd:project_detail', kwargs={'pk': project.pk}))

    def test_history_link_accessible_from_inbox(self):
        response = self.client.get(reverse('capture:inbox'))
        self.assertContains(response, reverse('capture:history'))

    def test_clarify_reference_redirects_to_reference_detail(self):
        item = InboxItem.objects.create(title='Some notes')
        url = reverse('capture:clarify', kwargs={'pk': item.pk})
        response = self.client.post(url, {'disposition': 'reference'})
        from apps.gtd.models import Reference
        ref = Reference.objects.get()
        self.assertRedirects(
            response,
            reverse('gtd:reference_detail', kwargs={'pk': ref.pk}),
        )
