from constants import LOGIN_ENDPOINT, REGISTER_ENDPOINT, AUTH_API_BASE_URL
from requester.custom_requester import CustomRequester


class AuthAPI(CustomRequester):
    """
    API class for handling authentication.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url=AUTH_API_BASE_URL)

    def register_user(self, user_data, expected_status=200):
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

    def login_user(self, login_data, expected_status=200):
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
