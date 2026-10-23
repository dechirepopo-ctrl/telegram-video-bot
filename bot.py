
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
import yt_dlp

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك! 🎬\n\n"
        "أرسل لي أي رابط فيديو (يوتيوب، تيك توك، إنستغرام) وسأقوم بتحميله لك فوراً."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.message.chat_id
    
    if text.lower() == 'start':
        await start(update, context)
        return

    if not text.startswith("http"):
        await update.message.reply_text("الرجاء إرسال رابط فيديو صحيح يبدأ بـ http أو أرسل start للبدء.")
        return

    status_msg = await update.message.reply_text("⏳ جاري تحميل الفيديو، يرجى الانتظار...")
    output_filename = f"video_{chat_id}.mp4"

    ydl_opts = {
        'outtmpl': output_filename,
        'format': 'best[ext=mp4]/best',
        'no_warnings': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])
        
        if os.path.exists(output_filename):
            with open(output_filename, 'rb') as video_file:
                await context.bot.send_video(chat_id=chat_id, video=video_file)
            os.remove(output_filename)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ لم نتمكن من العثور على الفيديو.")

    except Exception as e:
        if os.path.exists(output_filename):
            os.remove(output_filename)
        await status_msg.edit_text("❌ حدث خطأ أثناء تحميل الفيديو. تأكد من صحة الرابط.")

if __name__ == '__main__':
    TOKEN = "8958964646:AAFv2W0zGBiWLbMlAhT7z-A3sG7d2FXukQo"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🤖 البوت يعمل بنجاح...")
    app.run_polling()
