import telebot
from datetime import datetime
from zoneinfo import ZoneInfo
from telebot import types
import json
import os

API_TOKEN = os.getenv("BOT_TOKEN")
# bot = telebot.TeleBot(API_TOKEN)

if not API_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = telebot.TeleBot(API_TOKEN)

USERS_FILE = "users.json"

ADMIN_CHAT_ID = 5926784842



def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users), f)

users = load_users()

#  START
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    if chat_id not in users:
        users.add(chat_id)
        save_users()
        

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("/help", "/contact", "/time", "/random", "/broadcast")

    if message.chat.id == ADMIN_CHAT_ID:
        keyboard.add("/users")

    bot.send_message(chat_id, "Welcome to the bot! You are now subscribed to updates.\nUse /help to see available commands.", reply_markup=keyboard)


# HELP
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = ("Available commands:\n/start - Start the bot\n/help - Show this help message\n/contact - Contact the owner\n/time - Get the current time\n/random - Get a random number")
    bot.reply_to(message, help_text)


#  CONTACT
@bot.message_handler(commands=['contact'])
def contact_owner(message):
    bot.reply_to(message, "Contact the owner at: @xasanov_a87")



# TIME
@bot.message_handler(commands=['time'])
def get_time(message):
    uz_timezone = ZoneInfo('Asia/Tashkent')
    uz_time = datetime.now(uz_timezone)
    formatted_time = uz_time.strftime("%A, %d.%m.%Y %H:%M:%S")
    bot.reply_to(message, f"Current time in Uzbekistan: {formatted_time}")



#  RANDOM
@bot.message_handler(commands=['random'])
def get_random_number(message):
    import random
    random_number = random.randint(1, 100)
    bot.reply_to(message, f"Random number: {random_number}")



#  BROADCAST
@bot.message_handler(commands=['broadcast'])
def send_broadcast(message):

    #  ADMIN_CHAT_ID = 5926784842

    if message.chat.id != ADMIN_CHAT_ID:
        bot.reply_to(message, f"You are not authorized to send broadcasts!")
        return
    
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        bot.reply_to(message, f"Please, write a message after /broadcast")
        return
    
    broadcast_text = parts[1]

    sent_count = 0

    for user_id in users:
        if user_id == ADMIN_CHAT_ID:
            continue

        try:
            bot.send_message(user_id, f"Announcement:\n{broadcast_text}")
            sent_count = sent_count + 1
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")

    bot.reply_to(message, f"Broadcast was successfully sent to {sent_count} users")


@bot.message_handler(commands=['users'])
def count_users(message):
    if message.chat.id != ADMIN_CHAT_ID:
        return
    
    bot.reply_to(message, f"Total number of bot users is {len(users)}")



print("Bot is running and listening for messages...")
bot.polling()