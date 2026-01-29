"""
Тесты для класса Grid
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.grid import Grid, PlacedWord


class TestGrid:
    """Тесты класса Grid"""

    def test_init(self):
        """Тест инициализации сетки"""
        grid = Grid(10)
        assert grid.size == 10
        assert len(grid._grid) == 10
        assert len(grid._grid[0]) == 10

    def test_get_set_cell(self):
        """Тест получения и установки значения ячейки"""
        grid = Grid(10)

        # Установка значения
        assert grid.set_cell(5, 5, 'А') is True
        assert grid.get_cell(5, 5) == 'А'

        # Вне границ
        assert grid.set_cell(-1, 0, 'Б') is False
        assert grid.set_cell(0, 10, 'В') is False
        assert grid.get_cell(10, 10) == ''

    def test_can_place_word_horizontal(self):
        """Тест проверки размещения горизонтального слова"""
        grid = Grid(10)

        # Слово помещается
        assert grid.can_place_word('ТЕСТ', 5, 0, 'horizontal') is True

        # Слово не помещается (выходит за границу)
        assert grid.can_place_word('ТЕСТ', 5, 8, 'horizontal') is False

    def test_can_place_word_vertical(self):
        """Тест проверки размещения вертикального слова"""
        grid = Grid(10)

        # Слово помещается
        assert grid.can_place_word('ТЕСТ', 0, 5, 'vertical') is True

        # Слово не помещается
        assert grid.can_place_word('ТЕСТ', 8, 5, 'vertical') is False

    def test_place_word(self):
        """Тест размещения слова"""
        grid = Grid(10)

        # Размещаем горизонтальное слово
        success = grid.place_word('АТОМ', 'Частица', 'Подсказка', 5, 0, 'horizontal')
        assert success is True

        # Проверяем буквы
        assert grid.get_cell(5, 0) == 'А'
        assert grid.get_cell(5, 1) == 'Т'
        assert grid.get_cell(5, 2) == 'О'
        assert grid.get_cell(5, 3) == 'М'

        # Проверяем список размещённых слов
        placed = grid.get_placed_words()
        assert len(placed) == 1
        assert placed[0].word == 'АТОМ'

    def test_place_word_intersection(self):
        """Тест размещения пересекающихся слов"""
        grid = Grid(10)

        # Первое слово горизонтально: АТОМ на позиции (5, 0)
        # Буквы: А(5,0) Т(5,1) О(5,2) М(5,3)
        grid.place_word('АТОМ', 'Частица', 'Подсказка', 5, 0, 'horizontal')

        # Второе слово вертикально, пересекается по букве 'Т'
        # ТЕСТ начиная с (5, 1): Т(5,1) Е(6,1) С(7,1) Т(8,1)
        # Первая буква 'Т' совпадает с 'Т' из 'АТОМ' на (5, 1)
        success = grid.place_word('ТЕСТ', 'Проверка', 'Подсказка', 5, 1, 'vertical')
        assert success is True

        # Проверяем пересечение
        assert grid.get_cell(5, 1) == 'Т'
        # Проверяем что оба слова записаны
        assert len(grid.get_placed_words()) == 2

    def test_place_word_conflict(self):
        """Тест конфликта при размещении"""
        grid = Grid(10)

        # Первое слово
        grid.place_word('АТОМ', 'Частица', 'Подсказка', 5, 0, 'horizontal')

        # Второе слово с конфликтом (разные буквы в одной позиции)
        # Пытаемся поставить слово, которое конфликтует
        success = grid.can_place_word('МАМА', 5, 0, 'horizontal')
        assert success is False  # 'М' != 'А' в позиции (5, 0)

    def test_get_intersections(self):
        """Тест поиска пересечений"""
        grid = Grid(10)

        # Размещаем первое слово
        grid.place_word('АТОМ', 'Частица', 'Подсказка', 5, 3, 'horizontal')

        # Ищем пересечения для слова 'ТЕСТ' (общая буква 'Т')
        intersections = grid.get_intersections('ТЕСТ')

        # Должны найти пересечение по букве 'Т'
        assert len(intersections) > 0

    def test_crop_empty_edges(self):
        """Тест обрезки пустых краёв"""
        grid = Grid(10)

        # Размещаем слово не в углу
        grid.place_word('ТЕСТ', 'Проверка', 'Подсказка', 5, 5, 'horizontal')

        # Обрезаем
        height, width = grid.crop_empty_edges()

        # Сетка должна стать минимальной
        assert height == 1
        assert width == 4

        # Проверяем что слово на месте
        placed = grid.get_placed_words()
        assert placed[0].row == 0
        assert placed[0].col == 0

    def test_to_array(self):
        """Тест преобразования в массив"""
        grid = Grid(5)
        grid.place_word('АБВ', 'Тест', 'Подсказка', 0, 0, 'horizontal')

        array = grid.to_array()
        assert array[0][0] == 'А'
        assert array[0][1] == 'Б'
        assert array[0][2] == 'В'
        assert array[0][3] == ''

    def test_fill_density(self):
        """Тест вычисления плотности заполнения"""
        grid = Grid(10)

        # Пустая сетка
        assert grid.get_fill_density() == 0.0

        # Размещаем слово (4 буквы из 100 ячеек)
        grid.place_word('ТЕСТ', 'Проверка', 'Подсказка', 0, 0, 'horizontal')
        assert grid.get_fill_density() == 0.04

    def test_str_representation(self):
        """Тест строкового представления"""
        grid = Grid(5)
        grid.place_word('АБ', 'Тест', 'Подсказка', 0, 0, 'horizontal')

        string = str(grid)
        assert 'АБ' in string
        assert '.' in string  # Пустые ячейки


class TestPlacedWord:
    """Тесты класса PlacedWord"""

    def test_init(self):
        """Тест инициализации"""
        pw = PlacedWord(
            word='ТЕСТ',
            clue='Проверка',
            hint='Подсказка',
            row=5,
            col=3,
            direction='horizontal'
        )

        assert pw.word == 'ТЕСТ'
        assert pw.clue == 'Проверка'
        assert pw.hint == 'Подсказка'
        assert pw.row == 5
        assert pw.col == 3
        assert pw.direction == 'horizontal'
        assert pw.length == 4

    def test_to_dict(self):
        """Тест преобразования в словарь"""
        pw = PlacedWord(
            word='ТЕСТ',
            clue='Проверка',
            hint='Подсказка',
            row=5,
            col=3,
            direction='horizontal'
        )

        d = pw.to_dict()

        assert d['word'] == 'ТЕСТ'
        assert d['clue'] == 'Проверка'
        assert d['hint'] == 'Подсказка'
        assert d['startRow'] == 5
        assert d['startCol'] == 3
        assert d['direction'] == 'horizontal'
        assert d['length'] == 4
