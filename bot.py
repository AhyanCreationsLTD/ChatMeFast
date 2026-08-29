import os
import telebot
import requests

# GitHub Secrets থেকে টোকেনগুলো রিড করবে
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
XAI_API_KEY = os.environ.get('XAI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# xAI Grok API Endpoint
XAI_URL = "https://api.x.ai/v1/chat/completions"

def ask_grok(prompt):
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-beta",  # বর্তমান গ্ৰক মডেল নাম
        "messages": [
            {"role": "system", "content": "You are a girl, your name is Mahmuda, a helpful AI assistant made by Ahyan."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(XAI_URL, json=payload, headers=headers)
        res_data = response.json()
        return res_data['choices'][0]['message']['content']
    except Exception as e:
        return f"দুঃখিত, গ্ৰক এআই এর সাথে যোগাযোগ করতে সমস্যা হচ্ছে: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(bot_instance, message):
    bot.reply_to(message, "হ্যালো! আমি মাহমুদা। আমাকে যেকোনো প্রশ্ন করতে পারো।")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text
    # ইউজারকে দেখানোর জন্য যে বট টাইপ করছে
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Grok থেকে উত্তর আনা
    grok_reply = ask_grok(user_message)
    bot.reply_to(message, grok_reply)

if __name__ == "__main__":
    print("Grok Telegram Bot is running via Polling...")
    bot.infinity_polling()
