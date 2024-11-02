package repository

import (
	"nomoni/config"
	"nomoni/src/models"

	_ "github.com/lib/pq"
)

type TransactionsRepository struct{}

func (r *TransactionsRepository) GetAll(loggedUserId int) ([]models.ResponseTransaction, error) {
	sqlStatement := `
		SELECT
			id,
			to_char(date, 'YYYY-MM-DD HH24:MI:SS') AS date,
			amount,
			type_id,
			description
		FROM transactions
		WHERE user_id = $1
		ORDER BY date DESC, id DESC
	`
	var data []models.ResponseTransaction
	rows, err := config.DB.Query(sqlStatement, loggedUserId)
	if err != nil {
		return data, err
	}
	for rows.Next() {
		var transaction models.ResponseTransaction
		err := rows.Scan(
			&transaction.Id,
			&transaction.Date,
			&transaction.Amount,
			&transaction.TypeId,
			&transaction.Description,
		)
		if err != nil {
			return data, err
		}
		data = append(data, transaction)
	}
	return data, err
}

func (r *TransactionsRepository) Create(loggedUserId int, transaction models.RequestedTransaction) (int, error) {
	sqlStatement := `
		insert into transactions(created_by, user_id, date, amount, type_id, description)
		values ($1, $2, $3, $4, $5, NULLIF($6, '')) returning id
	`
	var id int
	err := config.DB.QueryRow(
		sqlStatement,
		loggedUserId,
		loggedUserId,
		transaction.Date,
		transaction.Amount,
		transaction.TypeId,
		transaction.Description,
	).Scan(&id)

	return id, err
}
