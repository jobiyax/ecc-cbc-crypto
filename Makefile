# Compilateur C
CC = gcc

# Dossier des headers (.h)
CFLAGS = -Iinclude

# Fichiers source C
SRC = src/main.c \
      src/rsa_core.c \
      src/file_crypto.c \
      src/folder_crypto.c \
      src/utils.c

# Exécutable C
OUT = build/rsa

# Build projet C
build-c:
	mkdir -p build
	$(CC) $(SRC) $(CFLAGS) -o $(OUT)

# Nettoyage
clean:
	rm -rf build

# Formatage du code C
format:
	clang-format -i src/*.c include/*.h

# Run serveur Go
run-go:
	go run server/main.go

# Build serveur Go
build-go:
	mkdir -p build
	go build -o build/server server/main.go
