import os
from http import HTTPStatus
import pytest
import requests
from faker import Faker
from api.api_manager import ApiManager
from constants import AUTH_DATA, HOST, PORT, DATABASE_NAME, USERNAME_SQL, PASSWORD
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker


@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    return requests.Session()


@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    return ApiManager(session)


@pytest.fixture(scope="session")
def super_admin_token(api_manager):
    """
    Фикстура для получения токена SUPER_ADMIN.
    """
    response = api_manager.auth_api.login_user(AUTH_DATA, expected_status=(200, 201))
    assert response.status_code in [200, 201], f"Failed to login: {response.text}"
    return response.json()["accessToken"]


@pytest.fixture(scope="function")
def movie_data():
    """
    Фикстура для генерации динамических данных фильма.
    """
    faker = Faker()
    return {
        "name": faker.catch_phrase(),
        "imageUrl": f"https://example.com/{faker.uuid4()}.jpg",
        "price": faker.random_int(min=100, max=5000),
        "description": faker.text(max_nb_chars=200),
        "location": faker.random_element(elements=("MSK", "SPB")),
        "published": faker.boolean(chance_of_getting_true=50),
        "genreId": faker.random_int(min=1, max=10)
    }


@pytest.fixture(scope="function")
def register_user_data():
    """
    Фикстура для генерации динамических данных пользователя.
    """
    faker = Faker()
    user_data = {
        "email": faker.email(),
        "fullName": faker.name(),
        "password": faker.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True),
        "passwordRepeat": None
    }
    user_data["passwordRepeat"] = user_data["password"]
    return user_data


@pytest.fixture(scope="function")
def create_movie(api_manager, super_admin_token, movie_data):
    """
    Фикстура, возвращающая функцию для создания фильма.
    Если need_delete=True, фильм удаляется сразу после создания.
    """

    def _create_movie(need_delete=True):
        response = api_manager.movies_api.create_movie(movie_data, super_admin_token)
        movie_id = response.json()["id"]
        if need_delete:
            api_manager.movies_api.delete_movie(movie_id, super_admin_token)
        return movie_id

    return _create_movie


@pytest.fixture(scope="function")
def user_create(api_manager, register_user_data, super_admin_token):
    """
    Фикстура для создания пользователя с заданной ролью.
    Поддерживаются роли:
      - "USER": регистрируется новый пользователь;
      - "SUPER_ADMIN": производится вход с данными из AUTH_DATA.
    """

    def _create_user(role: str):
        if role == "USER":
            # Регистрация нового пользователя
            user_data = register_user_data  # получаем динамические данные
            reg_response = api_manager.auth_api.register_user(user_data)
            assert reg_response.status_code in [200, 201], f"User registration failed: {reg_response.text}"

            login_payload = {"email": user_data["email"], "password": user_data["password"]}
            login_response = api_manager.auth_api.login_user(login_payload)
            assert login_response.status_code in [200, 201], f"User login failed: {login_response.text}"
            token = login_response.json()["accessToken"]

        elif role == "SUPER_ADMIN":
            # Вход с данными супер-админа
            login_response = api_manager.auth_api.login_user(AUTH_DATA)
            assert login_response.status_code in [200, 201], f"Super admin login failed: {login_response.text}"
            token = login_response.json()["accessToken"]
        else:
            raise ValueError(f"Unsupported role: {role}")

        class User:
            def __init__(self, role, token):
                self.role = role
                self.token = token

        return User(role, token)

    return _create_user

engine = create_engine(f"postgresql+psycopg2://{USERNAME_SQL}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}") # Создаем движок (engine) для подключения к базе данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Создаем фабрику сессий
@pytest.fixture(scope="module")
def db_session():
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных.
    После завершения теста сессия автоматически закрывается.
    """
    # Создаем новую сессию
    session = SessionLocal()
    # Возвращаем сессию в тест
    yield session
    # Закрываем сессию после завершения теста
    session.close()
