import functools
import logging
from pathlib import Path

from pydub import AudioSegment
from telegram import Update
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)

from .ai import Catifier

class CatBot:
    """
    Telegram chatbot talking like a cat using ChatGPT
    """
    def __init__(self, config: dict, catifier: Catifier):
        """

        :param config: dict containing key value pairs of configuration variables
        :param catifier: ChatGPT helper class
        """
        self.config = config
        self.catifier = catifier

        self.allowed_users = self.config["ALLOWED_USERS"].split(",")

    def run(self):
        """
        Runs the bot until interrupted by the user
        """
        app = ApplicationBuilder().token(self.config["BOT_TOKEN"]).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.reply))
        app.add_handler(CommandHandler("catify", self.catify))
        app.add_handler(
            MessageHandler(filters.VOICE | filters.AUDIO, self.voice_handler)
        )
        app.add_handler(MessageHandler(filters.COMMAND, self.unknown))
        app.add_handler(CommandHandler("help", self.help))

        app.run_polling()

    @staticmethod
    def check_authorized(func):
        """
        Decorator for chatbot functions to add a check for user authorization
        """
        @functools.wraps(func)
        async def inner(self, *args, **kwargs):
            update = args[0]
            user_name = update.message.chat.username
            if user_name not in self.allowed_users:
                logging.warning(
                    f"Unauthorized access from user: {user_name})"
                )
                logging.info(f"Allowed users are: {self.allowed_users}")
                await update.message.reply_text(
                    "You are not allowed to use this method."
                )
                return
            return await func(self, *args, **kwargs)

        return inner

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Show helpful information on the options that this bot provides
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Help me!"
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start the conversation
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello there, I'm a cool cat AI assistant, here to help you out! I'm not lion when I say that"
                 " I'm ready to pounce on any task you may have for me!"
         )

    @check_authorized
    async def reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Command to reply to what the user was saying, in cat style
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        message_text = update.message.text
        response = await self.catifier.reply(message_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    @check_authorized
    async def catify(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Command to send back the incoming message, but in cat style
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        message_text = update.message.text
        response = await self.catifier.catify(message_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

    @check_authorized
    async def voice_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Command to handle an incoming voice message or audio file
        :param update: object representing an incoming update (e.g. a new message or an edited message)
        :param context:
        :return:
        """
        file_id = update.message.voice.file_id
        file_ogg = f"{file_id}.ogg"
        file_mp3 = f"{file_id}.mp3"
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(file_ogg)

        AudioSegment.from_ogg(file_ogg).export(file_mp3, format="mp3")
        audio_file = open(file_mp3, "rb")

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=self.catifier.transcribe(audio_file)
        )
        # clean up audio files
        Path(file_ogg).unlink(missing_ok=True)
        Path(file_mp3).unlink(missing_ok=True)

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Reply to an unknown command
        :param update:
        :param context:
        :return:
        """
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, I didn't understand that command",
        )
