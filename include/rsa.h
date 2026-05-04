#ifndef RSA_H
#define RSA_H

// Chiffre un fichier
void chiffrer_fichier(const char *input, const char *output, int e, int n);

// Déchiffre un fichier
void dechiffrer_fichier(const char *input, const char *output, int d, int n);

// Chiffre un dossier
void chiffrer_dossier(const char *path, int e, int n);

// Déchiffre un dossier
void dechiffrer_dossier(const char *path, int d, int n);

// Génère les clés RSA
void generer_cles(int *p, int *q, int *n, int *phi, int *e, int *d);

#endif
