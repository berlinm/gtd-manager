from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    AgendaItem, AreaOfResponsibility, Context, Meeting, NextAction,
    Person, Project, SomedayMaybe, WaitingFor,
)


class NextActionForm(forms.ModelForm):
    contexts = forms.ModelMultipleChoiceField(
        queryset=Context.objects.filter(active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = NextAction
        fields = [
            'title', 'body', 'project', 'area', 'contexts',
            'defer_until', 'scheduled_for', 'deadline',
        ]
        widgets = {
            'defer_until': forms.DateInput(attrs={'type': 'date'}),
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'body': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(
            status__in=[Project.Status.ACTIVE, Project.Status.ON_HOLD]
        )
        self.fields['area'].queryset = AreaOfResponsibility.objects.filter(active=True)
        for field in ['project', 'area', 'defer_until', 'scheduled_for', 'deadline']:
            self.fields[field].required = False


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'desired_outcome', 'status', 'on_hold_reason', 'area', 'deadline']
        widgets = {
            'desired_outcome': forms.Textarea(attrs={'rows': 3}),
            'on_hold_reason': forms.Textarea(attrs={'rows': 2}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area'].queryset = AreaOfResponsibility.objects.filter(active=True)
        for field in ['desired_outcome', 'on_hold_reason', 'area', 'deadline']:
            self.fields[field].required = False

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get('status')
        on_hold_reason = cleaned.get('on_hold_reason', '').strip()
        if status == Project.Status.ON_HOLD and not on_hold_reason:
            self.add_error('on_hold_reason', 'A reason is required when putting a project on hold.')
        return cleaned


class WaitingForForm(forms.ModelForm):
    class Meta:
        model = WaitingFor
        fields = ['title', 'body', 'person', 'project', 'delegated_at', 'expected_by', 'follow_up_on']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3}),
            'delegated_at': forms.DateInput(attrs={'type': 'date'}),
            'expected_by': forms.DateInput(attrs={'type': 'date'}),
            'follow_up_on': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(
            status__in=[Project.Status.ACTIVE, Project.Status.ON_HOLD]
        )
        for field in ['body', 'project', 'expected_by', 'follow_up_on']:
            self.fields[field].required = False


class WaitingForReceiveForm(forms.ModelForm):
    class Meta:
        model = WaitingFor
        fields = ['result_notes']
        widgets = {'result_notes': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['result_notes'].required = False


class SomedayMaybeForm(forms.ModelForm):
    class Meta:
        model = SomedayMaybe
        fields = ['title', 'body', 'area']
        widgets = {'body': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area'].queryset = AreaOfResponsibility.objects.filter(active=True)
        for field in ['body', 'area']:
            self.fields[field].required = False


class SomedayPromoteForm(forms.Form):
    project_title = forms.CharField(max_length=500)
    desired_outcome = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    first_action_title = forms.CharField(max_length=500, required=False)


class AgendaItemForm(forms.ModelForm):
    class Meta:
        model = AgendaItem
        fields = ['title', 'body', 'person', 'meeting']
        widgets = {'body': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['person'].queryset = Person.objects.filter(active=True)
        self.fields['meeting'].queryset = Meeting.objects.filter(active=True)
        for field in ['body', 'person', 'meeting']:
            self.fields[field].required = False

    def clean(self):
        cleaned = super().clean()
        person = cleaned.get('person')
        meeting = cleaned.get('meeting')
        if not person and not meeting:
            raise ValidationError('Choose a person or a meeting.')
        if person and meeting:
            raise ValidationError('Choose either a person or a meeting, not both.')
        return cleaned
