"""Телефонные номера по локали."""
import random
from config import PHONE_FORMATS
from .base_generator import BaseGenerator


class PhoneGenerator(BaseGenerator):
    def __init__(self, locale: str = "ru"):
        super().__init__(locale)
        self._fmt = PHONE_FORMATS[self.locale]

    def generate(self) -> str:
        if self.locale == "ru":
            return self._fmt.format(
                code=random.randint(900, 999),
                first=random.randint(100, 999),
                second=random.randint(10, 99),
                third=random.randint(10, 99),
            )
        return self._fmt.format(
            code=random.randint(200, 999),
            first=random.randint(100, 999),
            second=random.randint(1000, 9999),
        )