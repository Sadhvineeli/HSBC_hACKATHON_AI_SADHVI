# bankapi.py

import uuid
from datetime import datetime, timedelta

# Dummy customer
CUSTOMERS = {
    "user1": {"name": "Alice", "email": "alice@example.com", "phone": "1234567890"}
}

# Dummy account balances
ACCOUNTS = {
    "user1": {"account_type": "savings", "balance": 12500.75}
}

# Dummy cards
CARDS = {
    "user1": {
        "debit":  {"last_four": "4567", "is_blocked": False, "issued_at": datetime.now()},
        "credit": {"last_four": "9876", "is_blocked": False, "issued_at": datetime.now()}
    }
}

# Dummy loans
LOANS = {}

# Dummy transactions
TRANSACTIONS = {
    "user1": [
        {"date": datetime.now().date(), "description": "Salary Credit",  "amount": 50000.0},
        {"date": (datetime.now() - timedelta(days=5)).date(), "description": "ATM Withdrawal", "amount": -2000.0}
    ]
}

def get_balance(user_id: str) -> dict:
    acct = ACCOUNTS.get(user_id)
    if acct:
        return {"status": "success", "balance": acct["balance"], "currency": "INR"}
    return {"status": "error",   "message": "Account not found"}

def get_statement(user_id: str, period_days: int = 30) -> dict:
    txns = TRANSACTIONS.get(user_id, [])
    cutoff = datetime.now().date() - timedelta(days=period_days)
    filtered = [t for t in txns if t["date"] >= cutoff]
    return {"status": "success", "transactions": filtered}

def block_card(user_id: str, card_type: str, last_four: str) -> dict:
    user_cards = CARDS.get(user_id, {})
    card = user_cards.get(card_type)
    if card and card["last_four"] == last_four:
        card["is_blocked"] = True
        block_id = f"BLOCK-{uuid.uuid4().hex[:8].upper()}"
        return {
            "status": "success",
            "message": f"{card_type.title()} card ending in {last_four} blocked.",
            "block_id": block_id
        }
    return {"status":"error", "message":"Card not found or type mismatch"}

def apply_loan(user_id: str, amount: float, tenure_months: int) -> dict:
    loan_id = f"LOAN-{uuid.uuid4().hex[:8].upper()}"
    rec = {
        "loan_id":     loan_id,
        "amount":      amount,
        "tenure_months": tenure_months,
        "status":      "PENDING",
        "applied_at":  datetime.now()
    }
    LOANS.setdefault(user_id, []).append(rec)
    return {
        "status":    "success",
        "message":   f"Loan of ₹{amount} for {tenure_months} months submitted.",
        "request_id": loan_id
    }
