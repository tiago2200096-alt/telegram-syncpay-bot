from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings
from app.keyboards import menu_kb
from app import db
from app.syncpay import create_pix_cash_in
import re
import httpx

bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher()

PLANS = {
    "monthly": {"label": "Plano Mensal", "amount_brl": 29.90},
    "yearly":  {"label": "Plano Anual",  "amount_brl": 199.90},
}

def support_url() -> str:
    return f"https://t.me/{settings.SUPPORT_USERNAME.lstrip('@')}"

# -----------------------------
# Fluxo simples de coleta (sem FSM)
# -----------------------------
pending = {}  # user_id -> {"plan": "...", "cpf": "...", "phone": "...", "email": "..." }
step = {}     # user_id -> "cpf" | "phone" | "email"

def pay_kb(plan: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pagar", callback_data=f"pay:{plan}")],
        [InlineKeyboardButton(text="✅ Já paguei (verificar)", callback_data="check:soon")],
        [InlineKeyboardButton(text="🆘 Suporte", url=support_url())],
    ])

def digits_only(s: str) -> str:
    return re.sub(r"\D+", "", s or "")

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer("Bem-vindo! Escolha um plano:", reply_markup=menu_kb())

@dp.message(Command("suporte"))
async def suporte(m: Message):
    await m.answer(f"Fale com o suporte: {support_url()}")

@dp.message(Command("cancelar"))
async def cancelar(m: Message):
    pending.pop(m.from_user.id, None)
    step.pop(m.from_user.id, None)
    await m.answer("Ok! Operação cancelada. Use /start para começar de novo.")

@dp.callback_query(F.data.startswith("plan:"))
async def pick_plan(c: CallbackQuery):
    plan = c.data.split(":")[1]
    p = PLANS[plan]
    await c.message.answer(
        f"Você escolheu: {p['label']}\nValor: R$ {p['amount_brl']:.2f}\n\nClique em **Pagar**.",
        reply_markup=pay_kb(plan),
        parse_mode="Markdown"
    )
    await c.answer()

@dp.callback_query(F.data.startswith("pay:"))
async def pay(c: CallbackQuery):
    plan = c.data.split(":")[1]
    pending[c.from_user.id] = {"plan": plan}
    step[c.from_user.id] = "cpf"
    await c.message.answer(
        "Para gerar o Pix, me envie seu **CPF** (apenas números).\n\n"
        "Se quiser cancelar: /cancelar"
    )
    await c.answer()

@dp.message(F.text)
async def handle_text(m: Message):
    uid = m.from_user.id
    if uid not in step:
        return  # mensagem normal, ignora

    current = step[uid]
    text = (m.text or "").strip()

    if current == "cpf":
        cpf = digits_only(text)
        if len(cpf) != 11:
            return await m.answer("CPF inválido. Envie o CPF com **11 números** (somente números).")
        pending[uid]["cpf"] = cpf
        step[uid] = "phone"
        return await m.answer("Agora me envie seu **telefone com DDD** (somente números). Ex: 11999998888")

    if current == "phone":
        phone = digits_only(text)
        if len(phone) not in (10, 11):
            return await m.answer("Telefone inválido. Envie com DDD (10 ou 11 números). Ex: 11999998888")
        pending[uid]["phone"] = phone
        step[uid] = "email"
        return await m.answer("Agora me envie seu **e-mail**:")

    if current == "email":
        email = text
        if "@" not in email or "." not in email:
            return await m.answer("E-mail inválido. Envie um e-mail válido (ex: nome@email.com).")
        pending[uid]["email"] = email

        plan = pending[uid]["plan"]
        p = PLANS[plan]

        client = {
            "name": m.from_user.full_name,
            "cpf": pending[uid]["cpf"],
            "email": pending[uid]["email"],
            "phone": pending[uid]["phone"],
        }

        try:
            resp = await create_pix_cash_in(
                amount_brl=round(p["amount_brl"], 2),
                description=f"{p['label']} - Telegram {uid}",
                client_data=client
            )
        except httpx.HTTPStatusError as e:
            # Mostra uma mensagem amigável e deixa o erro nos logs do Render
            detail = ""
            try:
                detail = e.response.text
            except Exception:
                pass

            pending.pop(uid, None)
            step.pop(uid, None)

            return await m.answer(
                "❌ Não consegui gerar o Pix agora (erro da SyncPay).\n"
                "Tente novamente em instantes ou fale com o suporte:\n"
                f"{support_url()}\n\n"
                "Se quiser tentar de novo: /start"
            )

        pix_code = resp.get("pix_code")
        identifier = resp.get("identifier")

        # cria pedido no DB
        order_id = await db.create_order(
            user_id=uid,
            plan=plan,
            amount_cents=int(round(p["amount_brl"] * 100)),
            sync_identifier=identifier
        )

        pending.pop(uid, None)
        step.pop(uid, None)

        await m.answer(
            f"✅ Pedido criado: #{order_id}\n\n"
            f"📌 **Pix Copia e Cola:**\n`{pix_code}`\n\n"
            f"Após pagar, clique em **Suporte** e envie o número do pedido: #{order_id}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🆘 Suporte", url=support_url())]
            ])
        )
@dp.message(Command("getfileid"))
async def get_file_id(m: Message):
    if m.reply_to_message and m.reply_to_message.photo:
        file_id = m.reply_to_message.photo[-1].file_id
        await m.answer(f"Photo file_id:\n{file_id}")

    elif m.reply_to_message and m.reply_to_message.document:
        file_id = m.reply_to_message.document.file_id
        await m.answer(f"Document file_id:\n{file_id}")

    elif m.reply_to_message and m.reply_to_message.video:
        file_id = m.reply_to_message.video.file_id
        await m.answer(f"Video file_id:\n{file_id}")

    else:
        await m.answer("Responda a uma imagem, vídeo ou arquivo com /getfileid")
        
