"""
Класс Validator - проверка корректности кроссворда
"""

from typing import List, Tuple, Set
from .grid import Grid, PlacedWord


class Validator:
    """Класс для валидации кроссворда"""

    MIN_WORDS = 8
    MIN_GRID_SIZE = 6
    MIN_FILL_DENSITY = 0.3
    MAX_FILL_DENSITY = 0.7

    @staticmethod
    def validate_crossword(grid: Grid, words: List[PlacedWord] = None) -> Tuple[bool, List[str]]:
        """
        Проверяет корректность кроссворда

        Args:
            grid: Объект Grid с размещёнными словами
            words: Опционально - список слов для проверки

        Returns:
            (is_valid: bool, errors: list)
        """
        errors = []

        if words is None:
            words = grid.get_placed_words()

        # Проверка минимального количества слов
        if len(words) < Validator.MIN_WORDS:
            errors.append(f"Недостаточно слов: {len(words)} < {Validator.MIN_WORDS}")

        # Проверка корректности всех пересечений
        intersection_errors = Validator.check_intersections(grid, words)
        errors.extend(intersection_errors)

        # Проверка связности слов
        if not Validator.check_all_words_connected(words):
            errors.append("Не все слова связаны между собой")

        # Проверка плотности заполнения
        density = grid.get_fill_density()
        if density < Validator.MIN_FILL_DENSITY:
            errors.append(f"Слишком низкая плотность: {density:.2f} < {Validator.MIN_FILL_DENSITY}")
        if density > Validator.MAX_FILL_DENSITY:
            errors.append(f"Слишком высокая плотность: {density:.2f} > {Validator.MAX_FILL_DENSITY}")

        # Проверка отсутствия дубликатов слов
        word_set = set()
        for placed in words:
            if placed.word in word_set:
                errors.append(f"Дублирующееся слово: {placed.word}")
            word_set.add(placed.word)

        # Проверка минимальной длины слов
        for placed in words:
            if len(placed.word) < 3:
                errors.append(f"Слово слишком короткое: {placed.word}")

        return (len(errors) == 0, errors)

    @staticmethod
    def check_intersections(grid: Grid, words: List[PlacedWord]) -> List[str]:
        """
        Проверяет корректность всех пересечений

        Returns:
            list: Список ошибок пересечений
        """
        errors = []
        grid_array = grid.to_array()

        if not grid_array:
            return errors

        grid_height = len(grid_array)
        grid_width = len(grid_array[0]) if grid_array else 0

        for placed in words:
            word = placed.word
            row, col = placed.row, placed.col

            for i, expected_char in enumerate(word):
                if placed.direction == 'horizontal':
                    actual_row, actual_col = row, col + i
                else:
                    actual_row, actual_col = row + i, col

                # Проверяем границы (включая отрицательные)
                if (actual_row < 0 or actual_row >= grid_height or
                    actual_col < 0 or actual_col >= grid_width):
                    errors.append(f"Слово {word} выходит за границы сетки")
                    continue

                # Проверяем что строка достаточно длинная
                if actual_col >= len(grid_array[actual_row]):
                    errors.append(f"Слово {word} выходит за границы строки")
                    continue

                actual_char = grid_array[actual_row][actual_col]

                if actual_char != expected_char:
                    errors.append(
                        f"Несовпадение букв в позиции ({actual_row}, {actual_col}): "
                        f"ожидалось '{expected_char}', найдено '{actual_char}'"
                    )

        return errors

    @staticmethod
    def check_all_words_connected(words: List[PlacedWord]) -> bool:
        """
        Проверяет связность всех слов (каждое слово должно пересекаться хотя бы с одним другим)

        Returns:
            bool: True если все слова связаны
        """
        if len(words) <= 1:
            return True

        # Строим граф связей между словами
        adjacency: dict = {i: set() for i in range(len(words))}

        for i, word1 in enumerate(words):
            for j, word2 in enumerate(words):
                if i >= j:
                    continue

                if Validator._words_intersect(word1, word2):
                    adjacency[i].add(j)
                    adjacency[j].add(i)

        # BFS для проверки связности
        visited: Set[int] = set()
        queue = [0]
        visited.add(0)

        while queue:
            current = queue.pop(0)
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return len(visited) == len(words)

    @staticmethod
    def _words_intersect(word1: PlacedWord, word2: PlacedWord) -> bool:
        """Проверяет, пересекаются ли два слова"""
        cells1 = Validator._get_word_cells(word1)
        cells2 = Validator._get_word_cells(word2)
        return bool(cells1 & cells2)

    @staticmethod
    def _get_word_cells(word: PlacedWord) -> Set[Tuple[int, int]]:
        """Возвращает множество ячеек, занятых словом"""
        cells = set()
        for i in range(word.length):
            if word.direction == 'horizontal':
                cells.add((word.row, word.col + i))
            else:
                cells.add((word.row + i, word.col))
        return cells

    @staticmethod
    def check_no_adjacent_parallel(grid: Grid, words: List[PlacedWord] = None) -> bool:
        """
        Проверяет отсутствие параллельных соседних слов

        Returns:
            bool: True если нет параллельных соседних слов
        """
        if words is None:
            words = grid.get_placed_words()

        for i, word1 in enumerate(words):
            for j, word2 in enumerate(words):
                if i >= j:
                    continue
                if word1.direction != word2.direction:
                    continue

                # Слова параллельны, проверяем соседство
                if Validator._are_parallel_adjacent(word1, word2):
                    return False

        return True

    @staticmethod
    def _are_parallel_adjacent(word1: PlacedWord, word2: PlacedWord) -> bool:
        """Проверяет, являются ли параллельные слова соседними"""
        if word1.direction == 'horizontal':
            # Горизонтальные слова - проверяем соседство по вертикали
            if abs(word1.row - word2.row) != 1:
                return False
            # Проверяем пересечение по горизонтали
            range1 = set(range(word1.col, word1.col + word1.length))
            range2 = set(range(word2.col, word2.col + word2.length))
            return bool(range1 & range2)
        else:
            # Вертикальные слова - проверяем соседство по горизонтали
            if abs(word1.col - word2.col) != 1:
                return False
            # Проверяем пересечение по вертикали
            range1 = set(range(word1.row, word1.row + word1.length))
            range2 = set(range(word2.row, word2.row + word2.length))
            return bool(range1 & range2)

    @staticmethod
    def validate_word_entry(word_entry: dict) -> Tuple[bool, List[str]]:
        """
        Проверяет корректность записи словаря

        Args:
            word_entry: Словарь с ключами 'word', 'clue', 'hint'

        Returns:
            (is_valid: bool, errors: list)
        """
        errors = []

        # Проверка наличия обязательных полей
        required_fields = ['word', 'clue', 'hint']
        for field in required_fields:
            if field not in word_entry:
                errors.append(f"Отсутствует поле: {field}")

        if 'word' in word_entry:
            word = word_entry['word']

            # Проверка длины
            if len(word) < 3:
                errors.append(f"Слово слишком короткое: {word}")
            if len(word) > 12:
                errors.append(f"Слово слишком длинное: {word}")

            # Проверка что только кириллица
            if not all('А' <= c <= 'Я' or c == 'Ё' for c in word.upper()):
                errors.append(f"Слово содержит недопустимые символы: {word}")

        return (len(errors) == 0, errors)

    @staticmethod
    def get_statistics(grid: Grid) -> dict:
        """
        Собирает статистику по кроссворду

        Returns:
            dict: Статистика
        """
        words = grid.get_placed_words()
        grid_array = grid.to_array()

        horizontal_count = sum(1 for w in words if w.direction == 'horizontal')
        vertical_count = len(words) - horizontal_count

        word_lengths = [w.length for w in words]

        return {
            'word_count': len(words),
            'horizontal_count': horizontal_count,
            'vertical_count': vertical_count,
            'grid_height': len(grid_array),
            'grid_width': len(grid_array[0]) if grid_array else 0,
            'fill_density': grid.get_fill_density(),
            'avg_word_length': sum(word_lengths) / len(word_lengths) if word_lengths else 0,
            'min_word_length': min(word_lengths) if word_lengths else 0,
            'max_word_length': max(word_lengths) if word_lengths else 0,
        }
