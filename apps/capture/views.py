from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import ListView, View

from apps.gtd.models import NextAction, Project, Reference, SomedayMaybe, WaitingFor
from .models import InboxItem


class InboxView(LoginRequiredMixin, ListView):
    model = InboxItem
    template_name = 'capture/inbox.html'
    context_object_name = 'inbox_items'

    def get_queryset(self):
        return InboxItem.objects.filter(processed_at__isnull=True)


class QuickCaptureView(LoginRequiredMixin, View):
    def post(self, request):
        title = request.POST.get('title', '').strip()
        if title:
            InboxItem.objects.create(title=title)
        count = InboxItem.objects.filter(processed_at__isnull=True).count()
        return render(request, 'capture/partials/captured.html', {'inbox_count': count})


class ClarifyView(LoginRequiredMixin, View):
    def _ctx(self, item, **extra):
        return {
            'item': item,
            'active_projects': Project.objects.filter(
                status=Project.Status.ACTIVE
            ).order_by('title'),
            **extra,
        }

    def get(self, request, pk):
        item = get_object_or_404(InboxItem, pk=pk, processed_at__isnull=True)
        return render(request, 'capture/clarify.html', self._ctx(item))

    def post(self, request, pk):
        item = get_object_or_404(InboxItem, pk=pk, processed_at__isnull=True)
        disposition = request.POST.get('disposition')
        now = timezone.now()

        created_object = None

        if disposition == 'trashed':
            item.disposition = InboxItem.Disposition.TRASHED

        elif disposition == 'done_immediately':
            item.disposition = InboxItem.Disposition.DONE_IMMEDIATELY

        elif disposition == 'someday':
            created_object = SomedayMaybe.objects.create(
                title=item.title,
                body=item.body,
            )
            item.disposition = InboxItem.Disposition.SOMEDAY_CREATED

        elif disposition == 'reference':
            created_object = Reference.objects.create(
                title=item.title,
                body=item.body,
            )
            item.disposition = InboxItem.Disposition.REFERENCE_CREATED

        elif disposition == 'delegate':
            from apps.gtd.models import Person
            person_name = request.POST.get('person_name', '').strip()
            if not person_name:
                return render(request, 'capture/clarify.html', self._ctx(
                    item,
                    error='Enter the name of the person you are waiting on.',
                    open_delegate=True,
                ))
            person, _ = Person.objects.get_or_create(name=person_name)
            delegate_project = None
            delegate_project_id = request.POST.get('delegate_project_id', '').strip()
            if delegate_project_id:
                try:
                    delegate_project = Project.objects.get(pk=delegate_project_id)
                except (Project.DoesNotExist, ValueError):
                    pass
            created_object = WaitingFor.objects.create(
                title=item.title,
                body=item.body,
                person=person,
                project=delegate_project,
            )
            item.disposition = InboxItem.Disposition.DELEGATED

        elif disposition == 'action':
            created_object = NextAction.objects.create(
                title=request.POST.get('action_title', item.title).strip() or item.title,
                body=item.body,
            )
            item.disposition = InboxItem.Disposition.ACTION_CREATED

        elif disposition == 'add_to_project':
            project_id = request.POST.get('add_project_id', '').strip()
            action_title = request.POST.get('add_project_action_title', item.title).strip() or item.title
            try:
                project = Project.objects.get(pk=project_id, status=Project.Status.ACTIVE)
            except (Project.DoesNotExist, ValueError):
                return render(request, 'capture/clarify.html', self._ctx(
                    item,
                    error='Select an active project.',
                    open_add_to_project=True,
                ))
            created_object = NextAction.objects.create(
                title=action_title,
                body=item.body,
                project=project,
            )
            item.disposition = InboxItem.Disposition.ACTION_ADDED_TO_PROJECT

        elif disposition == 'project':
            project_title = request.POST.get('project_title', item.title).strip() or item.title
            first_action_title = request.POST.get('first_action_title', '').strip()
            project = Project.objects.create(
                title=project_title,
                desired_outcome=request.POST.get('desired_outcome', '').strip(),
            )
            if first_action_title:
                NextAction.objects.create(title=first_action_title, project=project)
            created_object = project
            item.disposition = InboxItem.Disposition.PROJECT_CREATED

        else:
            return render(request, 'capture/clarify.html', self._ctx(
                item,
                error='Please choose a destination.',
            ))

        item.processed_at = now
        if created_object is not None:
            from django.contrib.contenttypes.models import ContentType
            item.content_type = ContentType.objects.get_for_model(created_object)
            item.object_id = created_object.pk
        item.save()

        if disposition == 'project' and created_object is not None:
            return redirect('gtd:project_detail', pk=created_object.pk)
        if disposition == 'add_to_project' and created_object is not None:
            return redirect('gtd:project_detail', pk=created_object.project_id)
        if disposition == 'action' and created_object is not None:
            return redirect('gtd:next_actions')
        if disposition == 'delegate' and created_object is not None:
            return redirect('gtd:waiting_for_list')
        if disposition == 'reference' and created_object is not None:
            return redirect('gtd:reference_detail', pk=created_object.pk)
        return redirect('capture:inbox')


class InboxHistoryView(LoginRequiredMixin, ListView):
    template_name = 'capture/inbox_history.html'
    context_object_name = 'processed_items'
    paginate_by = 50

    def get_queryset(self):
        return (
            InboxItem.objects.filter(processed_at__isnull=False)
            .select_related('content_type')
            .order_by('-processed_at')
        )
