#!/usr/bin/env python3
"""
Скрипт массовой генерации кроссвордов
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Добавляем путь к src для импорта
sys.path.insert(0, str(Path(__file__).parent))

from src.generator import CrosswordGenerator
from src.utils import save_crossword, generate_filename, ensure_output_directory


# Категории для генерации
CATEGORIES = [
    "Наука и технологии",
    "История",
    "Искусство",
    "Спорт",
    "Литература",
    "Кино и сериалы",
    "Музыка",
    "География",
    "Природа",
    "Кулинария",
    "Космос"
]


def generate_for_category(generator: CrosswordGenerator, category: str,
                          count: int, difficulty: str, output_dir: str) -> tuple:
    """
    Генерирует кроссворды для одной категории

    Returns:
        (successful, failed)
    """
    successful = 0
    failed = 0

    print(f"\nГенерация для категории: {category}")
    print("-" * 50)

    for i in range(count):
        crossword = generator.generate(category, difficulty)

        if crossword is not None:
            filename = generate_filename(category, i + 1, difficulty)
            filepath = os.path.join(output_dir, filename)
            save_crossword(crossword, filepath)
            successful += 1
            print(f"  [{i+1}/{count}] Успешно: {filename}")
        else:
            failed += 1
            print(f"  [{i+1}/{count}] Ошибка генерации")

    return (successful, failed)


def main():
    parser = argparse.ArgumentParser(
        description='Массовая генерация кроссвордов'
    )
    parser.add_argument(
        '-d', '--dictionary',
        default='data/dictionary.json',
        help='Путь к файлу словаря (default: data/dictionary.json)'
    )
    parser.add_argument(
        '-o', '--output',
        default='output/crosswords',
        help='Директория для вывода (default: output/crosswords)'
    )
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=50,
        help='Количество кроссвордов на категорию (default: 50)'
    )
    parser.add_argument(
        '-l', '--level',
        choices=['easy', 'medium', 'hard'],
        default='medium',
        help='Уровень сложности (default: medium)'
    )
    parser.add_argument(
        '--category',
        help='Генерировать только для указанной категории'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Только проверить словарь без генерации'
    )

    args = parser.parse_args()

    # Проверяем наличие словаря
    if not os.path.exists(args.dictionary):
        print(f"Ошибка: Файл словаря не найден: {args.dictionary}")
        sys.exit(1)

    # Инициализируем генератор
    print(f"Загрузка словаря: {args.dictionary}")
    generator = CrosswordGenerator(args.dictionary)

    # Проверка словаря
    print("\nПроверка словаря...")
    is_valid, errors = generator.validate_dictionary()

    if not is_valid:
        print("Обнаружены ошибки в словаре:")
        for error in errors[:10]:  # Показываем первые 10 ошибок
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... и ещё {len(errors) - 10} ошибок")

    if args.validate_only:
        if is_valid:
            print("Словарь корректен!")
        sys.exit(0 if is_valid else 1)

    # Показываем доступные категории
    available_categories = generator.get_available_categories()
    print(f"\nДоступные категории: {len(available_categories)}")
    for cat in available_categories:
        stats = generator.get_category_stats(cat)
        print(f"  - {cat}: {stats['total_words']} слов")

    # Определяем категории для генерации
    if args.category:
        if args.category not in available_categories:
            print(f"\nОшибка: Категория '{args.category}' не найдена")
            sys.exit(1)
        categories_to_generate = [args.category]
    else:
        categories_to_generate = [c for c in CATEGORIES if c in available_categories]

    if not categories_to_generate:
        print("\nНет категорий для генерации!")
        sys.exit(1)

    # Создаём директорию для вывода
    output_dir = ensure_output_directory(args.output)
    print(f"\nДиректория вывода: {output_dir}")

    # Генерация
    print(f"\n{'='*60}")
    print(f"Начало генерации: {len(categories_to_generate)} категорий x {args.count} кроссвордов")
    print(f"Сложность: {args.level}")
    print(f"{'='*60}")

    total_successful = 0
    total_failed = 0

    for category in categories_to_generate:
        try:
            successful, failed = generate_for_category(
                generator, category, args.count, args.level, output_dir
            )
            total_successful += successful
            total_failed += failed
        except ValueError as e:
            print(f"\nОшибка для категории {category}: {e}")

    # Итоговая статистика
    print(f"\n{'='*60}")
    print("ИТОГО:")
    print(f"  Успешно: {total_successful}")
    print(f"  Ошибок: {total_failed}")
    print(f"  Процент успеха: {total_successful / (total_successful + total_failed) * 100:.1f}%")

    stats = generator.get_generation_stats()
    print(f"  Среднее время генерации: {stats['avg_generation_time']:.3f} сек")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
