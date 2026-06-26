from django import forms

from apps.gtd.models import Meeting
from .models import MeetingSession


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'notes', 'active']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False


class MeetingSessionForm(forms.ModelForm):
    class Meta:
        model = MeetingSession
        fields = ['occurred_on', 'start_time', 'end_time', 'notes']
        widgets = {
            'occurred_on': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['start_time', 'end_time', 'notes']:
            self.fields[field].required = False
