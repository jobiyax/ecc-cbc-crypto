#include "rsa.h"
#include "utils.h"
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

// Génération des clés RSA
void generer_cles(int *p, int *q, int *n, int *phi, int *e, int *d) {
  *p = generer_premier();
  *q = generer_premier();

  // Eviter p = q
  while (*q == *p)
    *q = generer_premier();

  *n = (*p) * (*q);
  *phi = (*p - 1) * (*q - 1);

  // Choix de e
  *e = 3;
  while (pgcd(*e, *phi) != 1)
    *e += 2;

  // Calcul de d (inverse modulaire naïf)
  *d = 1;
  while (((*e) * (*d)) % (*phi) != 1)
    (*d)++;
}

// RSA sur entier
long long chiffrer(int message, int e, int n) { return mod_exp(message, e, n); }

long long dechiffrer(long long chiffre, int d, int n) {
  return mod_exp(chiffre, d, n);
}

// Fichiers
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

// Dossier (récursif)
void chiffrer_dossier(const char *path, int e, int n) {
  DIR *dir = opendir(path);
  if (!dir)
    return;

  struct dirent *entry;
  char input_path[512];
  char output_path[512];

  while ((entry = readdir(dir)) != NULL) {

    if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
      continue;

    snprintf(input_path, sizeof(input_path), "%s/%s", path, entry->d_name);

    struct stat st;
    stat(input_path, &st);

    if (S_ISDIR(st.st_mode)) {
      chiffrer_dossier(input_path, e, n);
    } else {
      // Eviter double chiffrement
      if (strstr(entry->d_name, ".bin"))
        continue;

      snprintf(output_path, sizeof(output_path), "%s.bin", input_path);

      chiffrer_fichier(input_path, output_path, e, n);
      printf("Chiffre: %s -> %s\n", input_path, output_path);
    }
  }

  closedir(dir);
}

void dechiffrer_dossier(const char *path, int d, int n) {
  DIR *dir = opendir(path);
  if (!dir)
    return;

  struct dirent *entry;
  char input_path[512];
  char output_path[512];

  while ((entry = readdir(dir)) != NULL) {

    if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
      continue;

    snprintf(input_path, sizeof(input_path), "%s/%s", path, entry->d_name);

    struct stat st;
    stat(input_path, &st);

    if (S_ISDIR(st.st_mode)) {
      dechiffrer_dossier(input_path, d, n);
    } else {
      // Ne traiter que les fichiers .bin
      if (!strstr(entry->d_name, ".bin"))
        continue;

      snprintf(output_path, sizeof(output_path), "%s.dec", input_path);

      dechiffrer_fichier(input_path, output_path, d, n);
      printf("Dechiffre: %s -> %s\n", input_path, output_path);
    }
  }

  closedir(dir);
}
