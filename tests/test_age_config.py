"""
Тесты для конфигурации возрастных групп
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.age_config import (
    AGE_GROUPS, VALID_AGE_GROUPS, DEFAULT_AGE_GROUP,
    validate_age_group, get_grid_size, get_effective_max_word_length,
    get_word_count_range, get_min_words_for_grid,
    get_category_age_groups, get_category_icon, get_category_description,
)


class TestValidateAgeGroup:
    """Тесты validate_age_group"""

    def test_valid_values(self):
        """Валидные значения проходят без изменений"""
        for group in VALID_AGE_GROUPS:
            assert validate_age_group(group) == group

    def test_none_defaults_to_adult(self):
        """None возвращает adult"""
        assert validate_age_group(None) == "adult"

    def test_invalid_defaults_to_adult(self):
        """Невалидные значения возвращают adult"""
        assert validate_age_group("banana") == "adult"
        assert validate_age_group("") == "adult"
        assert validate_age_group("KIDS") == "adult"


class TestGetGridSize:
    """Тесты get_grid_size"""

    def test_kids_easy(self):
        assert get_grid_size("kids", "easy") == (4, 4)

    def test_kids_hard(self):
        assert get_grid_size("kids", "hard") == (6, 6)

    def test_adult_hard(self):
        assert get_grid_size("adult", "hard") == (10, 10)

    def test_senior_medium(self):
        assert get_grid_size("senior", "medium") == (6, 6)

    def test_teens_all_difficulties(self):
        assert get_grid_size("teens", "easy") == (5, 5)
        assert get_grid_size("teens", "medium") == (7, 7)
        assert get_grid_size("teens", "hard") == (9, 9)

    def test_invalid_difficulty_defaults_to_medium(self):
        """Невалидная сложность возвращает medium размер"""
        assert get_grid_size("adult", "invalid") == (7, 7)


class TestGetEffectiveMaxWordLength:
    """Тесты get_effective_max_word_length"""

    def test_kids_limited_by_age(self):
        """Kids max=6, easy difficulty max=8 -> 6"""
        assert get_effective_max_word_length("kids", 8) == 6

    def test_adult_limited_by_difficulty(self):
        """Adult max=12, medium difficulty max=10 -> 10"""
        assert get_effective_max_word_length("adult", 10) == 10

    def test_equal_limits(self):
        """Одинаковые лимиты"""
        assert get_effective_max_word_length("teens", 10) == 10

    def test_hard_adult(self):
        """Adult max=12, hard difficulty max=12 -> 12"""
        assert get_effective_max_word_length("adult", 12) == 12


class TestGetWordCountRange:
    """Тесты get_word_count_range"""

    def test_4x4_grid(self):
        min_w, max_w = get_word_count_range(4, 4)
        assert min_w == 2
        assert max_w >= min_w

    def test_10x10_grid(self):
        min_w, max_w = get_word_count_range(10, 10)
        assert min_w >= 8
        assert max_w >= min_w

    def test_5x5_grid(self):
        min_w, max_w = get_word_count_range(5, 5)
        assert min_w == 3
        assert max_w >= min_w

    def test_min_always_at_least_2(self):
        """Минимум всегда >= 2"""
        min_w, _ = get_word_count_range(3, 3)
        assert min_w >= 2


class TestGetMinWordsForGrid:
    """Тесты get_min_words_for_grid"""

    def test_small_grid(self):
        assert get_min_words_for_grid(4, 4) == 2

    def test_large_grid(self):
        assert get_min_words_for_grid(10, 10) >= 8


class TestGetCategoryAgeGroups:
    """Тесты get_category_age_groups"""

    def test_direct_match(self):
        """Прямое совпадение с CATEGORY_AGE_MAP"""
        groups = get_category_age_groups("История")
        assert "teens" in groups
        assert "kids" not in groups

    def test_via_alias(self):
        """Через алиас: Наука и технологии -> Наука"""
        groups = get_category_age_groups("Наука и технологии")
        assert "teens" in groups
        assert "kids" not in groups

    def test_unknown_category_returns_all(self):
        """Неизвестная категория доступна всем"""
        groups = get_category_age_groups("Неизвестная категория")
        assert len(groups) == len(VALID_AGE_GROUPS)


class TestGetCategoryIcon:
    """Тесты get_category_icon"""

    def test_direct_match(self):
        assert get_category_icon("История") == "📜"

    def test_via_alias(self):
        assert get_category_icon("Наука и технологии") == "🧬"

    def test_unknown_returns_empty(self):
        assert get_category_icon("Неизвестная") == ""


class TestGetCategoryDescription:
    """Тесты get_category_description"""

    def test_direct_match(self):
        desc = get_category_description("История")
        assert len(desc) > 0

    def test_unknown_returns_empty(self):
        assert get_category_description("Неизвестная") == ""
