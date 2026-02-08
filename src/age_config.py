"""
Конфигурация возрастных групп для API v2
"""

from typing import Dict, List, Optional, Tuple


# Определения возрастных групп
AGE_GROUPS: Dict[str, dict] = {
    "kids": {
        "label": "До 12 лет",
        "max_word_length": 6,
        "grid_sizes": {"easy": (4, 4), "medium": (5, 5), "hard": (6, 6)},
        "vocabulary_level": "basic",
    },
    "teens": {
        "label": "13-17 лет",
        "max_word_length": 10,
        "grid_sizes": {"easy": (5, 5), "medium": (7, 7), "hard": (9, 9)},
        "vocabulary_level": "school",
    },
    "young": {
        "label": "18-25 лет",
        "max_word_length": 12,
        "grid_sizes": {"easy": (5, 5), "medium": (7, 7), "hard": (10, 10)},
        "vocabulary_level": "full",
    },
    "adult": {
        "label": "26-40 лет",
        "max_word_length": 12,
        "grid_sizes": {"easy": (5, 5), "medium": (7, 7), "hard": (10, 10)},
        "vocabulary_level": "academic",
    },
    "mature": {
        "label": "41-60 лет",
        "max_word_length": 12,
        "grid_sizes": {"easy": (5, 5), "medium": (7, 7), "hard": (10, 10)},
        "vocabulary_level": "full",
    },
    "senior": {
        "label": "60+ лет",
        "max_word_length": 10,
        "grid_sizes": {"easy": (5, 5), "medium": (6, 6), "hard": (8, 8)},
        "vocabulary_level": "classic",
    },
}

VALID_AGE_GROUPS = set(AGE_GROUPS.keys())
DEFAULT_AGE_GROUP = "adult"

# Маппинг категорий на возрастные группы (из спеки)
CATEGORY_AGE_MAP: Dict[str, List[str]] = {
    "Животные":          ["kids", "teens"],
    "Цвета и формы":     ["kids"],
    "Еда":               ["kids", "teens", "young", "adult", "mature", "senior"],
    "Транспорт":         ["kids", "teens"],
    "Творчество":        ["kids", "teens"],

    "Наука":             ["teens", "young", "adult", "mature", "senior"],
    "История":           ["teens", "young", "adult", "mature", "senior"],
    "География":         ["teens", "young", "adult", "mature", "senior"],
    "Литература":        ["teens", "young", "adult", "mature", "senior"],
    "Искусство":         ["teens", "young", "adult", "mature", "senior"],
    "Спорт":             ["kids", "teens", "young", "adult", "mature", "senior"],
    "Музыка":            ["teens", "young", "adult", "mature", "senior"],

    "Кино и культура":   ["teens", "young", "adult", "mature", "senior"],
    "Технологии":        ["teens", "young", "adult", "mature"],
    "Экономика":         ["young", "adult", "mature"],
    "Право":             ["adult", "mature"],
    "Политика":          ["adult", "mature"],
    "Кулинария":         ["young", "adult", "mature", "senior"],

    "Природа и садоводство":       ["mature", "senior"],
    "Советское кино":              ["senior"],
    "Классическая литература":     ["senior"],
    "Классическая музыка":         ["senior"],
    "История СССР/России":         ["senior"],
    "Садоводство и огородничество": ["senior"],
    "Живопись и скульптура":       ["senior"],
}

CATEGORY_ICONS: Dict[str, str] = {
    "Наука": "🧬",
    "Наука и технологии": "🧬",
    "Искусство": "🎭",
    "История": "📜",
    "География": "🌍",
    "Спорт": "⚽",
    "Музыка": "🎵",
    "Кино и культура": "🎬",
    "Технологии": "💻",
    "Экономика": "💼",
    "Литература": "📚",
    "Право": "⚖️",
    "Политика": "🏛️",
    "Кулинария": "🍷",
    "Животные": "🐾",
    "Цвета и формы": "🌈",
    "Еда": "🍎",
    "Транспорт": "🚗",
    "Творчество": "🎨",
    "Природа и садоводство": "🌿",
    "Советское кино": "📺",
    "Классическая литература": "📖",
    "Классическая музыка": "🎼",
    "История СССР/России": "🏛️",
    "Садоводство и огородничество": "🌾",
    "Живопись и скульптура": "🎨",
}

CATEGORY_DESCRIPTIONS: Dict[str, str] = {
    "Наука": "Биология, химия, физика",
    "Наука и технологии": "Биология, химия, физика и технологии",
    "История": "Исторические события и личности",
    "География": "Страны, города, природные объекты",
    "Литература": "Писатели и произведения",
    "Искусство": "Живопись, театр, архитектура",
    "Спорт": "Виды спорта и соревнования",
    "Музыка": "Жанры, инструменты, исполнители",
    "Кино и культура": "Фильмы, режиссёры, культура",
    "Технологии": "IT, гаджеты, интернет",
    "Экономика": "Финансы, бизнес, торговля",
    "Право": "Законы и юриспруденция",
    "Политика": "Государство и политические системы",
    "Кулинария": "Блюда, продукты, кухни мира",
    "Животные": "Домашние и дикие животные",
    "Цвета и формы": "Цвета, фигуры, узоры",
    "Еда": "Фрукты, овощи, продукты",
    "Транспорт": "Машины, поезда, самолёты",
    "Творчество": "Рисование, лепка, поделки",
    "Природа и садоводство": "Растения, сад, природа",
    "Советское кино": "Классика советского кинематографа",
    "Классическая литература": "Русская и мировая классика",
    "Классическая музыка": "Композиторы и произведения",
    "История СССР/России": "Советский период и история России",
    "Садоводство и огородничество": "Выращивание растений и уход за садом",
    "Живопись и скульптура": "Художники и их произведения",
}

# Маппинг имён из словаря на имена из спеки
# Решает проблему: в словаре "Наука и технологии", в спеке "Наука"
DICTIONARY_TO_SPEC_NAME: Dict[str, str] = {
    "Наука и технологии": "Наука",
}


def validate_age_group(age_group: Optional[str]) -> str:
    """Валидация и нормализация age_group, дефолт 'adult'."""
    if age_group is None or age_group not in VALID_AGE_GROUPS:
        return DEFAULT_AGE_GROUP
    return age_group


def get_grid_size(age_group: str, difficulty: str) -> Tuple[int, int]:
    """Возвращает (height, width) для age_group и difficulty."""
    config = AGE_GROUPS.get(age_group, AGE_GROUPS[DEFAULT_AGE_GROUP])
    return config["grid_sizes"].get(difficulty, config["grid_sizes"]["medium"])


def get_effective_max_word_length(age_group: str, difficulty_max: int) -> int:
    """Эффективная макс. длина слова: min от лимита возраста и сложности."""
    config = AGE_GROUPS.get(age_group, AGE_GROUPS[DEFAULT_AGE_GROUP])
    return min(config["max_word_length"], difficulty_max)


def get_word_count_range(grid_height: int, grid_width: int) -> Tuple[int, int]:
    """Диапазон количества слов на основе площади сетки."""
    area = grid_height * grid_width
    min_words = max(2, area // 8)
    max_words = max(min_words + 1, area // 4)
    return (min_words, max_words)


def get_min_words_for_grid(grid_height: int, grid_width: int) -> int:
    """Минимум слов для валидации на основе размера сетки."""
    area = grid_height * grid_width
    return max(2, area // 8)


def get_category_age_groups(category_name: str) -> List[str]:
    """Возрастные группы для категории (с поддержкой алиасов)."""
    # Прямой поиск
    if category_name in CATEGORY_AGE_MAP:
        return CATEGORY_AGE_MAP[category_name]
    # Через алиас (имя из словаря -> имя из спеки)
    spec_name = DICTIONARY_TO_SPEC_NAME.get(category_name)
    if spec_name and spec_name in CATEGORY_AGE_MAP:
        return CATEGORY_AGE_MAP[spec_name]
    # Дефолт: доступна всем группам
    return list(VALID_AGE_GROUPS)


def get_category_icon(category_name: str) -> str:
    """Иконка для категории с фоллбеком."""
    if category_name in CATEGORY_ICONS:
        return CATEGORY_ICONS[category_name]
    spec_name = DICTIONARY_TO_SPEC_NAME.get(category_name)
    if spec_name and spec_name in CATEGORY_ICONS:
        return CATEGORY_ICONS[spec_name]
    return ""


def get_category_description(category_name: str) -> str:
    """Описание категории с фоллбеком."""
    if category_name in CATEGORY_DESCRIPTIONS:
        return CATEGORY_DESCRIPTIONS[category_name]
    spec_name = DICTIONARY_TO_SPEC_NAME.get(category_name)
    if spec_name and spec_name in CATEGORY_DESCRIPTIONS:
        return CATEGORY_DESCRIPTIONS[spec_name]
    return ""
