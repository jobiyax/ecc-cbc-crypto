#include "config.h"
#include "rsa.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Fonction de suppression du binaire
void auto_delete(void) { remove(NAME_BUILD); }

int main() {

  // Initialisation du générateur aléatoire
  srand(time(NULL));

  // Variables des clés RSA
  int p, q, n, phi, e, d;

  // Génération des clés RSA
  generer_cles(&p, &q, &n, &phi, &e, &d);

  // Affichage des clés générées
  printf("=== CLES RSA ===\n");
  printf("p=%d q=%d\n", p, q);
  printf("n=%d phi=%d\n", n, phi);
  printf("e=%d d=%d\n\n", e, d);

  // Vérification que n est assez grand
  if (n <= 255) {
    printf("Erreur: n doit etre > 255\n");
    return 1;
  }

  const char *dossier = ".";

  printf("\n=== CHIFFREMENT AUTOMATIQUE ===\n");
  chiffrer_dossier(dossier, e, n);

  int choix;

  // Menu simplifié
  while (1) {
    printf("\n=== MENU ===\n");
    printf("1. Dechiffrer le dossier\n");
    printf("2. Quitter\n");
    printf("Choix : ");

    scanf("%d", &choix);

    switch (choix) {

    case 1:
      printf("\n=== DECHIFFREMENT ===\n");
      dechiffrer_dossier(dossier, d, n);

      printf("Suppression du binaire...\n");
      auto_delete();

      return 0;

    case 2:
      printf("Au revoir !\n");
      return 0;

    default:
      printf("Choix invalide\n");
    }
  }

  return 0;
}
