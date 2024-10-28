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
	ID     int64
	Date   string
	Amount float64
	Type   int16
}

// func getUsers() ([]User, error) {
// 	var users []User

// 	rows, err := db.Query("SELECT id, name, last_name FROM users")
// 	if err != nil {
// 		return nil, fmt.Errorf("getUsers %v", err)
// 	}
// 	defer rows.Close()

// 	for rows.Next() {
// 		var user User
// 		if err := rows.Scan(&user.ID, &user.Name, &user.LastName); err != nil {
// 			return nil, fmt.Errorf("getUsers %v", err)
// 		}
// 		users = append(users, user)
// 	}
// 	if err := rows.Err(); err != nil {
// 		return nil, fmt.Errorf("getUsers %v", err)
// 	}
// 	return users, nil
// }

func getTransactions() ([]Transaction, error) {
	var transactions []Transaction

	rows, err := db.Query("SELECT id, date, amount, type FROM transactions")
	if err != nil {
		return nil, fmt.Errorf("getTransactions %v", err)
	}
	defer rows.Close()

	for rows.Next() {
		var tran Transaction
		if err := rows.Scan(&tran.ID, &tran.Date, &tran.Amount, &tran.Type); err != nil {
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

	json.NewEncoder(w).Encode(transactions)
}

func main() {
	initDB()

	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Get("/", loadTransactions)

	http.ListenAndServe(":3000", r)
}
