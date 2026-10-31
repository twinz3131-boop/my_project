"""
Тесты валидатора.

Проверяют, что валидатор:
  * пропускает корректные данные;
  * ловит некорректные email, телефоны, даты, ФИО;
  * корректно работает с пачкой записей.
"""
import unittest

from src.validators import RecordValidator


class RecordValidatorTests(unittest.TestCase):
    def setUp(self):
        # Один валидатор для всех тестов класса.
        self.validator = RecordValidator(locale="ru")

    def test_valid_record_passes(self):
        rec = {
            "full_name": "Иванов Иван Иванович",
            "email": "ivan.ivanov@mail.ru",
            "phone": "+7 (912) 345-67-89",
            "address": "125467, г. Казань, ул. Садовая, д. 34",
            "birth_date": "1990-01-01",
        }
        ok, errs = self.validator.validate(rec)
        self.assertTrue(ok, msg=f"Неожиданные ошибки: {errs}")

    def test_bad_email_fails(self):
        ok, errs = self.validator.validate({"email": "not-an-email"})
        self.assertFalse(ok)
        self.assertTrue(any("email" in e for e in errs))

    def test_bad_phone_fails(self):
        ok, errs = self.validator.validate(
            {"phone": "+7 912 345 67 89"}  # без скобок и дефисов
        )
        self.assertFalse(ok)
        self.assertTrue(any("phone" in e for e in errs))

    def test_bad_date_format_fails(self):
        ok, _ = self.validator.validate({"birth_date": "31-12-2000"})
        self.assertFalse(ok)

    def test_date_out_of_range_fails(self):
        # Границы — 1950..2006; берём заведомо за пределами.
        ok, _ = self.validator.validate({"birth_date": "1900-01-01"})
        self.assertFalse(ok)

    def test_validate_many_splits_records(self):
        records = [
            {"email": "ok@mail.ru"},
            {"email": "not-email"},
            {"email": "also@yandex.ru"},
        ]
        report = self.validator.validate_many(records)
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["ok_count"], 2)
        self.assertEqual(report["err_count"], 1)

    def test_empty_field_values_are_ignored(self):
        # Если поля нет в записи — валидатор его не проверяет.
        ok, errs = self.validator.validate({})
        self.assertTrue(ok)
        self.assertEqual(errs, [])


if __name__ == "__main__":
    unittest.main()