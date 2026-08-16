<p align="center">
  <img src="assets/banner.webp" width="200">
</p>

<p align="center">
  Cryptosystème hybride échange de clé ECDH sur courbe elliptique puis chiffrement symétrique en mode CBC en Python pur
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
  - [Prérequis](#prérequis)
  - [Clonage et dépendances](#clonage-et-dépendances)
- [Utilisation](#utilisation)
  - [Tests](#tests)
  - [Qualité du code](#qualité-du-code)
- [Licence](#licence)

## Fonctionnalités

- Échange de clé sécurisé (ECDH) sur courbe elliptique, pas à pas
- Chiffrement symétrique en mode CBC, bloc par bloc (padding PKCS#7)
- Saisie de **texte libre** (lettres, chiffres, caractères spéciaux, espaces compris)
- Saisies **validées en direct** : une entrée invalide est refusée immédiatement, message en français
- **Mode sélectionnable** (Chiffrer / Déchiffrer) au lieu de taper `c`/`d`
- Exemple complet avec calculs numériques vérifiables
- Binaire détaillé exporté dans un dossier `output/` (IV, payload, blocs, XOR, chiffré) pour garder la console lisible
- Vérification automatique par déchiffrement à la fin

## Documentation

Toutes les explications, les concepts et l'exemple de A à Z sont détaillés dans le [wiki du projet](https://github.com/jobiyax/ecc-cbc-crypto/wiki).

| #   | Sujet                    | Lien                                                                                              |
| --- | ------------------------ | ------------------------------------------------------------------------------------------------- |
| 0   | Accueil                  | [Home](https://github.com/jobiyax/ecc-cbc-crypto/wiki)                                            |
| 1   | Les courbes elliptiques  | [Les-courbes-elliptiques](https://github.com/jobiyax/ecc-cbc-crypto/wiki/Les-courbes-elliptiques) |
| 2   | L'échange de clé ECDH    | [L-echange-de-cle-ECDH](https://github.com/jobiyax/ecc-cbc-crypto/wiki/L-echange-de-cle-ECDH)     |
| 3   | Le mode CBC              | [Le-mode-CBC](https://github.com/jobiyax/ecc-cbc-crypto/wiki/Le-mode-CBC)                         |
| 4   | Exemple complet de A à Z | [Exemple-complet](https://github.com/jobiyax/ecc-cbc-crypto/wiki/Exemple-complet)                 |

## Installation

### Prérequis

- Python 3.14 ou plus
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets et d'environnement)

Vérifier

```bash
python --version
uv --version
```

### Clonage et dépendances

```bash
git clone https://github.com/jobiyax/ecc-cbc-crypto.git
cd ecc-cbc-crypto
uv sync  # installe les dépendances
```

> Sans uv, utilisez `python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`

## Utilisation

Lancez le programme

```bash
uv run python src/main.py
```

Le CLI demande d'abord le **mode** dans une liste de sélection (flèches ↑/↓, **Entrée** pour valider) :

1. **Chiffrer** (défaut)
2. **Déchiffrer** de `output/ciphertext.txt`

### Chiffrement

1. `dA` (clé privée d'Alice)
2. `dB` (clé privée de Bob)
3. Le **texte à chiffrer** (texte, chiffres, accents, emojis, espaces…)
4. La personnalisation de `p/a/b` et de la taille de bloc _(question oui/non)_

Chaque champ pré-affiche sa valeur par défaut. Une entrée invalide est refusée
immédiatement avec un message sous le champ.

### Déchiffrement

Saisissez le même `dA`, `dB` et les mêmes paramètres de courbe que lors du chiffrement
(la clé en dérive via l'ECDH). Le résultat est affiché en console et écrit dans
`output/plain.txt`. Si le contenu n'est pas du texte, il est interprété comme un
nombre entier.

### Fichiers de sortie

Les représentations binaires ne sont plus affichées en console mais écrites dans le dossier `output/` (créé automatiquement, et ignoré par git) :

| Fichier             | Contenu                      |
| ------------------- | ---------------------------- |
| `iv.txt`            | IV en binaire                |
| `payload.txt`       | Payload binaire              |
| `blocks.txt`        | Blocs `P_i` après padding    |
| `xor.txt`           | Résultats `P_i XOR` (CBC)    |
| `cipher_blocks.txt` | Blocs chiffrés `C_i`         |
| `ciphertext.txt`    | Texte chiffré complet        |
| `plain.txt`         | Clair déchiffré _(mode `d`)_ |

Les chemins des fichiers écrits dans `output/` sont récapitulés en fin de chiffrement,
suivis de la vérification finale du déchiffrement.

### Tests

```bash
uv run pytest  # toute la suite
uv run pytest -v  # détail de chaque test
```

## Qualité du code

```bash
uv run ruff check .  # lint
uv run ruff format .  # format
```

## Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE).
