from http import HTTPStatus
from models.base_models import LoginData, UserDBModel


class TestAuthAPI:
    """
    Tests for verifying the functionality of the Authentication API.
    """

    def test_register_user(self, api_manager, register_user_data):
        """
        Checks successful user registration.
        """
        response = api_manager.auth_api.register_user(register_user_data)
        assert response.status_code in [200, 201], (
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
        Checks user registration with invalid password.
        """
        register_user_data["password"] = "123"
        response = api_manager.auth_api.register_user(register_user_data, expected_status=(400, 401))
        assert response.status_code in [400], (
            f"Unexpected status code: {response.status_code}, Response: {response.text}"
        )

    def test_login_user(self, api_manager, register_user_data):
        """
        Checks successful user login after registration.
        """
        # Регистрируем пользователя
        register_response = api_manager.auth_api.register_user(register_user_data)

        # Вместо словаря создаём экземпляр модели LoginData
        login_data = LoginData(
            email=register_user_data["email"],
            password=register_user_data["password"]
        )

        response = api_manager.auth_api.login_user(login_data)
        assert response.status_code in [200, 201], (
            f"Login failed: {response.status_code}, Response: {response.text}"
        )

        response_data = response.json()
        user_data = response_data.get("user", {})

        assert user_data.get("email") == login_data.email, (
            f"Expected email {login_data.email}, but got {user_data.get('email')}"
        )

    def test_invalid_login_user(self, api_manager, register_user_data):
        # Создаем экземпляр модели LoginData для невалидного логина
        login_data = LoginData(
            email=register_user_data["email"],
            password=register_user_data["password"]
        )
        response = api_manager.auth_api.login_user(login_data, expected_status=(400, 401))
        assert response.status_code in [400, 401]

    def test_register_user_db_session(self, api_manager, register_user_data, db_session):
        """
        Тест на регистрацию пользователя с проверкой в базе данных.
        """
        # выполняем запрос на регистрацию нового пользователя
        response = api_manager.auth_api.register_user(register_user_data)
        register_user_response = response.json()

        # Проверяем добавил ли сервис Auth нового пользователя в базу данных
        users_from_db = db_session.query(UserDBModel).filter(UserDBModel.id == register_user_response.get('id'))

        # получили обьект из бзы данных и проверили что он действительно существует в единственном экземпляре
        assert users_from_db.count() == 1, "обьект не попал в базу данных"
        # Достаем первый и единственный обьект из списка полученных
        user_from_db = users_from_db.first()
        # можем осуществить проверку всех полей в базе данных например Email
        assert user_from_db.email == register_user_data['email'], "Email не совпадает"
