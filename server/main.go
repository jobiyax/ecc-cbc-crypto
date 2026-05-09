package main

import (
	"fmt"
	"net/http"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
	// Répond à la requête HTTP
	fmt.Fprintln(w, "Serveur Banda Kolela 🚀")
}

func main() {
	// Définit la route principale
	http.HandleFunc("/", helloHandler)

	// Démarre le serveur sur le port 8080
	http.ListenAndServe(":8080", nil)
}
