"""
Основной класс CrosswordGenerator - генерация кроссвордов
"""

import random
import time
from typing import Dict, List, Optional, Tuple

from .grid import Grid
from .word_placer import WordPlacer
from .validator import Validator
from .utils import (
    load_dictionary,
    filter_words_by_length,
    sort_words_by_score,
    DIFFICULTY_SETTINGS
)
from .age_config import (
    AGE_GROUPS, DEFAULT_AGE_GROUP, VALID_AGE_GROUPS,
    validate_age_group, get_grid_size,
    get_effective_max_word_length, get_word_count_range,
    get_min_words_for_grid, get_category_age_groups,
    get_category_icon, get_category_description,
)


class CrosswordGenerator:
    """Генератор русскоязычных кроссвордов"""

    DEFAULT_GRID_SIZE = 10
    MIN_GRID_SIZE = 6
    MAX_REGENERATION_ATTEMPTS = 10

    def __init__(self, dictionary_path: str):
        """
        Инициализация генератора со словарём

        Args:
            dictionary_path: Путь к файлу словаря (JSON)
        """
        self.dictionary = load_dictionary(dictionary_path)
        self._stats = {
            'total_generated': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0.0
        }

    def generate(self, category: str, difficulty: str = "medium",
                 seed: Optional[int] = None,
                 excluded_words: Optional[set] = None,
                 age_group: Optional[str] = None,
                 user_progress: Optional[dict] = None) -> Optional[dict]:
        """
        Генерирует один кроссворд

        Args:
            category: Категория из словаря
            difficulty: "easy" | "medium" | "hard"
            seed: Опциональный seed для воспроизводимости
            excluded_words: Множество слов для исключения (в верхнем регистре)
            age_group: Возрастная группа (опционально)
            user_progress: Прогресс пользователя с recent_words (опционально)

        Returns:
            dict: Кроссворд в JSON формате или None при ошибке
        """
        start_time = time.time()

        if seed is not None:
            random.seed(seed)

        # Получаем настройки сложности
        settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS['medium'])

        # Параметры возрастной группы
        effective_age_group = validate_age_group(age_group)
        age_config = AGE_GROUPS[effective_age_group]
        grid_size = get_grid_size(effective_age_group, difficulty)
        effective_max_word_length = get_effective_max_word_length(
            effective_age_group, settings['max_word_length']
        )

        # Диапазон количества слов на основе площади сетки
        grid_word_range = get_word_count_range(grid_size[0], grid_size[1])
        effective_word_count_min = max(
            grid_word_range[0],
            min(settings['word_count'][0], grid_word_range[1])
        )
        effective_word_count_max = min(settings['word_count'][1], grid_word_range[1])
        if effective_word_count_min > effective_word_count_max:
            effective_word_count_max = effective_word_count_min

        min_words_for_validation = get_min_words_for_grid(grid_size[0], grid_size[1])

        # Получаем слова для категории
        if category not in self.dictionary:
            raise ValueError(f"Категория '{category}' не найдена в словаре")

        words = self.dictionary[category]

        # Исключаем использованные слова
        if excluded_words:
            words = [w for w in words if w['word'].upper() not in excluded_words]

        # Фильтруем по длине (учитываем ограничение возрастной группы)
        filtered_words = filter_words_by_length(
            words,
            settings['min_word_length'],
            effective_max_word_length
        )

        if len(filtered_words) < min_words_for_validation:
            raise ValueError(
                f"Недостаточно слов в категории '{category}': "
                f"{len(filtered_words)} < {min_words_for_validation}"
            )

        # Сортируем по приоритету
        sorted_words = sort_words_by_score(filtered_words)

        # Депроритизация недавних слов (user_progress)
        if user_progress and isinstance(user_progress, dict):
            recent_words = user_progress.get('recent_words', [])
            if recent_words:
                recent_set = {w.upper() for w in recent_words if isinstance(w, str)}
                sorted_words.sort(key=lambda w: w['word'].upper() in recent_set)

        # Определяем целевое количество слов
        target_count = random.randint(effective_word_count_min, effective_word_count_max)

        # Пытаемся сгенерировать кроссворд
        for attempt in range(self.MAX_REGENERATION_ATTEMPTS):
            result = self._generate_single(
                sorted_words, target_count, settings,
                grid_size=grid_size,
                min_words=min_words_for_validation
            )

            if result is not None:
                result['difficulty'] = difficulty
                result['category'] = category
                # Метаданные v2
                result['metadata']['vocabulary_level'] = age_config['vocabulary_level']
                result['metadata']['max_word_length'] = effective_max_word_length
                result['metadata']['age_adapted'] = age_group is not None

                # Обновляем статистику
                self._stats['total_generated'] += 1
                self._stats['successful'] += 1
                self._stats['total_time'] += time.time() - start_time

                return result

            # Перемешиваем слова для следующей попытки
            random.shuffle(sorted_words)

        # Не удалось сгенерировать
        self._stats['total_generated'] += 1
        self._stats['failed'] += 1
        self._stats['total_time'] += time.time() - start_time

        return None

    def _generate_single(self, words: List[Dict], target_count: int,
                         settings: dict,
                         grid_size: Optional[Tuple[int, int]] = None,
                         min_words: Optional[int] = None) -> Optional[dict]:
        """
        Одна попытка генерации кроссворда

        Args:
            words: Отсортированный список слов
            target_count: Целевое количество слов
            settings: Настройки сложности
            grid_size: Опционально (height, width) для сетки
            min_words: Опционально минимальное количество слов

        Returns:
            dict: Кроссворд или None
        """
        # Создаём сетку
        if grid_size:
            grid = Grid(height=grid_size[0], width=grid_size[1])
        else:
            grid = Grid(self.DEFAULT_GRID_SIZE)

        # Создаём placer
        placer = WordPlacer(grid, words)

        # Размещаем первое слово
        if not placer.place_initial_word():
            return None

        # Размещаем остальные слова
        placed_count = placer.place_remaining_words(target_count)

        # Проверяем минимальные требования
        effective_min_words = min_words if min_words is not None else Validator.MIN_WORDS
        if placed_count < effective_min_words:
            return None

        # Обрезаем пустые края
        height, width = grid.crop_empty_edges()

        # Проверяем размер сетки (только для v1 без явного grid_size)
        if grid_size is None:
            if height < self.MIN_GRID_SIZE or width < self.MIN_GRID_SIZE:
                return None

        # Валидируем кроссворд
        is_valid, errors = Validator.validate_crossword(grid, min_words=effective_min_words)

        if not is_valid:
            return None

        # Формируем результат
        return self._format_result(grid)

    def _format_result(self, grid: Grid) -> dict:
        """
        Форматирует результат в JSON структуру

        Args:
            grid: Заполненная сетка

        Returns:
            dict: Кроссворд в формате JSON
        """
        placed_words = grid.get_placed_words()
        grid_array = grid.to_array()

        return {
            'grid': grid_array,
            'words': [pw.to_dict() for pw in placed_words],
            'difficulty': '',  # Будет заполнено в generate()
            'category': '',    # Будет заполнено в generate()
            'metadata': {
                'word_count': len(placed_words),
                'grid_size': [len(grid_array), len(grid_array[0]) if grid_array else 0],
                'fill_density': round(grid.get_fill_density(), 2)
            }
        }

    def generate_batch(self, category: str, count: int = 50,
                       difficulty: str = "medium") -> List[dict]:
        """
        Генерирует несколько кроссвордов

        Args:
            category: Категория
            count: Количество кроссвордов
            difficulty: Сложность

        Returns:
            list: Список сгенерированных кроссвордов
        """
        crosswords = []

        for i in range(count):
            crossword = self.generate(category, difficulty)
            if crossword is not None:
                crosswords.append(crossword)

        return crosswords

    def get_available_categories(self) -> List[str]:
        """
        Возвращает список доступных категорий

        Returns:
            list: Названия категорий
        """
        return list(self.dictionary.keys())

    def get_category_stats(self, category: str) -> dict:
        """
        Возвращает статистику по категории

        Args:
            category: Название категории

        Returns:
            dict: Статистика
        """
        if category not in self.dictionary:
            return {}

        words = self.dictionary[category]
        lengths = [len(w['word']) for w in words]

        return {
            'total_words': len(words),
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'avg_length': sum(lengths) / len(lengths) if lengths else 0
        }

    def get_generation_stats(self) -> dict:
        """
        Возвращает статистику генерации

        Returns:
            dict: Статистика
        """
        success_rate = (
            self._stats['successful'] / self._stats['total_generated']
            if self._stats['total_generated'] > 0 else 0
        )

        avg_time = (
            self._stats['total_time'] / self._stats['total_generated']
            if self._stats['total_generated'] > 0 else 0
        )

        return {
            'total_generated': self._stats['total_generated'],
            'successful': self._stats['successful'],
            'failed': self._stats['failed'],
            'success_rate': success_rate,
            'avg_generation_time': avg_time
        }

    def validate_dictionary(self) -> Tuple[bool, List[str]]:
        """
        Проверяет корректность загруженного словаря

        Returns:
            (is_valid, errors)
        """
        errors = []

        for category, words in self.dictionary.items():
            if len(words) < 50:
                errors.append(f"Категория '{category}': мало слов ({len(words)} < 50)")

            for i, word_entry in enumerate(words):
                is_valid, word_errors = Validator.validate_word_entry(word_entry)
                if not is_valid:
                    for error in word_errors:
                        errors.append(f"Категория '{category}', слово #{i}: {error}")

        return (len(errors) == 0, errors)

    def get_categories(self) -> List[str]:
        """
        Возвращает список названий категорий (алиас для get_available_categories)

        Returns:
            list: Названия категорий
        """
        return self.get_available_categories()

    def get_categories_info(self) -> List[dict]:
        """
        Возвращает детальную информацию о категориях

        Returns:
            list: Список словарей с информацией о категориях
        """
        return [
            {
                'name': category,
                'word_count': len(words),
                'available': len(words) >= 50  # Минимум для генерации
            }
            for category, words in self.dictionary.items()
        ]

    def get_total_word_count(self) -> int:
        """
        Возвращает общее количество слов во всех категориях

        Returns:
            int: Общее количество слов
        """
        return sum(len(words) for words in self.dictionary.values())

    def get_categories_info_with_progress(self, guessed_words: Optional[Dict[str, set]] = None,
                                           age_group: Optional[str] = None) -> List[dict]:
        """
        Возвращает информацию о категориях с процентом отгаданных слов

        Args:
            guessed_words: Словарь {category_name: set(отгаданные слова в UPPER)}
            age_group: Возрастная группа для фильтрации (опционально)

        Returns:
            list: [{name, word_count, available, guessed_count, guessed_percent, icon, description, age_groups}]
        """
        guessed_words = guessed_words or {}

        # Фильтрация только если передан валидный age_group
        apply_filter = age_group is not None and age_group in VALID_AGE_GROUPS

        result = []

        for category, words in self.dictionary.items():
            # Получаем возрастные группы для категории
            category_age_groups = get_category_age_groups(category)

            # Фильтрация по возрастной группе
            if apply_filter and age_group not in category_age_groups:
                continue

            word_count = len(words)
            all_words_in_category = {w['word'].upper() for w in words}

            # Пересечение отгаданных и существующих в категории
            category_guessed = guessed_words.get(category, set())
            guessed_count = len(category_guessed & all_words_in_category)
            guessed_percent = round((guessed_count / word_count * 100), 1) if word_count > 0 else 0

            result.append({
                'name': category,
                'word_count': word_count,
                'available': word_count >= 50,
                'guessed_count': guessed_count,
                'guessed_percent': guessed_percent,
                'icon': get_category_icon(category),
                'description': get_category_description(category),
                'age_groups': category_age_groups,
            })

        return result
