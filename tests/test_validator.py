"""
Тесты для класса Validator
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.grid import Grid, PlacedWord
from src.validator import Validator


class TestValidator:
    """Тесты класса Validator"""

    def test_validate_word_entry_valid(self):
        """Тест валидации корректной записи"""
        entry = {
            'word': 'ТЕСТ',
            'clue': 'Проверка',
            'hint': 'Подсказка'
        }

        is_valid, errors = Validator.validate_word_entry(entry)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_word_entry_missing_field(self):
        """Тест валидации записи без поля"""
        entry = {
            'word': 'ТЕСТ',
            'clue': 'Проверка'
            # hint отсутствует
        }

        is_valid, errors = Validator.validate_word_entry(entry)
        assert is_valid is False
        assert 'Отсутствует поле: hint' in errors

    def test_validate_word_entry_short_word(self):
        """Тест валидации слишком короткого слова"""
        entry = {
            'word': 'АБ',  # 2 буквы < 3
            'clue': 'Проверка',
            'hint': 'Подсказка'
        }

        is_valid, errors = Validator.validate_word_entry(entry)
        assert is_valid is False
        assert any('короткое' in e for e in errors)

    def test_validate_word_entry_non_cyrillic(self):
        """Тест валидации слова с латиницей"""
        entry = {
            'word': 'TEST',  # Латиница
            'clue': 'Проверка',
            'hint': 'Подсказка'
        }

        is_valid, errors = Validator.validate_word_entry(entry)
        assert is_valid is False
        assert any('недопустимые символы' in e for e in errors)

    def test_check_intersections_valid(self):
        """Тест проверки корректных пересечений"""
        grid = Grid(10)
        # АТОМ: А(5,0) Т(5,1) О(5,2) М(5,3)
        grid.place_word('АТОМ', 'Частица', 'Подсказка', 5, 0, 'horizontal')
        # ТЕСТ: Т(5,1) Е(6,1) С(7,1) Т(8,1) - пересечение в (5,1)
        grid.place_word('ТЕСТ', 'Проверка', 'Подсказка', 5, 1, 'vertical')

        words = grid.get_placed_words()
        errors = Validator.check_intersections(grid, words)

        assert len(errors) == 0

    def test_check_all_words_connected_true(self):
        """Тест связности слов (все связаны)"""
        grid = Grid(10)
        grid.place_word('АТОМ', 'Частица', 'Подсказка', 5, 0, 'horizontal')
        grid.place_word('ТЕСТ', 'Проверка', 'Подсказка', 5, 1, 'vertical')

        words = grid.get_placed_words()
        is_connected = Validator.check_all_words_connected(words)

        assert is_connected is True

    def test_check_all_words_connected_single(self):
        """Тест связности одного слова"""
        grid = Grid(10)
        grid.place_word('АТОМ', 'Частица', 'Подсказка', 5, 0, 'horizontal')

        words = grid.get_placed_words()
        is_connected = Validator.check_all_words_connected(words)

        assert is_connected is True

    def test_check_no_adjacent_parallel(self):
        """Тест отсутствия параллельных соседних слов"""
        grid = Grid(10)
        grid.place_word('АТОМ', 'Частица', 'Подсказка', 5, 0, 'horizontal')
        grid.place_word('ТЕСТ', 'Проверка', 'Подсказка', 5, 1, 'vertical')

        is_valid = Validator.check_no_adjacent_parallel(grid)
        assert is_valid is True

    def test_get_statistics(self):
        """Тест получения статистики"""
        grid = Grid(10)
        grid.place_word('АТОМ', 'Частица', 'Подсказка', 5, 0, 'horizontal')
        grid.place_word('ТЕСТ', 'Проверка', 'Подсказка', 5, 1, 'vertical')

        stats = Validator.get_statistics(grid)

        assert stats['word_count'] == 2
        assert stats['horizontal_count'] == 1
        assert stats['vertical_count'] == 1
        assert stats['avg_word_length'] == 4.0

    def test_validate_crossword_insufficient_words(self):
        """Тест валидации с недостаточным количеством слов"""
        grid = Grid(10)
        grid.place_word('ТЕСТ', 'Проверка', 'Подсказка', 5, 0, 'horizontal')

        is_valid, errors = Validator.validate_crossword(grid)

        assert is_valid is False
        assert any('Недостаточно слов' in e for e in errors)
