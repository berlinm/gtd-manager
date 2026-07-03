import sys

import django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from apps.gtd.models import AreaOfResponsibility
from apps.core.forms import PreferencesForm
from apps.core.models import Preferences
from apps.core.management.commands.backupdb import run_backup


class AdminSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/settings.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        backup_dir = getattr(settings, 'BACKUP_DIR', settings.BASE_DIR / 'backups')
        backups = []
        if backup_dir.exists():
            backups = sorted(backup_dir.glob('gtd-*.db'), reverse=True)
        ctx['last_backup'] = backups[0] if backups else None
        ctx['backup_count'] = len(backups)
        ctx['backup_dir'] = backup_dir
        ctx['db_path'] = settings.DATABASES['default']['NAME']
        ctx['python_version'] = sys.version.split()[0]
        ctx['django_version'] = django.get_version()
        ctx['base_dir'] = settings.BASE_DIR
        ctx.setdefault('prefs_form', PreferencesForm(instance=Preferences.load()))
        return ctx

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'backup':
            try:
                dest = run_backup()
                messages.success(request, f'Backup saved: {dest.name}')
            except Exception as e:
                messages.error(request, f'Backup failed: {e}')
        elif action == 'preferences':
            form = PreferencesForm(request.POST, instance=Preferences.load())
            if form.is_valid():
                form.save()
                messages.success(request, 'Preferences saved.')
            else:
                context = self.get_context_data(prefs_form=form, **kwargs)
                return self.render_to_response(context)
        return self.get(request, *args, **kwargs)


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


class InstructionsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/instructions.html'


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
