import requests
from http import HTTPStatus


class CustomRequester:
    base_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, session, base_url):
        """
        Initialize the custom requester.
        :param session: requests.Session object.
        :param base_url: Base URL for the API.
        """
        self.base_url = base_url
        self.session = session
        self.headers = self.base_headers.copy()

    def send_request(self, method, endpoint, headers=None, data=None, params=None,
                     expected_status=HTTPStatus.OK, need_logging=True):
        """
        Universal method for sending HTTP requests.
        :param method: HTTP method (GET, POST, PUT, DELETE, etc.).
        :param endpoint: API endpoint (e.g., "/login").
        :param headers: Additional headers (e.g., with authorization token).
        :param data: Request body (JSON data).
        :param params: Query parameters.
        :param expected_status: Expected HTTP status code (default HTTPStatus.OK).
        :param need_logging: Flag to log the request/response (default True).
        :return: requests.Response object.
        """
        url = f"{self.base_url}{endpoint}"

        # Merge base headers with any provided headers
        request_headers = {**self.headers, **(headers or {})}

        response = self.session.request(method, url, json=data, params=params, headers=request_headers)

        if need_logging:
            self.log_request_and_response(response)

        if response.status_code != expected_status:
            raise ValueError(
                f"Unexpected status code: {response.status_code} ({HTTPStatus(response.status_code).phrase}). "
                f"Expected: {expected_status} ({expected_status.phrase})"
            )

        return response

    def log_request_and_response(self, response):
        """
        Logs the request and response details.
        :param response: Response object.
        """
        print("\n======================================== REQUEST ========================================")
        print(f"Method: {response.request.method}")
        print(f"URL: {response.request.url}")
        print(f"Headers: {response.request.headers}")
        if response.request.body:
            print(f"Body: {response.request.body}")

        print("\n======================================== RESPONSE =======================================")
        print(f"Status Code: {response.status_code} ({HTTPStatus(response.status_code).phrase})")
        print(f"Response Data: {response.text}")
