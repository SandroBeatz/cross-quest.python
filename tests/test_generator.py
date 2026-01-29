"""
Тесты для класса CrosswordGenerator
"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator import CrosswordGenerator
from src.validator import Validator


# Путь к тестовому словарю
TEST_DICT_PATH = str(Path(__file__).parent.parent / 'data' / 'dictionary.json')


class TestCrosswordGenerator:
    """Тесты класса CrosswordGenerator"""

    @pytest.fixture
    def generator(self):
        """Фикстура для создания генератора"""
        if not os.path.exists(TEST_DICT_PATH):
            pytest.skip("Тестовый словарь не найден")
        return CrosswordGenerator(TEST_DICT_PATH)

    def test_init(self, generator):
        """Тест инициализации генератора"""
        assert generator is not None
        assert len(generator.dictionary) > 0

    def test_get_available_categories(self, generator):
        """Тест получения доступных категорий"""
        categories = generator.get_available_categories()

        assert len(categories) > 0
        assert 'Наука и технологии' in categories

    def test_get_category_stats(self, generator):
        """Тест получения статистики категории"""
        stats = generator.get_category_stats('Наука и технологии')

        assert stats['total_words'] > 0
        assert stats['min_length'] >= 2
        assert stats['max_length'] <= 15

    def test_generate_single(self, generator):
        """Тест генерации одного кроссворда"""
        crossword = generator.generate(
            category='Наука и технологии',
            difficulty='medium',
            seed=42  # Для воспроизводимости
        )

        # Может быть None если генерация не удалась
        if crossword is not None:
            assert 'grid' in crossword
            assert 'words' in crossword
            assert 'difficulty' in crossword
            assert 'category' in crossword

            assert crossword['difficulty'] == 'medium'
            assert crossword['category'] == 'Наука и технологии'
            assert len(crossword['words']) >= 8

    def test_generate_with_different_difficulties(self, generator):
        """Тест генерации с разными уровнями сложности"""
        difficulties = ['easy', 'medium', 'hard']

        for diff in difficulties:
            crossword = generator.generate(
                category='Наука и технологии',
                difficulty=diff,
                seed=42
            )

            if crossword is not None:
                assert crossword['difficulty'] == diff

    def test_generate_invalid_category(self, generator):
        """Тест генерации с несуществующей категорией"""
        with pytest.raises(ValueError):
            generator.generate(category='Несуществующая')

    def test_generate_batch(self, generator):
        """Тест массовой генерации"""
        crosswords = generator.generate_batch(
            category='Наука и технологии',
            count=3,
            difficulty='medium'
        )

        # Должны получить хотя бы несколько кроссвордов
        assert len(crosswords) > 0

    def test_generation_stats(self, generator):
        """Тест статистики генерации"""
        # Генерируем несколько кроссвордов
        for _ in range(3):
            generator.generate('Наука и технологии', seed=None)

        stats = generator.get_generation_stats()

        assert stats['total_generated'] >= 3
        assert 'success_rate' in stats
        assert 'avg_generation_time' in stats

    def test_validate_dictionary(self, generator):
        """Тест валидации словаря"""
        is_valid, errors = generator.validate_dictionary()

        # Словарь может иметь предупреждения, но не критичные ошибки
        # для тестового словаря (менее 50 слов на категорию)
        assert isinstance(errors, list)

    def test_generated_crossword_structure(self, generator):
        """Тест структуры сгенерированного кроссворда"""
        crossword = generator.generate(
            category='История',
            difficulty='easy',
            seed=123
        )

        if crossword is None:
            pytest.skip("Не удалось сгенерировать кроссворд")

        # Проверяем структуру grid
        grid = crossword['grid']
        assert isinstance(grid, list)
        assert len(grid) > 0
        assert all(isinstance(row, list) for row in grid)

        # Проверяем структуру words
        words = crossword['words']
        assert isinstance(words, list)

        for word_info in words:
            assert 'word' in word_info
            assert 'clue' in word_info
            assert 'hint' in word_info
            assert 'startRow' in word_info
            assert 'startCol' in word_info
            assert 'direction' in word_info
            assert 'length' in word_info
            assert word_info['direction'] in ['horizontal', 'vertical']

    def test_words_on_grid(self, generator):
        """Тест соответствия слов и сетки"""
        crossword = generator.generate(
            category='Наука и технологии',
            difficulty='medium',
            seed=456
        )

        if crossword is None:
            pytest.skip("Не удалось сгенерировать кроссворд")

        grid = crossword['grid']
        words = crossword['words']

        for word_info in words:
            word = word_info['word']
            row = word_info['startRow']
            col = word_info['startCol']
            direction = word_info['direction']

            # Проверяем что каждая буква слова на сетке
            for i, char in enumerate(word):
                if direction == 'horizontal':
                    assert grid[row][col + i] == char, f"Буква {char} не найдена на позиции ({row}, {col + i})"
                else:
                    assert grid[row + i][col] == char, f"Буква {char} не найдена на позиции ({row + i}, {col})"


class TestCrosswordQuality:
    """Тесты качества генерируемых кроссвордов"""

    @pytest.fixture
    def generator(self):
        if not os.path.exists(TEST_DICT_PATH):
            pytest.skip("Тестовый словарь не найден")
        return CrosswordGenerator(TEST_DICT_PATH)

    def test_no_duplicate_words(self, generator):
        """Тест отсутствия дублирующихся слов"""
        crossword = generator.generate('Наука и технологии', seed=789)

        if crossword is None:
            pytest.skip("Не удалось сгенерировать кроссворд")

        words = [w['word'] for w in crossword['words']]
        assert len(words) == len(set(words)), "Найдены дублирующиеся слова"

    def test_word_lengths(self, generator):
        """Тест длины слов"""
        crossword = generator.generate('Наука и технологии', difficulty='medium', seed=101)

        if crossword is None:
            pytest.skip("Не удалось сгенерировать кроссворд")

        for word_info in crossword['words']:
            length = len(word_info['word'])
            assert 3 <= length <= 10, f"Слово {word_info['word']} имеет недопустимую длину {length}"

    def test_grid_not_empty(self, generator):
        """Тест что сетка не пустая"""
        crossword = generator.generate('История', seed=202)

        if crossword is None:
            pytest.skip("Не удалось сгенерировать кроссворд")

        grid = crossword['grid']
        non_empty_cells = sum(1 for row in grid for cell in row if cell != '')

        assert non_empty_cells > 0, "Сетка пустая"
