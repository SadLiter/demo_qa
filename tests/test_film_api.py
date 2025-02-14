class TestMoviesAPI:
    """
    Tests for verifying the functionality of the Movies API.
    """

    def test_auth_token(self, super_admin_token):
        """
        Checks that the authorization token is retrieved correctly.
        """
        assert super_admin_token, "Authorization token should not be empty"
        assert super_admin_token.startswith("eyJ"), "Token should be a valid JWT"

    def test_movie_data(self, movie_data):
        """
        Checks the correctness of the movie data.
        """
        assert "name" in movie_data, "Movie name must be provided"
        assert "price" in movie_data, "Movie price must be provided"
        assert movie_data["price"] > 0, "Movie price must be greater than 0"

    def test_get_all_movies(self, api_manager):
        """
        Checks retrieval of the movies list.
        """
        response = api_manager.movies_api.get_movies()
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
        assert "movies" in response.json(), "Response does not contain the 'movies' key"

    def test_filter_movies_by_price(self, api_manager):
        """
        Checks filtering movies by price.
        """
        response = api_manager.movies_api.get_movies(params={"minPrice": 100, "maxPrice": 500})
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
        for movie in response.json()["movies"]:
            assert 100 <= movie["price"] <= 500, f"Movie price {movie['price']} is out of the range [100, 500]"

    def test_create_movie(self, api_manager, super_admin_token, movie_data):
        """
        Checks successful movie creation and deletes it after the test.
        """
        movie_id = None
        try:
            response = api_manager.movies_api.create_movie(movie_data, super_admin_token)
            assert response.status_code == 201, f"Unexpected status code: {response.status_code}, Response: {response.text}"

            response_data = response.json()
            assert "id" in response_data, f"Response does not contain 'id': {response_data}"
            assert "name" in response_data, f"Response does not contain 'name': {response_data}"
            assert response_data["name"] == movie_data[
                "name"], f"Expected {movie_data['name']}, got {response_data['name']}"

            movie_id = response_data["id"]
        finally:
            if movie_id:
                response = api_manager.movies_api.delete_movie(movie_id, super_admin_token)
                assert response.status_code == 200, f"Failed to delete movie with ID {movie_id}. Response: {response.text}"

    def test_delete_movie_success(self, api_manager, create_movie, super_admin_token):
        """
        Checks successful deletion of a movie with a valid ID.
        """
        # Create a movie without auto-deletion
        movie_id = create_movie(need_delete=False)
        response = api_manager.movies_api.delete_movie(movie_id, super_admin_token)
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}, Response: {response.text}"
