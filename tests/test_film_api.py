import datetime
import random
from http import HTTPStatus

import pytest

from models.base_models import MovieDBModel, AccountTransactionTemplate


class TestMoviesAPI:
    """
    Tests for verifying the functionality of the Movies API.
    """

    def test_get_all_movies(self, api_manager):
        """
        Checks the retrieval of the movies list.
        """
        response = api_manager.movies_api.get_movies()
        assert response.status_code in [200, 201], (
            f"Unexpected status code: {response.status_code}"
        )
        assert "movies" in response.json(), "Response does not contain the 'movies' key"

    def test_filter_movies_by_price(self, api_manager):
        """
        Checks filtering movies by price.
        """
        response = api_manager.movies_api.get_movies(params={"minPrice": 100, "maxPrice": 500})
        assert response.status_code in [200, 201], (
            f"Unexpected status code: {response.status_code}"
        )

        for movie in response.json().get("movies", []):
            assert 100 <= movie["price"] <= 500, (
                f"Movie price {movie['price']} is out of the range [100, 500]"
            )

    def test_create_movie(self, api_manager, super_admin_token, movie_data):
        """
        Checks successful movie creation and verifies its existence via GET request.
        """
        movie_id = None
        try:
            response = api_manager.movies_api.create_movie(movie_data, super_admin_token)
            assert response.status_code in [200, 201], (
                f"Unexpected status code: {response.status_code}, Response: {response.text}"
            )

            response_data = response.json()
            assert "id" in response_data, f"Response does not contain 'id': {response_data}"
            assert "name" in response_data, f"Response does not contain 'name': {response_data}"
            assert response_data["name"] == movie_data["name"], (
                f"Expected {movie_data['name']}, but got {response_data['name']}"
            )

            movie_id = response_data["id"]

            get_response = api_manager.movies_api.get_movie(movie_id)
            assert get_response.status_code in [200, 201], (
                f"Failed to fetch movie, status code: {get_response.status_code}, Response: {get_response.text}"
            )

        finally:
            if movie_id:
                response = api_manager.movies_api.delete_movie(movie_id, super_admin_token)
                assert response.status_code in [200, 201], (
                    f"Failed to delete movie with ID {movie_id}. Response: {response.text}"
                )

    def test_delete_movie_success(self, api_manager, create_movie, super_admin_token):
        """
        Checks successful deletion of a movie with a valid ID.
        """
        movie_id = create_movie(need_delete=False)

        response = api_manager.movies_api.delete_movie(movie_id, super_admin_token)
        assert response.status_code in [200, 201], (
            f"Unexpected status code: {response.status_code}, Response: {response.text}"
        )

        get_response = api_manager.movies_api.get_movies(super_admin_token)
        assert get_response.status_code in [200, 201], (
            f"Failed to fetch movies, status code: {get_response.status_code}, Response: {get_response.text}"
        )

        movies = get_response.json().get("movies", [])
        assert all(movie["id"] != movie_id for movie in movies), (
            f"Movie with ID {movie_id} is still present in the movie list."
        )

    def test_create_delete_movie(self, api_manager, super_admin_token, db_session, movie_data):
        # как бы выглядел SQL запрос
        """SELECT id, "name", price, description, image_url, "location", published, rating, genre_id, created_at
           FROM public.movies
           WHERE name='Test Moviej1h8qss9s5';"""

        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_data["name"])

        # проверяем что до начала тестирования фильма с таким названием нет
        assert movies_from_db.count() == 0, "В базе уже присутствует фильм с таким названием"

        response = api_manager.movies_api.create_movie(
            movie_data,
            super_admin_token
        )
        assert response.status_code == 201, "Фильм должен успешно создаться"
        response = response.json()

        # проверяем после вызова api_manager.movies_api.create_movie в базе появился наш фильм
        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_data["name"])
        assert movies_from_db.count() == 1, "В базе уже присутствует фильм с таким названием"

        movie_from_db = movies_from_db.first()
        # можете обратить внимание что в базе данных етсь поле created_at которое мы не здавали явно
        # наш сервис сам его заполнил. проверим что он заполнил его верно с погрешностью в 5 минут
        assert movie_from_db.created_at >= (
                datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(
                minutes=5)), "Сервис выставил время создания с большой погрешностью"

        # Берем айди фильма который мы только что создали и  удаляем его из базы через апи
        # Удаляем фильм
        delete_response = api_manager.movies_api.delete_movie(movie_id=response["id"], token=super_admin_token)
        assert delete_response.status_code == 200, "Фильм должен успешно удалиться"

        # проверяем что в конце тестирования фильма с таким названием действительно нет в базе
        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_data["name"])
        assert movies_from_db.count() == 0, "Фильм небыл удален из базы!"

    @pytest.mark.parametrize(
        "stan_balance, bob_balance, transfer_amount, expected_exception, expected_stan_balance, expected_bob_balance",
        [
            # Позитивный кейс: перевод 200 единиц от Stan к Bob
            (1000, 500, 200, None, 800, 700),
            # Негативный кейс: на счёте Stan недостаточно средств для перевода 200 единиц
            (100, 500, 200, ValueError, 100, 500),
        ]
    )
    def test_accounts_transaction_template(self, db_session, stan_balance, bob_balance, transfer_amount, expected_exception,
                                           expected_stan_balance, expected_bob_balance):
        # ====================================================================== Подготовка к тесту
        # Создаем записи в базе данных с параметризованными балансами
        stan = AccountTransactionTemplate(user=f"Stan_{random.randint(1, 100)}", balance=stan_balance)
        bob = AccountTransactionTemplate(user=f"Bob_{random.randint(1, 100)}", balance=bob_balance)

        # Добавляем записи в сессию
        db_session.add_all([stan, bob])
        db_session.commit()

        def transfer_money(session, from_account, to_account, amount):
            """
            Переводит деньги с одного счета на другой.
            :param session: Сессия SQLAlchemy.
            :param from_account: имя счета, с которого списываются деньги.
            :param to_account: имя счета, на который зачисляются деньги.
            :param amount: Сумма перевода.
            """
            # Получаем счета
            from_acc = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
            to_acc = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            # Проверяем, что на счете достаточно средств
            if from_acc.balance < amount:
                raise ValueError("Недостаточно средств на счете")

            # Выполняем перевод
            from_acc.balance -= amount
            to_acc.balance += amount
            session.commit()

        # ====================================================================== Тест
        # Проверяем начальные балансы
        assert stan.balance == stan_balance
        assert bob.balance == bob_balance

        if expected_exception:
            with pytest.raises(expected_exception):
                transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=transfer_amount)
        else:
            transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=transfer_amount)
            # Обновляем объекты из базы, чтобы получить актуальные значения
            db_session.refresh(stan)
            db_session.refresh(bob)
            assert stan.balance == expected_stan_balance
            assert bob.balance == expected_bob_balance

        # ====================================================================== Очистка данных
        db_session.delete(stan)
        db_session.delete(bob)
        db_session.commit()