# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CrossQuest Python is a Russian-language crossword generator. It produces JSON crosswords compatible with a React frontend application. The generator places words on a 10×10 grid with proper intersections and validates the result.

## Commands

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_generator.py

# Run a specific test
pytest tests/test_generator.py::TestCrosswordGenerator::test_generate_single

# Generate crosswords (requires dictionary at data/dictionary.json)
python generate_batch.py -c 10 --category "Наука и технологии"
python generate_batch.py --validate-only  # validate dictionary only
```

## Architecture

The codebase follows a clear separation of concerns:

- **`src/generator.py`** - `CrosswordGenerator` orchestrates the generation process. It loads the dictionary, applies difficulty settings, delegates to `WordPlacer`, validates via `Validator`, and formats output JSON.

- **`src/grid.py`** - `Grid` manages the 2D character array. Key responsibilities:
  - `can_place_word()` checks placement validity including boundary checks and parallel word prevention
  - `get_intersections()` finds all valid positions where a word can cross existing words
  - `crop_empty_edges()` trims the grid after placement (updates word coordinates)
  - `PlacedWord` dataclass stores word metadata (word, clue, hint, position, direction)

- **`src/word_placer.py`** - `WordPlacer` implements the placement algorithm:
  - Places first word horizontally in center
  - Iterates remaining words sorted by length, finding positions with most intersections
  - Uses randomization from top-3 positions for variety

- **`src/validator.py`** - `Validator` performs static checks:
  - Minimum 8 words required
  - All words must be connected (graph connectivity via BFS)
  - Fill density between 30-70%
  - No parallel adjacent words

- **`src/utils.py`** - Helper functions: dictionary I/O, word scoring (prefers longer words with common Russian letters), filename generation with category transliteration.

## Dictionary Format

The dictionary (`data/dictionary.json`) uses this structure:

```json
{
  "Наука и технологии": [
    {"word": "АТОМ", "clue": "Наименьшая частица...", "hint": "Состоит из протонов..."}
  ]
}
```

Words must be 3-12 uppercase Cyrillic letters only.

## Output Format

Generated crosswords are JSON with:
- `grid`: 2D array of characters (empty string for blank cells)
- `words`: Array of objects with `word`, `clue`, `hint`, `startRow`, `startCol`, `direction`, `length`
- `difficulty`: "easy" | "medium" | "hard"
- `category`: Category name

## Difficulty Settings

- **easy**: 8-10 words, 4-8 letter length
- **medium**: 10-12 words, 3-10 letter length
- **hard**: 12-15 words, 3-12 letter length
