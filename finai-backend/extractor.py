import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
IMAP_SERVER = "imap.gmail.com"

def obter_corpo_email(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if "attachment" in content_disposition:
                continue
                
            if content_type == "text/plain":
                try:
                    return part.get_payload(decode=True).decode()
                except:
                    pass
    else:
        try:
            return msg.get_payload(decode=True).decode()
        except:
            pass
            
    return "Corpo do e-mail não encontrado ou formato não suportado."

def buscar_ultimos_emails_banco():
    print("Conectando ao IMAP...")
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("INBOX")
        
        print("Buscando e-mails do Nubank...")
        status, mensagens = mail.search(None, '(FROM "nubank.com.br")')
        
        if status == "OK":
            ids_emails = mensagens[0].split()
            print(f"Encontrados {len(ids_emails)} e-mails do Nubank.")
            
            if ids_emails:
                ultimo_id = ids_emails[-1]
                print(f"Baixando o e-mail mais recente (ID: {ultimo_id.decode()})...")
                
                status_fetch, dados_email = mail.fetch(ultimo_id, "(RFC822)")
                
                for resposta in dados_email:
                    if isinstance(resposta, tuple):
                        msg = email.message_from_bytes(resposta[1])
                        
                        assunto, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(assunto, bytes):
                            assunto = assunto.decode(encoding if encoding else "utf-8")
                            
                        corpo = obter_corpo_email(msg)
                            
                        print(f"\nASSUNTO: {assunto}")
                        print(f"DATA: {msg.get('Date')}")
                        print("\n--- CORPO DO E-MAIL ---")
                        print(corpo[:500])
                        print("-----------------------\n")
        
        mail.logout()

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    buscar_ultimos_emails_banco()