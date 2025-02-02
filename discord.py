import json
import time
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
# Token dan kunci API
discord_token = os.getenv('DISCORD_TOKEN')
google_api_key = os.getenv('GOOGLE_API_KEY')
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

# Set global untuk menyimpan ID pesan yang telah dibalas
last_message_id = None
bot_user_id = None

def log_message(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def generate_reply_google(prompt, api_key):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'contents': [
            {
                'parts': [
                    {
                        'text': prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log_message(f"Request failed: {e}")
        if response.content:
            log_message(f"Response content: {response.content.decode()}")
        return None

def generate_reply_openrouter(prompt, api_key):
    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "meta-llama/llama-3.1-70b-instruct:free",  # Model yang ingin digunakan
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        log_message(f"Request failed: {e}")
        if response.content:
            log_message(f"Response content: {response.content.decode()}")
        return None

def generate_reply(prompt, api_key, use_google_ai=True):
    if use_google_ai:
        result = generate_reply_google(prompt, api_key)
        if result:
            return result['candidates'][0]['content']['parts'][0]['text']
        return None
    else:
        return generate_reply_openrouter(prompt, api_key)

def send_reply(channel_id, message_id, response_text):
    headers = {
        'Authorization': f'{discord_token}',
        'Content-Type': 'application/json'
    }

    payload = {
        'content': response_text,
        'message_reference': {
            'message_id': message_id
        }
    }

    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", json=payload, headers=headers)
        response.raise_for_status()

        if response.status_code == 201:
            log_message(f"Replied with message: {response_text}")
        else:
            log_message(f"Failed to send reply: {response.status_code}")
            log_message(f"Response content: {response.content.decode()}")
    except requests.exceptions.RequestException as e:
        log_message(f"Request error: {e}")

def auto_reply(channel_id, read_delay, reply_delay):
    global last_message_id, bot_user_id

    headers = {
        'Authorization': f'{discord_token}'
    }

    try:
        bot_info_response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
        bot_info_response.raise_for_status()
        bot_user_id = bot_info_response.json().get('id')
    except requests.exceptions.RequestException as e:
        log_message(f"Failed to retrieve bot information: {e}")
        return

    while True:
        try:
            response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers)
            response.raise_for_status()

            if response.status_code == 200:
                messages = response.json()
                if len(messages) > 0:
                    most_recent_message = messages[0]
                    message_id = most_recent_message.get('id')
                    author_id = most_recent_message.get('author', {}).get('id')
                    message_type = most_recent_message.get('type', '')

                    if (last_message_id is None or int(message_id) > int(last_message_id)) and author_id != bot_user_id and message_type != 8:
                        user_message = most_recent_message.get('content', '')
                        log_message(f"Received message: {user_message}")

                        result = generate_reply(user_message, google_api_key if use_google_ai else openrouter_api_key, use_google_ai)

                        if result:
                            response_text = result
                            log_message(f"Waiting for {reply_delay} seconds before replying...")
                            time.sleep(reply_delay)
                            send_reply(channel_id, message_id, response_text)
                            last_message_id = message_id
            else:
                log_message(f'Failed to retrieve messages: {response.status_code}')

            log_message(f"Waiting for {read_delay} seconds before checking for new messages...")
            time.sleep(read_delay)
        except requests.exceptions.RequestException as e:
            log_message(f"Request error: {e}")
            time.sleep(read_delay)

if __name__ == "__main__":
    ai_choice = input("Pilih AI (Google Gemini (g) / OpenRouter (o)): ").lower()
    use_google_ai = ai_choice == 'g'
    channel_id = input("Masukkan ID channel: ")
    read_delay = int(input("Set Delay Membaca Pesan Terbaru (dalam detik): "))
    reply_delay = int(input("Set Delay Balas Pesan (dalam detik): "))

    log_message("Dimulai...")

    log_message("3")
    time.sleep(1)
    log_message("2")
    time.sleep(1)
    log_message("1")
    time.sleep(1)
    auto_reply(channel_id, read_delay, reply_delay)
