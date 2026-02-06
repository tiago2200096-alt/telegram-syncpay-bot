from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Plano Mensal", callback_data="plan:monthly")],
        [InlineKeyboardButton(text="🏆 Plano Anual", callback_data="plan:yearly")],
        [InlineKeyboardButton(text="🆘 Suporte", url="https://t.me/SEU_SUPORTE")]
    ])

def pay_kb(plan: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pagar", callback_data=f"pay:{plan}")],
        [InlineKeyboardButton(text="✅ Já paguei (verificar)", callback_data=f"check:{plan}")],
        [InlineKeyboardButton(text="🆘 Suporte", callback_data="support")]
    ])
  
