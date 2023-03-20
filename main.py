import asyncio
import telegram
import os

from dotenv import dotenv_values


async def main():
    config = dotenv_values(".env")
    bot = telegram.Bot(config["TOKEN"])
    async with bot:
        print((await bot.get_updates())[0])
        await bot.send_message(
            text="Hi Johannes!",
            chat_id=config["CHAT_ID"]
        )

if __name__ == "__main__":
    asyncio.run(main())