#ifndef UTILS_H
#define UTILS_H

// Vérifie si un nombre est premier
int est_premier(int n);

// Génère un nombre premier aléatoire
int generer_premier();

// Calcul du PGCD
int pgcd(int a, int b);

// Exponentiation modulaire rapide
long long mod_exp(long long base, long long exp, long long mod);

#endif
