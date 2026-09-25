import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import yt_dlp

BOT_TOKEN = os.environ["BOT_TOKEN"]


async def download_video(url):
    filename = "video.%(ext)s"

    options = {
        "outtmpl": filename,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.startswith(("http://", "https://")):
        await update.message.reply_text("Video ka link bhejo.")
        return

    await update.message.reply_text("⏳ Video download ho rahi hai...")

    try:
        file_path = await asyncio.to_thread(download_video, text)

        await update.message.reply_video(
            video=open(file_path, "rb"),
            supports_streaming=True
        )

        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(
            "❌ Video download nahi ho saki.\n"
            "Link public aur downloadable hona chahiye."
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
