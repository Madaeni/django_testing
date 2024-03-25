from datetime import datetime, timedelta
import pytest

from django.test.client import Client

from news.models import Comment, News
from yanews import settings


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def not_auth_client():
    return Client()


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def several_news():
    today = datetime.today()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст новости',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def news_pk(news):
    return (news.pk,)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст',
    )
    return comment


@pytest.fixture
def comments(news, author):
    today = datetime.today()
    return Comment.objects.bulk_create(
        Comment(
            news=news,
            author=author,
            text=f'Tекст {index}',
            created=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment_pk(comment):
    return (comment.pk,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
