from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AreaOfResponsibility(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'areas of responsibility'

    def __str__(self):
        return self.title


class Context(models.Model):
    """Filter tag for NextActions — where or with what an action can be done."""
    label = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['label']

    def __str__(self):
        return self.label


class Tag(models.Model):
    """Organisational tag for Reference items only. Distinct from Context."""
    label = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['label']

    def __str__(self):
        return self.label


class Person(models.Model):
    """Lightweight contact record used by WaitingFor and AgendaItem."""
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Meeting(models.Model):
    """A recurring agenda target (e.g. weekly standup, 1:1).
    Not a one-time occurrence — see MeetingSession in apps.meetings."""
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Project(models.Model):

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ON_HOLD = 'on_hold', 'On hold'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    title = models.CharField(max_length=500)
    desired_outcome = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    on_hold_reason = models.TextField(blank=True)
    area = models.ForeignKey(
        AreaOfResponsibility, null=True, blank=True, on_delete=models.SET_NULL
    )
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    next_review_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def clean(self):
        if self.status == self.Status.ON_HOLD and not self.on_hold_reason:
            raise ValidationError({'on_hold_reason': 'A reason is required when putting a project on hold.'})
        terminal = {self.Status.COMPLETED, self.Status.CANCELLED}
        if self.status in terminal and not self.completed_at:
            raise ValidationError({'completed_at': 'Completed/cancelled projects must have a completed_at timestamp.'})
        if self.status not in terminal and self.completed_at:
            raise ValidationError({'completed_at': 'Only completed or cancelled projects may have a completed_at timestamp.'})

    @property
    def is_stuck(self):
        if self.status != self.Status.ACTIVE:
            return False
        has_action = self.nextaction_set.filter(status=NextAction.Status.ACTIVE).exists()
        has_waiting = self.waitingfor_set.filter(status='waiting').exists()
        return not has_action and not has_waiting


class NextAction(models.Model):

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        DONE = 'done', 'Done'
        CANCELLED = 'cancelled', 'Cancelled'

    title = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    area = models.ForeignKey(
        AreaOfResponsibility, null=True, blank=True, on_delete=models.SET_NULL
    )
    contexts = models.ManyToManyField(Context, blank=True)
    defer_until = models.DateField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        errors = {}
        if self.defer_until and self.scheduled_for:
            if self.scheduled_for.date() < self.defer_until:
                errors['scheduled_for'] = 'Scheduled date cannot be before the defer-until date.'
        if self.scheduled_for and self.deadline:
            if self.deadline < self.scheduled_for.date():
                errors['deadline'] = 'Deadline cannot be before the scheduled date.'
        if self.defer_until and self.deadline:
            if self.deadline <= self.defer_until:
                errors['deadline'] = 'Deadline must be after the defer-until date.'
        terminal = {self.Status.DONE, self.Status.CANCELLED}
        if self.status in terminal and not self.completed_at:
            errors['completed_at'] = 'Done/cancelled actions must have a completed_at timestamp.'
        if self.status not in terminal and self.completed_at:
            errors['completed_at'] = 'Only done or cancelled actions may have a completed_at timestamp.'
        if errors:
            raise ValidationError(errors)

    @property
    def is_available(self):
        if self.defer_until and self.defer_until > timezone.now().date():
            return False
        return True

    @property
    def is_deferred(self):
        return bool(self.defer_until and self.defer_until > timezone.now().date())


class SomedayMaybe(models.Model):
    title = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    area = models.ForeignKey(
        AreaOfResponsibility, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    promoted_at = models.DateTimeField(null=True, blank=True)
    promoted_to_project = models.ForeignKey(
        Project, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='promoted_from'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'someday/maybe'
        verbose_name_plural = 'someday/maybe items'

    def __str__(self):
        return self.title

    def clean(self):
        if bool(self.promoted_at) != bool(self.promoted_to_project):
            raise ValidationError('promoted_at and promoted_to_project must both be set or both be null.')


class WaitingFor(models.Model):

    class Status(models.TextChoices):
        WAITING = 'waiting', 'Waiting'
        RECEIVED = 'received', 'Received'
        CANCELLED = 'cancelled', 'Cancelled'

    title = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    delegated_at = models.DateField(default=timezone.now)
    expected_by = models.DateField(null=True, blank=True)
    follow_up_on = models.DateField(null=True, blank=True)
    last_follow_up_at = models.DateField(null=True, blank=True)
    result_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['follow_up_on', '-created_at']
        verbose_name = 'waiting-for item'

    def __str__(self):
        return self.title

    def clean(self):
        terminal = {self.Status.RECEIVED, self.Status.CANCELLED}
        if self.status in terminal and not self.completed_at:
            raise ValidationError({'completed_at': 'Received/cancelled items must have a completed_at timestamp.'})
        if self.status not in terminal and self.completed_at:
            raise ValidationError({'completed_at': 'Only received or cancelled items may have a completed_at timestamp.'})


class AgendaItem(models.Model):
    title = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        has_person = bool(self.person_id)
        has_meeting = bool(self.meeting_id)
        if not has_person and not has_meeting:
            raise ValidationError('An agenda item must belong to a person or a meeting.')
        if has_person and has_meeting:
            raise ValidationError('An agenda item cannot belong to both a person and a meeting.')


class Reference(models.Model):
    title = models.CharField(max_length=500)
    body = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    area = models.ForeignKey(
        AreaOfResponsibility, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
