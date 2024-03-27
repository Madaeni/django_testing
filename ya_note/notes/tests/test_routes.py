from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.not_auth_client = Client()

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.success_url = reverse('notes:success')
        cls.note_add_url = reverse('notes:add')
        cls.note_list_url = reverse('notes:list')
        cls.note_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.note_detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.note_delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_availability(self):
        users_statuses = [
            (self.home_url, self.not_auth_client, HTTPStatus.OK),
            (self.home_url, self.reader_client, HTTPStatus.OK),
            (self.login_url, self.not_auth_client, HTTPStatus.OK),
            (self.login_url, self.reader_client, HTTPStatus.OK),
            (self.signup_url, self.not_auth_client, HTTPStatus.OK),
            (self.signup_url, self.reader_client, HTTPStatus.OK),
            (self.note_add_url, self.reader_client, HTTPStatus.OK),
            (self.note_list_url, self.reader_client, HTTPStatus.OK),
            (self.success_url, self.reader_client, HTTPStatus.OK),
            (self.note_edit_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.note_edit_url, self.author_client, HTTPStatus.OK),
            (self.note_detail_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.note_detail_url, self.author_client, HTTPStatus.OK),
            (self.note_delete_url, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.note_delete_url, self.author_client, HTTPStatus.OK),
            (self.logout_url, self.not_auth_client, HTTPStatus.OK),
            (self.logout_url, self.reader_client, HTTPStatus.OK),
        ]
        for url, user_client, status in users_statuses:
            with self.subTest(url=url, user_client=user_client, status=status):
                response = user_client.get(url)
                self.assertEqual(
                    response.status_code,
                    status,
                    msg=f'Редирект: {response.headers.get("Location")}'
                )

    def test_omg_wtf(self):
        users_statuses = [
            (self.note_edit_url, self.author_client, HTTPStatus.OK),
            (self.home_url, self.reader_client, HTTPStatus.NOT_FOUND),
        ]
        for url, user_client, status in users_statuses:
            with self.subTest(url=url, user_client=user_client, status=status):
                response = user_client.get(self.note_delete_url)
                self.assertEqual(
                    response.status_code,
                    status,
                    msg=f'Редирект: {response.headers.get("Location")}'
                )

    def test_redirect_for_anonymous_client(self):
        urls = [
            self.note_add_url,
            self.note_edit_url,
            self.note_detail_url,
            self.note_delete_url,
            self.note_list_url,
            self.success_url
        ]
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.not_auth_client.get(url)
                self.assertRedirects(response, redirect_url)
