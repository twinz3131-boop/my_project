"""
Сборка одной записи из выбранных полей.

Пример:
    rg = RecordGenerator(locale="ru", fields=["full_name", "email"])
    rg.generate_records(5)
"""
import random
from config import (
    SUPPORTED_FIELDS, DEFAULT_LOCALE,
    FIELD_FULL_NAME, FIELD_EMAIL, FIELD_PHONE,
    FIELD_ADDRESS, FIELD_BIRTH_DATE,
)
from .name_generator import NameGenerator
from .email_generator import EmailGenerator
from .phone_generator import PhoneGenerator
from .address_generator import AddressGenerator
from .date_generator import DateGenerator


class RecordGenerator:
    def __init__(self, locale: str = DEFAULT_LOCALE,
                 fields: list[str] | None = None,
                 seed: int | None = None):
        if locale not in ("ru", "en"):
            raise ValueError(f"Неподдерживаемая локаль: {locale}")
        self.locale = locale
        self.fields = fields or list(SUPPORTED_FIELDS)

        unknown = set(self.fields) - set(SUPPORTED_FIELDS)
        if unknown:
            raise ValueError(f"Неизвестные поля: {unknown}")

        if seed is not None:
            random.seed(seed)

        # Всегда создаём — даже если поле не запрошено, email зависит от имени
        self._name = NameGenerator(locale)
        self._email = EmailGenerator(locale)
        self._phone = PhoneGenerator(locale)
        self._address = AddressGenerator(locale)
        self._date = DateGenerator(locale)

    def generate_record(self, record_id: int | None = None) -> dict:
        record: dict = {}
        if record_id is not None:
            record["id"] = record_id

        # Имя генерируем, если нужно имя ИЛИ email (email из имени)
        needs_name = (FIELD_FULL_NAME in self.fields) or (FIELD_EMAIL in self.fields)
        name_parts = self._name.generate_with_parts() if needs_name else None

        if FIELD_FULL_NAME in self.fields:
            record[FIELD_FULL_NAME] = name_parts["full_name"]

        if FIELD_EMAIL in self.fields:
            record[FIELD_EMAIL] = self._email.generate_from_name(
                name_parts["first_name"], name_parts["last_name"]
            )

        if FIELD_PHONE in self.fields:
            record[FIELD_PHONE] = self._phone.generate()

        if FIELD_ADDRESS in self.fields:
            record[FIELD_ADDRESS] = self._address.generate()

        if FIELD_BIRTH_DATE in self.fields:
            record[FIELD_BIRTH_DATE] = self._date.generate()

        return record

    def generate_records(self, count: int, start_id: int = 1) -> list[dict]:
        if count < 0:
            raise ValueError("count должен быть >= 0")
        return [self.generate_record(start_id + i) for i in range(count)]


# ---------- Демонстрация ----------
if __name__ == "__main__":
    import json

    print("=== RU, все поля, 3 записи ===")
    gen = RecordGenerator(locale="ru", seed=42)
    for r in gen.generate_records(3):
        print(json.dumps(r, ensure_ascii=False, indent=2))

    print("\n=== EN, только name+email, 2 записи ===")
    gen = RecordGenerator(locale="en", fields=["full_name", "email"], seed=7)
    for r in gen.generate_records(2):
        print(json.dumps(r, ensure_ascii=False, indent=2))