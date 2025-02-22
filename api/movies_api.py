from http import HTTPStatus

from constants import MOVIES_API_BASE_URL
from requester.custom_requester import CustomRequester


class MoviesAPI(CustomRequester):
    """
    API class for handling movie-related operations.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIES_API_BASE_URL)

    def get_movies(self, params=None):
        """
        Retrieves the list of movies with optional filtering.
        :param params: Dictionary of query parameters.
        :return: Response object.
        """
        return self.send_request(method='GET', endpoint='/movies', params=params)

    def get_movie(self, movie_id):
        """
        Retrieves movie details by ID.
        :param movie_id: Movie identifier.
        :return: Response object.
        """
        return self.send_request(method='GET', endpoint=f'/movies/{movie_id}')

    def create_movie(self, data, token):
        """
        Creates a new movie.
        :param data: Dictionary with movie data.
        :param token: Authorization token for SUPER_ADMIN.
        :return: Response object.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self.send_request(
            method='POST',
            endpoint='/movies',
            data=data,
            headers=headers,
            expected_status=HTTPStatus.CREATED
        )

    def delete_movie(self, movie_id, token):
        """
        Deletes a movie by its ID.
        :param movie_id: Movie identifier.
        :param token: Authorization token for SUPER_ADMIN.
        :return: Response object.
        """
        headers = {"Authorization": f"Bearer {token}"}
        return self.send_request(method='DELETE', endpoint=f'/movies/{movie_id}', headers=headers)
