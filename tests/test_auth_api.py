from http import HTTPStatus


class TestAuthAPI:
    """
    Tests for verifying the functionality of the Authentication API.
    """

    def test_register_user(self, api_manager, register_user_data):
        """
        Checks successful user registration.
        """
        response = api_manager.auth_api.register_user(register_user_data)
        assert response.status_code == HTTPStatus.CREATED, (
            f"Unexpected status code: {response.status_code}, Response: {response.text}"
        )

        response_data = response.json()
        assert register_user_data["email"] == response_data.get("email"), (
            f"Expected email {register_user_data['email']}, but got {response_data.get('email')}"
        )
        assert register_user_data["fullName"] == response_data.get("fullName"), (
            f"Expected fullName {register_user_data['fullName']}, but got {response_data.get('fullName')}"
        )

    def test_register_invalid_user(self, api_manager, register_user_data):
        """
        Checks successful user registration.
        """
        register_user_data["password"] = "123"
        response = api_manager.auth_api.register_user(register_user_data, expected_status=HTTPStatus.BAD_REQUEST)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f"Unexpected status code: {response.status_code}, Response: {response.text}"
        )

    def test_login_user(self, api_manager, register_user_data):
        """
        Checks successful user login after registration.
        """
        register_response = api_manager.auth_api.register_user(register_user_data)
        assert register_response.status_code == HTTPStatus.CREATED, (
            f"Registration failed: {register_response.status_code}, Response: {register_response.text}"
        )

        login_user = {
            "email": register_user_data["email"],
            "password": register_user_data["password"]
        }

        response = api_manager.auth_api.login_user(login_user)
        assert response.status_code == HTTPStatus.OK, (
            f"Login failed: {response.status_code}, Response: {response.text}"
        )

        response_data = response.json()
        user_data = response_data.get("user", {})

        assert user_data.get("email") == login_user["email"], (
            f"Expected email {login_user['email']}, but got {user_data.get('email')}"
        )

    def test_invalid_login_user(self, api_manager, register_user_data):
        login_user = {
            "email": register_user_data["email"],
            "password": register_user_data["password"]
        }
        response = api_manager.auth_api.login_user(login_user, expected_status=HTTPStatus.UNAUTHORIZED)
        assert response.status_code == HTTPStatus.UNAUTHORIZED
