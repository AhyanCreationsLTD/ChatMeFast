import telebot
from groq import Groq

TELEGRAM_TOKEN = "8858810262:AAF14gSU22mPmxL9342fiX-VdjxIVhbNS_A" # আপনার টেলিগ্রাম টোকেন দিন
GROQ_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

# বর্তমান সময়ের লেটেস্ট এবং সচল মডেলগুলোর লিস্ট
GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b"
]

def ask_groq(prompt):
    for model_name in GROQ_MODELS:
        try:
            print(f"Trying model: {model_name}...")
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Answer accurately in Bengali.",
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
            print(f"Error with model {model_name}: {str(e)}")
            continue
            
    return "দুঃখিত, বর্তমানে Groq-এর কোনো মডেল দিয়েই রেসপন্স পাওয়া যাচ্ছে না।"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো! আমি রেডি আছি।")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    groq_reply = ask_groq(user_message)
    bot.reply_to(message, groq_reply)

if __name__ == "__main__":
    print("Bot is running with latest models...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
