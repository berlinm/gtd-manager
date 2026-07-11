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

    def test_time_options_respect_interval(self):
        p15 = Preferences(time_step_minutes=15)
        vals15 = [v for v, _ in p15.time_options() if v]
        self.assertEqual(len(vals15), 96)          # 24h / 15min
        self.assertIn('09:15:00', vals15)
        self.assertNotIn('09:07:00', vals15)       # off-interval never offered
        p30 = Preferences(time_step_minutes=30)
        vals30 = [v for v, _ in p30.time_options() if v]
        self.assertEqual(len(vals30), 48)
        self.assertNotIn('09:15:00', vals30)

    def test_time_options_labels_follow_time_format(self):
        labels12 = dict(Preferences(time_format='12').time_options())
        self.assertEqual(labels12['13:30:00'], '1:30 p.m.')
        labels24 = dict(Preferences(time_format='24').time_options())
        self.assertEqual(labels24['13:30:00'], '13:30')

    def test_action_form_renders_time_select_not_free_input(self):
        # The picker must OFFER only interval options (a <select>), not a free
        # datetime-local that lets a user type an off-interval minute.
        Preferences.objects.create(time_step_minutes=30)
        html = self.client.get(reverse('gtd:action_add')).content.decode()
        self.assertNotIn('datetime-local', html)
        self.assertIn('name="scheduled_for_1"', html)   # the time <select>
        self.assertIn('<option value="09:30:00"', html)
        self.assertNotIn('<option value="09:15:00"', html)  # off-interval absent
