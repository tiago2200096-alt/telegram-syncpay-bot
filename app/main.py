from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram.types import Update

from app.bot import bot, dp
from app.config import settings
from app.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await bot.set_webhook(settings.webhook_url)
    yield
    await bot.delete_webhook(drop_pending_updates=True)

app = FastAPI(lifespan=lifespan)

@app.post("/tg/webhook/{secret}")
async def telegram_webhook(secret: str, req: Request):
    if secret != settings.WEBHOOK_SECRET:
        return {"ok": False}
    data = await req.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
async def root():
    return {"status": "ok"}
  
