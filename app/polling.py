import asyncio
from app.bot import bot, dp
from app.db import init_db
from app.media_store import init_media_db


async def main():
    # Garante que não existe webhook e limpa fila antiga
    await bot.delete_webhook(drop_pending_updates=True)

    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
