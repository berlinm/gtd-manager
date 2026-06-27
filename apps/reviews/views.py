from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import View

from apps.capture.models import InboxItem
from apps.gtd.models import AgendaItem, NextAction, Project, SomedayMaybe, WaitingFor
from apps.meetings.models import MeetingNote

from .models import DailyReview, WeeklyReview

FOCUS_SESSION_KEY = 'gtd_focus_pks'


class DailyReviewView(LoginRequiredMixin, View):
    template_name = 'reviews/daily_review.html'

    def get(self, request):
        today = timezone.now().date()
        horizon = today + timedelta(days=7)

        inbox_count = InboxItem.objects.filter(processed_at__isnull=True).count()

        scheduled_today = (
            NextAction.objects.filter(
                status=NextAction.Status.ACTIVE,
                scheduled_for__date=today,
            )
            .select_related('project')
            .order_by('scheduled_for')
        )

        deadline_actions = (
            NextAction.objects.filter(
                status=NextAction.Status.ACTIVE,
                deadline__lte=horizon,
            )
            .select_related('project')
            .order_by('deadline')
        )

        deadline_projects = Project.objects.filter(
            status=Project.Status.ACTIVE,
            deadline__lte=horizon,
        ).order_by('deadline')

        follow_ups_due = (
            WaitingFor.objects.filter(
                status=WaitingFor.Status.WAITING,
                follow_up_on__lte=today,
            )
            .select_related('person', 'project')
        )

        available_actions = (
            NextAction.objects.filter(status=NextAction.Status.ACTIVE)
            .filter(Q(defer_until__isnull=True) | Q(defer_until__lte=today))
            .select_related('project')
            .order_by('deadline', '-created_at')
        )

        stuck_projects = [
            p for p in Project.objects.filter(status=Project.Status.ACTIVE)
            .prefetch_related('nextaction_set', 'waitingfor_set')
            if p.is_stuck
        ]

        focus_pks = request.session.get(FOCUS_SESSION_KEY, [])

        return render(request, self.template_name, {
            'inbox_count': inbox_count,
            'scheduled_today': scheduled_today,
            'deadline_actions': deadline_actions,
            'deadline_projects': deadline_projects,
            'follow_ups_due': follow_ups_due,
            'available_actions': available_actions,
            'stuck_projects': stuck_projects,
            'today': today,
            'focus_pks': focus_pks,
        })

    def post(self, request):
        notes = request.POST.get('notes', '')
        raw = request.POST.getlist('focus_pks')
        try:
            focus_pks = [int(pk) for pk in raw if str(pk).strip()]
        except ValueError:
            focus_pks = []

        request.session[FOCUS_SESSION_KEY] = focus_pks
        DailyReview.objects.create(notes=notes)

        if focus_pks:
            return redirect('reviews:focus_list')
        return redirect('dashboard')


class FocusListView(LoginRequiredMixin, View):
    template_name = 'reviews/focus_list.html'

    def get(self, request):
        pks = request.session.get(FOCUS_SESSION_KEY, [])
        actions = (
            NextAction.objects.filter(pk__in=pks, status=NextAction.Status.ACTIVE)
            .select_related('project')
        ) if pks else NextAction.objects.none()
        return render(request, self.template_name, {'focus_actions': actions})

    def post(self, request):
        request.session.pop(FOCUS_SESSION_KEY, None)
        return redirect('dashboard')


class WeeklyReviewView(LoginRequiredMixin, View):
    template_name = 'reviews/weekly_review.html'

    def get(self, request):
        today = timezone.now().date()
        horizon_2w = today + timedelta(days=14)
        horizon_1w = today + timedelta(days=7)

        inbox_count = InboxItem.objects.filter(processed_at__isnull=True).count()
        pending_notes_count = MeetingNote.objects.filter(
            processed_at__isnull=True,
            session__closed_at__isnull=False,
        ).count()

        active_projects = list(
            Project.objects.filter(status=Project.Status.ACTIVE)
            .prefetch_related('nextaction_set', 'waitingfor_set')
            .order_by('title')
        )
        stuck_projects = [p for p in active_projects if p.is_stuck]
        ok_projects = [p for p in active_projects if not p.is_stuck]

        on_hold_projects = Project.objects.filter(
            status=Project.Status.ON_HOLD
        ).order_by('next_review_on', 'title')

        deadline_projects = Project.objects.filter(
            status=Project.Status.ACTIVE,
            deadline__lte=horizon_2w,
        ).order_by('deadline')

        waiting_needs_attention = WaitingFor.objects.filter(
            status=WaitingFor.Status.WAITING,
        ).filter(
            Q(follow_up_on__lte=today) | Q(follow_up_on__isnull=True)
        ).select_related('person', 'project').order_by('follow_up_on')

        someday_count = SomedayMaybe.objects.filter(promoted_at__isnull=True).count()

        agenda_count = AgendaItem.objects.count()

        upcoming_actions = (
            NextAction.objects.filter(
                status=NextAction.Status.ACTIVE,
            )
            .filter(
                Q(scheduled_for__date__lte=horizon_1w, scheduled_for__isnull=False) |
                Q(deadline__lte=horizon_1w, deadline__isnull=False)
            )
            .select_related('project')
            .order_by('deadline', 'scheduled_for')
        )

        return render(request, self.template_name, {
            'inbox_count': inbox_count,
            'pending_notes_count': pending_notes_count,
            'stuck_projects': stuck_projects,
            'ok_projects': ok_projects,
            'on_hold_projects': on_hold_projects,
            'deadline_projects': deadline_projects,
            'waiting_needs_attention': waiting_needs_attention,
            'someday_count': someday_count,
            'agenda_count': agenda_count,
            'upcoming_actions': upcoming_actions,
            'today': today,
        })

    def post(self, request):
        notes = request.POST.get('notes', '')
        WeeklyReview.objects.create(notes=notes)
        return redirect('reviews:review_history')


class ReviewHistoryView(LoginRequiredMixin, View):
    template_name = 'reviews/review_history.html'

    def get(self, request):
        daily = DailyReview.objects.all()[:20]
        weekly = WeeklyReview.objects.all()[:20]
        return render(request, self.template_name, {
            'daily_reviews': daily,
            'weekly_reviews': weekly,
        })
