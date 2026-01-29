"""
Класс Grid - работа с сеткой кроссворда
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PlacedWord:
    """Информация о размещённом слове"""
    word: str
    clue: str
    hint: str
    row: int
    col: int
    direction: str  # 'horizontal' или 'vertical'

    @property
    def length(self) -> int:
        return len(self.word)

    def to_dict(self) -> dict:
        return {
            'word': self.word,
            'clue': self.clue,
            'hint': self.hint,
            'startRow': self.row,
            'startCol': self.col,
            'direction': self.direction,
            'length': self.length
        }


class Grid:
    """Класс для работы с сеткой кроссворда"""

    EMPTY = ''

    def __init__(self, size: int = 10):
        """Создаёт пустую сетку заданного размера"""
        self.size = size
        self._height = size
        self._width = size
        self._grid: List[List[str]] = [[self.EMPTY for _ in range(size)] for _ in range(size)]
        self._placed_words: List[PlacedWord] = []

    def get_cell(self, row: int, col: int) -> str:
        """Возвращает содержимое ячейки"""
        if 0 <= row < self._height and 0 <= col < self._width:
            return self._grid[row][col]
        return self.EMPTY

    def set_cell(self, row: int, col: int, char: str) -> bool:
        """Устанавливает значение в ячейку"""
        if 0 <= row < self._height and 0 <= col < self._width:
            self._grid[row][col] = char
            return True
        return False

    def can_place_word(self, word: str, row: int, col: int, direction: str) -> bool:
        """
        Проверяет возможность размещения слова

        Args:
            word: Слово для размещения
            row: Начальная строка
            col: Начальный столбец
            direction: 'horizontal' или 'vertical'

        Returns:
            bool: True если размещение возможно
        """
        word = word.upper()
        length = len(word)

        # Проверка границ
        if row < 0 or col < 0:
            return False

        if direction == 'horizontal':
            if col + length > self._width:
                return False
            if row >= self._height:
                return False
        else:  # vertical
            if row + length > self._height:
                return False
            if col >= self._width:
                return False

        has_intersection = False

        for i, char in enumerate(word):
            if direction == 'horizontal':
                curr_row, curr_col = row, col + i
            else:
                curr_row, curr_col = row + i, col

            current_cell = self.get_cell(curr_row, curr_col)

            # Если ячейка занята другой буквой - размещение невозможно
            if current_cell != self.EMPTY and current_cell != char:
                return False

            # Если буква совпадает - это пересечение
            if current_cell == char:
                has_intersection = True

            # Проверка соседних ячеек (избегаем параллельных слов)
            if current_cell == self.EMPTY:
                if not self._check_adjacent_cells(curr_row, curr_col, direction, i, length):
                    return False

        # Проверка ячеек перед и после слова
        if direction == 'horizontal':
            # Перед словом
            if col > 0 and self.get_cell(row, col - 1) != self.EMPTY:
                return False
            # После слова
            if col + length < self._width and self.get_cell(row, col + length) != self.EMPTY:
                return False
        else:  # vertical
            # Перед словом
            if row > 0 and self.get_cell(row - 1, col) != self.EMPTY:
                return False
            # После слова
            if row + length < self._height and self.get_cell(row + length, col) != self.EMPTY:
                return False

        return True

    def _check_adjacent_cells(self, row: int, col: int, direction: str,
                              pos_in_word: int, word_length: int) -> bool:
        """
        Проверяет соседние ячейки для избежания параллельных слов.
        Разрешает соседство только если это пересечение с существующим словом.

        Returns:
            bool: True если размещение корректно
        """
        if direction == 'horizontal':
            # Проверяем ячейки сверху и снизу
            above = self.get_cell(row - 1, col)
            below = self.get_cell(row + 1, col)

            # Если сверху или снизу есть буква, это должно быть частью
            # вертикального слова, которое пересекается с нашим
            if above != self.EMPTY or below != self.EMPTY:
                # Проверяем, есть ли вертикальное слово, проходящее через (row, col)
                if not self._has_perpendicular_word(row, col, 'vertical'):
                    return False
        else:  # vertical
            # Проверяем ячейки слева и справа
            left = self.get_cell(row, col - 1)
            right = self.get_cell(row, col + 1)

            if left != self.EMPTY or right != self.EMPTY:
                # Проверяем, есть ли горизонтальное слово, проходящее через (row, col)
                if not self._has_perpendicular_word(row, col, 'horizontal'):
                    return False

        return True

    def _has_perpendicular_word(self, row: int, col: int, direction: str) -> bool:
        """
        Проверяет, есть ли слово указанного направления, проходящее через позицию
        """
        for placed in self._placed_words:
            if placed.direction != direction:
                continue

            if direction == 'horizontal':
                if placed.row == row and placed.col <= col < placed.col + placed.length:
                    return True
            else:  # vertical
                if placed.col == col and placed.row <= row < placed.row + placed.length:
                    return True

        return False

    def place_word(self, word: str, clue: str, hint: str, row: int, col: int,
                   direction: str) -> bool:
        """
        Размещает слово на сетке

        Args:
            word: Слово для размещения
            clue: Подсказка
            hint: Дополнительная подсказка
            row: Начальная строка
            col: Начальный столбец
            direction: 'horizontal' или 'vertical'

        Returns:
            bool: True если размещение успешно
        """
        word = word.upper()

        if not self.can_place_word(word, row, col, direction):
            return False

        # Размещаем буквы
        for i, char in enumerate(word):
            if direction == 'horizontal':
                self.set_cell(row, col + i, char)
            else:
                self.set_cell(row + i, col, char)

        # Добавляем в список размещённых слов
        placed_word = PlacedWord(
            word=word,
            clue=clue,
            hint=hint,
            row=row,
            col=col,
            direction=direction
        )
        self._placed_words.append(placed_word)

        return True

    def get_intersections(self, word: str) -> List[Tuple[int, int, str, int]]:
        """
        Находит все возможные позиции для размещения слова с пересечениями

        Args:
            word: Слово для поиска пересечений

        Returns:
            List of (row, col, direction, intersection_count)
        """
        word = word.upper()
        intersections = []

        # Для каждого размещённого слова ищем общие буквы
        for placed in self._placed_words:
            for i, placed_char in enumerate(placed.word):
                for j, word_char in enumerate(word):
                    if placed_char == word_char:
                        # Вычисляем позицию для нового слова
                        if placed.direction == 'horizontal':
                            # Новое слово будет вертикальным
                            new_row = placed.row - j
                            new_col = placed.col + i
                            new_direction = 'vertical'
                        else:
                            # Новое слово будет горизонтальным
                            new_row = placed.row + i
                            new_col = placed.col - j
                            new_direction = 'horizontal'

                        # Проверяем возможность размещения
                        if self.can_place_word(word, new_row, new_col, new_direction):
                            # Считаем количество пересечений
                            intersection_count = self._count_intersections(
                                word, new_row, new_col, new_direction
                            )
                            intersections.append((
                                new_row, new_col, new_direction, intersection_count
                            ))

        return intersections

    def _count_intersections(self, word: str, row: int, col: int, direction: str) -> int:
        """Подсчитывает количество пересечений для позиции"""
        count = 0
        for i, char in enumerate(word):
            if direction == 'horizontal':
                if self.get_cell(row, col + i) == char:
                    count += 1
            else:
                if self.get_cell(row + i, col) == char:
                    count += 1
        return count

    def crop_empty_edges(self) -> Tuple[int, int]:
        """
        Обрезает пустые края сетки

        Returns:
            (new_height, new_width)
        """
        # Находим границы непустой области
        min_row, max_row = self._height, 0
        min_col, max_col = self._width, 0

        for row in range(self._height):
            for col in range(self._width):
                if self._grid[row][col] != self.EMPTY:
                    min_row = min(min_row, row)
                    max_row = max(max_row, row)
                    min_col = min(min_col, col)
                    max_col = max(max_col, col)

        if min_row > max_row:
            return (0, 0)

        # Создаём новую сетку
        new_height = max_row - min_row + 1
        new_width = max_col - min_col + 1
        new_grid = []

        for row in range(min_row, max_row + 1):
            new_row = []
            for col in range(min_col, max_col + 1):
                new_row.append(self._grid[row][col])
            new_grid.append(new_row)

        # Обновляем координаты размещённых слов
        for placed in self._placed_words:
            placed.row -= min_row
            placed.col -= min_col

        self._grid = new_grid
        self._height = new_height
        self._width = new_width
        self.size = max(new_height, new_width)

        return (new_height, new_width)

    def to_array(self) -> List[List[str]]:
        """Возвращает сетку как 2D массив"""
        return [row[:] for row in self._grid]

    def get_placed_words(self) -> List[PlacedWord]:
        """Возвращает список размещённых слов"""
        return self._placed_words[:]

    def get_fill_density(self) -> float:
        """Вычисляет плотность заполнения сетки"""
        total_cells = 0
        filled_cells = 0

        for row in self._grid:
            for cell in row:
                total_cells += 1
                if cell != self.EMPTY:
                    filled_cells += 1

        return filled_cells / total_cells if total_cells > 0 else 0.0

    def __str__(self) -> str:
        """Строковое представление сетки для отладки"""
        result = []
        for row in self._grid:
            line = ''
            for cell in row:
                if cell == self.EMPTY:
                    line += '.'
                else:
                    line += cell
            result.append(line)
        return '\n'.join(result)
