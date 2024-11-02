package router

import (
	"github.com/go-chi/chi/v5"

	"nomoni/src/handlers"
)

func SetTransactionsRouter() *chi.Mux {
	r := chi.NewRouter()

	var jobPost handlers.TransactionsHandler
	// r.Post("/", jobPost.Create)
	// r.Get("/{id:[0-9]+}", jobPost.GetById)
	r.Get("/", jobPost.GetAll)
	// r.Put("/{id:[0-9]+}/address", jobPost.SetAddress)
	// r.Put("/{id:[0-9]+}", jobPost.Update)
	return r
}
