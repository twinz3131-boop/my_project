"""
Утилиты: загрузка словарей, транслитерация, slugify.
"""
import json
import random
from pathlib import Path
from typing import Any

from config import DATA_DIR


# ---------- Транслитерация (RU -> EN) ----------
_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def transliterate(text: str) -> str:
    """Иван -> Ivan."""
    result = []
    for ch in text:
        low = ch.lower()
        if low in _TRANSLIT:
            tr = _TRANSLIT[low]
            result.append(tr.capitalize() if ch.isupper() else tr)
        else:
            result.append(ch)
    return "".join(result)


def slugify(text: str) -> str:
    """Иван Петров -> ivan.petrov (для email)."""
    text = transliterate(text).lower()
    return "".join(c for c in text if c.isalnum())


# ---------- Словари ----------
_DICT_CACHE: dict[str, Any] = {}

# Встроенные fallback-словари на случай отсутствия JSON-файлов
_FALLBACK: dict[str, Any] = {
    "names_ru": {
        "male_first_names": ["Иван", "Пётр", "Сергей", "Алексей", "Дмитрий",
                              "Андрей", "Михаил", "Николай", "Артём", "Максим"],
        "female_first_names": ["Анна", "Мария", "Ольга", "Екатерина", "Наталья",
                                "Ирина", "Елена", "Татьяна", "Светлана", "Юлия"],
        "last_names_male": ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов",
                             "Попов", "Соколов", "Лебедев", "Козлов", "Новиков"],
        "last_names_female": ["Иванова", "Петрова", "Сидорова", "Смирнова", "Кузнецова",
                               "Попова", "Соколова", "Лебедева", "Козлова", "Новикова"],
        "middle_names_male": ["Иванович", "Петрович", "Сергеевич", "Алексеевич",
                               "Дмитриевич", "Андреевич"],
        "middle_names_female": ["Ивановна", "Петровна", "Сергеевна", "Алексеевна",
                                 "Дмитриевна", "Андреевна"],
    },
    "names_en": {
        "male_first_names": ["John", "Michael", "David", "James", "Robert",
                              "William", "Daniel", "Thomas", "Matthew", "Charles"],
        "female_first_names": ["Mary", "Jennifer", "Linda", "Patricia", "Elizabeth",
                                "Susan", "Jessica", "Sarah", "Karen", "Emily"],
        "last_names": ["Smith", "Johnson", "Williams", "Brown", "Jones",
                        "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"],
    },
    "cities": {
        "ru": ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург",
                "Казань", "Нижний Новгород", "Самара", "Омск", "Ростов-на-Дону"],
        "en": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
                "Philadelphia", "San Antonio", "San Diego", "Dallas"],
    },
    "streets": {
        "ru": ["Ленина", "Пушкина", "Гагарина", "Мира", "Советская",
                "Центральная", "Садовая", "Лесная", "Школьная"],
        "en": ["Main", "Oak", "Pine", "Maple", "Cedar",
                "Elm", "Washington", "Lake", "Hill"],
    },
}


def load_dictionary(name: str) -> Any:
    """
    Загружает JSON-словарь из data/dictionaries/<name>.json.
    Если файла нет — возвращает fallback из _FALLBACK.
    Кеширует результат.
    """
    if name in _DICT_CACHE:
        return _DICT_CACHE[name]

    path = Path(DATA_DIR) / f"{name}.json"
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = _FALLBACK.get(name, {})

    _DICT_CACHE[name] = data
    return data


def pick(seq):
    """Случайный элемент списка."""
    return random.choice(seq)