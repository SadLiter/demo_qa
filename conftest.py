from http import HTTPStatus

import pytest
import requests
from faker import Faker
from api.api_manager import ApiManager
from constants import AUTH_DATA


@pytest.fixture(scope="session")
def session():
    """
    Fixture for creating an HTTP session.
    """
    return requests.Session()


@pytest.fixture(scope="session")
def api_manager(session):
    """
    Fixture for creating an instance of ApiManager.
    """
    return ApiManager(session)


@pytest.fixture(scope="session")
def super_admin_token(api_manager):
    """
    Fixture for obtaining the SUPER_ADMIN token.
    """
    response = api_manager.auth_api.login_user(AUTH_DATA)
    assert response.status_code == HTTPStatus.OK, f"Failed to login: {response.text}"
    return response.json()["accessToken"]


@pytest.fixture(scope="function")
def movie_data():
    """
    Fixture for generating dynamic movie data.
    """
    faker = Faker()
    return {
        "name": faker.catch_phrase(),
        "imageUrl": f"https://example.com/{faker.uuid4()}.jpg",
        "price": faker.random_int(min=100, max=5000),
        "description": faker.text(max_nb_chars=200),
        "location": faker.random_element(elements=("MSK", "SPB")),
        "published": faker.boolean(chance_of_getting_true=50),
        "genreId": faker.random_int(min=1, max=10)
    }


@pytest.fixture(scope="function")
def register_user_data():
    """
    Fixture for generating dynamic user data.
    """
    faker = Faker()
    user_data = {
        "email": faker.email(),
        "fullName": faker.name(),
        "password": faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "passwordRepeat": None
    }

    user_data["passwordRepeat"] = user_data["password"]
    return user_data


@pytest.fixture(scope="function")
def create_movie(api_manager, super_admin_token, movie_data):
    """
    Fixture that returns a function to create a movie.
    :param need_delete: If True, the movie is deleted immediately after creation.
    """

    def _create_movie(need_delete=True):
        response = api_manager.movies_api.create_movie(movie_data, super_admin_token)
        movie_id = response.json()["id"]
        if need_delete:
            api_manager.movies_api.delete_movie(movie_id, super_admin_token)
        return movie_id

    return _create_movie
