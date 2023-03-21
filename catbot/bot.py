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
        cat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.catify)
        unknown_handler = MessageHandler(filters.COMMAND, self.unknown)
        app.add_handler(start_handler)
        app.add_handler(cat_handler)
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

    async def catify(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Command to send back what a person was saying, but in all caps
        :param update:
        :param context:
        :return:
        """
        message_text = update.message.text
        response = await self.catifier.catify(message_text)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=response
        )

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, I didn't understand that command"
        )
