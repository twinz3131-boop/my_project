"""Базовый интерфейс всех генераторов."""
from abc import ABC, abstractmethod


class BaseGenerator(ABC):
    def __init__(self, locale: str = "ru"):
        self.locale = locale

    @abstractmethod
    def generate(self):
        """Вернуть очередное значение."""
        raise NotImplementedError

    def generate_many(self, count: int) -> list:
        return [self.generate() for _ in range(count)]