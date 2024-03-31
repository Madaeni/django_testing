from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING, BAD_WORDS
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(
    client, detail_url, form_data, count_comments_at_start
):
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() - count_comments_at_start == 0


def test_user_can_create_comment(
    author_client, news, detail_url, form_data, author
):
    comments = set(Comment.objects.all())
    assertRedirects(
        author_client.post(detail_url, data=form_data),
        f'{detail_url}#comments'
    )
    new_comments = set(Comment.objects.all())
    assert len(new_comments - comments) == 1
    new_comment = (new_comments - comments).pop()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_comment_not_contain_bad_words(
    author_client, detail_url, form_data, count_comments_at_start
):
    form_data['text'] = f'Некий {BAD_WORDS[0]} текст'
    response = author_client.post(detail_url, data=form_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() - count_comments_at_start == 0


def test_author_can_edit_note(
    author_client, detail_url, edit_url, comment, form_data
):
    assertRedirects(
        author_client.post(edit_url, form_data),
        f'{detail_url}#comments'
    )
    edited_comment = Comment.objects.get(pk=comment.pk)
    assert edited_comment.text == form_data['text']
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author


def test_not_author_cant_edit_note(
    not_author_client, edit_url, comment, form_data
):
    response = not_author_client.post(edit_url, form_data)
    edited_comment = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert edited_comment.text == comment.text
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author


def test_author_can_delete_note(
    author_client, detail_url, delete_url, comment
):
    assertRedirects(
        author_client.post(delete_url),
        f'{detail_url}#comments'
    )
    assert not Comment.objects.filter(id=comment.pk).exists()


def test_other_user_cant_delete_note(
    not_author_client, delete_url, comment
):
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.pk).exists()
