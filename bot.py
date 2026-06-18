import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {"role": "user", "content": user_text}
                ]
            },
            timeout=60
        )

        result = response.json()

        if "choices" in result:
            answer = result["choices"][0]["message"]["content"]
        else:
            answer = str(result)

    except Exception as e:
        answer = str(e)

    await update.message.reply_text(answer)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
    )

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()