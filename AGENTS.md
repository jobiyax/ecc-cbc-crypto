# AGENTS.md

## Project Overview

ECC + ECDH + CBC hybrid crypto in pure Python (3.14+).

## Commands

- Setup: `uv sync`
- Run: `uv run python src/main.py`
- Test: `uv run pytest`
- Test single: `uv run pytest tests/test_cbc.py`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`

## Architecture

- `src/` — source code (main.py, ecc.py, ecdh.py, cbc.py)
- `tests/` — mirrors src/ structure
- `output/` — generated files (gitignored)
- `wiki/` — documentation pages

## Code Style

- Python 3.14+ with type hints
- Pydantic models for validation
- Questionary for CLI prompts
- No comments unless requested
- Descriptive variable names
- Error messages in French

## Branch Naming

Format: `prefix/description-words`

- `feat/` — new features (2-3 words)
- `fix/` — bug fixes (2-3 words)
- `chore/` — maintenance tasks (2-3 words)
- `docs/` — documentation (2-3 words)

Examples: `feat/add-padding-mode`, `fix/prime-validation`, `chore/update-deps`

## Commit Messages

Format: `prefix: description (2-6 words)`

- `feat:` — new functionality
- `fix:` — bug fix
- `chore:` — maintenance
- `docs:` — documentation
- `test:` — adding tests
- `refactor:` — code restructuring

Examples: `feat: add CBC encryption`, `fix: validate prime numbers`

## Rules

- Run tests and lint before completing work
- Do not modify `output/` directory structure
- Keep error messages in French
- Use Pydantic for all data validation
