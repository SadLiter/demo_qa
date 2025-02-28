from constants import LOGIN_ENDPOINT, REGISTER_ENDPOINT, AUTH_API_BASE_URL
from requester.custom_requester import CustomRequester
from http import HTTPStatus


class AuthAPI(CustomRequester):
    """
    API class for handling authentication.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url=AUTH_API_BASE_URL)

    def register_user(self, user_data, expected_status=(200, 201)):
        """
        Registers a new user.
        :param user_data: User data.
        :param expected_status: Expected HTTP status code.
        :return: Response object.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=(200, 201)):
        """
        Logs in a user.
        :param login_data: Login credentials.
        :param expected_status: Expected HTTP status code.
        :return: Response object.
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=expected_status
        )

    def change_user_role(self, user_id, new_roles, admin_token):
        """Изменяет роль пользователя"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        data = {"roles": new_roles}
        return self.send_request("PATCH", f"/user/{user_id}", data=data, headers=headers)

    def delete_user(self, user_id, admin_token):
        """Удаляет пользователя (только для ADMIN и SUPER_ADMIN)"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        return self.send_request("DELETE", f"/user/{user_id}", headers=headers,
                                 expected_status=[200, 204, 404])

    def get_user(self, user_id, admin_token):
        """Получение информации о пользователе."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = self.send_request("GET", f"/user/{user_id}", headers=headers, expected_status=[200])
        return response.json()
