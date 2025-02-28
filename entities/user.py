class User:
    def __init__(self, email: str, password: str, roles: list, api_manager):
        self.email = email
        self.password = password
        self.roles = roles
        self.api_manager = api_manager  # Экземпляр API Manager для запросов

    @property
    def creds(self):
        """Возвращает кортеж (email, password)"""
        return self.email, self.password