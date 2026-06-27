from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Prefetch, Q
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from .forms import (
    AgendaItemForm, NextActionForm, ProjectForm, ReferenceForm,
    SomedayMaybeForm, SomedayPromoteForm, WaitingForForm, WaitingForReceiveForm,
)
from .models import (
    AgendaItem, AreaOfResponsibility, Context, Meeting, NextAction,
    Person, Project, Reference, SomedayMaybe, WaitingFor,
)


# ---------------------------------------------------------------------------
# Next Actions
# ---------------------------------------------------------------------------

class NextActionListView(LoginRequiredMixin, ListView):
    template_name = 'gtd/next_actions.html'
    context_object_name = 'actions'

    def get_queryset(self):
        today = timezone.now().date()
        qs = NextAction.objects.filter(status=NextAction.Status.ACTIVE).select_related(
            'project', 'area'
        ).prefetch_related('contexts')
        qs = qs.filter(
            Q(defer_until__isnull=True) | Q(defer_until__lte=today)
        )
        context_label = self.request.GET.get('context')
        if context_label:
            qs = qs.filter(contexts__label=context_label)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['contexts'] = Context.objects.filter(active=True)
        ctx['active_context'] = self.request.GET.get('context', '')
        return ctx


class NextActionCreateView(LoginRequiredMixin, CreateView):
    model = NextAction
    form_class = NextActionForm
    template_name = 'gtd/next_action_form.html'

    def get_success_url(self):
        return '/actions/'

    def get_initial(self):
        initial = super().get_initial()
        project_id = self.request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        return initial


class NextActionUpdateView(LoginRequiredMixin, UpdateView):
    model = NextAction
    form_class = NextActionForm
    template_name = 'gtd/next_action_form.html'

    def get_success_url(self):
        if self.object.project_id:
            return f'/projects/{self.object.project_id}/'
        return '/actions/'


class NextActionDoneView(LoginRequiredMixin, View):
    def post(self, request, pk):
        action = get_object_or_404(NextAction, pk=pk)
        action.status = NextAction.Status.DONE
        action.completed_at = timezone.now()
        action.save()
        next_url = request.POST.get('next', '/actions/')
        return redirect(next_url)


class NextActionCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        action = get_object_or_404(NextAction, pk=pk)
        action.status = NextAction.Status.CANCELLED
        action.completed_at = timezone.now()
        action.save()
        next_url = request.POST.get('next', '/actions/')
        return redirect(next_url)


class DelegateActionView(LoginRequiredMixin, View):
    """Convert a NextAction to a WaitingFor and cancel the original action."""

    def get(self, request, pk):
        action = get_object_or_404(NextAction, pk=pk, status=NextAction.Status.ACTIVE)
        form = WaitingForForm(initial={
            'title': action.title,
            'body': action.body,
            'project': action.project_id,
        })
        return render(request, 'gtd/delegate_action.html', {'action': action, 'form': form})

    def post(self, request, pk):
        action = get_object_or_404(NextAction, pk=pk, status=NextAction.Status.ACTIVE)
        form = WaitingForForm(request.POST)
        if form.is_valid():
            wf = form.save()
            action.status = NextAction.Status.CANCELLED
            action.completed_at = timezone.now()
            action.save()
            return redirect('gtd:waiting_for_list')
        return render(request, 'gtd/delegate_action.html', {'action': action, 'form': form})


class TodayView(LoginRequiredMixin, ListView):
    template_name = 'gtd/today.html'
    context_object_name = 'actions'

    def get_queryset(self):
        today = timezone.now().date()
        return (
            NextAction.objects.filter(status=NextAction.Status.ACTIVE)
            .filter(
                Q(scheduled_for__date__lte=today) |
                Q(deadline__lte=today)
            )
            .select_related('project', 'area')
            .prefetch_related('contexts')
            .order_by('deadline', 'scheduled_for')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()
        ctx['projects_with_deadline'] = Project.objects.filter(
            status=Project.Status.ACTIVE,
            deadline__lte=today,
        )
        ctx['follow_ups_due'] = WaitingFor.objects.filter(
            status=WaitingFor.Status.WAITING,
            follow_up_on__lte=today,
        ).select_related('person')
        return ctx


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class ProjectListView(LoginRequiredMixin, ListView):
    template_name = 'gtd/projects.html'
    context_object_name = 'active_projects'

    def get_queryset(self):
        return Project.objects.filter(status=Project.Status.ACTIVE).prefetch_related(
            Prefetch(
                'nextaction_set',
                queryset=NextAction.objects.filter(status=NextAction.Status.ACTIVE),
                to_attr='active_actions',
            )
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['on_hold_projects'] = Project.objects.filter(status=Project.Status.ON_HOLD)
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'gtd/project_form.html'

    def get_success_url(self):
        return f'/projects/{self.object.pk}/'


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'gtd/project_form.html'

    def get_success_url(self):
        return f'/projects/{self.object.pk}/'

    def form_valid(self, form):
        instance = form.instance
        terminal = {Project.Status.COMPLETED, Project.Status.CANCELLED}
        was_terminal = Project.objects.filter(
            pk=instance.pk, status__in=terminal
        ).exists()
        if instance.status in terminal and not was_terminal:
            instance.completed_at = timezone.now()
        elif instance.status not in terminal:
            instance.completed_at = None
        return super().form_valid(form)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'gtd/project_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object
        active_actions = (
            NextAction.objects.filter(project=project, status=NextAction.Status.ACTIVE)
            .prefetch_related('contexts')
        )
        ctx['available_actions'] = [a for a in active_actions if a.is_available]
        ctx['deferred_actions'] = [a for a in active_actions if a.is_deferred]
        ctx['scheduled_actions'] = [
            a for a in active_actions if a.scheduled_for and not a.is_deferred
        ]
        ctx['waiting_items'] = WaitingFor.objects.filter(
            project=project, status=WaitingFor.Status.WAITING
        ).select_related('person')
        ctx['agenda_items'] = AgendaItem.objects.filter(
            Q(person__waitingfor__project=project) | Q(meeting__isnull=False)
        ).distinct()
        return ctx


# ---------------------------------------------------------------------------
# Waiting For
# ---------------------------------------------------------------------------

class WaitingForListView(LoginRequiredMixin, ListView):
    template_name = 'gtd/waiting_for_list.html'
    context_object_name = 'waiting_items'

    def get_queryset(self):
        return (
            WaitingFor.objects.filter(status=WaitingFor.Status.WAITING)
            .select_related('person', 'project')
            .order_by('follow_up_on', '-created_at')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()
        ctx['today'] = today
        return ctx


class WaitingForCreateView(LoginRequiredMixin, CreateView):
    model = WaitingFor
    form_class = WaitingForForm
    template_name = 'gtd/waiting_for_form.html'

    def get_success_url(self):
        return '/waiting/'


class WaitingForUpdateView(LoginRequiredMixin, UpdateView):
    model = WaitingFor
    form_class = WaitingForForm
    template_name = 'gtd/waiting_for_form.html'

    def get_success_url(self):
        return '/waiting/'


class WaitingForReceiveView(LoginRequiredMixin, View):
    def get(self, request, pk):
        item = get_object_or_404(WaitingFor, pk=pk, status=WaitingFor.Status.WAITING)
        form = WaitingForReceiveForm(instance=item)
        return render(request, 'gtd/waiting_for_receive.html', {'item': item, 'form': form})

    def post(self, request, pk):
        item = get_object_or_404(WaitingFor, pk=pk, status=WaitingFor.Status.WAITING)
        form = WaitingForReceiveForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.status = WaitingFor.Status.RECEIVED
            item.completed_at = timezone.now()
            item.save()
            return redirect('gtd:waiting_for_list')
        return render(request, 'gtd/waiting_for_receive.html', {'item': item, 'form': form})


class WaitingForCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(WaitingFor, pk=pk, status=WaitingFor.Status.WAITING)
        item.status = WaitingFor.Status.CANCELLED
        item.completed_at = timezone.now()
        item.save()
        return redirect('gtd:waiting_for_list')


class WaitingForFollowUpView(LoginRequiredMixin, View):
    """Record that a follow-up was made and update the next follow-up date."""
    def post(self, request, pk):
        item = get_object_or_404(WaitingFor, pk=pk, status=WaitingFor.Status.WAITING)
        item.last_follow_up_at = timezone.now().date()
        new_date = request.POST.get('follow_up_on')
        if new_date:
            item.follow_up_on = new_date
        item.save()
        return redirect('gtd:waiting_for_list')


# ---------------------------------------------------------------------------
# Someday / Maybe
# ---------------------------------------------------------------------------

class SomedayMaybeListView(LoginRequiredMixin, ListView):
    template_name = 'gtd/someday_list.html'
    context_object_name = 'someday_items'

    def get_queryset(self):
        return SomedayMaybe.objects.filter(promoted_at__isnull=True).select_related('area')


class SomedayMaybeCreateView(LoginRequiredMixin, CreateView):
    model = SomedayMaybe
    form_class = SomedayMaybeForm
    template_name = 'gtd/someday_form.html'

    def get_success_url(self):
        return '/someday/'


class SomedayMaybeUpdateView(LoginRequiredMixin, UpdateView):
    model = SomedayMaybe
    form_class = SomedayMaybeForm
    template_name = 'gtd/someday_form.html'

    def get_success_url(self):
        return '/someday/'


class SomedayPromoteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        item = get_object_or_404(SomedayMaybe, pk=pk, promoted_at__isnull=True)
        form = SomedayPromoteForm(initial={'project_title': item.title})
        return render(request, 'gtd/someday_promote.html', {'item': item, 'form': form})

    def post(self, request, pk):
        item = get_object_or_404(SomedayMaybe, pk=pk, promoted_at__isnull=True)
        form = SomedayPromoteForm(request.POST)
        if form.is_valid():
            project = Project.objects.create(
                title=form.cleaned_data['project_title'],
                desired_outcome=form.cleaned_data.get('desired_outcome', ''),
                area=item.area,
            )
            first_action = form.cleaned_data.get('first_action_title', '').strip()
            if first_action:
                NextAction.objects.create(title=first_action, project=project)
            item.promoted_at = timezone.now()
            item.promoted_to_project = project
            item.save()
            return redirect('gtd:project_detail', pk=project.pk)
        return render(request, 'gtd/someday_promote.html', {'item': item, 'form': form})


# ---------------------------------------------------------------------------
# Agenda Items
# ---------------------------------------------------------------------------

class AgendaListView(LoginRequiredMixin, ListView):
    template_name = 'gtd/agenda.html'
    context_object_name = 'agenda_items'

    def get_queryset(self):
        return AgendaItem.objects.select_related('person', 'meeting')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = list(self.get_queryset())
        by_person = {}
        by_meeting = {}
        for item in items:
            if item.person_id:
                by_person.setdefault(item.person, []).append(item)
            elif item.meeting_id:
                by_meeting.setdefault(item.meeting, []).append(item)
        ctx['by_person'] = by_person
        ctx['by_meeting'] = by_meeting
        ctx['people'] = Person.objects.filter(active=True)
        ctx['meetings'] = Meeting.objects.filter(active=True)
        return ctx


class AgendaItemCreateView(LoginRequiredMixin, CreateView):
    model = AgendaItem
    form_class = AgendaItemForm
    template_name = 'gtd/agenda_item_form.html'

    def get_initial(self):
        initial = super().get_initial()
        person_id = self.request.GET.get('person')
        meeting_id = self.request.GET.get('meeting')
        if person_id:
            initial['person'] = person_id
        if meeting_id:
            initial['meeting'] = meeting_id
        return initial

    def get_success_url(self):
        return '/agenda/'


class AgendaItemUpdateView(LoginRequiredMixin, UpdateView):
    model = AgendaItem
    form_class = AgendaItemForm
    template_name = 'gtd/agenda_item_form.html'

    def get_success_url(self):
        return '/agenda/'


class AgendaItemDoneView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(AgendaItem, pk=pk)
        item.delete()
        next_url = request.POST.get('next', '/agenda/')
        return redirect(next_url)


# ---------------------------------------------------------------------------
# Reference
# ---------------------------------------------------------------------------

class ReferenceListView(LoginRequiredMixin, ListView):
    template_name = 'gtd/reference_list.html'
    context_object_name = 'references'

    def get_queryset(self):
        qs = Reference.objects.select_related('area').prefetch_related('tags')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class ReferenceDetailView(LoginRequiredMixin, DetailView):
    model = Reference
    template_name = 'gtd/reference_detail.html'


class ReferenceCreateView(LoginRequiredMixin, CreateView):
    model = Reference
    form_class = ReferenceForm
    template_name = 'gtd/reference_form.html'

    def get_success_url(self):
        return f'/reference/{self.object.pk}/'


class ReferenceUpdateView(LoginRequiredMixin, UpdateView):
    model = Reference
    form_class = ReferenceForm
    template_name = 'gtd/reference_form.html'

    def get_success_url(self):
        return f'/reference/{self.object.pk}/'


# ---------------------------------------------------------------------------
# Area detail
# ---------------------------------------------------------------------------

class AreaDetailView(LoginRequiredMixin, DetailView):
    model = AreaOfResponsibility
    template_name = 'gtd/area_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        area = self.object
        ctx['active_projects'] = Project.objects.filter(
            area=area, status=Project.Status.ACTIVE
        )
        ctx['on_hold_projects'] = Project.objects.filter(
            area=area, status=Project.Status.ON_HOLD
        )
        ctx['active_actions'] = (
            NextAction.objects.filter(area=area, status=NextAction.Status.ACTIVE)
            .filter(Q(defer_until__isnull=True) | Q(defer_until__lte=timezone.now().date()))
            .select_related('project')
        )
        ctx['references'] = Reference.objects.filter(area=area).prefetch_related('tags')
        ctx['someday_items'] = SomedayMaybe.objects.filter(
            area=area, promoted_at__isnull=True
        )
        return ctx
