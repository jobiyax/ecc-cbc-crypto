#include "rsa.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
  // Initialiser le générateur de nombres aléatoires
  srand(time(NULL));

  // Variables pour les clés RSA
  int p, q, n, phi, e, d;

  // Génération des clés
  generer_cles(&p, &q, &n, &phi, &e, &d);

  // Affichage des clés générées
  printf("=== CLES RSA ===\n");
  printf("p=%d q=%d\n", p, q);
  printf("n=%d phi=%d\n", n, phi);
  printf("e=%d d=%d\n\n", e, d);

  // Test de chiffrement sur un fichier
  printf("=== TEST FICHIER ===\n");

  // Chiffrement du fichier
  chiffrer_fichier("message.txt", "chiffre.bin", e, n);
  printf("Fichier chiffre -> chiffre.bin\n");

  // Déchiffrement du fichier
  dechiffrer_fichier("chiffre.bin", "dechiffre.txt", d, n);
  printf("Fichier dechiffre -> dechiffre.txt\n");

  // Fin du programme
  printf("Operation terminee !\n");

  return 0;
}
