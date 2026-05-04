#include "rsa.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
  // Initialisation du hasard
  srand(time(NULL));

  // Variables des clés RSA
  int p, q, n, phi, e, d;

  // Génération des clés
  generer_cles(&p, &q, &n, &phi, &e, &d);

  // Affichage des clés
  printf("=== CLES RSA ===\n");
  printf("p=%d q=%d\n", p, q);
  printf("n=%d phi=%d\n", n, phi);
  printf("e=%d d=%d\n\n", e, d);

  // Vérification taille de n
  if (n <= 255) {
    printf("Erreur: n doit etre > 255\n");
    return 1;
  }

  int choix;
  const char *dossier = ".";

  // Menu principal en boucle
  while (1) {
    printf("\n=== MENU RSA ===\n");
    printf("1. Chiffrer un dossier\n");
    printf("2. Dechiffrer un dossier\n");
    printf("3. Quitter\n");
    printf("Choix : ");

    scanf("%d", &choix);

    // Gestion des choix utilisateur
    switch (choix) {
    case 1:
      printf("\n=== CHIFFREMENT ===\n");
      chiffrer_dossier(dossier, e, n);
      break;

    case 2:
      printf("\n=== DECHIFFREMENT ===\n");
      dechiffrer_dossier(dossier, d, n);
      break;

    case 3:
      printf("Au revoir !\n");
      return 0;

    default:
      printf("Choix invalide\n");
    }
  }

  return 0;
}
