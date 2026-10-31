"""
Глобальные константы и настройки Test Data Generator.
"""
from pathlib import Path

# ---------- Пути ----------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "dictionaries"

# ---------- Локали ----------
DEFAULT_LOCALE = "ru"
SUPPORTED_LOCALES = ["ru", "en"]

# ---------- Поля записи ----------
FIELD_FULL_NAME = "full_name"
FIELD_EMAIL = "email"
FIELD_PHONE = "phone"
FIELD_ADDRESS = "address"
FIELD_BIRTH_DATE = "birth_date"

SUPPORTED_FIELDS = [
    FIELD_FULL_NAME,
    FIELD_EMAIL,
    FIELD_PHONE,
    FIELD_ADDRESS,
    FIELD_BIRTH_DATE,
]

# ---------- Экспорт ----------
SUPPORTED_FORMATS = ["csv", "json"]

# ---------- Email ----------
EMAIL_DOMAINS = {
    "ru": ["mail.ru", "yandex.ru", "gmail.com", "inbox.ru", "list.ru"],
    "en": ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"],
}
# Вероятность добавить цифры к логину email (чтобы избегать дублей)
EMAIL_DIGIT_CHANCE = 0.35

# ---------- Телефоны ----------
PHONE_FORMATS = {
    "ru": "+7 ({code}) {first}-{second}-{third}",
    "en": "+1-{code}-{first}-{second}",
}

# ---------- Даты ----------
# Границы «реалистичных» дат рождения
BIRTH_DATE_MIN = "1950-01-01"
BIRTH_DATE_MAX = "2006-12-31"  # обычно 18+ на момент генерации
DATE_FORMAT = "%Y-%m-%d"

# ---------- Адрес ----------
# Вероятность указать квартиру
ADDRESS_FLAT_CHANCE = 0.7

# ============================================================
# ВАЛИДАЦИЯ
# ============================================================
# Регулярные выражения для проверки полей записи.
# Шаблоны составлены с помощью ИИ-инструмента и вручную
# проверены на реальных данных (см. tests/).
#
# Компилируем через re.compile() один раз — при многократной
# валидации это заметно быстрее, чем re.match(pattern, ...)
# на каждый вызов.
import re  # noqa: E402  (осознанно — блок конфигурации ниже)

# Email: логины из букв/цифр/точек/подчёркиваний/плюсов,
# затем @, домен из букв/цифр/дефисов, затем точка и TLD 2+ букв.
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

# Телефон RU: строго "+7 (XXX) XXX-XX-XX" — как в config.PHONE_FORMATS.
PHONE_RU_PATTERN = re.compile(
    r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$"
)

# Телефон EN: "+1-XXX-XXX-XXXX".
PHONE_EN_PATTERN = re.compile(
    r"^\+1-\d{3}-\d{3}-\d{4}$"
)

# Адрес RU: "NNNNNN, г. Город, ул. Улица, д. N[, кв. N]".
ADDRESS_RU_PATTERN = re.compile(
    r"^\d{6}, г\. [^,]+, ул\. [^,]+, д\. \d+(, кв\. \d+)?$"
)

# Адрес EN: "NNNNN City, Street St., N[, кв. N]".
ADDRESS_EN_PATTERN = re.compile(
    r"^\d{5} [^,]+, [^,]+ St\., \d+(, кв\. \d+)?$"
)

# ФИО: минимум 2 слова, первое слово — с заглавной буквы,
# буквы только из кириллицы или латиницы (плюс дефис).
# Такая проверка отсекает пустые строки, цифры, мусор.
FULL_NAME_PATTERN = re.compile(
    r"^[A-ZА-ЯЁ][A-Za-zА-Яа-яЁё-]+(?: [A-ZА-ЯЁ][A-Za-zА-Яа-яЁё-]+)+$"
)

# Флаг «строгий режим». Если True — валидатор возвращает
# список ошибок по каждой невалидной записи. Если False —
# молча отбрасывает невалидные записи из результата.
VALIDATOR_STRICT = True