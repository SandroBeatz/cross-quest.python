"""
Вспомогательные функции для генератора кроссвордов
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path


# Настройки сложности
DIFFICULTY_SETTINGS = {
    "easy": {
        "word_count": (8, 10),
        "min_word_length": 4,
        "max_word_length": 8,
        "common_words_only": True
    },
    "medium": {
        "word_count": (10, 12),
        "min_word_length": 3,
        "max_word_length": 10,
        "common_words_only": False
    },
    "hard": {
        "word_count": (12, 15),
        "min_word_length": 3,
        "max_word_length": 12,
        "common_words_only": False,
        "obscure_words": True
    }
}


def load_dictionary(file_path: str) -> Dict[str, List[Dict]]:
    """
    Загружает словарь из JSON файла

    Args:
        file_path: Путь к файлу словаря

    Returns:
        dict: Словарь категорий со списками слов
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_crossword(crossword: dict, file_path: str) -> None:
    """
    Сохраняет кроссворд в JSON файл

    Args:
        crossword: Данные кроссворда
        file_path: Путь для сохранения
    """
    # Создаём директорию если не существует
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(crossword, f, ensure_ascii=False, indent=2)


def filter_words_by_length(words: List[Dict], min_length: int, max_length: int) -> List[Dict]:
    """
    Фильтрует слова по длине

    Args:
        words: Список слов
        min_length: Минимальная длина
        max_length: Максимальная длина

    Returns:
        list: Отфильтрованный список
    """
    return [
        w for w in words
        if min_length <= len(w['word']) <= max_length
    ]


def normalize_word(word: str) -> str:
    """
    Нормализует слово (верхний регистр, удаление пробелов)

    Args:
        word: Исходное слово

    Returns:
        str: Нормализованное слово
    """
    return word.upper().strip().replace(' ', '').replace('-', '')


def is_valid_cyrillic(word: str) -> bool:
    """
    Проверяет что слово содержит только кириллицу

    Args:
        word: Слово для проверки

    Returns:
        bool: True если только кириллица
    """
    word = word.upper()
    for char in word:
        if not ('А' <= char <= 'Я' or char == 'Ё'):
            return False
    return True


def get_common_letters() -> str:
    """
    Возвращает часто встречающиеся буквы в русском языке

    Returns:
        str: Строка с частыми буквами
    """
    return 'ОЕАИНТСРВЛКМДПУЯЫЬГЗБЧЙХЖШЮЦЩЭФЪЁ'


def calculate_word_score(word: str) -> int:
    """
    Вычисляет "оценку" слова для приоритезации при размещении

    Учитывает:
    - Длину слова (длинные = лучше)
    - Количество частых букв (больше = лучше для пересечений)

    Args:
        word: Слово

    Returns:
        int: Оценка слова
    """
    common = get_common_letters()
    word = word.upper()

    length_score = len(word) * 10

    common_letter_count = sum(1 for c in word if c in common[:15])  # Топ-15 частых букв
    common_score = common_letter_count * 5

    return length_score + common_score


def sort_words_by_score(words: List[Dict]) -> List[Dict]:
    """
    Сортирует слова по оценке (лучшие сначала)

    Args:
        words: Список слов

    Returns:
        list: Отсортированный список
    """
    return sorted(words, key=lambda w: calculate_word_score(w['word']), reverse=True)


def get_letter_positions(word: str) -> Dict[str, List[int]]:
    """
    Возвращает позиции каждой буквы в слове

    Args:
        word: Слово

    Returns:
        dict: Буква -> список позиций
    """
    positions = {}
    for i, char in enumerate(word.upper()):
        if char not in positions:
            positions[char] = []
        positions[char].append(i)
    return positions


def find_common_letters(word1: str, word2: str) -> List[tuple]:
    """
    Находит общие буквы между двумя словами

    Args:
        word1: Первое слово
        word2: Второе слово

    Returns:
        list: Список кортежей (буква, позиция_в_word1, позиция_в_word2)
    """
    word1 = word1.upper()
    word2 = word2.upper()

    common = []
    pos1 = get_letter_positions(word1)
    pos2 = get_letter_positions(word2)

    for letter in pos1:
        if letter in pos2:
            for p1 in pos1[letter]:
                for p2 in pos2[letter]:
                    common.append((letter, p1, p2))

    return common


def ensure_output_directory(base_path: str = 'output/crosswords') -> str:
    """
    Создаёт директорию для вывода если не существует

    Args:
        base_path: Базовый путь

    Returns:
        str: Абсолютный путь к директории
    """
    path = Path(base_path)
    path.mkdir(parents=True, exist_ok=True)
    return str(path.absolute())


def generate_filename(category: str, index: int, difficulty: str = 'medium') -> str:
    """
    Генерирует имя файла для кроссворда

    Args:
        category: Категория
        index: Порядковый номер
        difficulty: Сложность

    Returns:
        str: Имя файла
    """
    # Транслитерация категории для имени файла
    transliteration = {
        'Наука и технологии': 'science',
        'История': 'history',
        'Искусство': 'art',
        'Спорт': 'sport',
        'Литература': 'literature',
        'Кино и сериалы': 'cinema',
        'Музыка': 'music',
        'География': 'geography',
        'Природа': 'nature',
        'Кулинария': 'cooking',
        'Космос': 'space'
    }

    cat_name = transliteration.get(category, category.lower().replace(' ', '_'))
    return f"{cat_name}_{difficulty}_{index:03d}.json"


def print_crossword_ascii(grid_array: List[List[str]]) -> str:
    """
    Возвращает ASCII представление кроссворда для отладки

    Args:
        grid_array: 2D массив сетки

    Returns:
        str: ASCII представление
    """
    lines = []
    for row in grid_array:
        line = ''
        for cell in row:
            if cell == '':
                line += '█'
            else:
                line += cell
        lines.append(line)
    return '\n'.join(lines)
