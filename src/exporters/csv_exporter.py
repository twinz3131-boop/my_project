
import csv
from pathlib import Path

from .base_exporter import BaseExporter


class CsvExporter(BaseExporter):
    """Сохраняет записи в CSV-файл."""

    extension = "csv"

    def export(self, records: list[dict], path: str | Path) -> Path:
        """
        Пишет records в CSV по пути path.

        Аргументы:
            records: список словарей с одинаковым (обычно)
                     набором ключей;
            path:    путь к файлу; строка или Path.

        Возвращает Path к записанному файлу.
        """
        path = Path(path)
        # Создаём родительскую папку (например, "out/data.csv"
        # при отсутствии папки "out/").
        self._ensure_parent(path)

        # Определяем заголовки: сначала ключи первой записи
        # (сохраняет ожидаемый порядок), потом любые новые,
        # которых не было в первой.
        fieldnames: list[str] = []
        for rec in records:
            for key in rec:
                if key not in fieldnames:
                    fieldnames.append(key)

        # newline="" — обязательное требование модуля csv
        # при работе на Windows, иначе будут пустые строки
        # между записями.
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                # QUOTE_MINIMAL — ставим кавычки только там,
                # где они нужны (запятые, кавычки, переводы строк).
                quoting=csv.QUOTE_MINIMAL,
            )
            writer.writeheader()
            # extrasaction="ignore" на случай, если в записи
            # есть поле, которого нет в fieldnames — такое
            # маловероятно из-за кода выше, но безопаснее.
            for rec in records:
                writer.writerow(
                    {k: rec.get(k, "") for k in fieldnames}
                )

        return path


# ---------- Демонстрация ----------
# Запуск: python -m src.exporters.csv_exporter
if __name__ == "__main__":
    from src.generators import RecordGenerator

    print("=== Генерация и экспорт в CSV ===")
    gen = RecordGenerator(locale="ru", seed=42)
    records = gen.generate_records(5)
    out = CsvExporter().export(records, "out/demo_records.csv")
    print(f"Записано {len(records)} записей в {out}")