"""Адрес: индекс, город, улица, дом, квартира."""
import random
from config import ADDRESS_FLAT_CHANCE
from .base_generator import BaseGenerator
from src.utils.helpers import load_dictionary, pick


class AddressGenerator(BaseGenerator):
    def __init__(self, locale: str = "ru"):
        super().__init__(locale)
        self._cities = load_dictionary("cities")[locale]
        self._streets = load_dictionary("streets")[locale]

    def generate(self) -> str:
        city = pick(self._cities)
        street = pick(self._streets)
        house = random.randint(1, 150)
        flat = ""
        if random.random() < ADDRESS_FLAT_CHANCE:
            flat = f", кв. {random.randint(1, 300)}"

        if self.locale == "ru":
            index = random.randint(100000, 699999)
            return f"{index}, г. {city}, ул. {street}, д. {house}{flat}"
        zip_code = random.randint(10000, 99999)
        return f"{zip_code} {city}, {street} St., {house}{flat}"