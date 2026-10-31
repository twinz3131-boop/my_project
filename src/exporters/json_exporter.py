
import json
from pathlib import Path

from .base_exporter import BaseExporter


class JsonExporter(BaseExporter):
    """Сохраняет записи в JSON-файл."""

    extension = "json"

    def __init__(self, indent: int | None = 2):
        """
        Параметры:
            indent: отступ для pretty-print. 2 — читаемо,
                    None — компактно (без пробелов и переносов).
        """
        self._indent = indent

    def export(self, records: list[dict], path: str | Path) -> Path:
        """
        Пишет records в JSON по пути path.

        Аргументы:
            records: список словарей — будет сохранён
                     как JSON-массив объектов;
            path:    путь к файлу.

        Возвращает Path к записанному файлу.
        """
        path = Path(path)
        self._ensure_parent(path)

        with path.open("w", encoding="utf-8") as f:
            # ensure_ascii=False — сохраняем кириллицу как есть.
            # indent — pretty-print (None = компактный JSON).
            json.dump(
                records,
                f,
                ensure_ascii=False,
                indent=self._indent,
            )
            # Завершающий перевод строки — хороший тон для
            # текстовых файлов и удобно для git diff.
            f.write("\n")

        return path


# ---------- Демонстрация ----------
# Запуск: python -m src.exporters.json_exporter
if __name__ == "__main__":
    from src.generators import RecordGenerator

    print("=== Генерация и экспорт в JSON ===")
    gen = RecordGenerator(locale="en", seed=7,
                          fields=["full_name", "email", "phone"])
    records = gen.generate_records(3)
    out = JsonExporter().export(records, "out/demo_records.json")
    print(f"Записано {len(records)} записей в {out}")