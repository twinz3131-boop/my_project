"""
Email на основе имени и фамилии (реалистично, с транслитерацией).
"""
import random
from config import EMAIL_DOMAINS, EMAIL_DIGIT_CHANCE
from .base_generator import BaseGenerator
from src.utils.helpers import slugify


class EmailGenerator(BaseGenerator):
    def __init__(self, locale: str = "ru"):
        super().__init__(locale)
        self._domains = EMAIL_DOMAINS[self.locale]

    def generate_from_name(self, first_name: str, last_name: str) -> str:
        login = f"{slugify(first_name)}.{slugify(last_name)}"

        if random.random() < EMAIL_DIGIT_CHANCE:
            suffix = str(random.randint(1, 99))
            login = f"{login}{suffix}"

        domain = random.choice(self._domains)
        return f"{login}@{domain}"

    def generate(self) -> str:
        # fallback без контекста имени — генерирует псевдологин
        login = f"user{random.randint(1, 99999)}"
        return f"{login}@{random.choice(self._domains)}"