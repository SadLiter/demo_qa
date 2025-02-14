import pytest
import requests
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
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["accessToken"]


@pytest.fixture(scope="session")
def movie_data():
    """
    Fixture for movie data.
    """
    return {
        "name": "Test Movie8",
        "imageUrl": "https://example.com/movie.jpg",
        "price": 1000,
        "description": "Test movie description",
        "location": "MSK",
        "published": True,
        "genreId": 7,
    }


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
