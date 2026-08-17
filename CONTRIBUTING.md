# Guide de Contribution

Merci de votre intérêt pour ecc-cbc-crypto.

## Signaler des Bugs

Ouvrez une issue GitHub avec :

- Un titre et une description clairs
- Les étapes pour reproduire
- Le comportement attendu vs observé
- La version Python et le système d'exploitation

## Suggérer des Fonctionnalités

Ouvrez une issue avec le label `enhancement`. Décrivez le cas d'usage et le comportement attendu.

## Pull Requests

1. Forkez le dépôt et créez une branche depuis `main` (voir [AGENTS.md](AGENTS.md) pour les conventions de nommage)
2. Effectuez vos modifications
3. Lancez les tests : `uv run pytest`
4. Vérifiez le lint : `uv run ruff check .`
5. Formatez le code : `uv run ruff format .`
6. Committez avec un message clair (voir [AGENTS.md](AGENTS.md))
7. Ouvrez une pull request avec une description de vos changements

## Style de Code

- Python 3.14+ avec type hints
- Modèles Pydantic pour la validation des données
- Messages d'erreur en français
- Pas de commentaires sauf demande explicite

## Tests

```bash
uv run pytest  # suite complète
uv run pytest -v  # mode verbeux
uv run pytest tests/test_cbc.py  # fichier unique
```

Tous les tests doivent passer avant la fusion.
