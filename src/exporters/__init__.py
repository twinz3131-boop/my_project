"""
Пакет экспортёров.

Экспортирует готовые экспортёры и фабричную функцию
get_exporter(), которая выбирает класс по имени формата —
удобно для CLI, где формат приходит строкой.
"""
from .base_exporter import BaseExporter
from .csv_exporter import CsvExporter
from .json_exporter import JsonExporter


# Реестр «имя формата -> класс экспортёра».
# Пополняется при добавлении новых форматов (например,
# XLSX, SQL). Это единственное место, где перечисляются
# все поддерживаемые форматы — не считая SUPPORTED_FORMATS
# в config.py, который синхронизирован с этим реестром.
_EXPORTERS = {
    "csv": CsvExporter,
    "json": JsonExporter,
}


def get_exporter(fmt: str) -> BaseExporter:
    """
    Возвращает экземпляр экспортёра по имени формата.

    Пример:
        exporter = get_exporter("csv")
        exporter.export(records, "output.csv")

    Бросает ValueError, если формат не поддерживается —
    это защищает от опечаток вроде "CVS" вместо "CSV".
    """
    try:
        return _EXPORTERS[fmt.lower()]()
    except KeyError:
        supported = ", ".join(sorted(_EXPORTERS))
        raise ValueError(
            f"Формат {fmt!r} не поддерживается. "
            f"Доступные: {supported}"
        )


__all__ = [
    "BaseExporter",
    "CsvExporter",
    "JsonExporter",
    "get_exporter",
]