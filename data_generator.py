import random
import string


class DataGenerator:
    @staticmethod
    def generate_funny_movie_title():
        """Генерирует смешное название фильма с припиской _AQA_"""
        adjectives = ["Смешной", "Безумный", "Эпический", "Забавный", "Неожиданный"]
        nouns = ["Тестер", "Баг", "Джун", "Сеньор", "Плейсхолдер"]
        return f"{random.choice(adjectives)} {random.choice(nouns)}_AQA_"

    @staticmethod
    def generate_random_email():
        """Генерирует случайный email"""
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kekk{random_string}@gmail.com"
