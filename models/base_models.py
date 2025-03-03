from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, text, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, sessionmaker


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class LoginData(BaseModel):
    email: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Email пользователя для входа."
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Пароль пользователя."
    )
    passwordRepeat: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=100,
        description="Повтор пароля для супер-админа."
    )
    role: Optional[UserRole] = Field(
        default=UserRole.USER,
        description="Роль пользователя."
    )

    @field_validator("passwordRepeat")
    def check_password_repeat_if_superadmin(cls, repeat_value, values):
        role = values.get("role")
        password = values.get("password")
        if role == UserRole.SUPER_ADMIN:
            if not repeat_value:
                raise ValueError("Поле 'passwordRepeat' обязательно для SUPER_ADMIN.")
            if repeat_value != password:
                raise ValueError("Поля 'password' и 'passwordRepeat' должны совпадать.")
        return repeat_value


Base = declarative_base()
class UserDBModel(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    email = Column(String)
    full_name = Column(String)
    password = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    verified = Column(Boolean)
    banned = Column(Boolean)
    roles = Column(String)


class MovieDBModel(Base):
    """
    Модель для таблицы movies.
    """
    __tablename__ = 'movies'  # Имя таблицы в базе данных

    # Поля таблицы
    id = Column(String, primary_key=True)  # Уникальный идентификатор фильма
    name = Column(String, nullable=False)  # Название фильма
    description = Column(String)  # Описание фильма
    price = Column(Integer, nullable=False)  # Цена фильма
    genre_id = Column(String, ForeignKey('genres.id'), nullable=False)  # Ссылка на жанр
    image_url = Column(String)  # Ссылка на изображение
    location = Column(String)  # Локация фильма (например, "MSK")
    rating = Column(Integer)  # Рейтинг фильма
    published = Column(Boolean)  # Опубликован ли фильм
    created_at = Column(DateTime)  # Дата создания записи


class AccountTransactionTemplate(Base):
    __tablename__ = 'accounts_transaction_template'
    user = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False)