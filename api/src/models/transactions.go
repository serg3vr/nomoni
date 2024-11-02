package models

import (
	"time"
)

type RequestedTransaction struct {
	Id          int64   `json:"id"`
	Date        string  `json:"date"`
	Amount      float64 `json:"amount"`
	TypeId      int64   `json:"type"`
	Description *string `json:"description"`
}

type ResponseTransaction struct {
	Id          int64   `json:"id"`
	Date        string  `json:"date"`
	Amount      float64 `json:"amount"`
	TypeId      int64   `json:"type"`
	Description *string `json:"description"`
}

type DBTransaction struct {
	Id          int64      `json:"id"`
	CreatedAt   time.Time  `json:"created_at"`
	CreatedBy   int        `json:"created_by"`
	UpdatedAt   *time.Time `json:"updated_at"`
	UpdatedBy   *int       `json:"updated_by"`
	UserId      int64      `json:"user_id"`
	Date        string     `json:"date"`
	Amount      float64    `json:"amount"`
	TypeId      int64      `json:"type"`
	Description *string    `json:"description"`
}
