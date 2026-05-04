#include "rsa.h"
#include <stdio.h>

// Chiffrement fichier
void chiffrer_fichier(const char *input, const char *output, int e, int n) {
  FILE *in = fopen(input, "rb");
  FILE *out = fopen(output, "wb");

  if (!in || !out) {
    printf("Erreur ouverture fichier\n");
    return;
  }

  int byte;
  long long c;

  while ((byte = fgetc(in)) != EOF) {
    c = chiffrer(byte, e, n);
    fwrite(&c, sizeof(long long), 1, out);
  }

  fclose(in);
  fclose(out);
}

// Déchiffrement fichier
void dechiffrer_fichier(const char *input, const char *output, int d, int n) {
  FILE *in = fopen(input, "rb");
  FILE *out = fopen(output, "wb");

  if (!in || !out) {
    printf("Erreur ouverture fichier\n");
    return;
  }

  long long c;
  int m;

  while (fread(&c, sizeof(long long), 1, in) == 1) {
    m = dechiffrer(c, d, n);
    fputc(m, out);
  }

  fclose(in);
  fclose(out);
}
