"""
CrosswordGenerator - Генератор русскоязычных кроссвордов
"""

from .generator import CrosswordGenerator
from .grid import Grid
from .word_placer import WordPlacer
from .validator import Validator

__all__ = ['CrosswordGenerator', 'Grid', 'WordPlacer', 'Validator']
__version__ = '1.0.0'
