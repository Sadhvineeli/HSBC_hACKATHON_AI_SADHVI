# HSBC_hACKATHON_AI_SADHVI
# Banking Chatbot PoC

An end-to-end prototype of a conversational banking assistant supporting:

- **Goal-driven workflows**
  - Check account balance
  - Fetch transaction statements for a custom date range
  - Block lost/stolen debit or credit cards
  - Apply for personal loans
- **Multi-turn dialogues** with slot collection and validation
- **In-memory “bank” API** (`bankapi.py`) simulating real operations
- **Flask backend** (`app.py`) exposing a `/api/chat` endpoint and serving a static frontend
- **Rich single-page UI** (`frontend/index.html`) with two-tier header, hero promo, and floating chat widget
- ** LLM integration** via function-calling (e.g. Google Gemini) to replace regex logic for intent & slot handling

---

## 📁 Repository Structure

```
.
├── app.py
├── bankapi.py
├── frontend
│   ├── index.html
│   ├── hsbc_logo.png
│   ├── ru_pay_card.png
│   └── swirl_bg.png       # optional background graphic
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

1. **Clone** this repository
   ```bash
   git clone https://github.com/your-org/banking-chatbot-poc.git
   cd banking-chatbot-poc
   ```

2. **Create & activate** a Python 3.9+ virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows
   ```

3. **Install** dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. **Run** the Flask app
   ```bash
   python app.py
   ```

5. **Open** your browser at `http://127.0.0.1:8000/`

---

## 🛠️ How It Works

- **Frontend**
  - Served from `frontend/index.html`.
  - Contains a two-tier header, hero promo section, and a floating chat widget.
  - User messages are **POST**ed to `/api/chat` and responses rendered in the UI.

- **Backend**
  - `app.py` uses Flask (with CORS) to serve static files and handle chat requests.
  - A **Dialog Manager** tracks per-user state (`intent` & `slots`) in memory for multi-turn flows.
  - Simple NLU via keyword checks and regular expressions.
  - `bankapi.py` provides simulated banking functions:
    - `get_balance(user_id)`
    - `get_statement(user_id, period_days)`
    - `block_card(user_id, card_type, last_four)`
    - `apply_loan(user_id, amount, tenure_months)`

- **LLM Mode**
  - Swap regex/dialog logic in `app.py` for the Google Gemini function-calling example.
  - Define each banking operation as a JSON-schema “function” and let the LLM orchestrate calls.

---




