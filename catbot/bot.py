import openai
from pydub import AudioSegment
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

from .open_ai import OpenAiCatify

class CatBot:
    def __init__(self, config: dict, catifier: OpenAiCatify):
        self.config = config
        self.catifier = catifier

    def run(self):
        """
        Runs the bot until interrupted by the user
        :return:
        """
        app = ApplicationBuilder().token(self.config["TOKEN"]).build()
        start_handler = CommandHandler("start", self.start)
        reply_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.reply)
        catify_handler = CommandHandler("catify", self.catify)
        voice_handler = MessageHandler(filters.VOICE | filters.AUDIO, self.voice_handler)
        unknown_handler = MessageHandler(filters.COMMAND, self.unknown)
        app.add_handler(start_handler)
        app.add_handler(catify_handler)
        app.add_handler(reply_handler)
        app.add_handler(voice_handler)
        app.add_handler(unknown_handler)
        app.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start the conversation
        :param update:
        :param context:
        :return:
        """
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="I'm a cat bot, please talk to me"
        )

    async def reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Command to reply to what the user was saying, in cat style
        :param update:
        :param context:
        :return:
        """
        message_text = update.message.text
        response = await self.catifier.reply(message_text)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=response
        )

    async def catify(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Command to send back the incoming message, but in cat style
        :param update:
        :param context:
        :return:
        """
        message_text = update.message.text
        response = await self.catifier.catify(message_text)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=response
        )

    async def voice_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_id = update.message.voice.file_id
        file_ogg = f"{file_id}.ogg"
        file_mp3 = f"{file_id}.mp3"
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(file_ogg)
        voice = AudioSegment.from_ogg(file_ogg).export(file_mp3, format="mp3")

        # Snippet from openai
        audio_file = open(file_mp3, "rb")
        transcript = (await openai.Audio.atranscribe("whisper-1", audio_file))["text"]
        print(transcript)
        cat_transcript = await self.catifier.catify(transcript)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=cat_transcript
        )

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, I didn't understand that command"
        )
