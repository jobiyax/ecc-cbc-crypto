# 4. Exemple complet de A à Z

> **Objectif :** concevoir un cryptosystème qui chiffre le texte « BONJOUR » avec les courbes elliptiques en mode CBC, et le résoudre avec les **vrais calculs numériques**.

## Récapitulatif des 9 étapes

| Étape | Action                                                |
| ----- | ----------------------------------------------------- |
| 1     | Choisir la courbe elliptique                          |
| 2     | Vérifier le point générateur $G$                      |
| 3     | Générer les clés privées                              |
| 4     | Calculer les clés publiques ($5G$ et $7G$)            |
| 5     | Faire l'ECDH pour obtenir la clé secrète              |
| 6     | Transformer la clé pour le CBC                        |
| 7     | Découper le texte en blocs et le convertir en binaire |
| 8     | Appliquer le mode CBC                                 |
| 9     | Obtenir le texte chiffré                              |

## Étape 1 — Choisir la courbe elliptique

On prend une courbe simple pour que tous les calculs soient vérifiables à la main :

$$ p = 23 \qquad a = 1 \qquad b = 1 $$

$$ E : y^2 = x^3 + x + 1 \pmod{23} $$

Tous les calculs se font avec des nombres entre $0$ et $22$.

## Étape 2 — Choisir et vérifier le point générateur $G$

On choisit :

$$ G = (3, 10) $$

**Vérification** : on remplace $x = 3$ et $y = 10$ dans l'équation.

Côté gauche :

$$ y^2 = 10^2 = 100 \equiv 100 - 4 \times 23 = 8 \pmod{23} $$

Côté droit :

$$ x^3 + x + 1 = 3^3 + 3 + 1 = 27 + 3 + 1 = 31 \equiv 31 - 23 = 8 \pmod{23} $$

$$ 8 = 8 \quad \checkmark $$

**$G = (3, 10)$ appartient bien à la courbe.**

## Étape 3 — Générer les clés privées

Alice et Bob choisissent chacun un nombre secret :

$$ d_A = 5 \qquad \text{(clé privée d'Alice)} $$

$$ d_B = 7 \qquad \text{(clé privée de Bob)} $$

## Étape 4 — Calculer les clés publiques

Une clé publique se calcule par multiplication scalaire : $Q = d \cdot G$.

### Clé publique d'Alice : $Q_A = 5G$

On additionne $G$ à lui-même 5 fois. D'abord le doublement $2G$ :

$$ \lambda = \frac{3x^2 + a}{2y} = \frac{3 \times 3^2 + 1}{2 \times 10} = \frac{28}{20} \pmod{23} $$

$28 \equiv 5$ et $20^{-1} \equiv 15 \pmod{23}$, donc :

$$ \lambda = 5 \times 15 = 75 \equiv 6 \pmod{23} $$

$$ x = \lambda^2 - 2x_1 = 36 - 6 = 30 \equiv 7 \pmod{23} $$

$$ y = \lambda(x_1 - x_3) - y_1 = 6 \times (3 - 7) - 10 = -34 \equiv 12 \pmod{23} $$

$$ 2G = (7, 12) $$

On continue par additions successives (détail dans [01-ecc.md](01-ecc.md)) :

| Calcul        | Résultat  |
| ------------- | --------- |
| $2G = G + G$  | $(7, 12)$ |
| $3G = 2G + G$ | $(19, 5)$ |
| $4G = 3G + G$ | $(17, 3)$ |
| $5G = 4G + G$ | $(9, 16)$ |

**Clé publique d'Alice :**

$$ Q_A = 5G = (9, 16) $$

### Clé publique de Bob : $Q_B = 7G$

| Calcul        | Résultat  |
| ------------- | --------- |
| $6G = 5G + G$ | $(12, 4)$ |
| $7G = 6G + G$ | $(11, 3)$ |

**Clé publique de Bob :**

$$ Q_B = 7G = (11, 3) $$

## Étape 5 — L'échange de clé ECDH

Alice et Bob échangent leurs clés publiques. Alice reçoit $Q_B$, Bob reçoit $Q_A$.

**Alice calcule :**

$$ K = d_A \cdot Q_B = 5 \cdot (11, 3) $$

**Bob calcule :**

$$ K = d_B \cdot Q_A = 7 \cdot (9, 16) $$

Grâce aux propriétés de la courbe, les deux calculs donnent le même point :

$$ K = d_A d_B G = 5 \times 7 \times G = 35G $$

Sur notre courbe, le point $G$ a un ordre de 28 ($28G = \mathcal{O}$), donc $35G = 7G$ :

$$ K = 35G = 7G = (11, 3) $$

Vérifions côté Bob avec la multiplication $7 \cdot Q_A$ :

$$ 2 \cdot (9, 16) = (6, 4) \qquad 4 \cdot (9, 16) = (13, 7) $$

$$ 7 \cdot (9, 16) = (13, 7) + (6, 4) + (9, 16) = (7, 12) + (9, 16) = (11, 3) $$

**Alice et Bob obtiennent bien le même point secret :**

$$ K = (11, 3) $$

## Étape 6 — Transformer la clé ECC en clé CBC

La clé ECDH est un point $K = (x, y)$. Pour l'utiliser avec le mode CBC (qui attend une clé symétrique), on prend la coordonnée $x$ du point :

$$ K_x = 11 $$

**La clé de chiffrement CBC est :**

$$ K = 11 $$

## Étape 7 — Préparer le texte et le convertir en binaire

### 7.1 Découpage en blocs

On prend le texte « BONJOUR » (8 lettres) et on le découpe en blocs de 4 caractères :

$$ P_1 = \text{BONJ} \qquad P_2 = \text{OURX} $$

Le « X » final est un caractère de remplissage pour compléter le dernier bloc.

### 7.2 Conversion ASCII → binaire

Chaque lettre est codée par son code ASCII, puis convertie en binaire sur 8 bits.

**Bloc $P_1$ = BONJ :**

| Lettre | ASCII | Binaire  |
| ------ | ----- | -------- |
| B      | 66    | 01000010 |
| O      | 79    | 01001111 |
| N      | 78    | 01001110 |
| J      | 74    | 01001010 |

$$ P_1 = 01000010\ 01001111\ 01001110\ 01001010 $$

**Bloc $P_2$ = OURX :**

| Lettre | ASCII | Binaire  |
| ------ | ----- | -------- |
| O      | 79    | 01001111 |
| U      | 85    | 01010101 |
| R      | 82    | 01010010 |
| X      | 88    | 01011000 |

$$ P_2 = 01001111\ 01010101\ 01010010\ 01011000 $$

## Étape 8 — Appliquer le mode CBC

### 8.1 Rappel des formules

$$ C*i = E_K(P_i \oplus C*{i-1}) \qquad \text{avec } C_0 = IV $$

### 8.2 Choix de l'IV

On choisit un vecteur d'initialisation (par exemple) :

$$ IV = 11001010\ 01110101\ 10001101\ 01010011 $$

### 8.3 Exemple d'opération XOR

Rappel : le XOR donne 1 si les bits sont différents, 0 s'ils sont identiques.

$$ 10101010 \oplus 11001100 = 01100110 $$

### 8.4 Premier bloc

On combine $P_1$ avec l'IV :

$$ P_1 \oplus IV = 01000010\ 01001111\ 01001110\ 01001010 \oplus 11001010\ 01110101\ 10001101\ 01010011 $$

$$ P_1 \oplus IV = 10001000\ 00111010\ 11000011\ 00011001 $$

Puis on chiffre avec la clé $K = 11$ :

$$ C*1 = E*{11}(P_1 \oplus IV) $$

### 8.5 Deuxième bloc

On combine $P_2$ avec le bloc chiffré précédent $C_1$ :

$$ C*2 = E*{11}(P_2 \oplus C_1) $$

## Étape 9 — Résultat final

Le texte chiffré est la concaténation des blocs chiffrés :

$$ C = C_1 C_2 $$

> Le calcul exact des blocs $C_1$ et $C_2$ dépend de la fonction de chiffrement $E_K$ utilisée (AES, DES…). Le but de l'exercice est de montrer **comment on construit le système** : la clé vient de l'ECC, le chiffrement vient du CBC.

## Récapitulatif de tous les résultats

| Élément            | Valeur                              |
| ------------------ | ----------------------------------- |
| Courbe             | $E : y^2 = x^3 + x + 1 \pmod{23}$   |
| Générateur         | $G = (3, 10)$                       |
| Clé privée Alice   | $d_A = 5$                           |
| Clé privée Bob     | $d_B = 7$                           |
| Clé publique Alice | $Q_A = 5G = (9, 16)$                |
| Clé publique Bob   | $Q_B = 7G = (11, 3)$                |
| Clé partagée       | $K = 35G = (11, 3)$                 |
| Clé CBC            | $K_x = 11$                          |
| Texte clair        | BONJOUR                             |
| $P_1$              | 01000010 01001111 01001110 01001010 |
| $P_2$              | 01001111 01010101 01010010 01011000 |
| $IV$               | 11001010 01110101 10001101 01010011 |
| $C_1$              | $E_{11}(P_1 \oplus IV)$             |
| $C_2$              | $E_{11}(P_2 \oplus C_1)$            |
