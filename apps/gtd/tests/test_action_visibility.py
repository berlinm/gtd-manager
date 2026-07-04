from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.capture.models import InboxItem
from apps.gtd.models import NextAction


class DatedActionVisibilityTests(TestCase):
    """Regression guard for the clarify-with-date bug: a dated action must
    remain visible on the Next Actions page, never silently disappear."""

    def setUp(self):
        self.user = User.objects.create_user(username='t', password='p')
        self.client.force_login(self.user)

    def _clarify_as_action(self, title, **fields):
        item = InboxItem.objects.create(title=title)
        data = {'disposition': 'action', 'action_title': title}
        data.update(fields)
        self.client.post(reverse('capture:clarify', kwargs={'pk': item.pk}), data)
        return NextAction.objects.get(title=title)

    def test_clarify_with_scheduled_for_appears_in_list(self):
        dt = f'{(date.today() + timedelta(days=3)).isoformat()}T14:30'
        self._clarify_as_action('Scheduled task', action_scheduled_for=dt)
        html = self.client.get(reverse('gtd:next_actions')).content.decode()
        self.assertIn('Scheduled task', html)

    def test_clarify_with_deadline_appears_in_list(self):
        d = (date.today() + timedelta(days=10)).isoformat()
        self._clarify_as_action('Deadline task', action_deadline=d)
        html = self.client.get(reverse('gtd:next_actions')).content.decode()
        self.assertIn('Deadline task', html)

    def test_clarify_form_has_no_defer_until_field(self):
        item = InboxItem.objects.create(title='x')
        html = self.client.get(reverse('capture:clarify', kwargs={'pk': item.pk})).content.decode()
        # the removed footgun: defer_until must not be offered at clarify time
        self.assertNotIn('action_defer_until', html)
        self.assertNotIn('add_defer_until', html)

    def test_future_deferred_action_appears_in_deferred_section(self):
        """A future defer_until (settable via the edit form) must not make the
        action invisible — it belongs in the Deferred section."""
        NextAction.objects.create(
            title='Future deferred task',
            defer_until=date.today() + timedelta(days=14),
        )
        resp = self.client.get(reverse('gtd:next_actions'))
        html = resp.content.decode()
        self.assertIn('Future deferred task', html)
        self.assertIn('Deferred', html)
        self.assertIn('Future deferred task', [a.title for a in resp.context['deferred_actions']])

    def test_available_action_not_in_deferred_section(self):
        NextAction.objects.create(title='Available now')
        resp = self.client.get(reverse('gtd:next_actions'))
        self.assertNotIn('Available now', [a.title for a in resp.context['deferred_actions']])
