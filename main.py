import asyncio
import logging

from dotenv import dotenv_values
from catbot import CatBot, OpenAiCatify

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


if __name__ == "__main__":
    config = dotenv_values()
    ai = OpenAiCatify(config)
    bot = CatBot(config, ai)
    bot.run()
