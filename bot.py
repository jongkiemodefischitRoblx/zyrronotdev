import json
import os
from telebot import TeleBot, types

# =========================
# CONFIG
# =========================
PASSWORD = "Zyrroganteng"
BOT_TOKEN = "YOUR_ZYRROBUTTONBOT_TOKEN_HERE"
DEVELOPER_ID = 123456789  # <-- Masukkan ID Telegram developer kamu di sini
PRICE_PER_BUTTON = 5000

DB_FILE = "db.json"
bot = TeleBot(BOT_TOKEN)

# =========================
# DATABASE
# =========================
def load_db():
    if not os.path.exists(DB_FILE):
        return {"developer": DEVELOPER_ID, "users": [], "admins": [], "button_data": {}, "links_final": {}, "shutdown": {"status": False, "message": ""}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

db = load_db()

# =========================
# USER AUTH
# =========================
user_auth = {}

# =========================
# HELPERS
# =========================
def is_admin(user_id):
    return user_id == db.get('developer', 0) or user_id in db['admins']

def shutdown_mode():
    return db['shutdown']['status']

# =========================
# START / LOGIN
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    if shutdown_mode():
        bot.send_message(message.chat.id, f"⚠ BOT SEDANG TIDAK AKTIF\n\n{db['shutdown']['message']}")
        return

    user_auth[message.chat.id] = False
    bot.send_message(message.chat.id, "[ WELCOME TO ZYRROBUTTONBOT ]\n\nMasukan Pw:")
    bot.register_next_step_handler(message, check_pw)

def check_pw(message):
    if message.text == PASSWORD:
        user_auth[message.chat.id] = True
        main_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Password salah! Coba lagi /start")

# =========================
# MAIN MENU
# =========================
def main_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("➕ Add Button", callback_data="addbutton")
    btn2 = types.InlineKeyboardButton("📢 Broadcast", callback_data="krl")
    btn3 = types.InlineKeyboardButton("🔗 Add Link Final", callback_data="addlink")
    btn4 = types.InlineKeyboardButton("❌ Shutdown Semua Bot", callback_data="shutdown")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)

    bot.send_message(chat_id, "Developer Panel:\nSilakan pilih menu:", reply_markup=markup)

# =========================
# CALLBACK HANDLER
# =========================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if not user_auth.get(call.message.chat.id, False):
        bot.answer_callback_query(call.id, "Akses ditolak")
        return

    if call.data == "addbutton":
        bot.send_message(call.message.chat.id, "Format: /addbutton jumlah token link_misi")

    elif call.data == "krl":
        bot.send_message(call.message.chat.id, "Format broadcast: /krl teks")

    elif call.data == "addlink":
        bot.send_message(call.message.chat.id, "Format: /addlink link_final token_bot")

    elif call.data == "shutdown":
        bot.send_message(call.message.chat.id, "Format: /shutdown pesan_shutdown")

# =========================
# COMMANDS
# =========================
@bot.message_handler(commands=['addbutton'])
def add_button(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Kamu bukan admin")
        return
    try:
        parts = message.text.split()
        jumlah = int(parts[1])
        token = parts[2]
        link_misi = parts[3]
        if token not in db['button_data']:
            db['button_data'][token] = []
        for _ in range(jumlah):
            db['button_data'][token].append(link_misi)
        save_db(db)
        total_harga = jumlah * PRICE_PER_BUTTON
        bot.reply_to(message, f"✔ Berhasil menambah {jumlah} button ke {token}\nTotal Harga: {total_harga}")
    except:
        bot.reply_to(message, "Format salah! /addbutton jumlah token link_misi")

@bot.message_handler(commands=['deletebutton'])
def delete_button(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Kamu bukan admin")
        return
    try:
        parts = message.text.split()
        jumlah = int(parts[1])
        token = parts[2]
        if token in db['button_data']:
            db['button_data'][token] = db['button_data'][token][:-jumlah]
            save_db(db)
        bot.reply_to(message, f"✔ Berhasil mengurangi {jumlah} button dari {token}")
    except:
        bot.reply_to(message, "Format salah! /deletebutton jumlah token")

@bot.message_handler(commands=['addlink'])
def add_link(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Kamu bukan admin")
        return
    try:
        parts = message.text.split()
        link = parts[1]
        token = parts[2]
        db['links_final'][token] = link
        save_db(db)
        bot.reply_to(message, f"✔ Link final berhasil ditambahkan untuk {token}")
    except:
        bot.reply_to(message, "Format salah! /addlink link_final token_bot")

@bot.message_handler(commands=['krl'])
def krl(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Kamu bukan admin")
        return
    try:
        text = ' '.join(message.text.split()[1:])
        sent = 0
        for uid in db['users']:
            try:
                bot.send_message(uid, text)
                sent += 1
            except:
                pass
        bot.reply_to(message, f"✔ Broadcast terkirim ke {sent} user")
    except:
        bot.reply_to(message, "Format salah! /krl teks")

@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Kamu bukan admin")
        return
    msg = ' '.join(message.text.split()[1:])
    db['shutdown']['status'] = True
    db['shutdown']['message'] = msg
    save_db(db)
    bot.reply_to(message, f"✔ Semua bot dimatikan dengan pesan: {msg}")

@bot.message_handler(commands=['unshutdown'])
def unshutdown(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ Kamu bukan admin")
        return
    db['shutdown']['status'] = False
    db['shutdown']['message'] = ''
    save_db(db)
    bot.reply_to(message, f"✔ Semua bot diaktifkan kembali")

# =========================
# RUN BOT
# =========================
print("ZyrroButtonBot aktif...")
bot.infinity_polling()
