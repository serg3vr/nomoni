export interface UserOut {
  id: string;
  email: string;
  name: string | null;
  currency: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Category {
  id: string;
  name: string;
  type: string;
  color: string | null;
  hidden: boolean;
  is_system: boolean;
}

export interface Wallet {
  id: string;
  name: string;
  type: string;
  initial_balance: number;
  hidden: boolean;
  is_system: boolean;
}

export interface WalletBalance {
  id: string;
  name: string;
  type: string;
  initial_balance: number;
  spent: number;
  balance: number;
}

export interface Transaction {
  id: string;
  amount: number;
  note: string | null;
  category_id: string | null;
  wallet_id: string | null;
  occurred_at: string;
}

export interface TransactionFilters {
  year?: number | undefined;
  month?: number | undefined;
  category_id?: string | undefined;
  wallet_id?: string | undefined;
  pending?: boolean | undefined;
}
