import os
import telebot
from groq import Groq

# GitHub Secrets থেকে টোকেনগুলো রিড করবে
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

def ask_groq(prompt):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-70b-8192", # Groq এর অত্যন্ত ফাস্ট ও জনপ্রিয় মডেল
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"দুঃখিত, Groq API এর সাথে যোগাযোগ করতে সমস্যা হচ্ছে: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো! আমি Groq চালিত এআই বট। আমাকে যেকোনো প্রশ্ন করতে পারো।")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text
    # ইউজারকে টাইপিং স্ট্যাটাস দেখানো
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Groq থেকে উত্তর আনা
    groq_reply = ask_groq(user_message)
    bot.reply_to(message, groq_reply)

if __name__ == "__main__":
    print("Groq Telegram Bot is running via Polling...")
    bot.infinity_polling()
