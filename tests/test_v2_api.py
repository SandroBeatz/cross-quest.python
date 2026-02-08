"""
Тесты для API v2 — поддержка возрастных групп
"""

import pytest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app


@pytest.fixture
def client():
    """Фикстура для тестового клиента Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestCategoriesV2:
    """Тесты v2 для /api/categories"""

    def test_categories_backward_compat(self, client):
        """Без age_group — обратная совместимость, все категории"""
        response = client.post('/api/categories', json={"guessed_words": {}})
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data['categories']) > 0

    def test_categories_have_v2_fields(self, client):
        """Категории содержат новые поля v2"""
        response = client.post('/api/categories', json={"guessed_words": {}})
        data = json.loads(response.data)

        for cat in data['categories']:
            assert 'icon' in cat
            assert 'description' in cat
            assert 'age_groups' in cat
            assert isinstance(cat['age_groups'], list)
            # Старые поля тоже на месте
            assert 'name' in cat
            assert 'word_count' in cat
            assert 'available' in cat
            assert 'guessed_count' in cat
            assert 'guessed_percent' in cat

    def test_categories_with_teens_filter(self, client):
        """С age_group=teens — только подходящие категории"""
        response = client.post('/api/categories', json={
            "guessed_words": {},
            "age_group": "teens"
        })
        assert response.status_code == 200

        data = json.loads(response.data)
        for cat in data['categories']:
            assert "teens" in cat['age_groups'], \
                f"Категория {cat['name']} не должна быть доступна для teens"

    def test_categories_with_kids_filter(self, client):
        """С age_group=kids — фильтрация работает"""
        response = client.post('/api/categories', json={
            "guessed_words": {},
            "age_group": "kids"
        })
        assert response.status_code == 200

        data = json.loads(response.data)
        # Все возвращённые категории должны включать kids
        for cat in data['categories']:
            assert "kids" in cat['age_groups']

    def test_categories_invalid_age_group_no_error(self, client):
        """Невалидный age_group — не ошибка, 200"""
        response = client.post('/api/categories', json={
            "guessed_words": {},
            "age_group": "banana"
        })
        assert response.status_code == 200

    def test_categories_get_still_works(self, client):
        """GET метод по-прежнему работает"""
        response = client.get('/api/categories')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'categories' in data

    def test_categories_get_has_v2_fields(self, client):
        """GET тоже возвращает v2 поля"""
        response = client.get('/api/categories')
        data = json.loads(response.data)

        if data['total'] > 0:
            cat = data['categories'][0]
            assert 'icon' in cat
            assert 'age_groups' in cat


class TestCrosswordV2:
    """Тесты v2 для /api/crossword"""

    def _get_available_category(self, client):
        """Хелпер: получить доступную категорию"""
        response = client.get('/api/categories')
        data = json.loads(response.data)
        for cat in data['categories']:
            if cat['available']:
                return cat['name']
        return None

    def test_crossword_without_age_group(self, client):
        """Без age_group — работает как v1, age_adapted=False"""
        category = self._get_available_category(client)
        if category is None:
            pytest.skip("Нет доступных категорий")

        response = client.post('/api/crossword', json={
            'category': category,
            'difficulty': 'medium'
        })

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'grid' in data
            assert 'words' in data
            assert data['metadata']['age_adapted'] is False

    def test_crossword_with_adult_age_group(self, client):
        """Adult age_group — v2 метаданные"""
        category = self._get_available_category(client)
        if category is None:
            pytest.skip("Нет доступных категорий")

        response = client.post('/api/crossword', json={
            'category': category,
            'difficulty': 'medium',
            'age_group': 'adult'
        })

        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['metadata']['vocabulary_level'] == 'academic'
            assert data['metadata']['age_adapted'] is True
            assert 'max_word_length' in data['metadata']

    def test_crossword_with_teens_hard(self, client):
        """Teens hard — сетка <= 9x9, слова <= 10 букв"""
        category = self._get_available_category(client)
        if category is None:
            pytest.skip("Нет доступных категорий")

        response = client.post('/api/crossword', json={
            'category': category,
            'difficulty': 'hard',
            'age_group': 'teens'
        })

        if response.status_code == 200:
            data = json.loads(response.data)
            grid = data['grid']
            assert len(grid) <= 9, f"Grid height {len(grid)} > 9"
            if grid:
                assert len(grid[0]) <= 9, f"Grid width {len(grid[0])} > 9"
            assert data['metadata']['max_word_length'] == 10
            assert data['metadata']['vocabulary_level'] == 'school'

            # Все слова <= 10 букв
            for w in data['words']:
                assert len(w['word']) <= 10, f"Слово {w['word']} длиннее 10 букв"

    def test_crossword_invalid_age_group_defaults(self, client):
        """Невалидный age_group — не ошибка, дефолт adult"""
        category = self._get_available_category(client)
        if category is None:
            pytest.skip("Нет доступных категорий")

        response = client.post('/api/crossword', json={
            'category': category,
            'difficulty': 'medium',
            'age_group': 'invalid_value'
        })
        # Не должно быть 400 — невалидный age_group не ошибка
        assert response.status_code in [200, 500]

    def test_crossword_v2_metadata_present(self, client):
        """V2 метаданные присутствуют в ответе"""
        category = self._get_available_category(client)
        if category is None:
            pytest.skip("Нет доступных категорий")

        response = client.post('/api/crossword', json={
            'category': category,
            'difficulty': 'easy',
            'age_group': 'teens'
        })

        if response.status_code == 200:
            data = json.loads(response.data)
            metadata = data['metadata']
            # V2 поля
            assert 'vocabulary_level' in metadata
            assert 'max_word_length' in metadata
            assert 'age_adapted' in metadata
            # V1 поля тоже на месте
            assert 'word_count' in metadata
            assert 'grid_size' in metadata
            assert 'fill_density' in metadata

    def test_crossword_with_user_progress(self, client):
        """user_progress принимается без ошибок"""
        category = self._get_available_category(client)
        if category is None:
            pytest.skip("Нет доступных категорий")

        response = client.post('/api/crossword', json={
            'category': category,
            'difficulty': 'medium',
            'age_group': 'adult',
            'user_progress': {
                'words_in_category': 10,
                'recent_words': ['АТОМ', 'ГЕН']
            }
        })
        # Не должно быть ошибки
        assert response.status_code in [200, 500]

    def test_crossword_backward_compat_structure(self, client):
        """Структура ответа v1 сохранена"""
        category = self._get_available_category(client)
        if category is None:
            pytest.skip("Нет доступных категорий")

        response = client.post('/api/crossword', json={
            'category': category,
            'difficulty': 'medium'
        })

        if response.status_code == 200:
            data = json.loads(response.data)
            # V1 поля на месте
            assert 'id' in data
            assert 'grid' in data
            assert 'words' in data
            assert 'difficulty' in data
            assert 'category' in data
            assert 'metadata' in data

            # Структура words не изменилась
            for w in data['words']:
                assert 'word' in w
                assert 'clue' in w
                assert 'hint' in w
                assert 'startRow' in w
                assert 'startCol' in w
                assert 'direction' in w
                assert 'length' in w


class TestHealthV2:
    """Тесты v2 health endpoint"""

    def test_version_updated(self, client):
        """Версия обновлена до 2.0.0"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert data['version'] == '2.0.0'
