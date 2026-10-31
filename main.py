"""
Точка входа Test Data Generator.

Поддерживает два режима работы:

1. CLI (argparse):
       python main.py --count 100 --format csv --output data.csv
       python main.py --count 50 --fields name,email --locale en

2. Интерактивный:
       python main.py
   Программа задаёт вопросы по очереди и генерирует данные
   по ответам. Удобно для тех, кто не хочет помнить флаги.

Логика пайплайна:
   RecordGenerator -> RecordValidator -> get_exporter().export()
"""
import argparse
import sys
from pathlib import Path

from config import (
    DEFAULT_LOCALE,
    FIELD_ADDRESS,
    FIELD_BIRTH_DATE,
    FIELD_EMAIL,
    FIELD_FULL_NAME,
    FIELD_PHONE,
    SUPPORTED_FIELDS,
    SUPPORTED_FORMATS,
    SUPPORTED_LOCALES,
)
from src.exporters import get_exporter
from src.generators import RecordGenerator
from src.validators import RecordValidator


# ============================================================
# ВСПОМОГАТЕЛЬНОЕ: РАЗБОР ПОЛЕЙ ИЗ CLI
# ============================================================
# Пользователю удобнее писать короткие имена ("name", "phone"),
# а внутри проекта используются константы ("full_name", "email").
# Этот словарь — «переводчик» между ними.
_FIELD_ALIASES = {
    "name": FIELD_FULL_NAME,
    "full_name": FIELD_FULL_NAME,
    "email": FIELD_EMAIL,
    "phone": FIELD_PHONE,
    "address": FIELD_ADDRESS,
    "birth_date": FIELD_BIRTH_DATE,
    "date": FIELD_BIRTH_DATE,
}


def _parse_fields(raw: str) -> list[str]:
    """
    Превращает строку "name,email,phone" в список полей.

    Алиасы ("name", "date") разворачиваются в константы
    ("full_name", "birth_date"). Неизвестные имена —
    ValueError, чтобы пользователь сразу увидел опечатку.

    Пустая строка или None -> возвращаем все поля.
    """
    if not raw:
        return list(SUPPORTED_FIELDS)

    result: list[str] = []
    for part in raw.split(","):
        key = part.strip().lower()
        if not key:
            continue
        if key not in _FIELD_ALIASES:
            allowed = ", ".join(sorted(_FIELD_ALIASES))
            raise ValueError(
                f"Неизвестное поле: {key!r}. Доступные: {allowed}"
            )
        # Дубликаты убираем, сохраняя порядок.
        canonical = _FIELD_ALIASES[key]
        if canonical not in result:
            result.append(canonical)
    return result or list(SUPPORTED_FIELDS)


# ============================================================
# CLI-РЕЖИМ
# ============================================================
def _build_arg_parser() -> argparse.ArgumentParser:
    """
    Собирает парсер аргументов командной строки.

    Вынесено в отдельную функцию, чтобы:
      * было проще тестировать (можно импортировать и вызвать
        parse_args на списке строк);
      * держать main() коротким и читаемым.
    """
    parser = argparse.ArgumentParser(
        prog="test-data-generator",
        description=(
            "Генератор тестовых данных: имена, email, телефоны, "
            "адреса, даты рождения."
        ),
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        help="сколько записей сгенерировать (по умолчанию: 10)",
    )
    parser.add_argument(
        "-f", "--fields",
        type=str,
        default="",
        help=(
            "список полей через запятую. Доступные: "
            "name, email, phone, address, date. "
            "По умолчанию — все поля."
        ),
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=SUPPORTED_FORMATS,
        default="json",
        help="формат файла: csv или json (по умолчанию: json)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="",
        help=(
            "путь к файлу результата. Если не указан — "
            "будет использован generated_data.<формат>"
        ),
    )
    parser.add_argument(
        "--locale",
        choices=SUPPORTED_LOCALES,
        default=DEFAULT_LOCALE,
        help="язык данных (по умолчанию: ru)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="seed для random — для воспроизводимых результатов",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="не запускать валидатор перед сохранением",
    )
    return parser


def _run_cli(argv: list[str] | None = None) -> int:
    """
    Запускает программу в режиме CLI.

    Возвращает код выхода: 0 — успех, 1 — ошибка.
    Так main() может возвращать код и использовать его
    в sys.exit(), что правильно для скриптов.
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    try:
        fields = _parse_fields(args.fields)
    except ValueError as exc:
        # Сообщаем об ошибке и явно выходим с кодом 2
        # (argparse использует 2 для ошибок ввода).
        parser.error(str(exc))
        return 2  # недостижимо, но для линтера

    if args.count < 0:
        parser.error("--count должен быть >= 0")
        return 2

    # Путь по умолчанию: generated_data.<формат> в текущей папке.
    output = args.output or f"generated_data.{args.fmt}"

    return _generate_and_save(
        count=args.count,
        fields=fields,
        locale=args.locale,
        fmt=args.fmt,
        output=output,
        seed=args.seed,
        validate=not args.no_validate,
    )


# ============================================================
# ИНТЕРАКТИВНЫЙ РЕЖИМ
# ============================================================
def _ask(prompt: str, default: str = "") -> str:
    """
    Задаёт вопрос и возвращает ответ.

    Если пользователь нажал Enter (пустой ввод) —
    возвращается значение по умолчанию.
    """
    suffix = f" [{default}]" if default else ""
    raw = input(f"{prompt}{suffix}: ").strip()
    return raw or default


def _run_interactive() -> int:
    """
    Интерактивный режим: спрашивает параметры по одному.

    Все ответы имеют разумные значения по умолчанию —
    пользователь может жать Enter, чтобы не выбирать.
    """
    print("=== Test Data Generator (интерактивный режим) ===")

    # Локаль.
    locale = _ask("Локаль (ru/en)", DEFAULT_LOCALE).lower()
    if locale not in SUPPORTED_LOCALES:
        print(f"Неподдерживаемая локаль: {locale}. Выхожу.")
        return 1

    # Количество записей.
    raw_count = _ask("Сколько записей сгенерировать", "10")
    try:
        count = int(raw_count)
    except ValueError:
        print(f"Не число: {raw_count!r}. Выхожу.")
        return 1
    if count < 0:
        print("count должен быть >= 0. Выхожу.")
        return 1

    # Поля.
    print(
        "Доступные поля: name, email, phone, address, date. "
        "Через запятую; Enter — все."
    )
    raw_fields = _ask("Поля")
    try:
        fields = _parse_fields(raw_fields)
    except ValueError as exc:
        print(f"Ошибка полей: {exc}. Выхожу.")
        return 1

    # Формат.
    fmt = _ask("Формат (csv/json)", "json").lower()
    if fmt not in SUPPORTED_FORMATS:
        print(f"Неподдерживаемый формат: {fmt}. Выхожу.")
        return 1

    # Путь.
    output = _ask("Путь к файлу", f"generated_data.{fmt}")

    # Seed.
    raw_seed = _ask("Seed (Enter — случайный)", "")
    seed = None
    if raw_seed:
        try:
            seed = int(raw_seed)
        except ValueError:
            print(f"seed должен быть числом: {raw_seed!r}")
            return 1

    return _generate_and_save(
        count=count,
        fields=fields,
        locale=locale,
        fmt=fmt,
        output=output,
        seed=seed,
        validate=True,
    )


# ============================================================
# ОБЩИЙ ПАЙПЛАЙН
# ============================================================
def _generate_and_save(
    count: int,
    fields: list[str],
    locale: str,
    fmt: str,
    output: str,
    seed: int | None,
    validate: bool,
) -> int:
    """
    Генерирует записи, при необходимости валидирует
    и сохраняет в файл.

    Возвращает код выхода (0 — успех, 1 — ошибка).
    Общая функция для CLI и интерактивного режима,
    чтобы не дублировать логику.
    """
    print(
        f"Генерация {count} записей "
        f"(локаль={locale}, поля={', '.join(fields)})..."
    )
    gen = RecordGenerator(locale=locale, fields=fields, seed=seed)
    records = gen.generate_records(count)

    if validate:
        validator = RecordValidator(locale=locale)
        report = validator.validate_many(records)
        print(
            f"Валидация: всего={report['total']}, "
            f"валидных={report['ok_count']}, "
            f"битых={report['err_count']}"
        )
        if report["err_count"]:
            # Показываем первые 3 ошибки, чтобы не спамить.
            for rec, errs in report["invalid"][:3]:
                print(f"  ! {rec}")
                for e in errs:
                    print(f"    - {e}")
        records = report["valid"]

    # Экспорт. get_exporter() сам бросит ValueError
    # на неизвестный формат — но у нас fmt проверен
    # argparse'ом/интерактивом, так что здесь всё ок.
    path = get_exporter(fmt).export(records, Path(output))
    print(f"Готово: {len(records)} записей -> {path.resolve()}")
    return 0


# ============================================================
# ТОЧКА ВХОДА
# ============================================================
def main(argv: list[str] | None = None) -> int:
    """
    Главная функция.

    Если argv не передан и в командной строке нет аргументов —
    запускается интерактивный режим. Иначе — CLI.
    argv можно передать явно из тестов:
        main(["--count", "5", "--format", "csv"])
    """
    if argv is None:
        argv = sys.argv[1:]

    # Нет аргументов — спрашиваем интерактивно.
    if not argv:
        return _run_interactive()

    return _run_cli(argv)


if __name__ == "__main__":
    sys.exit(main())