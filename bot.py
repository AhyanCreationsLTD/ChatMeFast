import telebot
from groq import Groq

# সরাসরি আপনার টোকেনগুলো এখানে বসিয়ে দিন
TELEGRAM_TOKEN = "8858810262:AAF14gSU22mPmxL9342fiX-VdjxIVhbNS_A" # আপনার আসল টেলিগ্রাম টোকেন দিন
GROQ_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

# কার্যকর মডেলগুলোর তালিকা (Fallback Order অনুযায়ী সাজানো)
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

def ask_groq(prompt):
    # তালিকার মডেলগুলো একে একে ট্রাই করবে
    for model_name in GROQ_MODELS:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Your name is Aira, you are a girl AI made by Ahyan",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model_name,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            # যদি বর্তমান মডেলে এরর বা ডিকমিশনের সমস্যা হয়, তবে লুপ পরের মডেলে চলে যাবে
            continue
            
    return "দুঃখিত, বর্তমানে আমার মন ভালো নেই, কথা বলতে ইচ্ছা করছে না।"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো! আমার নাম আইরা। বলুন, আপনাকে কীভাবে সাহায্য করতে পারি?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    groq_reply = ask_groq(user_message)
    bot.reply_to(message, groq_reply)

if __name__ == "__main__":
    print("Multi-model Groq Telegram Bot is running via Polling...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
