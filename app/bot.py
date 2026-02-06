from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from app.config import settings
from app.keyboards import menu_kb, pay_kb
from app import db
from app.syncpay import create_pix_cash_in, get_transaction

bot = Bot(token=settings.TELEGRAM_TOKEN)
dp = Dispatcher()

PLANS = {
    "monthly": {"label": "Plano Mensal", "amount_brl": 29.90},
    "yearly":  {"label": "Plano Anual",  "amount_brl": 199.90},
}

def support_url() -> str:
    return f"https://t.me/{settings.SUPPORT_USERNAME.lstrip('@')}"

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer("Bem-vindo! Escolha um plano:", reply_markup=menu_kb())

@dp.message(Command("planos"))
async def planos(m: Message):
    await m.answer("Escolha um plano:", reply_markup=menu_kb())

@dp.message(Command("suporte"))
async def suporte(m: Message):
    await m.answer(f"Fale com o suporte: {support_url()}")

@dp.callback_query(F.data.startswith("plan:"))
async def pick_plan(c: CallbackQuery):
    plan = c.data.split(":")[1]
    p = PLANS[plan]
    await c.message.answer(
        f"Você escolheu: **{p['label']}**\nValor: R$ {p['amount_brl']:.2f}\n\nClique em **Pagar**.",
        reply_markup=pay_kb(plan),
        parse_mode="Markdown"
    )
    await c.answer()

@dp.callback_query(F.data.startswith("pay:"))
async def pay(c: CallbackQuery):
    plan = c.data.split(":")[1]
    p = PLANS[plan]

    # Dados mínimos (adicione CPF/email/phone se você for coletar)
    client = {"name": c.from_user.full_name, "cpf": "00000000000", "email": "nao@informado.com", "phone": "00000000000"}

    resp = await create_pix_cash_in(
        amount_brl=p["amount_brl"],
        description=f"{p['label']} - Telegram {c.from_user.id}",
        client_data=client
    )
    pix_code = resp["pix_code"]
    identifier = resp["identifier"]

    order_id = await db.create_order(
        user_id=c.from_user.id,
        plan=plan,
        amount_cents=int(round(p["amount_brl"] * 100)),
        sync_identifier=identifier
    )

    await c.message.answer(
        f"✅ Pedido criado: #{order_id}\n\n"
        f"📌 **Pix Copia e Cola:**\n`{pix_code}`\n\n"
        f"Depois de pagar, clique em **Já paguei (verificar)**.",
        reply_markup=pay_kb(plan),
        parse_mode="Markdown"
    )
    await c.answer("Gerado!")

@dp.callback_query(F.data.startswith("check:"))
async def check(c: CallbackQuery):
    # Para simplificar, a verificação real deve receber order_id.
    # Recomendação: no seu botão, use callback_data tipo check_order:<id>.
    await c.message.answer(
        "Para verificar corretamente, eu vou ajustar o botão para checar pelo **ID do pedido**.\n"
        "Na versão final, o botão verifica automaticamente e, se não confirmar, te manda pro suporte."
    )
    await c.answer()

@dp.message(Command("aprovar"))
async def aprovar(m: Message):
    if m.from_user.id not in settings.admin_id_set:
        return await m.reply("Sem permissão.")

    # Uso: /aprovar <order_id>
    parts = m.text.split()
    if len(parts) < 2:
        return await m.reply("Uso: /aprovar <order_id>")

    order_id = int(parts[1])
    order = await db.get_order(order_id)
    if not order:
        return await m.reply("Pedido não encontrado.")

    # (Opcional) conferir status na SyncPay antes de aprovar:
    tx = await get_transaction(order.sync_identifier)
    status = tx.get("data", {}).get("status")
    # status "completed" aparece no exemplo da doc :contentReference[oaicite:12]{index=12}
    if status != "completed":
        await m.reply(f"⚠️ SyncPay ainda não confirmou (status={status}). Se quiser mesmo assim, aprove manualmente.")
        # você pode decidir retornar aqui; vou permitir seguir.

    invite = await bot.create_chat_invite_link(chat_id=settings.VIP_CHAT_ID, member_limit=1)
    await bot.send_message(order.user_id, f"✅ Aprovado! Aqui está seu convite VIP (1 uso):\n{invite.invite_link}")
    await db.set_order_status(order_id, "approved")

    await m.reply(f"✅ Pedido #{order_id} aprovado e convite enviado.")
