#include "rsa.h"
#include "utils.h"

// Génération des clés RSA
void generer_cles(int *p, int *q, int *n, int *phi, int *e, int *d) {
  *p = generer_premier();
  *q = generer_premier();

  while (*q == *p)
    *q = generer_premier();

  *n = (*p) * (*q);
  *phi = (*p - 1) * (*q - 1);

  *e = 3;
  while (pgcd(*e, *phi) != 1)
    *e += 2;

  *d = 1;
  while (((*e) * (*d)) % (*phi) != 1)
    (*d)++;
}

// RSA sur entier
long long chiffrer(int message, int e, int n) { return mod_exp(message, e, n); }

long long dechiffrer(long long chiffre, int d, int n) {
  return mod_exp(chiffre, d, n);
}
