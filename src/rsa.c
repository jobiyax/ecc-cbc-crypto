#include "rsa.h"
#include "utils.h"
#include <stdio.h>
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

// Chiffre un fichier
void chiffrer_fichier(const char *input, const char *output, int e, int n) {
  // Ouvrir le fichier d'entrée et de sortie
  FILE *in = fopen(input, "rb");
  FILE *out = fopen(output, "wb");

  // Vérifier l'ouverture des fichiers
  if (!in || !out) {
    printf("Erreur ouverture fichier\n");
    return;
  }

  int byte;
  long long c;

  // Lire chaque octet, le chiffrer et l'écrire
  while ((byte = fgetc(in)) != EOF) {
    c = chiffrer(byte, e, n);
    fwrite(&c, sizeof(long long), 1, out);
  }

  // Fermer les fichiers
  fclose(in);
  fclose(out);
}

// Déchiffre un fichier
void dechiffrer_fichier(const char *input, const char *output, int d, int n) {
  // Ouvrir le fichier chiffré et le fichier de sortie
  FILE *in = fopen(input, "rb");
  FILE *out = fopen(output, "wb");

  // Vérifier l'ouverture des fichiers
  if (!in || !out) {
    printf("Erreur ouverture fichier\n");
    return;
  }

  long long c;
  int m;

  // Lire chaque bloc chiffré, le déchiffrer et l'écrire
  while (fread(&c, sizeof(long long), 1, in) == 1) {
    m = dechiffrer(c, d, n);
    fputc(m, out);
  }

  // Fermer les fichiers
  fclose(in);
  fclose(out);
}
