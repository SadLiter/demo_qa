import pytest

class TestRoles:
    @pytest.mark.parametrize("role, expected_status", [
        ("USER", [403]),       # Пользователь с ролью USER не может удалять фильмы
        ("SUPER_ADMIN", [200, 201])         # SUPER_ADMIN может удалять фильмы
    ])
    def test_delete_movie_by_role(self, api_manager, user_create, movie_data, super_admin_token, role, expected_status):
        """
        Проверяет, какие роли могут удалять фильмы.
        Для SUPER_ADMIN фильм создаётся с его же токеном.
        Для USER фильм создаётся через супер-админа (чтобы гарантировать, что он существует),
        а попытка удаления от имени USER должна вернуть статус 403.
        """
        user = user_create(role)

        if role == "SUPER_ADMIN":
            # Создаем фильм от имени SUPER_ADMIN
            movie_data_local = movie_data.copy()
            movie_data_local["name"] = f"{role} Movie to Delete)"
            create_response = api_manager.movies_api.create_movie(movie_data_local, user.token)
            assert create_response.status_code in [200, 201], (
                f"{role} должен создавать фильм, но получил {create_response.status_code}"
            )
            movie_id = create_response.json()["id"]
        else:  # role == "USER"
            # Создаем фильм через супер-админа, чтобы фильм точно существовал
            create_response = api_manager.movies_api.create_movie(movie_data, super_admin_token)
            assert create_response.status_code in [200, 201], (
                f"Movie creation via super admin failed: {create_response.status_code}"
            )
            movie_id = create_response.json()["id"]

        # Пытаемся удалить фильм с использованием токена созданного пользователя
        delete_response = api_manager.movies_api.delete_movie(movie_id, user.token, expected_status=expected_status)
        assert delete_response.status_code in expected_status, (
            f"{role} должен получить статус {expected_status}, но получил {delete_response.status_code}"
        )

        # Если удаление не произошло (для USER), делаем cleanup от имени супер-админа
        if delete_response.status_code not in [200, 201]:
            cleanup_response = api_manager.movies_api.delete_movie(movie_id, super_admin_token)
            assert cleanup_response.status_code in [200, 201], (
                f"Cleanup deletion failed: {cleanup_response.status_code}"
            )
