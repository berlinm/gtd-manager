from datetime import date, datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.gtd.models import (
    AgendaItem, Meeting, NextAction, Person, Project,
    SomedayMaybe, WaitingFor,
)


def aware_dt(d):
    """Return a timezone-aware datetime at midnight on the given date."""
    return timezone.make_aware(datetime.combine(d, datetime.min.time()))


today = date.today
tomorrow = lambda: date.today() + timedelta(days=1)
yesterday = lambda: date.today() - timedelta(days=1)


# ---------------------------------------------------------------------------
# NextAction
# ---------------------------------------------------------------------------

class NextActionDateValidationTests(TestCase):

    def test_no_dates_is_valid(self):
        NextAction(title='Test').full_clean()

    def test_defer_until_alone_is_valid(self):
        NextAction(title='Test', defer_until=today()).full_clean()

    def test_scheduled_for_alone_is_valid(self):
        NextAction(title='Test', scheduled_for=aware_dt(today())).full_clean()

    def test_deadline_alone_is_valid(self):
        NextAction(title='Test', deadline=today()).full_clean()

    def test_defer_until_before_scheduled_for_is_valid(self):
        NextAction(
            title='Test',
            defer_until=today(),
            scheduled_for=aware_dt(tomorrow()),
        ).full_clean()

    def test_scheduled_for_before_defer_until_raises(self):
        action = NextAction(
            title='Test',
            defer_until=today(),
            scheduled_for=aware_dt(yesterday()),
        )
        with self.assertRaises(ValidationError) as cm:
            action.full_clean()
        self.assertIn('scheduled_for', cm.exception.message_dict)

    def test_deadline_before_scheduled_for_raises(self):
        action = NextAction(
            title='Test',
            scheduled_for=aware_dt(tomorrow()),
            deadline=today(),
        )
        with self.assertRaises(ValidationError) as cm:
            action.full_clean()
        self.assertIn('deadline', cm.exception.message_dict)

    def test_deadline_equal_to_defer_until_raises(self):
        # deadline must be AFTER defer_until, not equal
        action = NextAction(title='Test', defer_until=today(), deadline=today())
        with self.assertRaises(ValidationError) as cm:
            action.full_clean()
        self.assertIn('deadline', cm.exception.message_dict)

    def test_deadline_after_defer_until_is_valid(self):
        NextAction(
            title='Test',
            defer_until=today(),
            deadline=tomorrow(),
        ).full_clean()

    def test_all_three_dates_in_order_is_valid(self):
        d = today()
        NextAction(
            title='Test',
            defer_until=d,
            scheduled_for=aware_dt(d + timedelta(days=1)),
            deadline=d + timedelta(days=2),
        ).full_clean()


class NextActionStatusValidationTests(TestCase):

    def test_done_without_completed_at_raises(self):
        action = NextAction(title='Test', status=NextAction.Status.DONE)
        with self.assertRaises(ValidationError):
            action.full_clean()

    def test_cancelled_without_completed_at_raises(self):
        action = NextAction(title='Test', status=NextAction.Status.CANCELLED)
        with self.assertRaises(ValidationError):
            action.full_clean()

    def test_active_with_completed_at_raises(self):
        action = NextAction(
            title='Test',
            status=NextAction.Status.ACTIVE,
            completed_at=timezone.now(),
        )
        with self.assertRaises(ValidationError):
            action.full_clean()

    def test_done_with_completed_at_is_valid(self):
        NextAction(
            title='Test',
            status=NextAction.Status.DONE,
            completed_at=timezone.now(),
        ).full_clean()


class NextActionAvailabilityTests(TestCase):

    def test_available_when_no_defer_until(self):
        self.assertTrue(NextAction(title='Test').is_available)

    def test_available_when_defer_until_is_today(self):
        self.assertTrue(NextAction(title='Test', defer_until=today()).is_available)

    def test_not_available_when_defer_until_is_tomorrow(self):
        self.assertFalse(NextAction(title='Test', defer_until=tomorrow()).is_available)

    def test_not_deferred_when_no_defer_until(self):
        self.assertFalse(NextAction(title='Test').is_deferred)

    def test_deferred_when_defer_until_is_tomorrow(self):
        self.assertTrue(NextAction(title='Test', defer_until=tomorrow()).is_deferred)

    def test_not_deferred_when_defer_until_is_today(self):
        self.assertFalse(NextAction(title='Test', defer_until=today()).is_deferred)


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class ProjectValidationTests(TestCase):

    def test_active_project_is_valid(self):
        Project(title='Test').full_clean()

    def test_on_hold_without_reason_raises(self):
        project = Project(title='Test', status=Project.Status.ON_HOLD)
        with self.assertRaises(ValidationError) as cm:
            project.full_clean()
        self.assertIn('on_hold_reason', cm.exception.message_dict)

    def test_on_hold_with_reason_is_valid(self):
        Project(
            title='Test',
            status=Project.Status.ON_HOLD,
            on_hold_reason='Blocked on budget approval',
        ).full_clean()

    def test_completed_without_completed_at_raises(self):
        project = Project(title='Test', status=Project.Status.COMPLETED)
        with self.assertRaises(ValidationError) as cm:
            project.full_clean()
        self.assertIn('completed_at', cm.exception.message_dict)

    def test_cancelled_without_completed_at_raises(self):
        project = Project(title='Test', status=Project.Status.CANCELLED)
        with self.assertRaises(ValidationError) as cm:
            project.full_clean()
        self.assertIn('completed_at', cm.exception.message_dict)

    def test_active_with_completed_at_raises(self):
        project = Project(
            title='Test',
            status=Project.Status.ACTIVE,
            completed_at=timezone.now(),
        )
        with self.assertRaises(ValidationError) as cm:
            project.full_clean()
        self.assertIn('completed_at', cm.exception.message_dict)


class ProjectStuckTests(TestCase):

    def test_stuck_when_active_and_no_actions(self):
        project = Project.objects.create(title='Test')
        self.assertTrue(project.is_stuck)

    def test_not_stuck_when_has_active_next_action(self):
        project = Project.objects.create(title='Test')
        NextAction.objects.create(title='Step 1', project=project)
        self.assertFalse(project.is_stuck)

    def test_not_stuck_when_done_action_only(self):
        # Done actions do not count — project should still be stuck
        project = Project.objects.create(title='Test')
        NextAction.objects.create(
            title='Step 1',
            project=project,
            status=NextAction.Status.DONE,
            completed_at=timezone.now(),
        )
        self.assertTrue(project.is_stuck)

    def test_not_stuck_when_has_waiting_for(self):
        project = Project.objects.create(title='Test')
        person = Person.objects.create(name='Alice')
        WaitingFor.objects.create(title='Waiting', person=person, project=project)
        self.assertFalse(project.is_stuck)

    def test_not_stuck_when_status_is_on_hold(self):
        project = Project.objects.create(
            title='Test',
            status=Project.Status.ON_HOLD,
            on_hold_reason='Blocked',
        )
        self.assertFalse(project.is_stuck)

    def test_not_stuck_when_status_is_completed(self):
        project = Project.objects.create(
            title='Test',
            status=Project.Status.COMPLETED,
            completed_at=timezone.now(),
        )
        self.assertFalse(project.is_stuck)


# ---------------------------------------------------------------------------
# AgendaItem
# ---------------------------------------------------------------------------

class AgendaItemValidationTests(TestCase):

    def setUp(self):
        self.person = Person.objects.create(name='Alice')
        self.meeting = Meeting.objects.create(title='Weekly standup')

    def test_person_only_is_valid(self):
        AgendaItem(title='Discuss budget', person=self.person).full_clean()

    def test_meeting_only_is_valid(self):
        AgendaItem(title='Review Q3 results', meeting=self.meeting).full_clean()

    def test_neither_person_nor_meeting_raises(self):
        with self.assertRaises(ValidationError):
            AgendaItem(title='Orphan item').full_clean()

    def test_both_person_and_meeting_raises(self):
        with self.assertRaises(ValidationError):
            AgendaItem(
                title='Ambiguous item',
                person=self.person,
                meeting=self.meeting,
            ).full_clean()


# ---------------------------------------------------------------------------
# SomedayMaybe
# ---------------------------------------------------------------------------

class SomedayMaybeValidationTests(TestCase):

    def test_unpromoted_is_valid(self):
        SomedayMaybe(title='Learn Spanish').full_clean()

    def test_promoted_at_without_project_raises(self):
        item = SomedayMaybe(title='Learn Spanish', promoted_at=timezone.now())
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_project_without_promoted_at_raises(self):
        project = Project.objects.create(title='Learn Spanish project')
        item = SomedayMaybe(title='Learn Spanish', promoted_to_project=project)
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_both_set_is_valid(self):
        project = Project.objects.create(title='Learn Spanish project')
        SomedayMaybe(
            title='Learn Spanish',
            promoted_at=timezone.now(),
            promoted_to_project=project,
        ).full_clean()


# ---------------------------------------------------------------------------
# WaitingFor
# ---------------------------------------------------------------------------

class WaitingForValidationTests(TestCase):

    def setUp(self):
        self.person = Person.objects.create(name='Bob')

    def test_waiting_is_valid(self):
        WaitingFor(title='Code review', person=self.person).full_clean()

    def test_received_without_completed_at_raises(self):
        item = WaitingFor(
            title='Code review',
            person=self.person,
            status=WaitingFor.Status.RECEIVED,
        )
        with self.assertRaises(ValidationError) as cm:
            item.full_clean()
        self.assertIn('completed_at', cm.exception.message_dict)

    def test_cancelled_without_completed_at_raises(self):
        item = WaitingFor(
            title='Code review',
            person=self.person,
            status=WaitingFor.Status.CANCELLED,
        )
        with self.assertRaises(ValidationError) as cm:
            item.full_clean()
        self.assertIn('completed_at', cm.exception.message_dict)

    def test_waiting_with_completed_at_raises(self):
        item = WaitingFor(
            title='Code review',
            person=self.person,
            status=WaitingFor.Status.WAITING,
            completed_at=timezone.now(),
        )
        with self.assertRaises(ValidationError) as cm:
            item.full_clean()
        self.assertIn('completed_at', cm.exception.message_dict)

    def test_received_with_completed_at_is_valid(self):
        WaitingFor(
            title='Code review',
            person=self.person,
            status=WaitingFor.Status.RECEIVED,
            completed_at=timezone.now(),
        ).full_clean()
