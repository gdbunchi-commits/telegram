import os
import requests
from huggingface_hub import InferenceClient

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================
# CONFIG
# =========================


BOT_TOKEN = "7917133208:AAEs-BYLVzdyridkoJZScpQlB5LKwkwpVsw"
OPENROUTER_API_KEY = "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"
REMOVE_BG_API_KEY = "CMj4qzQkFnvxm24ZsrS5Zbho"
HF_API_KEY = "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"

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Assistant Bot\n\n"
        "Commands:\n"
        "/image <prompt> - Generate image\n\n"
        "Send text = AI Chat\n"
        "Send photo = Remove Background"
    )

# =========================
# AI CHAT
# =========================

async def chat_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "user", "content": user_text}
                ]
            },
            timeout=120,
        )

        data = response.json()

        if "choices" not in data:
            await update.message.reply_text(str(data))
            return
        reply = data["choices"][0]["message"]["content"]
        reply += (
            "\n\n🌐 Visit:\n"
            "https://omg10.com/4/11163312"
            )
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# =========================
# IMAGE GENERATOR
# =========================

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    prompt = " ".join(context.args)

    if not prompt:
        await update.message.reply_text(
            "Usage:\n/image astronaut riding horse"
        )
        return

    try:
        await update.message.reply_text(
            "🎨 Generating image..."
        )

        client = InferenceClient(
            provider="fal-ai",
            api_key=HF_API_KEY,
        )

        image = client.text_to_image(
            prompt,
            model="davisbro/half_illustration",
        )

        image_path = "generated.png"

        image.save(image_path)

        with open(image_path, "rb") as img:
            await update.message.reply_photo(
                photo=img,
                caption=f"🎨 {prompt}"
            )

    except Exception as e:
        await update.message.reply_text(
            f"Image Error:\n{e}"
        )

# =========================
# BACKGROUND REMOVER
# =========================

async def remove_background(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        await update.message.reply_text(
            "⏳ Removing background..."
        )

        photo = update.message.photo[-1]

        tg_file = await context.bot.get_file(
            photo.file_id
        )

        input_path = "input.jpg"
        output_path = "removed.png"

        await tg_file.download_to_drive(
            custom_path=input_path
        )

        with open(input_path, "rb") as image_file:

            response = requests.post(
                "https://api.remove.bg/v1.0/removebg",
                files={
                    "image_file": image_file
                },
                data={
                    "size": "auto"
                },
                headers={
                    "X-Api-Key": REMOVE_BG_API_KEY
                },
                timeout=300,
            )

        if response.status_code == 200:

            with open(output_path, "wb") as out:
                out.write(response.content)

            with open(output_path, "rb") as img:

                await update.message.reply_photo(
                    photo=img,
                    caption="✅ Background Removed"
                )

        else:
            await update.message.reply_text(
                f"Remove.bg Error:\n{response.text}"
            )

    except Exception as e:
        await update.message.reply_text(
            f"Error: {e}"
        )

# =========================
# MAIN
# =========================

def main():

    if not BOT_TOKEN:
        print("BOT_TOKEN missing")
        return

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("image", image_command)
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            remove_background
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat_with_ai
        )
    )

    print("Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()