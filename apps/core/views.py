from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from apps.gtd.models import AreaOfResponsibility


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            from django.utils import timezone
            from apps.gtd.models import Project, WaitingFor
            today = timezone.now().date()
            active_projects = Project.objects.filter(status=Project.Status.ACTIVE)
            ctx['stuck_count'] = sum(1 for p in active_projects if p.is_stuck)
            ctx['followups_due'] = WaitingFor.objects.filter(
                status=WaitingFor.Status.WAITING,
                follow_up_on__lte=today,
            ).count()
        except Exception:
            ctx['stuck_count'] = 0
            ctx['followups_due'] = 0
        return ctx


class AreaListView(LoginRequiredMixin, ListView):
    model = AreaOfResponsibility
    template_name = 'core/area_list.html'
    context_object_name = 'areas'


class AreaCreateView(LoginRequiredMixin, CreateView):
    model = AreaOfResponsibility
    fields = ['title', 'description', 'active']
    template_name = 'core/area_form.html'
    success_url = reverse_lazy('core:area_list')


class AreaUpdateView(LoginRequiredMixin, UpdateView):
    model = AreaOfResponsibility
    fields = ['title', 'description', 'active']
    template_name = 'core/area_form.html'
    success_url = reverse_lazy('core:area_list')
