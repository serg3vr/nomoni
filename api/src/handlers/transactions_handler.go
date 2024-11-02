package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"nomoni/src/repository"

	keys "nomoni/src/lib"

	_ "github.com/lib/pq"
)

type TransactionsHandler struct {
	*repository.TransactionsRepository
}

func (h *TransactionsHandler) GetAll(w http.ResponseWriter, r *http.Request) {
	loggedUserId := r.Context().Value(keys.LoggedUserId).(int)
	dbJobPosts, err := h.TransactionsRepository.GetAll(loggedUserId)
	if err != nil {
		fmt.Printf("Error %v", err)
		http.Error(w, "Could not find the post", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(dbJobPosts)
}
