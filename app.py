from flask import Flask, request, jsonify
import requests
import openai
import os
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)

# BestCRM API credentials from environment variables
BESTCRM_API_URL = "https://app.bestcrmapp.in/api/v2/whatsapp-business/messages"
ACCESS_TOKEN = os.environ.get("BESTCRM_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# OpenAI API key from environment
openai.api_key = os.environ.get("OPENAI_API_KEY")

def send_whatsapp_message(to_number, message):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": to_number,
        "phoneNoId": PHONE_NUMBER_ID,
        "type": "text",
        "text": message
    }
    try:
        response = requests.post(BESTCRM_API_URL, headers=headers, json=payload, verify=False)
        print("BestCRM API status:", response.status_code)
        print("BestCRM API response:", response.text)
        return response.json()
    except requests.exceptions.RequestException as e:
        print("BestCRM Request Error:", e)

def get_openai_response(prompt_text):
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_text}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print("OpenAI Error:", e)
        return "Sorry, I couldn't process your request right now."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received:", data)

    try:
        phone_number = data['data']['senderPhoneNumber']
        message_text = data['data']['content']['text'].strip()

        if message_text.lower().startswith("cyber genie,"):
            user_prompt = message_text[len("Cyber Genie,"):].strip()
            reply = get_openai_response(user_prompt)
        else:
            reply = "Please start your message with 'Cyber Genie,' to get a response."

        send_whatsapp_message(phone_number, reply)
    except Exception as e:
        print("Webhook Error:", e)

    return jsonify(status="success"), 200
    
@app.route("/", methods=["GET"])
def index():
    return "Cyber Genie bot is running!", 200
    
# ✅ Use this for Railway production
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

