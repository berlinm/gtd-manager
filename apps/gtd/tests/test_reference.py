import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.gtd.models import (
    AreaOfResponsibility, NextAction, Project, Reference,
    ReferenceAttachment, SomedayMaybe,
)


class ReferenceViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)

    def test_list_shows_all_references(self):
        Reference.objects.create(title='Alpha')
        Reference.objects.create(title='Beta')
        response = self.client.get(reverse('gtd:reference_list'))
        self.assertContains(response, 'Alpha')
        self.assertContains(response, 'Beta')

    def test_search_filters_by_title(self):
        Reference.objects.create(title='Django tips')
        Reference.objects.create(title='Python notes')
        response = self.client.get(reverse('gtd:reference_list'), {'q': 'Django'})
        self.assertContains(response, 'Django tips')
        self.assertNotContains(response, 'Python notes')

    def test_search_filters_by_body(self):
        Reference.objects.create(title='Notes', body='queryset optimization')
        Reference.objects.create(title='Other', body='unrelated content')
        response = self.client.get(reverse('gtd:reference_list'), {'q': 'queryset'})
        self.assertContains(response, 'Notes')
        self.assertNotContains(response, 'Other')

    def test_search_no_results_shows_message(self):
        response = self.client.get(reverse('gtd:reference_list'), {'q': 'xyznotfound'})
        self.assertContains(response, 'No results')

    def test_detail_renders_markdown(self):
        ref = Reference.objects.create(title='Notes', body='## Heading\n\n- item one')
        response = self.client.get(reverse('gtd:reference_detail', kwargs={'pk': ref.pk}))
        self.assertContains(response, '<h2')
        self.assertContains(response, 'item one')

    def test_create_redirects_to_detail(self):
        response = self.client.post(
            reverse('gtd:reference_add'),
            {'title': 'New ref', 'body': 'some content'},
        )
        ref = Reference.objects.get()
        self.assertRedirects(response, reverse('gtd:reference_detail', kwargs={'pk': ref.pk}))

    def test_create_with_empty_body_is_valid(self):
        self.client.post(reverse('gtd:reference_add'), {'title': 'Shell note', 'body': ''})
        self.assertEqual(Reference.objects.count(), 1)

    def test_edit_redirects_to_detail(self):
        ref = Reference.objects.create(title='Original')
        response = self.client.post(
            reverse('gtd:reference_edit', kwargs={'pk': ref.pk}),
            {'title': 'Updated', 'body': ''},
        )
        self.assertRedirects(response, reverse('gtd:reference_detail', kwargs={'pk': ref.pk}))
        ref.refresh_from_db()
        self.assertEqual(ref.title, 'Updated')


class ReferenceAttachmentTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._media)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        shutil.rmtree(cls._media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)

    def _file(self, name='notes.txt', content=b'hello world'):
        return SimpleUploadedFile(name, content, content_type='text/plain')

    def test_create_with_attachment(self):
        self.client.post(
            reverse('gtd:reference_add'),
            {'title': 'With file', 'body': '', 'attachments': self._file()},
        )
        ref = Reference.objects.get()
        self.assertEqual(ref.attachments.count(), 1)
        self.assertEqual(ref.attachments.first().original_name, 'notes.txt')

    def test_detail_lists_attachment(self):
        ref = Reference.objects.create(title='Docs')
        ReferenceAttachment.objects.create(
            reference=ref, file=self._file(), original_name='notes.txt'
        )
        response = self.client.get(reverse('gtd:reference_detail', kwargs={'pk': ref.pk}))
        self.assertContains(response, 'notes.txt')

    def test_download_returns_file_contents(self):
        ref = Reference.objects.create(title='Docs')
        att = ReferenceAttachment.objects.create(
            reference=ref, file=self._file(content=b'payload'), original_name='notes.txt'
        )
        response = self.client.get(
            reverse('gtd:reference_attachment_download', kwargs={'pk': att.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b''.join(response.streaming_content), b'payload')

    def test_delete_removes_attachment(self):
        ref = Reference.objects.create(title='Docs')
        att = ReferenceAttachment.objects.create(
            reference=ref, file=self._file(), original_name='notes.txt'
        )
        response = self.client.post(
            reverse('gtd:reference_attachment_delete', kwargs={'pk': att.pk})
        )
        self.assertRedirects(response, reverse('gtd:reference_edit', kwargs={'pk': ref.pk}))
        self.assertEqual(ref.attachments.count(), 0)

    def test_download_requires_login(self):
        ref = Reference.objects.create(title='Docs')
        att = ReferenceAttachment.objects.create(
            reference=ref, file=self._file(), original_name='notes.txt'
        )
        self.client.logout()
        response = self.client.get(
            reverse('gtd:reference_attachment_download', kwargs={'pk': att.pk})
        )
        self.assertEqual(response.status_code, 302)


class AreaDetailViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(self.user)
        self.area = AreaOfResponsibility.objects.create(title='Work')

    def test_empty_area_shows_nothing_assigned(self):
        response = self.client.get(reverse('gtd:area_detail', kwargs={'pk': self.area.pk}))
        self.assertContains(response, 'Nothing assigned')

    def test_active_project_appears(self):
        Project.objects.create(title='Big initiative', area=self.area)
        response = self.client.get(reverse('gtd:area_detail', kwargs={'pk': self.area.pk}))
        self.assertContains(response, 'Big initiative')

    def test_on_hold_project_in_separate_section(self):
        Project.objects.create(
            title='Paused project',
            area=self.area,
            status=Project.Status.ON_HOLD,
            on_hold_reason='waiting',
        )
        response = self.client.get(reverse('gtd:area_detail', kwargs={'pk': self.area.pk}))
        self.assertContains(response, 'Paused project')
        self.assertContains(response, 'On hold')

    def test_reference_appears(self):
        Reference.objects.create(title='Work guidelines', area=self.area)
        response = self.client.get(reverse('gtd:area_detail', kwargs={'pk': self.area.pk}))
        self.assertContains(response, 'Work guidelines')

    def test_someday_item_appears(self):
        SomedayMaybe.objects.create(title='Automate reporting', area=self.area)
        response = self.client.get(reverse('gtd:area_detail', kwargs={'pk': self.area.pk}))
        self.assertContains(response, 'Automate reporting')

    def test_deferred_action_excluded_from_standalone_actions(self):
        from datetime import date, timedelta
        NextAction.objects.create(
            title='Future task',
            area=self.area,
            defer_until=date.today() + timedelta(days=5),
        )
        response = self.client.get(reverse('gtd:area_detail', kwargs={'pk': self.area.pk}))
        self.assertNotContains(response, 'Future task')
