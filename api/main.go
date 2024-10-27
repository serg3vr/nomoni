package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/lib/pq"
)

var db *sql.DB

type User struct {
	ID       int64
	Name     string
	LastName string
}

func getUsers() ([]User, error) {
	var users []User

	rows, err := db.Query("SELECT id, name, last_name FROM users")
	if err != nil {
		return nil, fmt.Errorf("getUsers %v", err)
	}
	defer rows.Close()

	for rows.Next() {
		var user User
		if err := rows.Scan(&user.ID, &user.Name, &user.LastName); err != nil {
			return nil, fmt.Errorf("getUsers %v", err)
		}
		users = append(users, user)
	}
	if err := rows.Err(); err != nil {
		return nil, fmt.Errorf("getUsers %v", err)
	}
	return users, nil
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

func main() {
	initDB()

	users, err := getUsers()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Users found: %v\n", users)
}
