from django.contrib.auth.models import User
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Preferences


class PreferencesModelTests(TestCase):

    def test_load_creates_singleton(self):
        p1 = Preferences.load()
        p2 = Preferences.load()
        self.assertEqual(p1.pk, 1)
        self.assertEqual(p2.pk, 1)
        self.assertEqual(Preferences.objects.count(), 1)

    def test_save_forces_pk_one(self):
        p = Preferences(time_step_minutes=30)
        p.save()
        self.assertEqual(p.pk, 1)

    def test_defaults(self):
        p = Preferences.load()
        self.assertEqual(p.time_step_minutes, 15)
        self.assertEqual(p.step_seconds, 900)
        self.assertEqual(p.time_format, '12')
        self.assertEqual(p.date_style, 'month_first')

    def test_step_seconds(self):
        self.assertEqual(Preferences(time_step_minutes=5).step_seconds, 300)
        self.assertEqual(Preferences(time_step_minutes=60).step_seconds, 3600)

    def test_time_format_property(self):
        self.assertEqual(Preferences(time_format='12').f_time, 'g:i a')
        self.assertEqual(Preferences(time_format='24').f_time, 'G:i')

    def test_date_style_properties(self):
        month = Preferences(date_style='month_first')
        self.assertEqual(month.f_date, 'N j, Y')
        self.assertEqual(month.f_date_short, 'N j')
        iso = Preferences(date_style='iso')
        self.assertEqual(iso.f_date, 'Y-m-d')

    def test_datetime_composes_date_and_time(self):
        p = Preferences(date_style='iso', time_format='24')
        self.assertEqual(p.f_datetime, 'Y-m-d G:i')
        self.assertEqual(p.f_datetime_short, 'Y-m-d G:i')

    def test_format_string_renders_in_date_filter(self):
        from datetime import datetime
        p = Preferences(date_style='iso', time_format='24')
        tpl = Template('{{ d|date:fmt }}')
        out = tpl.render(Context({'d': datetime(2026, 7, 4, 17, 30), 'fmt': p.f_datetime}))
        self.assertEqual(out, '2026-07-04 17:30')


class PreferencesViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)

    def test_settings_page_shows_pref_form(self):
        response = self.client.get(reverse('core:settings'))
        self.assertContains(response, 'Time picker interval')
        self.assertContains(response, 'name="time_step_minutes"')

    def test_post_saves_preferences(self):
        response = self.client.post(reverse('core:settings'), {
            'action': 'preferences',
            'time_step_minutes': '30',
            'time_format': '24',
            'date_style': 'iso',
        })
        self.assertEqual(response.status_code, 200)
        p = Preferences.load()
        self.assertEqual(p.time_step_minutes, 30)
        self.assertEqual(p.time_format, '24')
        self.assertEqual(p.date_style, 'iso')

    def test_context_processor_injects_prefs(self):
        response = self.client.get(reverse('gtd:next_actions'))
        self.assertIn('prefs', response.context)
        self.assertIsInstance(response.context['prefs'], Preferences)

    def test_next_action_form_applies_step(self):
        Preferences.objects.create(time_step_minutes=30)
        response = self.client.get(reverse('gtd:action_add'))
        self.assertContains(response, 'step="1800"')

    def test_snap_script_shipped_on_authenticated_pages(self):
        # base.html carries the client-side interval-snap enhancement that
        # enforces the picker interval (native `step` alone lets users type
        # off-step minutes). Confirm it is delivered.
        response = self.client.get(reverse('gtd:action_add'))
        self.assertContains(response, 'input[type="datetime-local"][step]')
