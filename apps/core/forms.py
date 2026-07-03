from django import forms

from apps.core.models import Preferences


class PreferencesForm(forms.ModelForm):
    class Meta:
        model = Preferences
        fields = ['time_step_minutes', 'time_format', 'date_style']
        widgets = {
            'time_step_minutes': forms.Select,
            'time_format': forms.Select,
            'date_style': forms.Select,
        }
