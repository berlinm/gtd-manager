from django.db import models


class Preferences(models.Model):
    """Single-user application preferences (one row, pk=1)."""

    class TimeFormat(models.TextChoices):
        H12 = '12', '12-hour (5:30 p.m.)'
        H24 = '24', '24-hour (17:30)'

    class DateStyle(models.TextChoices):
        MONTH_FIRST = 'month_first', 'Month first (Jul 4, 2026)'
        DAY_FIRST = 'day_first', 'Day first (4 Jul 2026)'
        ISO = 'iso', 'ISO (2026-07-04)'

    STEP_CHOICES = [
        (5, '5 minutes'),
        (10, '10 minutes'),
        (15, '15 minutes'),
        (30, '30 minutes'),
        (60, '1 hour'),
    ]

    _DATE_FORMATS = {
        'month_first': {'date': 'N j, Y', 'short': 'N j', 'weekday': 'l, N j, Y'},
        'day_first': {'date': 'j N Y', 'short': 'j N', 'weekday': 'l, j N Y'},
        'iso': {'date': 'Y-m-d', 'short': 'Y-m-d', 'weekday': 'l, Y-m-d'},
    }

    time_step_minutes = models.PositiveSmallIntegerField(
        default=15, choices=STEP_CHOICES
    )
    time_format = models.CharField(
        max_length=2, choices=TimeFormat.choices, default=TimeFormat.H12
    )
    date_style = models.CharField(
        max_length=20, choices=DateStyle.choices, default=DateStyle.MONTH_FIRST
    )

    class Meta:
        verbose_name = 'preferences'
        verbose_name_plural = 'preferences'

    def __str__(self):
        return 'Application preferences'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def step_seconds(self):
        return self.time_step_minutes * 60

    @property
    def _time_fmt(self):
        return 'g:i a' if self.time_format == self.TimeFormat.H12 else 'G:i'

    @property
    def _dates(self):
        return self._DATE_FORMATS.get(self.date_style, self._DATE_FORMATS['month_first'])

    @property
    def f_date(self):
        return self._dates['date']

    @property
    def f_date_short(self):
        return self._dates['short']

    @property
    def f_weekday(self):
        return self._dates['weekday']

    @property
    def f_time(self):
        return self._time_fmt

    @property
    def f_datetime(self):
        return self._dates['date'] + ' ' + self._time_fmt

    @property
    def f_datetime_short(self):
        return self._dates['short'] + ' ' + self._time_fmt
