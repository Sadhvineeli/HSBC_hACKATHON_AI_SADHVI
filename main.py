# chat_test.py

import os
from google import genai

# 1. Read your Gemini API key from the environment
API_KEY = os.getenv("AIzaSyBHDcjza9PLXJlKVoDkwSHDZZJ-JVKSlJY")
if not API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in your environment before running.")

# 2. Initialize the Gemini client
client = genai.Client()  # it picks up GEMINI_API_KEY automatically

# 3. System prompt to anchor the assistant’s behavior
SYSTEM_PROMPT = """
You are a secure banking assistant. You can:
 - Apply for loans
 - Block lost/stolen debit or credit cards
 - Fetch account balances, interest rates, and statements
Always ask follow-up questions if the user hasn’t provided all required info.
Handle mid-conversation context switches smoothly.
"""

def build_prompt(history):
    """
    Combines system prompt with the full chat history.
    History is a list of dicts: {"role": "user"|"assistant", "content": "..."}
    """
    prompt = SYSTEM_PROMPT.strip() + "\n\n"
    for turn in history:
        role = "User" if turn["role"] == "user" else "Assistant"
        prompt += f"{role}: {turn['content']}\n"
    prompt += "Assistant:"
    return prompt

def send_to_gemini(prompt: str) -> str:
    """
    Sends the full prompt to Gemini and returns the assistant’s reply.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()

def main():
    history = []
    print("🟢 Banking Chat Test (type 'exit' to quit)\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("🔴 Exiting chat. Goodbye!")
            break

        # Record user turn
        history.append({"role": "user", "content": user_input})

        # Build prompt & call Gemini
        prompt = build_prompt(history)
        bot_reply = send_to_gemini(prompt)

        # Record assistant turn & display
        history.append({"role": "assistant", "content": bot_reply})
        print(f"Bot: {bot_reply}\n")

if __name__ == "__main__":
    main()
