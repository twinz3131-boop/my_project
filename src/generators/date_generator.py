"""Случайные даты (по умолчанию — дата рождения)."""
import random
from datetime import datetime, timedelta
from config import BIRTH_DATE_MIN, BIRTH_DATE_MAX, DATE_FORMAT
from .base_generator import BaseGenerator


class DateGenerator(BaseGenerator):
    def __init__(self, locale: str = "ru",
                 start: str = BIRTH_DATE_MIN,
                 end: str = BIRTH_DATE_MAX,
                 fmt: str = DATE_FORMAT):
        super().__init__(locale)
        self._start = datetime.strptime(start, DATE_FORMAT)
        self._end = datetime.strptime(end, DATE_FORMAT)
        self._fmt = fmt

    def generate(self) -> str:
        delta_days = (self._end - self._start).days
        random_days = random.randint(0, delta_days)
        date = self._start + timedelta(days=random_days)
        return date.strftime(self._fmt)

    def generate_date(self) -> datetime:
        delta_days = (self._end - self._start).days
        return self._start + timedelta(days=random.randint(0, delta_days))