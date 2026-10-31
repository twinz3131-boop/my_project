"""
Валидатор сгенерированных записей.

Проверяет каждое поле на соответствие ожидаемому формату
и диапазону. Регулярные выражения и базовая логика проверки
дат подготовлены с помощью ИИ-инструмента (п.5 задания)
и дополнены тестами (tests/test_validators.py).

Основные сценарии использования:
  * фильтрация «плохих» записей перед экспортом;
  * проверка данных после правок вручную;
  * самопроверка генераторов в тестах.

Пример:
    validator = RecordValidator(locale="ru")
    ok, errors = validator.validate(record)
    if not ok:
        print("Ошибки:", errors)
"""
from datetime import datetime

from config import (
    ADDRESS_RU_PATTERN,
    ADDRESS_EN_PATTERN,
    DATE_FORMAT,
    EMAIL_PATTERN,
    FIELD_ADDRESS,
    FIELD_BIRTH_DATE,
    FIELD_EMAIL,
    FIELD_FULL_NAME,
    FIELD_PHONE,
    FULL_NAME_PATTERN,
    PHONE_EN_PATTERN,
    PHONE_RU_PATTERN,
)
from src.generators.date_generator import DateGenerator


class RecordValidator:
    """
    Валидатор одной записи (dict) и списка записей.

    Параметры конструктора:
        locale:      "ru" или "en" — определяет регулярки
                     для телефона и адреса;
        date_range:  кортеж (start, end) в формате DATE_FORMAT —
                     допустимый диапазон дат рождения;
        check_date_range: проверять ли попадание даты в диапазон.
                     Полезно отключать, если данные приходят
                     из внешнего источника с расширенным диапазоном.
    """

    def __init__(
        self,
        locale: str = "ru",
        date_range: tuple[str, str] | None = None,
        check_date_range: bool = True,
    ):
        if locale not in ("ru", "en"):
            raise ValueError(f"Неподдерживаемая локаль: {locale}")
        self.locale = locale
        self.check_date_range = check_date_range

        # Регулярки телефона и адреса зависят от локали.
        # Проверка email и ФИО — общая для обеих локалей.
        self._phone_re = (
            PHONE_RU_PATTERN if locale == "ru" else PHONE_EN_PATTERN
        )
        self._address_re = (
            ADDRESS_RU_PATTERN if locale == "ru" else ADDRESS_EN_PATTERN
        )

        # Диапазон дат рождения. Если не задан — берём
        # дефолтный из DateGenerator (те же границы, что
        # при генерации, чтобы не отвергать свои же записи).
        if date_range is None:
            # Импортируем BIRTH_DATE_MIN/MAX здесь, а не в шапке,
            # чтобы не тянуть лишние константы ради двух значений.
            from config import BIRTH_DATE_MIN, BIRTH_DATE_MAX
            date_range = (BIRTH_DATE_MIN, BIRTH_DATE_MAX)

        self._date_min = datetime.strptime(date_range[0], DATE_FORMAT)
        self._date_max = datetime.strptime(date_range[1], DATE_FORMAT)

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------
    def validate(self, record: dict) -> tuple[bool, list[str]]:
        """
        Проверяет одну запись.

        Возвращает кортеж (is_valid, errors):
            is_valid — True, если ошибок нет;
            errors   — список строк формата "поле: причина".

        Проверяются только те поля, что реально присутствуют
        в записи. Отсутствующие пропускаются — это позволяет
        валидировать частично заполненные записи (например,
        только name + email).
        """
        errors: list[str] = []

        # Каждое поле проверяем отдельным методом — так легко
        # добавлять новые проверки, не раздувая validate().
        if FIELD_FULL_NAME in record:
            err = self._check_full_name(record[FIELD_FULL_NAME])
            if err:
                errors.append(f"{FIELD_FULL_NAME}: {err}")

        if FIELD_EMAIL in record:
            err = self._check_email(record[FIELD_EMAIL])
            if err:
                errors.append(f"{FIELD_EMAIL}: {err}")

        if FIELD_PHONE in record:
            err = self._check_phone(record[FIELD_PHONE])
            if err:
                errors.append(f"{FIELD_PHONE}: {err}")

        if FIELD_ADDRESS in record:
            err = self._check_address(record[FIELD_ADDRESS])
            if err:
                errors.append(f"{FIELD_ADDRESS}: {err}")

        if FIELD_BIRTH_DATE in record:
            err = self._check_birth_date(record[FIELD_BIRTH_DATE])
            if err:
                errors.append(f"{FIELD_BIRTH_DATE}: {err}")

        return (not errors, errors)

    def validate_many(self, records: list[dict]) -> dict:
        """
        Проверяет пачку записей.

        Возвращает dict с результатами:
            valid    — список валидных записей;
            invalid  — список пар (record, errors) для невалидных;
            total    — общее количество проверенных записей;
            ok_count — количество валидных;
            err_count — количество невалидных.

        Удобно, когда нужно отфильтровать «мусор» перед
        экспортом и при этом сохранить отчёт о том, что
        именно не прошло проверку.
        """
        valid: list[dict] = []
        invalid: list[tuple[dict, list[str]]] = []

        for rec in records:
            ok, errs = self.validate(rec)
            if ok:
                valid.append(rec)
            else:
                invalid.append((rec, errs))

        return {
            "valid": valid,
            "invalid": invalid,
            "total": len(records),
            "ok_count": len(valid),
            "err_count": len(invalid),
        }

    # ------------------------------------------------------------------
    # Внутренние проверки полей
    # ------------------------------------------------------------------
    def _check_full_name(self, value) -> str | None:
        """
        Проверяет ФИО.

        Требования:
          * непустая строка;
          * минимум два слова (имя + фамилия);
          * каждое слово — с заглавной буквы;
          * буквы только кириллица/латиница и дефис.

        Возвращает текст ошибки или None, если всё в порядке.
        """
        if not isinstance(value, str) or not value.strip():
            return "пустое или нестроковое значение"
        if not FULL_NAME_PATTERN.match(value):
            return f"не похоже на ФИО: {value!r}"
        return None

    def _check_email(self, value) -> str | None:
        """
        Проверяет email по регулярному выражению EMAIL_PATTERN.

        Отдельная проверка длины логина и домена не делается —
        это редкий крайний случай, а базовая структура уже
        покрыта регуляркой. Если нужно строже — добавьте
        здесь проверку len(value) <= 254 (RFC 5321).
        """
        if not isinstance(value, str) or not value:
            return "пустое или нестроковое значение"
        if not EMAIL_PATTERN.match(value):
            return f"некорректный email: {value!r}"
        return None

    def _check_phone(self, value) -> str | None:
        """
        Проверяет телефон регуляркой, выбранной по локали.

        RU: "+7 (912) 345-67-89".
        EN: "+1-212-345-6789".
        """
        if not isinstance(value, str) or not value:
            return "пустое или нестроковое значение"
        if not self._phone_re.match(value):
            return f"некорректный телефон: {value!r}"
        return None

    def _check_address(self, value) -> str | None:
        """
        Проверяет адрес регуляркой по локали.

        Регулярка проверяет общую структуру, а не существование
        реального адреса (это потребовало бы внешнего API).
        """
        if not isinstance(value, str) or not value:
            return "пустое или нестроковое значение"
        if not self._address_re.match(value):
            return f"некорректный адрес: {value!r}"
        return None

    def _check_birth_date(self, value) -> str | None:
        """
        Проверяет дату рождения.

        Шаги:
          1. Парсится ли строка в datetime по DATE_FORMAT?
          2. (опционально) попадает ли дата в допустимый
             диапазон self._date_min..self._date_max?

        Возвращает текст ошибки или None.
        """
        if not isinstance(value, str) or not value:
            return "пустое или нестроковое значение"

        try:
            date = datetime.strptime(value, DATE_FORMAT)
        except ValueError:
            return f"некорректный формат даты: {value!r}"

        if not self.check_date_range:
            return None

        # Проверка диапазона: дата должна быть не «из будущего»
        # и не «из глубокого прошлого» — по границам, заданным
        # в config.BIRTH_DATE_MIN/MAX.
        if not (self._date_min <= date <= self._date_max):
            return (
                f"дата вне диапазона "
                f"{self._date_min.strftime(DATE_FORMAT)}"
                f"..{self._date_max.strftime(DATE_FORMAT)}: {value!r}"
            )
        return None


# ---------- Демонстрация ----------
# Запуск: python -m src.validators.record_validator
# Генерируем записи и прогоняем через валидатор —
# все должны быть валидными (проверка «самопроверки»).
if __name__ == "__main__":
    import json

    from src.generators import RecordGenerator

    print("=== Генерация + валидация (RU, 3 записи) ===")
    gen = RecordGenerator(locale="ru", seed=42)
    records = gen.generate_records(3)

    validator = RecordValidator(locale="ru")
    for rec in records:
        ok, errs = validator.validate(rec)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {json.dumps(rec, ensure_ascii=False)}")
        for e in errs:
            print(f"    ! {e}")

    # Проверим, что валидатор умеет ловить «мусор».
    print("\n=== Проверка заведомо битых записей ===")
    bad_samples = [
        {"email": "not-an-email"},
        {"phone": "+7 999 111 22 33"},  # неверный формат
        {"birth_date": "31-12-2000"},   # не ISO
        {"full_name": "иван петров"},   # со строчной
    ]
    for rec in bad_samples:
        ok, errs = validator.validate(rec)
        print(f"{rec} -> {'OK' if ok else 'FAIL: ' + '; '.join(errs)}")