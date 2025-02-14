from api.movies_api import MoviesAPI
from api.auth_api import AuthAPI


class ApiManager:
    """
    Class for managing API classes using a shared HTTP session.
    """

    def __init__(self, session):
        """
        Initialize ApiManager.
        :param session: HTTP session used by all API classes.
        """
        self.session = session
        self.movies_api = MoviesAPI(session)
        self.auth_api = AuthAPI(session)
