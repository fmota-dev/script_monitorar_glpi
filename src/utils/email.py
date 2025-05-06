import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import DESTINATARIO, GMAIL_PASSWORD, GMAIL_USER


def enviar_email(titulo_chamado, link_chamado, descricao, imagens, id_chamado):
    """
    Envia um e‑mail com os detalhes de um chamado, mantendo a formatação original
    da descrição, incluindo linhas em branco.
    """
    subject = f"🚨 Alerta GLPI"

    # Formata a descrição para HTML, preservando as quebras de linha originais
    paragrafos_html = descricao.replace("\n", "<br>")

    # Monta o HTML com os dados
    html_corpo = f"""
    <html>
      <body style="font-family:Arial,sans-serif; color:#333;">
        <h2 style="margin-bottom:0.5em;">📥 Chamado #{id_chamado}</h2>
        <h3 style="margin-bottom:0.25em;">📌 Título</h3>
        <p style="margin:0 0 1em;">{titulo_chamado}</p>

        <h3 style="margin-bottom:0.25em;">🔗 Link</h3>
        <p style="margin:0 0 1em;"><a href="{link_chamado}">{link_chamado}</a></p>

        <h3 style="margin-bottom:0.25em;">📝 Descrição</h3>
        <div style="background-color: #f9f9f9; padding:10px; border-radius:4px; border:1px solid #ddd; margin-bottom:1em;">
          {paragrafos_html}
        </div>

        <h3 style="margin-bottom:0.25em;">🖼️ Imagens</h3>
        {
        "".join(
            f'<p style="margin:0 0 1em;"><img src="cid:img{idx + 1}" style="max-width:600px;"/></p>'
            for idx in range(len(imagens))
        )
        or '<p style="margin:0 0 1em;">(nenhuma imagem)</p>'
    }
      </body>
    </html>
    """

    # Criação da mensagem
    msg = MIMEMultipart("related")
    msg["From"] = GMAIL_USER
    msg["To"] = DESTINATARIO
    msg["Subject"] = subject

    # Anexa o corpo HTML
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(html_corpo, "html"))
    msg.attach(alt)

    # Anexa as imagens inline
    for idx, img_path in enumerate(imagens, start=1):
        try:
            with open(img_path, "rb") as f:
                img_data = f.read()
            mime_img = MIMEImage(img_data)
            cid = f"img{idx}"
            mime_img.add_header("Content-ID", f"<{cid}>")
            msg.attach(mime_img)
        except Exception as e:
            print(f"❌ Não foi possível anexar imagem {img_path}: {e}")

    # Envio do e-mail
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
        print("✅ E‑mail enviado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao enviar o e-mail: {e}")
