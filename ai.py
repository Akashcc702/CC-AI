import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# ---------------- WEB SERVER ----------------
app_web = Flask('')

@app_web.route('/')
def home():
    return "CC AI Bot Running"

def run():
    app_web.run(host='0.0.0.0', port=8080, use_reloader=False)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- AI CLIENT ----------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# memory store
user_memory = {}

# ---------------- START COMMAND ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Hello! I am CC AI Bot.\nAsk me anything.")

# ---------------- MESSAGE HANDLER ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.chat_id
    user_input = update.message.text

    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="nvidia/nemotron-nano-9b-v2:free",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."}
        ] + user_memory[user_id]
    )

    ai_reply = response.choices[0].message.content

    user_memory[user_id].append({"role": "assistant", "content": ai_reply})

    await update.message.reply_text(ai_reply)

# ---------------- BOT START ----------------
keep_alive()

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("CC AI Bot Running...")

app.run_polling()
