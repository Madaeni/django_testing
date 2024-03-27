from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note',
            author=cls.author
        )
        cls.another_author = User.objects.create(
            username='Другой пользователь'
        )
        cls.another_note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='another_note',
            author=cls.another_author
        )
        cls.detail_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.list_url = reverse('notes:list')

    def test_authorized_client_has_form(self):
        response = self.author_client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_in_notes(self):
        response = self.author_client.get(self.list_url)
        self.assertIn(self.note, response.context['object_list'])

    def test_correct_author_note_in_notes(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        note_authors = [note.author for note in object_list]
        self.assertNotIn(self.another_author, note_authors)
