#include "rsa.h"
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

// Chiffrement dossier
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
      if (strstr(entry->d_name, ".bin"))
        continue;

      snprintf(output_path, sizeof(output_path), "%s.bin", input_path);

      chiffrer_fichier(input_path, output_path, e, n);
      printf("Chiffre: %s -> %s\n", input_path, output_path);
    }
  }

  closedir(dir);
}

// Déchiffrement dossier
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
      if (!strstr(entry->d_name, ".bin"))
        continue;

      snprintf(output_path, sizeof(output_path), "%s.dec", input_path);

      dechiffrer_fichier(input_path, output_path, d, n);
      printf("Dechiffre: %s -> %s\n", input_path, output_path);
    }
  }

  closedir(dir);
}
