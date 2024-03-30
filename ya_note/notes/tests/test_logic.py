from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TITLE = 'Другой заголовок'
    NEW_NOTE_TEXT = 'Другой текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.user = User.objects.create(username='Читатель')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )

        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
        }

        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

        cls.notes_count_at_start = Note.objects.count()

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(
            self.add_url, data=self.form_data
        )
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count() - self.notes_count_at_start, 0)

    def test_empty_slug(self):
        notes = set(Note.objects.all())
        response = self.auth_client.post(
            self.add_url, data=self.form_data
        )
        new_note = set(Note.objects.all())
        self.assertRedirects(response, self.success_url)
        self.assertEqual(len(new_note) - self.notes_count_at_start, 1)
        self.assertEqual(
            (new_note - notes).pop().slug,
            slugify(self.form_data['title'])
        )

    def test_user_can_create_note(self):
        response = self.author_client.post(self.add_url, data=self.form_data)
        new_notes = Note.objects.all()
        self.assertRedirects(response, self.success_url)
        self.assertEqual(new_notes.count() - self.notes_count_at_start, 1)
        note = new_notes.latest('pk')
        self.assertEqual(note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count() - self.notes_count_at_start, 0)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertFalse(
            Note.objects.filter(slug=self.note.slug).exists()
        )

    def test_user_cant_delete_note_of_another_user(self):
        response = self.auth_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(
            Note.objects.filter(slug=self.note.slug).exists()
        )

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.note.author)
