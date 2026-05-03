#include "rsa.h"
#include "utils.h"
#include <stdlib.h>

// Génère p, q, e, d
void generer_cles(int *p, int *q, int *n, int *phi, int *e, int *d) {
  *p = generer_premier();
  *q = generer_premier();

  // éviter p = q
  while (*q == *p)
    *q = generer_premier();

  *n = (*p) * (*q);
  *phi = (*p - 1) * (*q - 1);

  // choisir e
  *e = 3;
  while (pgcd(*e, *phi) != 1)
    *e += 2;

  // calcul simple de d
  *d = 1;
  while (((*e) * (*d)) % (*phi) != 1)
    (*d)++;
}

// Chiffrement RSA
long long chiffrer(int message, int e, int n) { return mod_exp(message, e, n); }

// Déchiffrement RSA
long long dechiffrer(long long chiffre, int d, int n) {
  return mod_exp(chiffre, d, n);
}
