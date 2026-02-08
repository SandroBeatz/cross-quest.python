# Миграция API кроссвордов: v1 → v2 (MVP)

> Инструкция для бэкенда. Описывает изменения, которые нужно внести в Python API
> на Railway для поддержки возрастных групп, адаптивного контента и расширенных метаданных.

**Дата:** 07.02.2026
**Статус:** Спецификация для реализации
**Приоритет:** P0 — блокирует фронтенд MVP
**Base URL:** `https://cross-questpython-production.up.railway.app/api`

---

## Оглавление

1. [Сводка изменений](#1-сводка-изменений)
2. [Возрастные группы — справочник](#2-возрастные-группы--справочник)
3. [POST /categories — обновление](#3-post-categories--обновление)
4. [POST /crossword — обновление](#4-post-crossword--обновление)
5. [Адаптация контента по возрасту](#5-адаптация-контента-по-возрасту)
6. [Приоритеты реализации](#6-приоритеты-реализации)
7. [Обратная совместимость](#7-обратная-совместимость)
8. [Тестирование](#8-тестирование)

---

## 1. Сводка изменений

| Что меняется                                   | Текущее (v1) | Новое (v2)                             | Приоритет |
| ---------------------------------------------- | ------------ | -------------------------------------- | --------- |
| `/categories` принимает `age_group`            | Нет          | Да, опциональный                       | P0        |
| `/categories` возвращает `icon`, `description` | Нет          | Да                                     | P1        |
| `/categories` фильтрует по возрасту            | Нет          | Да, если передан `age_group`           | P0        |
| `/crossword` принимает `age_group`             | Нет          | Да, опциональный                       | P0        |
| `/crossword` адаптирует размер сетки           | Нет          | Да, по возрасту + сложности            | P0        |
| `/crossword` адаптирует словарь                | Нет          | Да, макс. длина слова по возрасту      | P0        |
| `/crossword` возвращает `age_adapted`          | Нет          | Да, boolean                            | P1        |
| `/crossword` принимает `user_progress`         | Нет          | Да, опциональный                       | P2        |
| Response metadata расширен                     | Базовый      | `vocabulary_level`, `grid_size` строка | P1        |

---

## 2. Возрастные группы — справочник

API должен знать эти группы и их параметры:

```python
AGE_GROUPS = {
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
```

**Дефолт:** если `age_group` не передан — использовать `"adult"` (поведение как сейчас).

---

## 3. POST /categories — обновление

### Текущий контракт (v1)

```
POST /api/categories
Content-Type: application/json

{
  "guessed_words": {
    "Наука": ["АТОМ", "ГЕН"],
    "История": ["ПЁТР"]
  }
}
```

**Response:**

```json
{
  "categories": [
    {
      "name": "Наука",
      "word_count": 100,
      "guessed_count": 2,
      "guessed_percent": 2.0,
      "available": true
    }
  ]
}
```

### Новый контракт (v2)

```
POST /api/categories
Content-Type: application/json

{
  "guessed_words": {"Наука": ["АТОМ", "ГЕН"]},
  "age_group": "teens"                           // <-- НОВОЕ, опциональное
}
```

**Response (расширенный):**

```json
{
  "categories": [
    {
      "name": "Наука",
      "word_count": 100,
      "guessed_count": 2,
      "guessed_percent": 2.0,
      "available": true,
      "icon": "🧬", // <-- НОВОЕ
      "description": "Биология, химия, физика", // <-- НОВОЕ
      "age_groups": ["teens", "young", "adult", "mature", "senior"] // <-- НОВОЕ
    }
  ]
}
```

### Логика фильтрации

```python
def get_categories(guessed_words, age_group=None):
    categories = load_all_categories()

    if age_group and age_group in AGE_GROUPS:
        # Фильтруем: оставляем только категории доступные для этой возрастной группы
        categories = [c for c in categories if age_group in c["age_groups"]]

    # Считаем прогресс как раньше
    for cat in categories:
        cat["guessed_count"] = len(guessed_words.get(cat["name"], []))
        cat["guessed_percent"] = (cat["guessed_count"] / cat["word_count"]) * 100

    return categories
```

### Маппинг категорий по возрастным группам

```python
CATEGORY_AGE_MAP = {
    # Категория: [доступные возрастные группы]
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

CATEGORY_ICONS = {
    "Наука": "🧬",
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
```

---

## 4. POST /crossword — обновление

### Текущий контракт (v1)

```
POST /api/crossword
Content-Type: application/json

{
  "category": "Наука",
  "difficulty": "medium",
  "excluded_words": ["АТОМ", "ГЕН"]
}
```

**Response:**

```json
{
  "id": "abc123",
  "grid": [["М","И","Т","О","З"], ...],
  "words": [
    {
      "word": "МИТОЗ",
      "clue": "Процесс деления клетки",
      "hint": "Происходит в ядре клетки",
      "startRow": 0,
      "startCol": 0,
      "direction": "horizontal",
      "length": 5
    }
  ],
  "difficulty": "medium",
  "category": "Наука",
  "metadata": {
    "word_count": 7,
    "grid_size": {"rows": 7, "cols": 7},
    "generation_time_ms": 1230,
    "attempts": 3
  }
}
```

### Новый контракт (v2)

```
POST /api/crossword
Content-Type: application/json

{
  "category": "Наука",
  "difficulty": "medium",
  "excluded_words": ["АТОМ", "ГЕН"],
  "age_group": "teens",                          // <-- НОВОЕ, опциональное
  "user_progress": {                              // <-- НОВОЕ, опциональное
    "words_in_category": 67,
    "recent_words": ["КЛЕТКА", "МИТОЗ"]
  }
}
```

**Response (расширенный):**

```json
{
  "id": "abc123",
  "grid": [["М","И","Т","О","З"], ...],
  "words": [
    {
      "word": "МИТОЗ",
      "clue": "Процесс деления клетки",
      "hint": "Происходит в ядре клетки",
      "startRow": 0,
      "startCol": 0,
      "direction": "horizontal",
      "length": 5
    }
  ],
  "difficulty": "medium",
  "category": "Наука",
  "metadata": {
    "word_count": 7,
    "grid_size": {"rows": 7, "cols": 7},
    "generation_time_ms": 1230,
    "attempts": 3,
    "vocabulary_level": "school",                 // <-- НОВОЕ
    "max_word_length": 10,                        // <-- НОВОЕ
    "age_adapted": true                           // <-- НОВОЕ
  }
}
```

### Логика адаптации при генерации

```python
def generate_crossword(category, difficulty, excluded_words, age_group=None, user_progress=None):
    # 1. Определить параметры по возрасту
    if age_group and age_group in AGE_GROUPS:
        config = AGE_GROUPS[age_group]
    else:
        config = AGE_GROUPS["adult"]  # дефолт

    grid_size = config["grid_sizes"][difficulty]     # (rows, cols)
    max_word_length = config["max_word_length"]
    vocabulary_level = config["vocabulary_level"]

    # 2. Фильтровать словарь
    words = get_words_for_category(category)
    words = [w for w in words if len(w) <= max_word_length]
    words = [w for w in words if w not in excluded_words]

    # 3. Если есть user_progress — приоритизировать новые слова
    if user_progress and user_progress.get("recent_words"):
        # Понизить приоритет недавних слов (не исключать, но ставить в конец)
        recent = set(user_progress["recent_words"])
        words.sort(key=lambda w: w in recent)

    # 4. Генерировать кроссворд с заданным grid_size
    crossword = build_crossword(
        words=words,
        rows=grid_size[0],
        cols=grid_size[1],
        difficulty=difficulty,
    )

    # 5. Добавить метаданные адаптации
    crossword["metadata"]["vocabulary_level"] = vocabulary_level
    crossword["metadata"]["max_word_length"] = max_word_length
    crossword["metadata"]["age_adapted"] = age_group is not None

    return crossword
```

### Таблица размеров сеток

| Возраст \ Сложность | easy    | medium  | hard      |
| ------------------- | ------- | ------- | --------- |
| kids (до 12)        | **4x4** | **5x5** | **6x6**   |
| teens (13-17)       | 5x5     | **7x7** | **9x9**   |
| young (18-25)       | 5x5     | 7x7     | **10x10** |
| adult (26-40)       | 5x5     | 7x7     | 10x10     |
| mature (41-60)      | 5x5     | 7x7     | 10x10     |
| senior (60+)        | 5x5     | **6x6** | **8x8**   |

### Ограничения длины слов

| Возраст              | Макс. длина слова |
| -------------------- | ----------------- |
| kids                 | 6 букв            |
| teens                | 10 букв           |
| young, adult, mature | 12 букв           |
| senior               | 10 букв           |

---

## 5. Адаптация контента по возрасту

### Стиль вопросов (clue)

| Группа        | Стиль                 | Пример (слово: АТОМ)                                                    |
| ------------- | --------------------- | ----------------------------------------------------------------------- |
| kids          | Простой, короткий     | "Самая маленькая частичка вещества"                                     |
| teens         | Понятный, с примерами | "Мельчайшая частица химического элемента. Состоит из ядра и электронов" |
| young/adult   | Академический         | "Наименьшая единица химического элемента, сохраняющая его свойства"     |
| mature/senior | Классический          | "Мельчайшая частица вещества. Термин ввёл Демокрит"                     |

### Стиль подсказок (hint)

| Группа | Стиль                     | Пример                                                              |
| ------ | ------------------------- | ------------------------------------------------------------------- |
| kids   | Очень простой, ободряющий | "Подумай, из чего состоит всё вокруг! Ты справишься!"               |
| teens  | Намёк с контекстом        | "Вспомни уроки химии — из чего состоят молекулы?"                   |
| adult  | Лаконичный                | "Элементарная частица. Состоит из протонов, нейтронов и электронов" |
| senior | Подробный, с историей     | "Греческое слово 'неделимый'. Открыт в начале XX века"              |

---

## 6. Приоритеты реализации

### Фаза 1 — Критический путь (блокирует фронтенд)

Без этого фронтенд не может завершить MVP.

| #   | Задача                                                  | Эндпоинт         | Описание                                                                  |
| --- | ------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------- |
| 1   | Принять `age_group` в `/categories`                     | POST /categories | Новое опциональное поле в body. Игнорировать если не передано.            |
| 2   | Фильтровать категории по `age_group`                    | POST /categories | Если `age_group` передан — вернуть только категории из `CATEGORY_AGE_MAP` |
| 3   | Принять `age_group` в `/crossword`                      | POST /crossword  | Новое опциональное поле в body                                            |
| 4   | Адаптировать размер сетки по `age_group` + `difficulty` | POST /crossword  | Использовать таблицу `grid_sizes` из AGE_GROUPS                           |
| 5   | Ограничить длину слов по `age_group`                    | POST /crossword  | `max_word_length` из AGE_GROUPS                                           |

### Фаза 2 — Метаданные и UX

| #   | Задача                                               | Эндпоинт         | Описание                       |
| --- | ---------------------------------------------------- | ---------------- | ------------------------------ |
| 6   | Добавить `icon` и `description` к категориям         | POST /categories | Из `CATEGORY_ICONS` + описания |
| 7   | Добавить `age_groups` к каждой категории             | POST /categories | Из `CATEGORY_AGE_MAP`          |
| 8   | Вернуть `vocabulary_level`, `age_adapted` в metadata | POST /crossword  | Для аналитики на фронтенде     |

### Фаза 3 — Контекст пользователя

| #   | Задача                                                | Эндпоинт        | Описание                        |
| --- | ----------------------------------------------------- | --------------- | ------------------------------- |
| 9   | Принять `user_progress` в `/crossword`                | POST /crossword | Для умного выбора слов          |
| 10  | Приоритизировать новые слова на основе `recent_words` | POST /crossword | Уменьшить повторы               |
| 11  | Адаптировать стиль вопросов по `age_group`            | POST /crossword | Разный тон для разных возрастов |

---

## 7. Обратная совместимость

### Критически важно

Все изменения должны быть **обратно совместимы**. Фронтенд обновится позже бэкенда.

| Правило                       | Описание                                                                           |
| ----------------------------- | ---------------------------------------------------------------------------------- |
| `age_group` опционален        | Если не передан — поведение как сейчас (дефолт `"adult"`)                          |
| `user_progress` опционален    | Если не передан — генерация как раньше                                             |
| Новые поля в response         | Добавляются поверх существующих. Существующие поля НЕ меняются и НЕ удаляются      |
| Формат `words[]` не меняется  | Сохраняем `word`, `clue`, `hint`, `startRow`, `startCol`, `direction`, `length`    |
| Формат `grid[][]` не меняется | Двумерный массив строк                                                             |
| `metadata` расширяется        | Старые поля (`word_count`, `grid_size`, `generation_time_ms`, `attempts`) остаются |

### Что НЕ НАДО делать

- НЕ менять URL эндпоинтов (`/api/categories` и `/api/crossword` остаются)
- НЕ менять метод (POST остаётся для обоих)
- НЕ менять формат `guessed_words` в `/categories`
- НЕ менять формат `excluded_words` в `/crossword`
- НЕ менять структуру `Word` объекта в response
- НЕ менять формат `grid` в response
- НЕ удалять поле `name` из категорий (даже если добавляется `id`)

### Валидация age_group

```python
VALID_AGE_GROUPS = {"kids", "teens", "young", "adult", "mature", "senior"}

def validate_age_group(age_group):
    if age_group is None:
        return "adult"  # дефолт
    if age_group not in VALID_AGE_GROUPS:
        return "adult"  # невалидное значение — дефолт, не ошибка
    return age_group
```

**Не возвращать ошибку** при невалидном `age_group`. Просто использовать дефолт.

---

## 8. Тестирование

### Чеклист для ручного тестирования

#### /categories

```bash
# Без age_group (обратная совместимость)
curl -X POST https://cross-questpython-production.up.railway.app/api/categories \
  -H "Content-Type: application/json" \
  -d '{"guessed_words":{}}'
# Ожидание: все категории, как раньше

# С age_group=kids
curl -X POST https://cross-questpython-production.up.railway.app/api/categories \
  -H "Content-Type: application/json" \
  -d '{"guessed_words":{}, "age_group":"kids"}'
# Ожидание: только детские категории (Животные, Еда, Спорт, Транспорт, Цвета, Творчество)

# С age_group=senior
curl -X POST https://cross-questpython-production.up.railway.app/api/categories \
  -H "Content-Type: application/json" \
  -d '{"guessed_words":{}, "age_group":"senior"}'
# Ожидание: стандартные + специальные категории (Советское кино, Классическая литература и т.д.)

# С невалидным age_group
curl -X POST https://cross-questpython-production.up.railway.app/api/categories \
  -H "Content-Type: application/json" \
  -d '{"guessed_words":{}, "age_group":"invalid"}'
# Ожидание: все категории (дефолт adult), НЕ ошибка
```

#### /crossword

```bash
# Без age_group (обратная совместимость)
curl -X POST https://cross-questpython-production.up.railway.app/api/crossword \
  -H "Content-Type: application/json" \
  -d '{"category":"Наука", "difficulty":"medium", "excluded_words":[]}'
# Ожидание: кроссворд 7x7 (adult дефолт), как раньше

# С age_group=kids + easy
curl -X POST https://cross-questpython-production.up.railway.app/api/crossword \
  -H "Content-Type: application/json" \
  -d '{"category":"Животные", "difficulty":"easy", "excluded_words":[], "age_group":"kids"}'
# Ожидание: кроссворд 4x4, слова <= 6 букв

# С age_group=teens + hard
curl -X POST https://cross-questpython-production.up.railway.app/api/crossword \
  -H "Content-Type: application/json" \
  -d '{"category":"Наука", "difficulty":"hard", "excluded_words":[], "age_group":"teens"}'
# Ожидание: кроссворд 9x9, слова <= 10 букв
```

### Автотесты (рекомендуемые)

```python
def test_categories_without_age_group():
    """Обратная совместимость: без age_group возвращает все категории"""
    response = client.post("/api/categories", json={"guessed_words": {}})
    assert response.status_code == 200
    assert len(response.json()["categories"]) > 0

def test_categories_kids_filter():
    """Kids видят только детские категории"""
    response = client.post("/api/categories", json={"guessed_words": {}, "age_group": "kids"})
    categories = response.json()["categories"]
    names = [c["name"] for c in categories]
    assert "Животные" in names
    assert "Право" not in names
    assert "Политика" not in names

def test_categories_senior_has_special():
    """Seniors видят специальные категории"""
    response = client.post("/api/categories", json={"guessed_words": {}, "age_group": "senior"})
    names = [c["name"] for c in response.json()["categories"]]
    assert "Советское кино" in names or "Классическая литература" in names

def test_crossword_kids_grid_size():
    """Kids easy = 4x4 сетка"""
    response = client.post("/api/crossword", json={
        "category": "Животные", "difficulty": "easy",
        "excluded_words": [], "age_group": "kids"
    })
    grid = response.json()["grid"]
    assert len(grid) == 4
    assert len(grid[0]) == 4

def test_crossword_kids_word_length():
    """Kids: все слова <= 6 букв"""
    response = client.post("/api/crossword", json={
        "category": "Животные", "difficulty": "medium",
        "excluded_words": [], "age_group": "kids"
    })
    words = response.json()["words"]
    for w in words:
        assert len(w["word"]) <= 6

def test_crossword_backward_compatible():
    """Без age_group — работает как раньше"""
    response = client.post("/api/crossword", json={
        "category": "Наука", "difficulty": "medium", "excluded_words": []
    })
    assert response.status_code == 200
    assert "grid" in response.json()
    assert "words" in response.json()

def test_invalid_age_group_not_error():
    """Невалидный age_group — не ошибка, дефолт adult"""
    response = client.post("/api/categories", json={
        "guessed_words": {}, "age_group": "banana"
    })
    assert response.status_code == 200
```

---

## Диаграмма изменений

```
Фронтенд (Next.js)                       Бэкенд (Python/Railway)
─────────────────                         ──────────────────────

                    POST /categories
profile.ageGroup ──→ { age_group: "teens",  ──→ Фильтрация по
                      guessed_words: {} }       CATEGORY_AGE_MAP
                                            ──→ Добавить icon,
                                                description,
                                                age_groups[]
                    ←── categories[] ────────

                    POST /crossword
profile.ageGroup ──→ { age_group: "teens",  ──→ Выбрать grid_size
                      category: "Наука",        по AGE_GROUPS
                      difficulty: "medium",  ──→ Ограничить словарь
                      excluded_words: [],       max_word_length
                      user_progress: {...} } ──→ Приоритизировать
                                                новые слова
                    ←── crossword data ─────
                        + metadata.age_adapted
                        + metadata.vocabulary_level
```
