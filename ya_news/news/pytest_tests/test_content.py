import pytest

from news.forms import CommentForm
from yanews import settings

pytestmark = pytest.mark.django_db


def test_news_count_on_page(client, several_news, home_url):
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, several_news, home_url):
    response = client.get(home_url)
    all_timestamps = [
        news.date for news in response.context['object_list']
    ]
    assert all_timestamps == sorted(all_timestamps, reverse=True)


def test_comments_order(client, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_timestamps = [
        comment.created for comment in news.comment_set.all()
    ]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
