# Crossword Generator API

**Production:** `https://cross-questpython-production.up.railway.app`

**Local:** `http://localhost:8080`

---

## Endpoints

### 1. Generate Crossword

Генерирует новый кроссворд для указанной категории.

```
POST /api/crossword
```

**Request Body:**

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `category` | string | да | Название категории |
| `difficulty` | string | нет | Сложность: `easy`, `medium`, `hard`. По умолчанию `medium` |
| `excluded_ids` | string[] | нет | ID уже решённых кроссвордов (макс. 100) |
| `excluded_words` | string[] | нет | Слова для исключения из генерации (макс. 500) |

**Пример запроса:**

```bash
curl -X POST https://cross-questpython-production.up.railway.app/api/crossword \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Наука и технологии",
    "difficulty": "medium",
    "excluded_ids": ["a1b2c3d4e5f67890"],
    "excluded_words": ["АТОМ", "ЛАЗЕР", "РОБОТ"]
  }'
```

**Успешный ответ (200):**

```json
{
  "id": "a1b2c3d4e5f67890",
  "grid": [
    ["А", "Т", "О", "М", "", "", "", ""],
    ["", "", "", "О", "", "", "", ""],
    ["", "", "", "Л", "А", "З", "Е", "Р"],
    ["", "", "", "Е", "", "", "", ""],
    ["", "", "", "К", "", "", "", ""],
    ["", "", "", "У", "", "", "", ""],
    ["", "", "", "Л", "", "", "", ""],
    ["", "", "", "А", "", "", "", ""]
  ],
  "words": [
    {
      "word": "АТОМ",
      "clue": "Наименьшая частица химического элемента",
      "hint": "Состоит из протонов, нейтронов и электронов",
      "startRow": 0,
      "startCol": 0,
      "direction": "horizontal",
      "length": 4
    },
    {
      "word": "МОЛЕКУЛА",
      "clue": "Группа атомов, связанных химическими связями",
      "hint": "Наименьшая частица вещества",
      "startRow": 0,
      "startCol": 3,
      "direction": "vertical",
      "length": 8
    },
    {
      "word": "ЛАЗЕР",
      "clue": "Источник когерентного излучения",
      "hint": "Используется в указках и принтерах",
      "startRow": 2,
      "startCol": 3,
      "direction": "horizontal",
      "length": 5
    }
  ],
  "difficulty": "medium",
  "category": "Наука и технологии",
  "metadata": {
    "word_count": 3,
    "grid_size": {
      "rows": 8,
      "cols": 8
    },
    "generation_time_ms": 45.23,
    "attempts": 1
  }
}
```

**Ошибки:**

| Код | Причина |
|-----|---------|
| 400 | Отсутствует `category` или невалидный JSON |
| 404 | Категория не найдена |
| 500 | Ошибка генерации |

---

### 2. Get Categories

Возвращает список доступных категорий с опциональным прогрессом.

```
GET /api/categories
POST /api/categories
```

**Request Body (только для POST):**

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `guessed_words` | object | нет | Отгаданные слова по категориям: `{category: [слова]}` |

**Пример GET запроса:**

```bash
curl https://cross-questpython-production.up.railway.app/api/categories
```

**Пример POST запроса (с прогрессом):**

```bash
curl -X POST https://cross-questpython-production.up.railway.app/api/categories \
  -H "Content-Type: application/json" \
  -d '{
    "guessed_words": {
      "Наука и технологии": ["АТОМ", "ЛАЗЕР"],
      "История": ["ЦАРЬ"]
    }
  }'
```

**Успешный ответ (200):**

```json
{
  "categories": [
    {
      "name": "Наука и технологии",
      "word_count": 150,
      "available": true,
      "guessed_count": 2,
      "guessed_percent": 1.3
    },
    {
      "name": "История",
      "word_count": 120,
      "available": true,
      "guessed_count": 1,
      "guessed_percent": 0.8
    },
    {
      "name": "География",
      "word_count": 95,
      "available": true,
      "guessed_count": 0,
      "guessed_percent": 0
    }
  ],
  "total": 3
}
```

| Поле | Описание |
|------|----------|
| `word_count` | Общее количество слов в категории |
| `available` | Доступна ли категория для генерации (≥50 слов) |
| `guessed_count` | Количество отгаданных слов |
| `guessed_percent` | Процент отгаданных слов |

---

### 3. Health Check

Проверка работоспособности API.

```
GET /api/health
```

**Пример запроса:**

```bash
curl https://cross-questpython-production.up.railway.app/api/health
```

**Успешный ответ (200):**

```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "dictionary_loaded": true,
  "total_words": 500,
  "categories_count": 5
}
```

---

## Типы данных

### Word

```typescript
interface Word {
  word: string;           // Слово (uppercase)
  clue: string;           // Определение/вопрос
  hint: string;           // Подсказка
  startRow: number;       // Строка начала (0-indexed)
  startCol: number;       // Колонка начала (0-indexed)
  direction: "horizontal" | "vertical";
  length: number;         // Длина слова
}
```

### Grid

```typescript
type Grid = string[][];   // 2D массив символов, "" для пустых ячеек
```

### Difficulty

```typescript
type Difficulty = "easy" | "medium" | "hard";
```

| Уровень | Слов | Длина слов |
|---------|------|------------|
| easy | 8-10 | 4-8 букв |
| medium | 10-12 | 3-10 букв |
| hard | 12-15 | 3-12 букв |

---

## CORS

API поддерживает CORS для всех origins (`*`).

Разрешённые методы: `GET`, `POST`, `OPTIONS`

---

## Локальный запуск (Docker)

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down
```

Локально API будет доступен на `http://localhost:8080`
