"""
Тесты экспортёров.

Проверяют, что CSV и JSON сохраняют данные корректно:
количество записей, наличие заголовков, кодировку.
"""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.exporters import CsvExporter, JsonExporter, get_exporter


class ExporterTests(unittest.TestCase):
    def setUp(self):
        # Каждый тест получает свою временную папку,
        # чтобы не мешать друг другу и не оставлять мусор.
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_csv_export_round_trip(self):
        records = [
            {"id": 1, "name": "Иван", "email": "ivan@mail.ru"},
            {"id": 2, "name": "Мария", "email": "maria@mail.ru"},
        ]
        path = self.tmp / "out.csv"
        CsvExporter().export(records, path)

        self.assertTrue(path.exists())
        # utf-8-sig в файле — читаем обратно с той же кодировкой.
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "Иван")
        self.assertEqual(rows[1]["email"], "maria@mail.ru")

    def test_json_export_round_trip(self):
        records = [{"id": 1, "name": "Иван"}]
        path = self.tmp / "out.json"
        JsonExporter().export(records, path)

        with path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
        self.assertEqual(loaded, records)

    def test_get_exporter_returns_correct_class(self):
        self.assertIsInstance(get_exporter("csv"), CsvExporter)
        self.assertIsInstance(get_exporter("JSON"), JsonExporter)

    def test_get_exporter_unknown_format_raises(self):
        with self.assertRaises(ValueError):
            get_exporter("xlsx")

    def test_export_creates_parent_dirs(self):
        records = [{"id": 1}]
        path = self.tmp / "nested" / "sub" / "out.json"
        JsonExporter().export(records, path)
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()