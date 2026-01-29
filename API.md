# Crossword Generator API

Base URL: `http://localhost:8080`

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

**Пример запроса:**

```bash
curl -X POST http://localhost:8080/api/crossword \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Наука и технологии",
    "difficulty": "medium",
    "excluded_ids": ["a1b2c3d4e5f67890"]
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

Возвращает список доступных категорий.

```
GET /api/categories
```

**Пример запроса:**

```bash
curl http://localhost:8080/api/categories
```

**Успешный ответ (200):**

```json
{
  "categories": [
    {
      "name": "Наука и технологии",
      "word_count": 150
    },
    {
      "name": "История",
      "word_count": 120
    },
    {
      "name": "География",
      "word_count": 95
    }
  ],
  "total": 3
}
```

---

### 3. Health Check

Проверка работоспособности API.

```
GET /api/health
```

**Пример запроса:**

```bash
curl http://localhost:8080/api/health
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

## Docker

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down
```

API будет доступен на `http://localhost:8080`
