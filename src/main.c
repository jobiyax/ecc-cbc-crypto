#include "rsa.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
  srand(time(NULL)); // initialiser le hasard

  int p, q, n, phi, e, d;

  generer_cles(&p, &q, &n, &phi, &e, &d);

  int message = 2026;

  long long c = chiffrer(message, e, n);
  long long m = dechiffrer(c, d, n);

  printf("p=%d q=%d\n", p, q);
  printf("n=%d phi=%d\n", n, phi);
  printf("e=%d d=%d\n", e, d);

  printf("\nMessage=%d\n", message);
  printf("Chiffre=%lld\n", c);
  printf("Dechiffre=%lld\n", m);

  return 0;
}
