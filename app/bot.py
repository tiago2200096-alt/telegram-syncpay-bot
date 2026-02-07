from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from app.config import settings

# Core do bot (NÃO coloque mídias aqui)
bot = Bot(token=settings.TELEGRAM_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

# Aqui a gente só registra os handlers
# (depois vamos criar/organizar handlers e mídias em arquivos separados)
