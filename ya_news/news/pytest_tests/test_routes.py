from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (
            pytest.lazy_fixture('home_url'),
            pytest.lazy_fixture('not_auth_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('login_url'),
            pytest.lazy_fixture('not_auth_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('logout_url'),
            pytest.lazy_fixture('not_auth_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('signup_url'),
            pytest.lazy_fixture('not_auth_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('detail_url'),
            pytest.lazy_fixture('not_auth_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('edit_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('delete_url'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
    ),
)
def test_pages_availability_for_users(
    parametrized_client, expected_status, url
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url'),
    ),
)
def test_redirects_for_anonymous_user(client, url, login_url):
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
