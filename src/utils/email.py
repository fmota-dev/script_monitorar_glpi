import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import DESTINATARIO, GMAIL_PASSWORD, GMAIL_USER


def enviar_email(titulo_chamado, link_chamado):
    """
    Envia um e-mail com os detalhes de um chamado.

    Args:
        titulo_chamado (str): Título do chamado.
        link_chamado (str): Link do chamado.
    """
    try:
        subject = "🚨 Alerta de chamado em potencial"
        body = f"📌 Título: {titulo_chamado}\n🔗 Link: {link_chamado}"

        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = DESTINATARIO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, DESTINATARIO, msg.as_string())

        print("✅ E-mail enviado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
