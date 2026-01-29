"""
Crossword Generator API - REST API для генерации кроссвордов
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
import hashlib
import json
import time
import logging
import os
from dotenv import load_dotenv

from src.generator import CrosswordGenerator

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация Flask приложения
app = Flask(__name__)

# Настройка CORS
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('CORS_ORIGINS', '*').split(','),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Ограничение размера JSON payload
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB

# Глобальные настройки
DICTIONARY_PATH = os.getenv('DICTIONARY_PATH', 'data/dictionary.json')
MAX_ATTEMPTS = int(os.getenv('MAX_GENERATION_ATTEMPTS', 50))
MAX_EXCLUDED_IDS = 100  # Ограничение на размер excluded_ids

# Инициализация генератора
generator = None
try:
    generator = CrosswordGenerator(DICTIONARY_PATH)
    logger.info(f"Crossword generator initialized with dictionary: {DICTIONARY_PATH}")
except Exception as e:
    logger.error(f"Failed to initialize generator: {e}")

# Время запуска сервера
START_TIME = time.time()


def generate_crossword_id(grid: list, words: list) -> str:
    """
    Генерирует уникальный 16-символьный ID для кроссворда

    Args:
        grid: Двумерный массив сетки
        words: Список слов с позициями

    Returns:
        16-символьный hexadecimal ID
    """
    crossword_content = {
        'grid': grid,
        'words': [
            {
                'word': w['word'],
                'startRow': w['startRow'],
                'startCol': w['startCol'],
                'direction': w['direction']
            }
            for w in words
        ]
    }

    content_str = json.dumps(crossword_content, sort_keys=True, ensure_ascii=False)
    hash_object = hashlib.md5(content_str.encode('utf-8'))
    return hash_object.hexdigest()[:16]


@app.route('/api/crossword', methods=['POST'])
def get_crossword():
    """
    Генерирует новый кроссворд

    Body:
        category (str): Категория кроссворда
        difficulty (str, optional): Уровень сложности
        excluded_ids (list, optional): ID уже решённых кроссвордов
    """
    if generator is None:
        return jsonify({
            'error': 'Generator not initialized',
            'status': 500
        }), 500

    try:
        data = request.get_json()

        # Валидация обязательных полей
        if not data or 'category' not in data:
            return jsonify({
                'error': 'Category is required',
                'status': 400
            }), 400

        category = data['category']
        difficulty = data.get('difficulty', 'medium')
        excluded_ids = data.get('excluded_ids', [])

        # Валидация difficulty
        if difficulty not in ['easy', 'medium', 'hard']:
            difficulty = 'medium'

        # Ограничиваем размер excluded_ids
        if len(excluded_ids) > MAX_EXCLUDED_IDS:
            excluded_ids = excluded_ids[-MAX_EXCLUDED_IDS:]
            logger.warning(f"excluded_ids truncated to {MAX_EXCLUDED_IDS} items")

        excluded_set = set(excluded_ids)

        # Проверка существования категории
        available_categories = generator.get_categories()
        if category not in available_categories:
            return jsonify({
                'error': f"Category '{category}' not found",
                'available_categories': available_categories,
                'status': 404
            }), 404

        # Генерация с попытками избежать дубликатов
        start_time = time.time()
        crossword = None
        crossword_id = None

        for attempt in range(MAX_ATTEMPTS):
            crossword = generator.generate(category, difficulty)

            if crossword is None:
                continue

            crossword_id = generate_crossword_id(
                crossword['grid'],
                crossword['words']
            )

            # Проверяем уникальность
            if crossword_id not in excluded_set:
                generation_time = (time.time() - start_time) * 1000

                crossword['id'] = crossword_id
                crossword['metadata']['generation_time_ms'] = round(generation_time, 2)
                crossword['metadata']['attempts'] = attempt + 1

                logger.info(
                    f"Generated crossword {crossword_id} for {category} "
                    f"in {attempt + 1} attempts ({generation_time:.2f}ms)"
                )

                return jsonify(crossword), 200

        # Если не нашли уникальный за MAX_ATTEMPTS - отдаём последний
        if crossword is not None:
            generation_time = (time.time() - start_time) * 1000
            crossword['id'] = crossword_id
            crossword['metadata']['generation_time_ms'] = round(generation_time, 2)
            crossword['metadata']['attempts'] = MAX_ATTEMPTS
            crossword['metadata']['warning'] = 'Could not find unique crossword, returning duplicate'

            logger.warning(
                f"Failed to generate unique crossword after {MAX_ATTEMPTS} attempts"
            )

            return jsonify(crossword), 200

        # Не удалось сгенерировать ни одного кроссворда
        return jsonify({
            'error': f'Failed to generate crossword after {MAX_ATTEMPTS} attempts',
            'status': 500
        }), 500

    except BadRequest as e:
        logger.error(f"Bad request: {e}")
        return jsonify({
            'error': 'Invalid JSON in request body',
            'status': 400
        }), 400
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return jsonify({
            'error': str(e),
            'status': 400
        }), 400
    except Exception as e:
        logger.error(f"Error generating crossword: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'details': str(e),
            'status': 500
        }), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Возвращает список доступных категорий"""
    if generator is None:
        return jsonify({
            'error': 'Generator not initialized',
            'status': 500
        }), 500

    try:
        categories_info = generator.get_categories_info()
        return jsonify({
            'categories': categories_info,
            'total': len(categories_info)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching categories: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to fetch categories',
            'status': 500
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API"""
    uptime = time.time() - START_TIME

    health_status = {
        'status': 'ok' if generator is not None else 'error',
        'version': '1.0.0',
        'uptime_seconds': round(uptime, 2),
        'dictionary_loaded': generator is not None
    }

    if generator is not None:
        try:
            health_status['total_words'] = generator.get_total_word_count()
            health_status['categories_count'] = len(generator.get_categories())
        except Exception as e:
            logger.error(f"Error in health check: {e}")

    return jsonify(health_status), 200


@app.errorhandler(404)
def not_found(error):
    """Обработчик 404 ошибок"""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик 500 ошибок"""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'status': 500
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting Crossword API on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"CORS origins: {os.getenv('CORS_ORIGINS', '*')}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
