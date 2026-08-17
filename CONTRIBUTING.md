# Guide de Contribution

Merci de votre intérêt pour ecc-cbc-crypto.

## Signaler des Bugs

Ouvrez une issue GitHub avec :

- Titre et description clairs
- Étapes pour reproduire
- Comportement attendu vs observé
- Version Python et OS

## Pull Requests

1. Forkez et créez une branche depuis `main` (voir [AGENTS.md](AGENTS.md))
2. Effectuez vos modifications
3. Lancez les tests : `uv run pytest`
4. Vérifiez le lint : `uv run ruff check .`
5. Formatez : `uv run ruff format .`
6. Committez avec un message clair (voir [AGENTS.md](AGENTS.md))
7. Ouvrez une PR avec une description

## Style de Code

- Python 3.14+ avec type hints
- Modèles Pydantic pour la validation
- Messages d'erreur en français
- Pas de commentaires sauf demande explicite

## Tests

```bash
uv run pytest # suite complète
uv run pytest -v # mode verbeux
uv run pytest tests/test_cbc.py # fichier unique
```

Tous les tests doivent passer avant la fusion.
