from aiogram.types import URLInputFile

MEDIA = {
    "M1_SECURITY_IMG": "https://res.cloudinary.com/declnidxc/image/upload/IMG_20260206_234032_lfnlfc.png",
    "M2_PAY_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/https:/res.cloudinary.com/lv_0_20260207052358/video/upload/v123456/video.mp4",
    "M3_TRUST_IMG": "https://res.cloudinary.com/declnidxc/image/upload/IMG_20260206_234057_x4o7r7.png",
    "M4_SUPPORT_VIDEO": "https://res.cloudinary.com/declnidxc/video/upload/v1770454441/lv_0_20260207055140_obfflt.mp4",
    "M5_LAST_CALL": "https://res.cloudinary.com/declnidxc/video/upload/v1770453000/lv_0_20260128120445_ltxyrw.mp4",  # pode ser img ou vídeo
}

async def send_m1_security(bot, chat_id: int):
    await bot.send_photo(
        chat_id,
        photo=URLInputFile(MEDIA["M1_SECURITY_IMG"]),
        caption=("🔒 *Etapa de segurança*\n"
                 "Seus dados são usados *somente* para validar seu acesso.\n"
                 "✅ Ambiente protegido • ✅ Pix oficial • ✅ Liberação automática"),
        parse_mode="Markdown"
    )

async def send_m2_pay_video(bot, chat_id: int, pix_code: str, order_id: int):
    await bot.send_video(
        chat_id,
        video=URLInputFile(MEDIA["M2_PAY_VIDEO"]),
        caption=(
            "⚡ *Só falta concluir o Pix*\n"
            "É bem rápido (menos de 1 minuto).\n\n"
            f"Pedido: #{order_id}\n"
            f"Pix Copia e Cola:\n{pix_code}\n\n"
            "Depois clique em *Já paguei (verificar)* ✅"
        ),
        parse_mode="Markdown"
    )


async def send_m3_trust(bot, chat_id: int):
    await bot.send_photo(
        chat_id,
        photo=URLInputFile(MEDIA["M3_TRUST_IMG"]),
        caption=("✅ *Tudo certo por aqui*\n"
                 "Seu pedido fica reservado por alguns minutos.\n"
                 "Se travar em qualquer parte, chama no *Suporte* que eu destravo com você."),
        parse_mode="Markdown"
    )

async def send_m4_support(bot, chat_id: int):
    await bot.send_video(
        chat_id,
        photo=URLInputFile(MEDIA["M4_SUPPORT_IMG"]),
        caption=("💬 *Se demorou, é normal.*\n"
                 "Esse processo é assim por segurança.\n"
                 "Quer que eu te guie agora? Pague o Pix e clique em *Já paguei* ✅"),
        parse_mode="Markdown"
    )

async def send_m5_last_call(bot, chat_id: int):
    url = MEDIA["M5_LAST_CALL"]
    # se for vídeo (mp4), manda vídeo; se não, manda foto
    if ".mp4" in url or "/video/" in url:
        await bot.send_video(
            chat_id,
            video=URLInputFile(url),
            caption=("⏳ *Seu pedido ainda está pendente*\n"
                     "Assim que o Pix confirmar, seu acesso entra automaticamente.\n"
                     "Se preferir, posso te ajudar no passo a passo no *Suporte* ✅"),
            parse_mode="Markdown"
        )
    else:
        await bot.send_photo(
            chat_id,
            photo=URLInputFile(url),
            caption=("⏳ *Seu pedido ainda está pendente*\n"
                     "Assim que o Pix confirmar, seu acesso entra automaticamente.\n"
                     "Se preferir, posso te ajudar no passo a passo no *Suporte* ✅"),
            parse_mode="Markdown"
        )
        
