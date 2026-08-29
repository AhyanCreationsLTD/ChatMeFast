import os
import telebot
from groq import Groq

# সরাসরি আপনার ভেরিফাইড টোকেনটি এখানে বসিয়ে দিন
TELEGRAM_TOKEN = "8858810262:AAF14gSU22mPmxL9342fiX-VdjxIVhbNS_A" # আপনার পুরো টোকেনটি এখানে বসাবেন
GROQ_API_KEY = "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"

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
            model="llama3-70b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"দুঃখিত, Groq API এর সাথে যোগাযোগ করতে সমস্যা হচ্ছে: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো! আমি আপনার Groq এআই বট। বলুন, কীভাবে সাহায্য করতে পারি?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    groq_reply = ask_groq(user_message)
    bot.reply_to(message, groq_reply)

if __name__ == "__main__":
    print("Bot is starting polling...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
