from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from apps.gtd.models import Meeting


class MeetingSession(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='sessions')
    occurred_on = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-occurred_on', '-created_at']

    def __str__(self):
        return f'{self.meeting.title} — {self.occurred_on}'

    @property
    def is_open(self):
        return self.closed_at is None


class MeetingNote(models.Model):

    class Disposition(models.TextChoices):
        PENDING = 'pending', 'Pending'
        TRASHED = 'trashed', 'Trashed'
        DONE_IMMEDIATELY = 'done_immediately', 'Done immediately'
        DELEGATED = 'delegated', 'Delegated'
        ACTION_CREATED = 'action_created', 'Action created'
        PROJECT_CREATED = 'project_created', 'Project created'
        SOMEDAY_CREATED = 'someday_created', 'Someday/maybe created'
        REFERENCE_CREATED = 'reference_created', 'Reference created'
        ACTION_ADDED_TO_PROJECT = 'action_added_to_project', 'Action added to project'

    session = models.ForeignKey(MeetingSession, on_delete=models.CASCADE, related_name='meeting_notes')
    title = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    captured_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    disposition = models.CharField(
        max_length=50,
        choices=Disposition.choices,
        default=Disposition.PENDING,
    )
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    created_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['captured_at']

    def __str__(self):
        return self.title

    @property
    def is_processed(self):
        return self.processed_at is not None
