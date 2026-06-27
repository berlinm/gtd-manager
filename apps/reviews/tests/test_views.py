from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.capture.models import InboxItem
from apps.gtd.models import NextAction, Person, Project, WaitingFor
from apps.reviews.models import DailyReview, WeeklyReview
from apps.reviews.views import FOCUS_SESSION_KEY


class DailyReviewViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.url = reverse('reviews:daily_review')

    def test_get_renders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Daily Review')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_inbox_count_shown(self):
        InboxItem.objects.create(title='Unprocessed item')
        response = self.client.get(self.url)
        self.assertContains(response, '1 unprocessed item')

    def test_scheduled_today_shown(self):
        now = timezone.now()
        NextAction.objects.create(title='Morning call', scheduled_for=now)
        response = self.client.get(self.url)
        self.assertContains(response, 'Morning call')

    def test_deadline_action_shown(self):
        today = date.today()
        NextAction.objects.create(title='File report', deadline=today)
        response = self.client.get(self.url)
        self.assertContains(response, 'File report')

    def test_follow_up_due_shown(self):
        person = Person.objects.create(name='Alice')
        yesterday = date.today() - timedelta(days=1)
        WaitingFor.objects.create(
            title='Budget approval',
            person=person,
            follow_up_on=yesterday,
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Budget approval')

    def test_stuck_project_shown(self):
        p = Project.objects.create(title='Stuck project')
        response = self.client.get(self.url)
        self.assertContains(response, 'Stuck project')

    def test_post_creates_daily_review(self):
        self.assertEqual(DailyReview.objects.count(), 0)
        response = self.client.post(self.url, {'notes': 'Quiet day'})
        self.assertEqual(DailyReview.objects.count(), 1)
        self.assertEqual(DailyReview.objects.first().notes, 'Quiet day')
        self.assertRedirects(response, '/')

    def test_post_with_focus_stores_in_session(self):
        action = NextAction.objects.create(title='Write proposal')
        self.client.post(self.url, {'focus_pks': [str(action.pk)]})
        session = self.client.session
        self.assertIn(FOCUS_SESSION_KEY, session)
        self.assertEqual(session[FOCUS_SESSION_KEY], [action.pk])

    def test_post_with_focus_redirects_to_focus_list(self):
        action = NextAction.objects.create(title='Write proposal')
        response = self.client.post(self.url, {'focus_pks': [str(action.pk)]})
        self.assertRedirects(response, reverse('reviews:focus_list'))

    def test_post_without_focus_redirects_to_dashboard(self):
        response = self.client.post(self.url, {})
        self.assertRedirects(response, '/')

    def test_existing_focus_shown_checked(self):
        action = NextAction.objects.create(title='Focused action')
        session = self.client.session
        session[FOCUS_SESSION_KEY] = [action.pk]
        session.save()
        response = self.client.get(self.url)
        self.assertContains(response, 'checked')


class FocusListViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.url = reverse('reviews:focus_list')

    def test_get_renders_with_empty_focus(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_shows_focused_actions(self):
        action = NextAction.objects.create(title='Priority task')
        session = self.client.session
        session[FOCUS_SESSION_KEY] = [action.pk]
        session.save()
        response = self.client.get(self.url)
        self.assertContains(response, 'Priority task')

    def test_does_not_show_completed_action(self):
        action = NextAction.objects.create(
            title='Old task',
            status=NextAction.Status.DONE,
            completed_at=timezone.now(),
        )
        session = self.client.session
        session[FOCUS_SESSION_KEY] = [action.pk]
        session.save()
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Old task')

    def test_post_clears_focus_and_redirects(self):
        action = NextAction.objects.create(title='Task')
        session = self.client.session
        session[FOCUS_SESSION_KEY] = [action.pk]
        session.save()
        response = self.client.post(self.url)
        self.assertRedirects(response, '/')
        self.assertNotIn(FOCUS_SESSION_KEY, self.client.session)


class WeeklyReviewViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.url = reverse('reviews:weekly_review')

    def test_get_renders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Weekly Review')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_stuck_project_shown(self):
        Project.objects.create(title='Empty project')
        response = self.client.get(self.url)
        self.assertContains(response, 'Empty project')

    def test_on_hold_project_shown(self):
        Project.objects.create(
            title='Paused initiative',
            status=Project.Status.ON_HOLD,
            on_hold_reason='Waiting for budget',
            completed_at=None,
        )
        response = self.client.get(self.url)
        self.assertContains(response, 'Paused initiative')

    def test_waiting_no_followup_shown(self):
        person = Person.objects.create(name='Bob')
        WaitingFor.objects.create(title='Contract review', person=person)
        response = self.client.get(self.url)
        self.assertContains(response, 'Contract review')

    def test_post_creates_weekly_review(self):
        self.assertEqual(WeeklyReview.objects.count(), 0)
        response = self.client.post(self.url, {'notes': 'Good week'})
        self.assertEqual(WeeklyReview.objects.count(), 1)
        self.assertEqual(WeeklyReview.objects.first().notes, 'Good week')
        self.assertRedirects(response, reverse('reviews:review_history'))


class ReviewHistoryViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.url = reverse('reviews:review_history')

    def test_get_renders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_shows_daily_review(self):
        DailyReview.objects.create(notes='Morning check')
        response = self.client.get(self.url)
        self.assertContains(response, 'Morning check')

    def test_shows_weekly_review(self):
        WeeklyReview.objects.create(notes='Solid week')
        response = self.client.get(self.url)
        self.assertContains(response, 'Solid week')
