package handlers

import (
	"encoding/json"
	"fmt"
	"net/http"
	"nomoni/src/models"
	"nomoni/src/repository"

	keys "nomoni/src/lib"

	_ "github.com/lib/pq"
)

type TransactionsHandler struct {
	*repository.TransactionsRepository
}

func (h *TransactionsHandler) GetAll(w http.ResponseWriter, r *http.Request) {
	loggedUserId := r.Context().Value(keys.LoggedUserId).(int)
	transactions, err := h.TransactionsRepository.GetAll(loggedUserId)
	if err != nil {
		fmt.Printf("Error %v", err)
		http.Error(w, "Could not find the transaction", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(transactions)
}

func (h *TransactionsHandler) Create(w http.ResponseWriter, r *http.Request) {
	loggedUserId := r.Context().Value(keys.LoggedUserId).(int)

	var reqTransaction models.RequestedTransaction
	decoder := json.NewDecoder(r.Body)

	if err := decoder.Decode(&reqTransaction); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	id, err := h.TransactionsRepository.Create(loggedUserId, reqTransaction)
	if err != nil {
		fmt.Printf("Error %v", err)
		http.Error(w, "Could create the transaction", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(id)
}
