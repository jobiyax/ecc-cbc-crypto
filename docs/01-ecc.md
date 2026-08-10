# 1. Les courbes elliptiques (ECC)

## 1.1 Pourquoi les courbes elliptiques ?

Les systèmes asymétriques classiques comme **RSA** reposent sur la difficulté de factoriser de très grands nombres premiers. Les **courbes elliptiques** (ECC, _Elliptic Curve Cryptography_) reposent sur une autre base mathématique : les points d'une courbe.

**Avantage majeur de l'ECC : la même sécurité avec des clés beaucoup plus petites.**

| Niveau de sécurité | RSA        | ECC      |
| ------------------ | ---------- | -------- |
| 128 bits           | 3072 bits  | 256 bits |
| 256 bits           | 15360 bits | 512 bits |

Par exemple, une clé ECC de 256 bits offre une sécurité comparable à une clé RSA de 3072 bits, avec bien moins de calculs et de données à transmettre. C'est pour cela que l'ECC est utilisée partout aujourd'hui (TLS, Bitcoin, cartes bancaires).

## 1.2 L'équation d'une courbe elliptique

Une courbe elliptique a une équation de la forme :

$$ y^2 = x^3 + ax + b $$

En cryptographie, on travaille **modulo un nombre premier** $p$ :

$$ y^2 = x^3 + ax + b \pmod p $$

Tous les calculs se font donc avec des nombres entre $0$ et $p-1$ uniquement. C'est ce qu'on appelle un **corps fini** $\mathbb{F}_p$.

Dans notre exercice :

$$ p = 23 \qquad a = 1 \qquad b = 1 $$

$$ E : y^2 = x^3 + x + 1 \pmod{23} $$

## 1.3 Qu'est-ce qu'un point de la courbe ?

Un point est un couple de coordonnées :

$$ P = (x, y) $$

Il **appartient à la courbe** s'il vérifie l'équation, c'est-à-dire si :

$$ y^2 \equiv x^3 + ax + b \pmod p $$

### Vérification d'un point

Prenons le point $G = (3, 10)$ et vérifions qu'il appartient à $E : y^2 = x^3 + x + 1 \pmod{23}$.

Calcul du côté gauche :

$$ y^2 = 10^2 = 100 \equiv 100 - 4 \times 23 = 100 - 92 = 8 \pmod{23} $$

Calcul du côté droit :

$$ x^3 + x + 1 = 3^3 + 3 + 1 = 27 + 3 + 1 = 31 \equiv 31 - 23 = 8 \pmod{23} $$

Les deux côtés valent $8$ modulo $23$ :

$$ 8 = 8 \quad \checkmark $$

**Donc $G = (3, 10)$ appartient bien à la courbe.**

Il existe aussi un point très spécial appelé **point à l'infini**, noté $\mathcal{O}$. C'est l'équivalent du « zéro » : il sert de neutre pour l'addition.

## 1.4 La grande idée : additionner des points

Sur une courbe elliptique, on peut **additionner des points**. C'est cette opération qui rend tout le système possible.

### Interprétation géométrique (sur les réels)

Pour additionner deux points $P$ et $Q$ :

$$
\begin{aligned}
&P, Q : \text{points sur la courbe} \\
&\text{droite } (PQ) \text{ coupe la courbe en } R' \\
&R = -R' = P + Q \qquad (\text{symétrie par rapport à l'axe } x)
\end{aligned}
$$

### Formules algébriques (sur $\mathbb{F}_p$)

En pratique, on utilise des formules exactes.

**Cas 1 — Addition de deux points distincts** $P \neq Q$ :

$$ \lambda = \frac{y_2 - y_1}{x_2 - x_1} \pmod p $$

$$ x_3 = \lambda^2 - x_1 - x_2 \pmod p $$

$$ y_3 = \lambda(x_1 - x_3) - y_1 \pmod p $$

**Cas 2 — Doublement d'un point** $P = Q$ (on trace la tangente) :

$$ \lambda = \frac{3x_1^2 + a}{2y_1} \pmod p $$

$$ x_3 = \lambda^2 - 2x_1 \pmod p $$

$$ y_3 = \lambda(x_1 - x_3) - y_1 \pmod p $$

Dans ces formules, $\pmod p$ signifie que **chaque résultat est ramené entre 0 et 22** pour notre courbe.

> **Remarque :** la division se fait « modulo $p$ », c'est-à-dire qu'au lieu de diviser on multiplie par l'**inverse modulaire** du dénominateur.

### Exemple : calcul de $2G$

Calculons $2G = G + G$ avec $G = (3, 10)$, $a = 1$, $p = 23$.

On utilise le doublement :

$$ \lambda = \frac{3x_1^2 + a}{2y_1} = \frac{3 \times 3^2 + 1}{2 \times 10} = \frac{28}{20} \pmod{23} $$

$$ 28 \equiv 5 \pmod{23} $$

L'inverse de $20$ modulo $23$ est $15$ car $20 \times 15 = 300 \equiv 1 \pmod{23}$. Donc :

$$ \lambda = 5 \times 15 = 75 \equiv 6 \pmod{23} $$

$$ x_3 = \lambda^2 - 2x_1 = 6^2 - 2 \times 3 = 36 - 6 = 30 \equiv 7 \pmod{23} $$

$$ y_3 = \lambda(x_1 - x_3) - y_1 = 6 \times (3 - 7) - 10 = -24 - 10 = -34 \equiv 12 \pmod{23} $$

Résultat :

$$ 2G = (7, 12) $$

### Exemple : calcul de $3G$

$3G = 2G + G = (7, 12) + (3, 10)$ (addition de points distincts) :

$$ \lambda = \frac{10 - 12}{3 - 7} = \frac{-2}{-4} = \frac{1}{2} \pmod{23} $$

L'inverse de $2$ modulo $23$ est $12$ car $2 \times 12 = 24 \equiv 1 \pmod{23}$ :

$$ \lambda = 12 $$

$$ x_3 = \lambda^2 - x_1 - x_2 = 12^2 - 7 - 3 = 144 - 10 = 134 \equiv 19 \pmod{23} $$

$$ y_3 = \lambda(x_1 - x_3) - y_1 = 12 \times (7 - 19) - 12 = 12 \times (-12) - 12 = -156 \equiv 5 \pmod{23} $$

Résultat :

$$ 3G = (19, 5) $$

## 1.5 La multiplication scalaire

La **multiplication scalaire** consiste à additionner un point avec lui-même $k$ fois :

$$ Q = kP = \underbrace{P + P + \cdots + P}\_{k \text{ fois}} $$

C'est l'opération fondamentale de l'ECC. Exemple avec notre point générateur $G$ :

$$ 5G = G + G + G + G + G $$

En calculant étape par étape, on obtient pour notre courbe :

| Multiplication | Point résultant                  |
| -------------- | -------------------------------- |
| $1G$           | $(3, 10)$                        |
| $2G$           | $(7, 12)$                        |
| $3G$           | $(19, 5)$                        |
| $4G$           | $(17, 3)$                        |
| $5G$           | $(9, 16)$                        |
| $6G$           | $(12, 4)$                        |
| $7G$           | $(11, 3)$                        |
| $28G$          | $\mathcal{O}$ (point à l'infini) |

> Le point $G$ a un **ordre** de $28$ : $28G = \mathcal{O}$, puis les points se répètent. C'est la taille du groupe généré.

## 1.6 Le problème du logarithme discret (ECDLP)

Soit $Q = d \cdot G$. On connaît $Q$ et $G$, mais pas $d$.

**Retrouver $d$ revient à résoudre le problème du logarithme discret sur courbe elliptique (ECDLP).**

- Sur une petite courbe comme la nôtre ($p = 23$), on peut essayer tous les $d$ possibles et trouver $d$ en quelques secondes.
- Mais sur une vraie courbe (avec $p$ de 256 bits), il n'existe **aucune méthode efficace** : il faudrait des milliards d'années même pour un supercalculateur.

C'est cette « porte à sens unique » (facile dans un sens, impossible dans l'autre) qui garantit la sécurité de tout le système.

## 1.7 Les courbes réelles

En pratique, on n'utilise pas des courbes aussi petites. Les courbes standards sont :

| Courbe                  | Corps                            | Usage                      |
| ----------------------- | -------------------------------- | -------------------------- |
| **secp256k1**           | $\mathbb{F}_p$, $p$ sur 256 bits | Bitcoin, Ethereum          |
| **P-256** (prime256v1)  | $\mathbb{F}_p$, $p$ sur 256 bits | TLS, cartes bancaires      |
| **Curve25519** (X25519) | $\mathbb{F}_{2^{255}-19}$        | Signal, TLS 1.3, WireGuard |

Le principe reste exactement le même que notre petite courbe, seuls les nombres sont beaucoup plus grands.

## 1.8 Récapitulatif

- Une courbe elliptique : $y^2 = x^3 + ax + b \pmod p$.
- Un point $P = (x, y)$ appartient à la courbe s'il vérifie l'équation.
- On peut **additionner** et **doubler** des points (formules algébriques).
- La **multiplication scalaire** $Q = kP$ est facile à calculer…
- …mais retrouver $k$ à partir de $Q$ (l'ECDLP) est **quasi impossible** sur une grande courbe.
