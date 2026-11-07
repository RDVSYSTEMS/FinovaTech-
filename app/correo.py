"""=============================================================
FinovaTech v10 - Envío de correo
==============================================================
Usa SMTP configurado por variables de entorno. Sin servidor SMTP
registra el enlace en el log para pruebas locales.
=============================================================="""

import logging
import smtplib
import ssl

from email.message import EmailMessage

from app.config import Config

logger = logging.getLogger(__name__)


def enviar_correo_recuperacion(destinatario: str, enlace: str) -> bool:
    """Envía el enlace de recuperación; devuelve True si salió por SMTP."""
    if not Config.MAIL_SERVER:
        logger.warning(
            "SMTP no configurado. Enlace de recuperación para %s: %s",
            destinatario,
            enlace,
        )
        return False

    mensaje = EmailMessage()
    mensaje["Subject"] = "Recupera tu contraseña - FinovaTech"
    mensaje["From"] = Config.MAIL_FROM
    mensaje["To"] = destinatario
    mensaje.set_content(
        "Hola,\n\n"
        "Recibimos una solicitud para restablecer tu contraseña de FinovaTech.\n"
        f"Abre este enlace (válido por {Config.PASSWORD_RESET_MINUTES} minutos):\n\n"
        f"{enlace}\n\n"
        "Si no solicitaste el cambio, ignora este mensaje.\n"
    )

    contexto = ssl.create_default_context()
    if Config.MAIL_USE_SSL:
        with smtplib.SMTP_SSL(
            Config.MAIL_SERVER, Config.MAIL_PORT, context=contexto, timeout=15
        ) as servidor:
            if Config.MAIL_USERNAME:
                servidor.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            servidor.send_message(mensaje)
    else:
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT, timeout=15) as servidor:
            if Config.MAIL_USE_TLS:
                servidor.starttls(context=contexto)
            if Config.MAIL_USERNAME:
                servidor.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            servidor.send_message(mensaje)

    return True
