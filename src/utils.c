#include "utils.h"
#include <stdlib.h>

// Test simple de primalité
int est_premier(int n) {
  if (n < 2)
    return 0;

  for (int i = 2; i * i <= n; i++)
    if (n % i == 0)
      return 0;

  return 1;
}

// Génère un nombre premier entre 50 et 149
int generer_premier() {
  int num;

  do {
    num = rand() % 100 + 50;
  } while (!est_premier(num));

  return num;
}

// Algorithme d'Euclide
int pgcd(int a, int b) {
  while (b != 0) {
    int t = b;
    b = a % b;
    a = t;
  }
  return a;
}

// Calcul rapide de (base^exp) % mod
long long mod_exp(long long base, long long exp, long long mod) {
  long long res = 1;
  base %= mod;

  while (exp > 0) {
    if (exp % 2)
      res = (res * base) % mod;

    base = (base * base) % mod;
    exp /= 2;
  }

  return res;
}
