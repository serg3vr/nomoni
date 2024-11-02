package repository

import (
	"nomoni/config"
	"nomoni/src/models"

	_ "github.com/lib/pq"
)

type TransactionsRepository struct{}

func (jp *TransactionsRepository) GetAll(loggedUserId int) ([]models.ResponseTransaction, error) {
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
