from http import HTTPStatus

class TestMoviesAPI:
    """
    Tests for verifying the functionality of the Movies API.
    """

    def test_get_all_movies(self, api_manager):
        """
        Checks the retrieval of the movies list.
        """
        response = api_manager.movies_api.get_movies()
        assert response.status_code == HTTPStatus.OK, (
            f"Unexpected status code: {response.status_code}"
        )
        assert "movies" in response.json(), "Response does not contain the 'movies' key"

    def test_filter_movies_by_price(self, api_manager):
        """
        Checks filtering movies by price.
        """
        response = api_manager.movies_api.get_movies(params={"minPrice": 100, "maxPrice": 500})
        assert response.status_code == HTTPStatus.OK, (
            f"Unexpected status code: {response.status_code}"
        )

        for movie in response.json().get("movies", []):
            assert 100 <= movie["price"] <= 500, (
                f"Movie price {movie['price']} is out of the range [100, 500]"
            )

    def test_create_movie(self, api_manager, super_admin_token, movie_data):
        """
        Checks successful movie creation and verifies its existence via GET request.
        """
        movie_id = None
        try:
            response = api_manager.movies_api.create_movie(movie_data, super_admin_token)
            assert response.status_code == HTTPStatus.CREATED, (
                f"Unexpected status code: {response.status_code}, Response: {response.text}"
            )

            response_data = response.json()
            assert "id" in response_data, f"Response does not contain 'id': {response_data}"
            assert "name" in response_data, f"Response does not contain 'name': {response_data}"
            assert response_data["name"] == movie_data["name"], (
                f"Expected {movie_data['name']}, but got {response_data['name']}"
            )

            movie_id = response_data["id"]

            get_response = api_manager.movies_api.get_movie(movie_id)
            assert get_response.status_code == HTTPStatus.OK, (
                f"Failed to fetch movie, status code: {get_response.status_code}, Response: {get_response.text}"
            )

        finally:
            if movie_id:
                response = api_manager.movies_api.delete_movie(movie_id, super_admin_token)
                assert response.status_code == HTTPStatus.OK, (
                    f"Failed to delete movie with ID {movie_id}. Response: {response.text}"
                )

    def test_delete_movie_success(self, api_manager, create_movie, super_admin_token):
        """
        Checks successful deletion of a movie with a valid ID.
        """
        movie_id = create_movie(need_delete=False)

        response = api_manager.movies_api.delete_movie(movie_id, super_admin_token)
        assert response.status_code == HTTPStatus.OK, (
            f"Unexpected status code: {response.status_code}, Response: {response.text}"
        )

        get_response = api_manager.movies_api.get_movies(super_admin_token)
        assert get_response.status_code == HTTPStatus.OK, (
            f"Failed to fetch movies, status code: {get_response.status_code}, Response: {get_response.text}"
        )

        movies = get_response.json().get("movies", [])
        assert all(movie["id"] != movie_id for movie in movies), (
            f"Movie with ID {movie_id} is still present in the movie list."
        )
