
import os
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "BOT_TOKEN"
OPENROUTER_API_KEY = "OPENROUTER_API_KEY"
REMOVE_BG_API_KEY = "REMOVE_BG_API_KEY"

user_photos = {}

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Telegram Bot\n\n"
        "Commands:\n"
        "/image <prompt> - Generate image\n"
        "/removebg - Remove background from last photo\n\n"
        "Or just send a text message to chat with AI.\n\n\n"
        "⚙ Website : https://omg10.com/4/11163312"
    )

# =========================
# AI CHAT
# =========================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly Telegram AI assistant. "
                            "Answer clearly and helpfully."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_text,
                    },
                ],
            },
            timeout=60,
        )

        data = response.json()

        if response.status_code != 200:
            answer = data.get("error", {}).get("message", "API Error")
        else:
            answer = data["choices"][0]["message"]["content"]

    except Exception as e:
        answer = f"Error: {e}"

    if len(answer) > 4000:
        answer = answer[:4000]

    await update.message.reply_text(answer)

# =========================
# SAVE PHOTO
# =========================

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    path = f"{update.effective_user.id}.jpg"
    await file.download_to_drive(path)

    user_photos[update.effective_user.id] = path

    await update.message.reply_text(
        "✅ Photo saved.\nUse /removebg\n\n\n⚙ Website : https://omg10.com/4/11163312"
    )

# =========================
# REMOVE BACKGROUND
# =========================

async def removebg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_photos:
        await update.message.reply_text("Send a photo first.\n\n\n⚙ Website : https://omg10.com/4/11163312")
        return

    image_path = user_photos[user_id]

    try:
        with open(image_path, "rb") as img:
            response = requests.post(
                "https://api.remove.bg/v1.0/removebg",
                files={"image_file": img},
                data={"size": "auto"},
                headers={"X-Api-Key": REMOVE_BG_API_KEY},
                timeout=120,
            )

        if response.status_code == 200:
            out_path = f"nobg_{user_id}.png"

            with open(out_path, "wb") as f:
                f.write(response.content)

            await update.message.reply_document(
                document=open(out_path, "rb"),
                filename="removed.png",
            )
        else:
            await update.message.reply_text(response.text)

    except Exception as e:
        await update.message.reply_text(str(e))

# =========================
# IMAGE GENERATOR
# =========================

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text(
            "Usage:\n/image a futuristic robot"
        )
        return

    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}"

        img = requests.get(url, timeout=120)

        file_path = f"img_{update.effective_user.id}.jpg"

        with open(file_path, "wb") as f:
            f.write(img.content)

        await update.message.reply_photo(
            photo=open(file_path, "rb")
        )

    except Exception as e:
        await update.message.reply_text(str(e))

# =========================
# MAIN
# =========================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(CommandHandler("removebg", removebg))

    app.add_handler(
        MessageHandler(filters.PHOTO, photo_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
