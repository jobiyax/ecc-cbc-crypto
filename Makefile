CC = gcc                # compilateur utilisé
CFLAGS = -Iinclude      # dossier des fichiers d'en-tête (.h)

# Fichiers source du projet
SRC = src/main.c \
      src/rsa_core.c \
      src/file_crypto.c \
      src/folder_crypto.c \
      src/utils.c

# Nom de l'exécutable
OUT = build/rsa

# Compilation du projet
all:
	mkdir -p build
	$(CC) $(SRC) $(CFLAGS) -o $(OUT)

# Supprime les fichiers générés
clean:
	rm -rf build

# Formate le code source
format:
	clang-format -i src/*.c include/*.h