<p align="center">
  <img src="assets/banner.webp" width="200">
</p>

<p align="center">
  Cryptosystème hybride échange de clé ECDH sur courbe elliptique puis chiffrement symétrique en mode CBC
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.14-inactive?style=flat-square" alt="Python 3.14">
  <img src="https://img.shields.io/badge/deps-pydantic%2Bquestionary-inactive?style=flat-square" alt="Pydantic + questionary">
  <img src="https://img.shields.io/badge/license-MIT-inactive?style=flat-square" alt="Licence MIT">
  <img src="https://img.shields.io/badge/tests-39%20passing-inactive?style=flat-square" alt="39 tests">
</p>

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Documentation](#documentation)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Tests](#tests)
- [Communauté](#communauté)
- [Licence](#licence)

## Fonctionnalités

- Échange de clé ECDH sur courbe elliptique
- Chiffrement symétrique CBC (padding PKCS#7)
- Saisie de texte libre avec validation en direct
- Mode sélectionnable (Chiffrer / Déchiffrer)
- Vérification automatique par déchiffrement
- Détails binaires exportés dans `output/`

## Documentation

Consultez le [wiki du projet](https://github.com/jobiyax/ecc-cbc-crypto/wiki) pour les explications complètes (courbes elliptiques, ECDH, CBC, exemple de A à Z).

## Installation

Prérequis : Python 3.14+ et [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/jobiyax/ecc-cbc-crypto.git
cd ecc-cbc-crypto
uv sync # installe les dépendances
```

## Utilisation

```bash
uv run python src/main.py
```

Le CLI demande le mode (Chiffrer / Déchiffrer), puis les clés `dA`, `dB` et le texte. Les paramètres de courbe (`p/a/b`, taille de bloc) sont personnalisables. Les entrées invalides sont rejetées immédiatement.

En déchiffrement, saisissez les mêmes clés et paramètres que lors du chiffrement.

### Fichiers de sortie

| Fichier             | Contenu                         |
| ------------------- | ------------------------------- |
| `iv.txt`            | IV en binaire                   |
| `payload.txt`       | Payload binaire                 |
| `blocks.txt`        | Blocs `P_i` après padding       |
| `xor.txt`           | Résultats `P_i XOR` (CBC)       |
| `cipher_blocks.txt` | Blocs chiffrés `C_i`            |
| `ciphertext.txt`    | Texte chiffré complet           |
| `plain.txt`         | Clair déchiffré (déchiffrement) |

## Tests

```bash
uv run pytest # toute la suite
uv run pytest tests/test_cbc.py # un fichier
uv run pytest -v # détail
```

### Qualité du code

```bash
uv run ruff check . # lint
uv run ruff format . # format
```

## Communauté

- [CONTRIBUTING.md](CONTRIBUTING.md) guide de contribution
- [SECURITY.md](SECURITY.md) politique de sécurité
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) code de conduite

## Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE).
