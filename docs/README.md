# Documentation du cryptosystème ECC + CBC

Bienvenue dans la documentation complète du projet. Ici, tout est expliqué **par sujet**, avec des formules en LaTeX et des exemples numériques détaillés.

## Sommaire

| # | Sujet | Fichier |
|---|-------|---------|
| 1 | Les courbes elliptiques | [01-ecc.md](01-ecc.md) |
| 2 | L'échange de clé ECDH | [02-ecdh.md](02-ecdh.md) |
| 3 | Le mode CBC | [03-cbc.md](03-cbc.md) |
| 4 | Exemple complet de A à Z | [04-exemple.md](04-exemple.md) |

## Parcours conseillé

1. Lis d'abord les **courbes elliptiques** : c'est le cœur de la création de la clé.
2. Ensuite **ECDH** : comment deux personnes obtiennent la même clé secrète.
3. Puis le **mode CBC** : comment cette clé sert à chiffrer le texte.
4. Termine par **l'exemple complet** qui assemble tout, étape par étape, avec les vrais calculs numériques.

## L'idée à retenir

$$ \text{ECC + ECDH} \longrightarrow \text{clé secrète } K \longrightarrow \text{CBC} \longrightarrow \text{texte chiffré} $$
