#ifndef RSA_H
#define RSA_H

// Génère les clés RSA
void generer_cles(int *p, int *q, int *n, int *phi, int *e, int *d);

// Chiffre un message
long long chiffrer(int message, int e, int n);

// Déchiffre un message
long long dechiffrer(long long chiffre, int d, int n);

#endif
