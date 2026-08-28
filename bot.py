import os
import logging
import asyncio
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

API_TOKEN = os.getenv('API_TOKEN')
LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

app = Flask(__name__)

class ChatState(StatesGroup):
    waiting_for_partner = State()
    in_chat = State()

waiting_queue = []
active_chats = {}

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add(
        types.KeyboardButton("🔍 Find New Friend"),
        types.KeyboardButton("ℹ️ Help")
    )
    return kb

def chat_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add(
        types.KeyboardButton("❌ End Chat")
    )
    return kb

@dp.message_handler(commands=['start'], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username or "N/A"

    try:
        await bot.send_message(
            LOG_CHANNEL_ID,
            f"👤 **New User Registered:**\n"
            f"• Name: {user_name}\n"
            f"• ID: `{user_id}`\n"
            f"• Username: @{username}"
        )
    except Exception as e:
        logging.error(f"Failed to log user: {e}")

    await message.answer(
        f"Welcome, {user_name}! 👋\n\n"
        "This bot allows you to chat anonymously with strangers. "
        "Click the button below to start:",
        reply_markup=main_menu()
    )

@dp.message_handler(text="🔍 Find New Friend", state="*")
async def find_friend(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id in active_chats:
        await message.answer("You are already in an active chat. End it first to find a new friend.")
        return

    if user_id in waiting_queue:
        await message.answer("You are already in the waiting queue, please wait...")
        return

    await message.answer("🔍 Searching for an anonymous friend...", reply_markup=chat_menu())
    await ChatState.waiting_for_partner.set()

    if waiting_queue:
        partner_id = waiting_queue.pop(0)
        
        if partner_id == user_id:
            waiting_queue.append(user_id)
            return

        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        try:
            await bot.send_message(user_id, "🎉 Partner found! You can now start chatting.", reply_markup=chat_menu())
            await bot.send_message(partner_id, "🎉 Partner found! You can now start chatting.", reply_markup=chat_menu())
        except Exception as e:
            logging.error(f"Error notifying matched users: {e}")
    else:
        waiting_queue.append(user_id)

@dp.message_handler(text="❌ End Chat", state="*")
async def stop_chat(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id in waiting_queue:
        waiting_queue.remove(user_id)
        await state.finish()
        await message.answer("Search cancelled.", reply_markup=main_menu())
        return

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        
        del active_chats[user_id]
        if partner_id in active_chats:
            del active_chats[partner_id]

        try:
            await bot.send_message(user_id, "⚠️ Chat ended. Click below to find a new friend.", reply_markup=main_menu())
            await bot.send_message(partner_id, "⚠️ Your partner has ended the chat. Find a new friend:", reply_markup=main_menu())
        except Exception as e:
            logging.error(f"Error ending chat: {e}")

    await state.finish()

@dp.message_handler(state=ChatState.in_chat, content_types=types.ContentTypes.ANY)
async def chat_proxy(message: types.Message):
    user_id = message.from_user.id

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            await message.send_copy(chat_id=partner_id)
        except Exception as e:
            await message.answer("⚠️ Message could not be sent. Partner may have left.")
            logging.error(f"Proxy error: {e}")
    else:
        await message.answer("You are not in an active chat. Click below to find a friend:", reply_markup=main_menu())

@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = types.Update.de_json(json_str)
    asyncio.run(dp.process_update(update))
    return 'OK', 200

@app.route('/')
def index():
    return "Telegram Anonymous Chat Bot is running on Vercel!"
  
