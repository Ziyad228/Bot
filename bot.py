import telebot
from telebot import types

TOKEN = '7592227260:AAEaFQPZmZriULaP1IVPW9FTA4A42eMMx1k'
bot = telebot.TeleBot(TOKEN)

banned_users = set()
admins = [6593948633, 1279364480]

@bot.message_handler(commands=['start'])
def start_message(message):
    if message.from_user.id in banned_users:
        bot.send_message(message.chat.id, "Вы заблокированы в боте 🚫")
        return
    
    welcome_text = "Добро пожаловать! Если у вас есть вопросы по поводу клана ПГТ" Ильинский", нажмите на кнопку ниже."
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Связь с тех.поддержкой 📩", callback_data='support_request')
    markup.add(button)
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'support_request')
def handle_support_request(call):
    if call.from_user.id in banned_users:
        bot.send_message(call.message.chat.id, "Вы заблокированы в боте 🚫")
        return
    
    bot.send_message(call.message.chat.id, "Напишите свой запрос:")
    bot.register_next_step_handler(call.message, process_support_request)

def process_support_request(message):
    if message.from_user.id in banned_users:
        bot.send_message(message.chat.id, "Вы заблокированы в боте 🚫")
        return
    
    request_text = message.text
    request_info = f"ID: {message.from_user.id}\nUsername: @{message.from_user.username}\nЗапрос: {request_text}"
    
    for admin_id in admins:
        try:
            bot.get_chat_member(admin_id, admin_id)
            markup = types.InlineKeyboardMarkup()
            reply_button = types.InlineKeyboardButton("Ответить ✍️", callback_data=f'reply_{message.from_user.id}_{request_text}')
            ban_button = types.InlineKeyboardButton("Заблокировать 🚫", callback_data=f'ban_{message.from_user.id}')
            markup.add(reply_button, ban_button)
            bot.send_message(admin_id, request_info, reply_markup=markup)
        except Exception as e:
            print(f"Не удалось отправить сообщение администратору {admin_id}: {e}")
    
    bot.send_message(message.chat.id, "Ваш запрос отправлен. Пожалуйста, подождите ответ.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_reply_request(call):
    _, user_id, request_text = call.data.split('_', 2)
    bot.send_message(call.message.chat.id, "Напишите ответ:")
    bot.register_next_step_handler(call.message, process_reply, user_id)

def process_reply(message, user_id):
    bot.send_message(user_id, f"Ответ от админа: {message.text}")
    bot.send_message(message.chat.id, "Ответ отправлен пользователю.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('ban_'))
def handle_ban_request(call):
    user_id = call.data.split('_')[1]
    banned_users.add(int(user_id))
    bot.send_message(call.message.chat.id, f"Пользователь с ID {user_id} был заблокирован.")
    bot.send_message(user_id, "Вы заблокированы в боте 🚫")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "У вас нет прав для этой команды.")
        return

    try:
        user_id = int(message.text.split()[1])
        banned_users.discard(user_id)
        bot.send_message(message.chat.id, f"Пользователь с ID {user_id} был разблокирован.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Неверный формат команды. Используйте: /unban <user_id>")

bot.polling(none_stop=True)