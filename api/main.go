package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	_ "github.com/lib/pq"
)

var db *sql.DB

type Transaction struct {
	ID          int64   `json:"id"`
	Date        string  `json:"date"`
	Amount      float64 `json:"amount"`
	Type        int16   `json:"type"`
	Description string  `json:"description"`
}

func getTransactions() ([]Transaction, error) {
	var transactions []Transaction

	rows, err := db.Query("SELECT id, to_char(date, 'YYYY-MM-DD HH24:MI:SS') AS date, amount, type, description FROM transactions")
	if err != nil {
		return nil, fmt.Errorf("getTransactions %v", err)
	}
	defer rows.Close()

	for rows.Next() {
		var tran Transaction
		if err := rows.Scan(&tran.ID, &tran.Date, &tran.Amount, &tran.Type, &tran.Description); err != nil {
			return nil, fmt.Errorf("getTransactions %v", err)
		}
		transactions = append(transactions, tran)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("getTransactions %v", err)
	}
	return transactions, nil
}

func initDB() {
	user := os.Getenv("DBUSER")
	password := os.Getenv("DBPASS")
	host := os.Getenv("DBHOST")
	database := os.Getenv("DBNAME")

	var err error
	connStr := fmt.Sprintf("postgres://%s:%s@%s/%s?sslmode=disable", user, password, host, database)
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}

	pingErr := db.Ping()
	if pingErr != nil {
		log.Fatal(pingErr)
	}
	fmt.Println("Connected!")
}

func loadTransactions(w http.ResponseWriter, r *http.Request) {
	transactions, err := getTransactions()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Users found: %v\n", transactions)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(transactions)
}

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

func main() {
	initDB()

	r := chi.NewRouter()
	r.Use(CorsMiddleware)

	r.Use(middleware.Logger)
	r.Get("/transactions", loadTransactions)

	http.ListenAndServe(":3000", r)
}
