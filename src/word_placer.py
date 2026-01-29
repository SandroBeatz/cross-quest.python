"""
Класс WordPlacer - алгоритм размещения слов на сетке
"""

import random
from typing import List, Dict, Optional, Tuple
from .grid import Grid


class WordPlacer:
    """Класс для размещения слов на сетке кроссворда"""

    MAX_ATTEMPTS_PER_WORD = 100
    MAX_BACKTRACK_DEPTH = 3

    def __init__(self, grid: Grid, word_list: List[Dict]):
        """
        Инициализация с сеткой и списком слов

        Args:
            grid: Объект Grid
            word_list: Список словарей с ключами 'word', 'clue', 'hint'
        """
        self.grid = grid
        self.word_list = word_list
        self._used_words: set = set()

    def place_initial_word(self, center: bool = True) -> bool:
        """
        Размещает первое слово (обычно самое длинное)

        Args:
            center: Размещать ли в центре сетки

        Returns:
            bool: True если размещение успешно
        """
        if not self.word_list:
            return False

        # Выбираем самое длинное слово или случайное из топ-5
        sorted_words = sorted(self.word_list, key=lambda x: len(x['word']), reverse=True)
        candidates = sorted_words[:5]
        word_entry = random.choice(candidates)

        word = word_entry['word'].upper()
        length = len(word)

        if center:
            # Размещаем горизонтально в центре
            row = self.grid.size // 2
            col = (self.grid.size - length) // 2
        else:
            row = 0
            col = 0

        # Проверяем что слово помещается
        if col < 0:
            col = 0
        if col + length > self.grid.size:
            return False

        success = self.grid.place_word(
            word=word,
            clue=word_entry['clue'],
            hint=word_entry['hint'],
            row=row,
            col=col,
            direction='horizontal'
        )

        if success:
            self._used_words.add(word)

        return success

    def place_remaining_words(self, target_count: int = 12,
                              max_attempts: int = 1000) -> int:
        """
        Размещает остальные слова с пересечениями

        Args:
            target_count: Целевое количество слов
            max_attempts: Максимальное количество общих попыток

        Returns:
            int: Количество успешно размещённых слов (включая первое)
        """
        # Сортируем по длине (длинные слова сначала)
        available_words = [
            w for w in self.word_list
            if w['word'].upper() not in self._used_words
        ]
        available_words = sorted(available_words, key=lambda x: len(x['word']), reverse=True)

        attempts = 0
        word_index = 0

        while (len(self.grid.get_placed_words()) < target_count and
               attempts < max_attempts and
               word_index < len(available_words)):

            word_entry = available_words[word_index]
            word = word_entry['word'].upper()

            # Пропускаем уже использованные слова
            if word in self._used_words:
                word_index += 1
                continue

            # Ищем лучшую позицию
            best_position = self.find_best_position(word)

            if best_position:
                row, col, direction, _ = best_position
                success = self.grid.place_word(
                    word=word,
                    clue=word_entry['clue'],
                    hint=word_entry['hint'],
                    row=row,
                    col=col,
                    direction=direction
                )

                if success:
                    self._used_words.add(word)
                    # После успешного размещения пробуем следующее слово
                    word_index += 1
                    attempts = 0  # Сбрасываем счётчик попыток
                else:
                    attempts += 1
            else:
                # Не нашли позицию для этого слова, пробуем следующее
                word_index += 1
                attempts += 1

        return len(self.grid.get_placed_words())

    def find_best_position(self, word: str) -> Optional[Tuple[int, int, str, int]]:
        """
        Находит оптимальную позицию для слова

        Args:
            word: Слово для размещения

        Returns:
            (row, col, direction, intersection_count) или None
        """
        intersections = self.grid.get_intersections(word)

        if not intersections:
            return None

        # Сортируем по количеству пересечений (больше = лучше)
        # и по близости к центру
        center = self.grid.size // 2

        def score(position):
            row, col, direction, intersection_count = position
            # Приоритет: количество пересечений и близость к центру
            distance_to_center = abs(row - center) + abs(col - center)
            return (intersection_count * 10) - distance_to_center

        sorted_positions = sorted(intersections, key=score, reverse=True)

        # Добавляем элемент случайности из топ-3 позиций
        top_positions = sorted_positions[:3]
        if top_positions:
            return random.choice(top_positions)

        return None

    def place_words_with_backtracking(self, target_count: int = 12,
                                       max_global_attempts: int = 5) -> int:
        """
        Размещает слова с возможностью отката

        Args:
            target_count: Целевое количество слов
            max_global_attempts: Максимальное количество полных перезапусков

        Returns:
            int: Количество размещённых слов
        """
        best_result = 0
        best_grid_state = None
        best_placed_words = None

        for attempt in range(max_global_attempts):
            # Сохраняем текущее состояние
            current_count = self.place_remaining_words(target_count)

            if current_count > best_result:
                best_result = current_count
                best_grid_state = self.grid.to_array()
                best_placed_words = self.grid.get_placed_words()

            if current_count >= target_count:
                break

            # Если не достигли цели, пробуем заново с другим порядком
            if attempt < max_global_attempts - 1:
                self._reset_grid()
                random.shuffle(self.word_list)
                self.place_initial_word()

        return best_result

    def _reset_grid(self):
        """Сбрасывает сетку в начальное состояние"""
        size = self.grid.size
        self.grid = Grid(size)
        self._used_words.clear()

    def get_used_words(self) -> set:
        """Возвращает множество использованных слов"""
        return self._used_words.copy()

    def balance_directions(self) -> Tuple[int, int]:
        """
        Возвращает баланс направлений размещённых слов

        Returns:
            (horizontal_count, vertical_count)
        """
        horizontal = 0
        vertical = 0

        for placed in self.grid.get_placed_words():
            if placed.direction == 'horizontal':
                horizontal += 1
            else:
                vertical += 1

        return (horizontal, vertical)
