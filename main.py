import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_reader import config
from hendlers import basic_handlers, macroscope_handler

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value(),
          default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def main():
    dp.include_router(macroscope_handler.router)
    dp.include_router(basic_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())