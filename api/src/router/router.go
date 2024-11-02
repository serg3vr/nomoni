package router

import (
	"context"
	"fmt"
	"net/http"
	keys "nomoni/src/lib"

	"github.com/go-chi/chi/v5"
	// "github.com/go-chi/chi/v5/middleware"
	_ "github.com/lib/pq"
)

func CorsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Set CORS headers to allow requests from any origin
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Authorization, X-CSRF-Token")
		w.Header().Set("Allow-Control-Allow-Credentials", "false")

		// Handle preflight OPTIONS request
		if r.Method == http.MethodOptions {
			return
		}

		next.ServeHTTP(w, r)
	})
}

func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// bearerToken := r.Header.Get("Authorization")
		// splitBearerToken := strings.Fields(bearerToken)
		// var token string

		// if len(splitBearerToken) > 1 {
		// 	token = splitBearerToken[1]
		// }

		// symmetricKey, err := hex.DecodeString(config.SecretKey)
		// if err != nil {
		// 	fmt.Printf("Error: %v", err)
		// 	http.Error(w, "Could not decode key", http.StatusNotFound)
		// 	return
		// }

		// var jsonToken paseto.JSONToken
		// err = paseto.NewV2().Decrypt(token, symmetricKey, &jsonToken, nil)
		// if err != nil {
		// 	fmt.Printf("Error: %v", err)
		// 	http.Error(w, "Access is not authorized", http.StatusUnauthorized)
		// 	return
		// }

		// if time.Now().After(jsonToken.Expiration) {
		// 	http.Error(w, "Access is not authorized", http.StatusUnauthorized)
		// 	return
		// }

		// id, _ := strconv.Atoi(jsonToken.Get("Id"))
		id := 1

		ctx := context.WithValue(r.Context(), keys.LoggedUserId, id)

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

type RouteHandlers struct {
	Pattern string
	Handler *chi.Mux
}

func Start() {
	r := chi.NewRouter()

	r.Use(CorsMiddleware)

	r.Get("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Index"))
	})

	// r.Mount("/auth", SetAuthRouter())

	r.Group(func(r chi.Router) {
		r.Use(AuthMiddleware)
		routeHandlers := []RouteHandlers{
			{Pattern: "/transactions", Handler: SetTransactionsRouter()},
		}

		for _, rh := range routeHandlers {
			r.Mount(rh.Pattern, rh.Handler)
		}
	})

	fmt.Printf("Server running at 127.0.0.1:8090\n")
	http.ListenAndServe("127.0.0.1:8090", r)
}
