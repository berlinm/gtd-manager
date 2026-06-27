from django.db import models
from django.utils import timezone


class DailyReview(models.Model):
    completed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"Daily review {self.completed_at.date()}"


class WeeklyReview(models.Model):
    completed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"Weekly review {self.completed_at.date()}"
