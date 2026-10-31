"""
Пакет валидаторов.

Экспортирует публичный класс RecordValidator. Внутренние
проверки (регулярки, диапазоны дат) спрятаны внутри —
пользователю достаточно вызвать validate().
"""
from .record_validator import RecordValidator

__all__ = ["RecordValidator"]