import requests
from http import HTTPStatus
from enums.colors import RED, GREEN, RESET
import logging
import os


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
        self.logger = logging.getLogger(__name__)

    def send_request(self, method, endpoint, headers=None, data=None, params=None,
                     expected_status=(200, 201), need_logging=True):
        """
        Universal method for sending HTTP requests.
        :param method: HTTP method (GET, POST, PUT, DELETE, etc.).
        :param endpoint: API endpoint (e.g., "/login").
        :param headers: Additional headers (e.g., with authorization token).
        :param data: Request body (JSON data).
        :param params: Query parameters.
        :param expected_status: Expected HTTP status code (default (200, 201)).
        :param need_logging: Flag to log the request/response (default True).
        :return: requests.Response object.
        """
        url = f"{self.base_url}{endpoint}"

        # Merge base headers with any provided headers
        request_headers = {**self.headers, **(headers or {})}

        response = self.session.request(method, url, json=data, params=params, headers=request_headers)

        if need_logging:
            self.log_request_and_response(response)

        # Подготовка строки с ожидаемыми статусами
        if isinstance(expected_status, (list, tuple)):
            expected_phrase = ", ".join(f"{s} ({HTTPStatus(s).phrase})" for s in expected_status)
        else:
            expected_phrase = f"{expected_status} ({HTTPStatus(expected_status).phrase})"

        if response.status_code not in expected_status:
            raise ValueError(
                f"Unexpected status code: {response.status_code} ({HTTPStatus(response.status_code).phrase}). "
                f"Expected: {expected_phrase}"
            )

        return response

    def log_request_and_response(self, response):
        """
        Logs the request and response details.
        :param response: Response object.
        """
        try:
            request = response.request
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                body = f"-d '{body}' \n" if body != '{}' else ''

            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_status = response.status_code
            is_success = response.ok
            response_data = response.text
            if not is_success:
                self.logger.info(f"\tRESPONSE:"
                                 f"\nSTATUS_CODE: {RED}{response_status}{RESET}"
                                 f"\nDATA: {RED}{response_data}{RESET}")
        except Exception as e:
            self.logger.info(f"\nLogging went wrong: {type(e)} - {e}")
