# 🔔 Automação de Monitoramento de Chamados do GLPI com Alertas por E-mail

## 📌 Finalidade

Este projeto foi criado com o objetivo de **automatizar e facilitar o recebimento de chamados registrados no sistema GLPI**, enviando **alertas por e-mail** sempre que forem identificados chamados que correspondam a categorias relevantes previamente definidas.

## ⚙️ O que ele faz?

- Acessa o sistema GLPI automaticamente com Selenium (modo headless).
- Coleta os títulos e categorias dos chamados.
- Compara os títulos com uma base de conhecimento (JSON local) utilizando palavras-chave.
- Envia alertas por e-mail quando há coincidências significativas.
- Garante que o mesmo chamado não seja alertado mais de uma vez.
- Executa o monitoramento de forma contínua, com verificação a cada 10 minutos.

## 🧠 Base de conhecimento

A base de conhecimento é um arquivo JSON (`base_de_conhecimentos.json`) que contém as palavras-chave para identificar chamados relevantes. Exemplo de estrutura:

```json
{
  "conhecimentos": [
    {
      "titulo": "Erro de autenticação",
      "categoria": "TI > Redes",
      "palavras_chave": ["senha", "login", "autenticação", "usuário"]
    }
  ]
}
```

## 📁 Variáveis de ambiente (.env)

As seguintes variáveis devem ser definidas no arquivo `.env`:

```env
GMAIL_USER=seu_email@gmail.com
GMAIL_PASSWORD=sua_senha_de_aplicativo
DESTINATARIO=email_de_destino

GLPI_USER=seu_usuario_glpi
GLPI_PASS=sua_senha_glpi

EDGE_DRIVER_PATH=C:\caminho\para\msedgedriver.exe
```

> ⚠️ Utilize uma **senha de aplicativo do Gmail**, não sua senha principal.

## 💌 Envio de alertas

Os alertas são enviados por e-mail com o título do chamado e um link direto para acessá-lo no GLPI. O sistema verifica se já enviou aquele chamado anteriormente, evitando mensagens duplicadas.

## 🔁 Execução contínua

O script é executado em loop, verificando novos chamados a cada 10 minutos:

```python
while True:
    abrir_glpi_e_extrair_titulos()
    time.sleep(600)  # Aguarda 10 minutos
```

## 🛠️ Tecnologias usadas

- Python
- Selenium
- smtplib (e-mail)
- dotenv (gerenciamento de variáveis de ambiente)
- JSON

## 🧩 Requisitos

- Python 3.8+
- WebDriver do Microsoft Edge (`msedgedriver.exe`)
- Acesso ao GLPI e permissões adequadas
- Conta Gmail com autenticação de dois fatores e senha de aplicativo

## 🛡️ Segurança

- As credenciais são armazenadas no arquivo `.env`, que **não deve ser versionado**.
- Adicione `.env` ao `.gitignore` para evitar vazamentos acidentais.

## ✅ Resultado esperado

A cada novo chamado identificado com relevância:

- Um e-mail é enviado ao responsável.
- O chamado é marcado como "enviado" para evitar duplicidade.
- Um log de execução é exibido no terminal com o resumo.

---

Desenvolvido para tornar o processo de triagem de chamados mais ágil, automatizado e confiável. 🚀

⚠️ Feito por fmota.dev para uso pessoal!
