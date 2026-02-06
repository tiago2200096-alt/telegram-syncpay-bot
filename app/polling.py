import asyncio
from app.bot import bot, dp
from app.db import init_db

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
