# app.py

import re
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import bankapi

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

# Per‐user dialog state: intent name + collected slots
STATE = {}  # user_id -> {"intent": str|None, "slots": {}}

def get_state(user_id):
    return STATE.setdefault(user_id, {"intent": None, "slots": {}})

@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json(force=True)
    user_id = data.get("user_id", "user1")
    msg     = data.get("message", "").strip().lower()

    state   = get_state(user_id)
    intent  = state["intent"]
    slots   = state["slots"]

    # 1) GREETING
    if intent is None and msg in ("hi", "hello", "hey"):
        return jsonify({"reply":
          "Hi there 👋 How can I help?\n"
          "• Check account balance\n"
          "• Get a transaction statement\n"
          "• Block a card\n"
          "• Apply for a loan"
        })

    # 2) TRANSACTION STATEMENT FLOW
    if intent == "statement":
        # ask for start date
        if "start_date" not in slots:
            try:
                # validate YYYY-MM-DD
                datetime.strptime(msg, "%Y-%m-%d")
                slots["start_date"] = msg
                return jsonify({"reply":"Great—now please provide the end date (YYYY-MM-DD)."})
            except ValueError:
                return jsonify({"reply":"Invalid date. Enter start date as YYYY-MM-DD."})
        # ask for end date
        if "end_date" not in slots:
            try:
                datetime.strptime(msg, "%Y-%m-%d")
                slots["end_date"] = msg

                # both dates present → filter transactions
                start = datetime.strptime(slots["start_date"], "%Y-%m-%d").date()
                end   = datetime.strptime(slots["end_date"],   "%Y-%m-%d").date()
                txns  = bankapi.TRANSACTIONS.get(user_id, [])
                filtered = [t for t in txns if start <= t["date"] <= end]

                if filtered:
                    lines = [f"{t['date']}: {t['description']} {t['amount']:+}" for t in filtered]
                    reply = "Here are your transactions:\n" + "\n".join(lines)
                else:
                    reply = "No transactions found in that range."

                # clear state
                state["intent"] = None
                state["slots"]  = {}
                return jsonify({"reply": reply})

            except ValueError:
                return jsonify({"reply":"Invalid date. Enter end date as YYYY-MM-DD."})

    # detect start of statement flow
    if intent is None and ("statement" in msg or "transactions" in msg):
        state["intent"] = "statement"
        state["slots"]  = {}
        return jsonify({"reply":"Sure—please provide the start date (YYYY-MM-DD)."})


    # 3) CARD BLOCK FLOW
    if intent == "block_card":
        # we already have card_type slot
        if "last_four" not in slots:
            m = re.search(r"\b(\d{4})\b", msg)
            if m:
                slots["last_four"] = m.group(1)
                # perform block
                res = bankapi.block_card(user_id, slots["card_type"], slots["last_four"])
                # clear
                state["intent"] = None
                state["slots"]  = {}
                return jsonify({"reply": res.get("message", "Could not block card.")})
            else:
                return jsonify({"reply":"Please send the last four digits of your card."})

    # detect start of block flow
    if intent is None and "block" in msg and "card" in msg:
        # figure out debit vs credit
        if "debit" in msg:   slots["card_type"] = "debit"
        elif "credit" in msg: slots["card_type"] = "credit"
        else:                 slots["card_type"] = None

        state["intent"] = "block_card"
        # ask type if missing
        if slots["card_type"] is None:
            return jsonify({"reply":"Which card type—debit or credit?"})
        # else ask last four
        return jsonify({"reply":"Sure—what are the last four digits of the card?"})


    # 4) LOAN APPLICATION FLOW
    if intent == "apply_loan":
        # ask amount
        if "amount" not in slots:
            m = re.search(r"\b(\d+(\.\d{1,2})?)\b", msg)
            if m:
                slots["amount"] = float(m.group(1))
                return jsonify({"reply":"Got it. Over how many months would you like to repay?"})
            else:
                return jsonify({"reply":"Please tell me the loan amount (just numbers)."})
        # ask tenure
        if "tenure_months" not in slots:
            m = re.search(r"\b(\d+)\b", msg)
            if m:
                slots["tenure_months"] = int(m.group(1))
                # apply loan
                res = bankapi.apply_loan(user_id, slots["amount"], slots["tenure_months"])
                state["intent"] = None
                state["slots"]  = {}
                return jsonify({"reply": res.get("message", "Loan application failed.")})
            else:
                return jsonify({"reply":"Please specify repayment duration in months."})

    # detect start of loan flow
    if intent is None and ("loan" in msg or "apply" in msg):
        state["intent"] = "apply_loan"
        state["slots"]  = {}
        return jsonify({"reply":"Sure—how much would you like to borrow (in INR)?"})


    # 5) BALANCE (one‐shot)
    if intent is None and "balance" in msg:
        res = bankapi.get_balance(user_id)
        if res["status"] == "success":
            acct = bankapi.ACCOUNTS[user_id]
            return jsonify({"reply":
                f"Your {acct['account_type']} account balance is ₹{res['balance']} {res['currency']}."
            })
        else:
            return jsonify({"reply": res["message"]})

    # 6) FALLBACK HELP
    return jsonify({"reply":
      "Sorry, I didn’t understand that.\n"
      "You can say:\n"
      "• Check my balance\n"
      "• Get a transaction statement\n"
      "• Block a card\n"
      "• Apply for a loan\n"
      "• Or just say “Hi” for options."
    })


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:p>")
def static_file(p):
    return send_from_directory(app.static_folder, p)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
