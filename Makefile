CC = gcc                # Compilateur utilisé
CFLAGS = -Iinclude      # Dossier des fichiers d'en-tête (.h)

SRC = src/main.c src/rsa.c src/utils.c   # Fichiers source
OUT = build/rsa                          # Nom de l'exécutable

# Compilation du projet
all:
	mkdir -p build
	$(CC) $(SRC) $(CFLAGS) -o $(OUT)

# Compile et lance le programme
run: all
	./$(OUT)

# Supprime les fichiers générés
clean:
	rm -rf build

# Formate le code source
format:
	clang-format -i src/*.c include/*.h