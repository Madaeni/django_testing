from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import WARNING, BAD_WORDS
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news_pk, form_data):
    client.post(reverse('news:detail', args=news_pk), data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, news, news_pk, form_data, author
):
    url = reverse('news:detail', args=news_pk)
    assertRedirects(author_client.post(url, data=form_data), f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == 'Новый текст'
    assert comment.news == news
    assert comment.author == author


def test_comment_not_contain_bad_words(
    author_client, news_pk, comment, form_data
):
    url = reverse('news:detail', args=news_pk)
    form_data['text'] = f'Некий {BAD_WORDS[0]} текст'
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 1


def test_author_can_edit_note(
    author_client, news_pk, comment_pk, form_data, comment
):
    response = author_client.post(
        reverse('news:edit', args=comment_pk),
        form_data
    )
    assertRedirects(
        response,
        f'{reverse("news:detail", args=news_pk)}#comments'
    )
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_not_author_cant_edit_note(
    not_author_client, comment, comment_pk, form_data
):
    response = not_author_client.post(
        reverse('news:edit', args=comment_pk), form_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == Comment.objects.get(id=comment.id).text


def test_author_can_delete_note(author_client, news_pk, comment_pk):
    response = author_client.post(
        reverse('news:delete', args=comment_pk)
    )
    assertRedirects(
        response,
        f'{reverse("news:detail", args=news_pk)}#comments'
    )
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(
    not_author_client, comment_pk
):
    response = not_author_client.post(
        reverse('news:delete', args=comment_pk)
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
