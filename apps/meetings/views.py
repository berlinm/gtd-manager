from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView, View

from apps.gtd.models import AgendaItem, Meeting, NextAction, Project, Reference, SomedayMaybe, WaitingFor
from .forms import MeetingForm, MeetingSessionForm
from .models import MeetingNote, MeetingSession


class MeetingListView(LoginRequiredMixin, ListView):
    template_name = 'meetings/meeting_list.html'
    context_object_name = 'meetings'

    def get_queryset(self):
        return Meeting.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pending_count'] = MeetingNote.objects.filter(
            processed_at__isnull=True,
            session__closed_at__isnull=False,
        ).count()
        return ctx


class MeetingCreateView(LoginRequiredMixin, CreateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'meetings/meeting_form.html'

    def get_success_url(self):
        return f'/meetings/{self.object.pk}/'


class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'meetings/meeting_form.html'

    def get_success_url(self):
        return f'/meetings/{self.object.pk}/'


class MeetingDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        sessions = list(
            meeting.sessions.prefetch_related('meeting_notes').order_by('-occurred_on', '-created_at')
        )
        for s in sessions:
            all_notes = list(s.meeting_notes.all())
            s.note_count = len(all_notes)
            s.unprocessed_count = sum(1 for n in all_notes if not n.is_processed)
        agenda_items = AgendaItem.objects.filter(meeting=meeting)
        return render(request, 'meetings/meeting_detail.html', {
            'meeting': meeting,
            'sessions': sessions,
            'agenda_items': agenda_items,
        })


class SessionCreateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        form = MeetingSessionForm(initial={'occurred_on': timezone.now().date()})
        return render(request, 'meetings/session_form.html', {'meeting': meeting, 'form': form})

    def post(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        form = MeetingSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.meeting = meeting
            session.save()
            return redirect('meetings:session_detail', pk=session.pk)
        return render(request, 'meetings/session_form.html', {'meeting': meeting, 'form': form})


class SessionDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        session = get_object_or_404(MeetingSession, pk=pk)
        notes = session.meeting_notes.all()
        agenda_items = AgendaItem.objects.filter(meeting=session.meeting)
        unprocessed = [n for n in notes if not n.is_processed]
        processed = [n for n in notes if n.is_processed]
        return render(request, 'meetings/session_detail.html', {
            'session': session,
            'notes': notes,
            'unprocessed_notes': unprocessed,
            'processed_notes': processed,
            'agenda_items': agenda_items,
        })


class SessionCloseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(MeetingSession, pk=pk)
        if session.is_open:
            session.closed_at = timezone.now()
            session.save()
        return redirect('meetings:session_detail', pk=session.pk)


class QuickNoteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(MeetingSession, pk=pk)
        title = request.POST.get('title', '').strip()
        if title and session.is_open:
            note = MeetingNote.objects.create(session=session, title=title)
            return render(request, 'meetings/partials/note_item.html', {'note': note})
        return render(request, 'meetings/partials/note_item.html', {'note': None})


class NoteClarifyView(LoginRequiredMixin, View):
    def _ctx(self, note, **extra):
        return {
            'note': note,
            'active_projects': Project.objects.filter(
                status=Project.Status.ACTIVE
            ).order_by('title'),
            **extra,
        }

    def get(self, request, pk):
        note = get_object_or_404(MeetingNote, pk=pk, processed_at__isnull=True)
        return render(request, 'meetings/note_clarify.html', self._ctx(note))

    def post(self, request, pk):
        note = get_object_or_404(MeetingNote, pk=pk, processed_at__isnull=True)
        disposition = request.POST.get('disposition')
        now = timezone.now()

        created_object = None

        if disposition == 'trashed':
            note.disposition = MeetingNote.Disposition.TRASHED

        elif disposition == 'done_immediately':
            note.disposition = MeetingNote.Disposition.DONE_IMMEDIATELY

        elif disposition == 'someday':
            created_object = SomedayMaybe.objects.create(
                title=note.title,
                body=note.body,
            )
            note.disposition = MeetingNote.Disposition.SOMEDAY_CREATED

        elif disposition == 'reference':
            created_object = Reference.objects.create(
                title=note.title,
                body=note.body,
            )
            note.disposition = MeetingNote.Disposition.REFERENCE_CREATED

        elif disposition == 'delegate':
            from apps.gtd.models import Person
            person_name = request.POST.get('person_name', '').strip()
            if not person_name:
                return render(request, 'meetings/note_clarify.html', self._ctx(
                    note,
                    error='Enter the name of the person you are waiting on.',
                    open_delegate=True,
                ))
            person, _ = Person.objects.get_or_create(name=person_name)
            delegate_project_id = request.POST.get('delegate_project_id', '').strip()
            delegate_project = None
            if delegate_project_id:
                try:
                    delegate_project = Project.objects.get(pk=delegate_project_id)
                except (Project.DoesNotExist, ValueError):
                    pass
            created_object = WaitingFor.objects.create(
                title=note.title,
                body=note.body,
                person=person,
                project=delegate_project,
            )
            note.disposition = MeetingNote.Disposition.DELEGATED

        elif disposition == 'action':
            created_object = NextAction.objects.create(
                title=request.POST.get('action_title', note.title).strip() or note.title,
                body=note.body,
            )
            note.disposition = MeetingNote.Disposition.ACTION_CREATED

        elif disposition == 'add_to_project':
            project_id = request.POST.get('add_project_id', '').strip()
            action_title = request.POST.get('add_project_action_title', note.title).strip() or note.title
            try:
                project = Project.objects.get(pk=project_id, status=Project.Status.ACTIVE)
            except (Project.DoesNotExist, ValueError):
                return render(request, 'meetings/note_clarify.html', self._ctx(
                    note,
                    error='Select an active project.',
                    open_add_to_project=True,
                ))
            created_object = NextAction.objects.create(
                title=action_title,
                body=note.body,
                project=project,
            )
            note.disposition = MeetingNote.Disposition.ACTION_ADDED_TO_PROJECT

        elif disposition == 'project':
            project_title = request.POST.get('project_title', note.title).strip() or note.title
            first_action_title = request.POST.get('first_action_title', '').strip()
            project = Project.objects.create(
                title=project_title,
                desired_outcome=request.POST.get('desired_outcome', '').strip(),
            )
            if first_action_title:
                NextAction.objects.create(title=first_action_title, project=project)
            created_object = project
            note.disposition = MeetingNote.Disposition.PROJECT_CREATED

        else:
            return render(request, 'meetings/note_clarify.html', self._ctx(
                note,
                error='Please choose a destination.',
            ))

        note.processed_at = now
        if created_object is not None:
            from django.contrib.contenttypes.models import ContentType
            note.content_type = ContentType.objects.get_for_model(created_object)
            note.object_id = created_object.pk
        note.save()

        session_pk = note.session_id
        if disposition == 'project' and created_object is not None:
            return redirect('gtd:project_detail', pk=created_object.pk)
        if disposition == 'add_to_project' and created_object is not None:
            return redirect('gtd:project_detail', pk=created_object.project_id)
        return redirect('meetings:session_detail', pk=session_pk)
