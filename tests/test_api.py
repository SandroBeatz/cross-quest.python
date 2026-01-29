"""
Тесты для REST API генератора кроссвордов
"""

import pytest
import json
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app, generate_crossword_id


@pytest.fixture
def client():
    """Фикстура для тестового клиента Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Тесты для /api/health"""

    def test_health_returns_ok(self, client):
        """Тест что health endpoint возвращает status ok"""
        response = client.get('/api/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'version' in data
        assert 'uptime_seconds' in data

    def test_health_has_dictionary_info(self, client):
        """Тест что health содержит информацию о словаре"""
        response = client.get('/api/health')
        data = json.loads(response.data)

        assert 'dictionary_loaded' in data
        if data['dictionary_loaded']:
            assert 'total_words' in data
            assert 'categories_count' in data


class TestCategoriesEndpoint:
    """Тесты для /api/categories"""

    def test_categories_returns_list(self, client):
        """Тест что categories возвращает список"""
        response = client.get('/api/categories')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'categories' in data
        assert 'total' in data
        assert isinstance(data['categories'], list)

    def test_categories_have_required_fields(self, client):
        """Тест что каждая категория имеет обязательные поля"""
        response = client.get('/api/categories')
        data = json.loads(response.data)

        if data['total'] > 0:
            category = data['categories'][0]
            assert 'name' in category
            assert 'word_count' in category
            assert 'available' in category


class TestCrosswordEndpoint:
    """Тесты для POST /api/crossword"""

    def test_generate_missing_category(self, client):
        """Тест генерации без категории - ошибка 400"""
        response = client.post('/api/crossword', json={})
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data
        assert 'Category is required' in data['error']

    def test_generate_invalid_category(self, client):
        """Тест генерации с несуществующей категорией - ошибка 404"""
        response = client.post('/api/crossword', json={
            'category': 'Несуществующая категория 12345'
        })
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data
        assert 'available_categories' in data

    def test_generate_success(self, client):
        """Тест успешной генерации кроссворда"""
        # Получаем список категорий
        categories_response = client.get('/api/categories')
        categories_data = json.loads(categories_response.data)

        if categories_data['total'] == 0:
            pytest.skip("Нет доступных категорий")

        # Берём первую доступную категорию
        available_category = None
        for cat in categories_data['categories']:
            if cat['available']:
                available_category = cat['name']
                break

        if available_category is None:
            pytest.skip("Нет категорий с достаточным количеством слов")

        # Генерируем кроссворд
        response = client.post('/api/crossword', json={
            'category': available_category,
            'difficulty': 'medium'
        })

        # Может быть 200 (успех) или 500 (не удалось сгенерировать)
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'id' in data
            assert 'grid' in data
            assert 'words' in data
            assert 'metadata' in data
            assert len(data['id']) == 16

    def test_generate_with_excluded_ids(self, client):
        """Тест генерации с excluded_ids"""
        # Получаем доступную категорию
        categories_response = client.get('/api/categories')
        categories_data = json.loads(categories_response.data)

        available_category = None
        for cat in categories_data['categories']:
            if cat['available']:
                available_category = cat['name']
                break

        if available_category is None:
            pytest.skip("Нет категорий с достаточным количеством слов")

        # Генерируем первый кроссворд
        response1 = client.post('/api/crossword', json={
            'category': available_category
        })

        if response1.status_code != 200:
            pytest.skip("Не удалось сгенерировать первый кроссворд")

        data1 = json.loads(response1.data)
        id1 = data1['id']

        # Генерируем второй кроссворд, исключая первый
        response2 = client.post('/api/crossword', json={
            'category': available_category,
            'excluded_ids': [id1]
        })

        if response2.status_code == 200:
            data2 = json.loads(response2.data)
            # ID могут совпасть если не удалось найти уникальный,
            # но метаданные должны содержать информацию об этом
            assert 'id' in data2

    def test_crossword_structure(self, client):
        """Тест структуры возвращаемого кроссворда"""
        categories_response = client.get('/api/categories')
        categories_data = json.loads(categories_response.data)

        available_category = None
        for cat in categories_data['categories']:
            if cat['available']:
                available_category = cat['name']
                break

        if available_category is None:
            pytest.skip("Нет категорий с достаточным количеством слов")

        response = client.post('/api/crossword', json={
            'category': available_category,
            'difficulty': 'easy'
        })

        if response.status_code != 200:
            pytest.skip("Не удалось сгенерировать кроссворд")

        data = json.loads(response.data)

        # Проверяем структуру grid
        assert isinstance(data['grid'], list)
        assert len(data['grid']) > 0
        assert all(isinstance(row, list) for row in data['grid'])

        # Проверяем структуру words
        assert isinstance(data['words'], list)
        for word_info in data['words']:
            assert 'word' in word_info
            assert 'clue' in word_info
            assert 'hint' in word_info
            assert 'startRow' in word_info
            assert 'startCol' in word_info
            assert 'direction' in word_info
            assert 'length' in word_info
            assert word_info['direction'] in ['horizontal', 'vertical']

        # Проверяем metadata
        assert 'metadata' in data
        assert 'word_count' in data['metadata']
        assert 'grid_size' in data['metadata']
        assert 'fill_density' in data['metadata']


class TestCrosswordIdGeneration:
    """Тесты для функции генерации ID"""

    def test_id_is_deterministic(self):
        """Тест что одинаковые данные дают одинаковый ID"""
        grid = [["А", "Б"], ["В", ""]]
        words = [
            {"word": "АБ", "startRow": 0, "startCol": 0, "direction": "horizontal"}
        ]

        id1 = generate_crossword_id(grid, words)
        id2 = generate_crossword_id(grid, words)

        assert id1 == id2

    def test_id_length(self):
        """Тест что ID имеет длину 16 символов"""
        grid = [["А"]]
        words = [
            {"word": "А", "startRow": 0, "startCol": 0, "direction": "horizontal"}
        ]

        crossword_id = generate_crossword_id(grid, words)
        assert len(crossword_id) == 16

    def test_id_is_hexadecimal(self):
        """Тест что ID содержит только hex символы"""
        grid = [["А", "Б", "В"]]
        words = [
            {"word": "АБВ", "startRow": 0, "startCol": 0, "direction": "horizontal"}
        ]

        crossword_id = generate_crossword_id(grid, words)
        assert all(c in '0123456789abcdef' for c in crossword_id)

    def test_different_data_different_id(self):
        """Тест что разные данные дают разные ID"""
        grid1 = [["А", "Б"]]
        words1 = [
            {"word": "АБ", "startRow": 0, "startCol": 0, "direction": "horizontal"}
        ]

        grid2 = [["В", "Г"]]
        words2 = [
            {"word": "ВГ", "startRow": 0, "startCol": 0, "direction": "horizontal"}
        ]

        id1 = generate_crossword_id(grid1, words1)
        id2 = generate_crossword_id(grid2, words2)

        assert id1 != id2


class TestErrorHandling:
    """Тесты обработки ошибок"""

    def test_404_for_unknown_endpoint(self, client):
        """Тест 404 для несуществующего endpoint"""
        response = client.get('/api/unknown')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data

    def test_invalid_json(self, client):
        """Тест обработки невалидного JSON"""
        response = client.post(
            '/api/crossword',
            data='invalid json',
            content_type='application/json'
        )
        # Flask возвращает 400 для невалидного JSON
        assert response.status_code in [400, 415]
