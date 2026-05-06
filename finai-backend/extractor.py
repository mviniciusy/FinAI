import os
import imaplib
from dotenv import load_dotenv

load_dotenv()

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
IMAP_SERVER = "imap.gmail.com"

def testar_conexao_imap():
    print("Iniciando conexao com o servidor IMAP . . .")

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        print("Login realizado com sucesso no e-mail:", EMAIL_ACCOUNT)
        status, mensagens = mail.select("INBOX")

        if status == "OK":
            quantidade_emails = mensagens [0].decode('utf-8')
            print(f"Você tem {quantidade_emails} e-mails na sua Caixa de entrada.")
        mail.logout()
        print("Conexão encerrada com segurança.")
    
    except imaplib.IMAP4.error as e:
        print("Erro de autenticação. Verifique seu e-mail e Senha de Aplicativo.")
        print(f"Detalhe do erro: {e}")
    
    except Exception as e:
        print("Ocorreu um erro inesperado.")
        print(f"Detalhe do erro: {e}")

if __name__ == "__main__":
    testar_conexao_imap()