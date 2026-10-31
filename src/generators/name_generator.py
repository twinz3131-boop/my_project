"""
Генератор ФИО.
RU: Имя Фамилия Отчество (+ пол для согласования).
EN: Имя Фамилия.
"""
import random
from .base_generator import BaseGenerator
from src.utils.helpers import load_dictionary, pick


class NameGenerator(BaseGenerator):
    def __init__(self, locale: str = "ru"):
        super().__init__(locale)
        self._dict = load_dictionary(f"names_{locale}")

    def generate_with_parts(self) -> dict:
        """Возвращает dict: first_name, last_name, middle_name, full_name, gender."""
        gender = random.choice(["male", "female"])

        if self.locale == "ru":
            first = pick(self._dict[f"{gender}_first_names"])
            last = pick(self._dict[f"last_names_{gender}"])
            middle = pick(self._dict[f"middle_names_{gender}"])
            full = f"{last} {first} {middle}"
        else:  # en
            first = pick(self._dict[f"{gender}_first_names"])
            last = pick(self._dict["last_names"])
            middle = ""
            full = f"{first} {last}"

        return {
            "first_name": first,
            "last_name": last,
            "middle_name": middle,
            "full_name": full,
            "gender": gender,
        }

    def generate(self) -> str:
        return self.generate_with_parts()["full_name"]