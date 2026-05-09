import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

load_dotenv()

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
IMAP_SERVER = "imap.gmail.com"

def limpar_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def obter_corpo_email(msg):
    corpo_texto = ""
    corpo_html = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if "attachment" in content_disposition:
                continue
                
            if content_type == "text/plain":
                try:
                    corpo_texto = part.get_payload(decode=True).decode()
                except:
                    pass
            elif content_type == "text/html":
                try:
                    corpo_html = part.get_payload(decode=True).decode()
                except:
                    pass
    else:
        content_type = msg.get_content_type()
        try:
            payload = msg.get_payload(decode=True).decode()
            if content_type == "text/html":
                corpo_html = payload
            else:
                corpo_texto = payload
        except:
            pass
            
    if corpo_texto:
        return corpo_texto
    elif corpo_html:
        return limpar_html(corpo_html)
        
    return ""

def extrair_dados_transacao(assunto, corpo, data_email):
    transacao = {
        "banco": "Nubank",
        "data": data_email,
        "tipo": "Desconhecido",
        "valor": 0.0,
        "estabelecimento": "N/A"
    }

    padrao_valor = r"R\$\s*(\d+(?:\.\d{3})*,\d{2})"
    match_valor = re.search(padrao_valor, corpo)
    
    if match_valor:
        valor_str = match_valor.group(1).replace(".", "").replace(",", ".")
        transacao["valor"] = float(valor_str)

    assunto_lower = assunto.lower()
    corpo_lower = corpo.lower()

    if "pagamento de fatura" in assunto_lower:
        transacao["tipo"] = "Pagamento de Fatura"
        transacao["estabelecimento"] = "Nubank"
    elif "sua fatura" in assunto_lower:
        if "não precisa pagar nada" in corpo_lower or "nao precisa pagar nada" in corpo_lower:
            transacao["tipo"] = "Fatura Zerada"
            transacao["estabelecimento"] = "Nubank"
            transacao["valor"] = 0.0
        else:
            transacao["tipo"] = "Fechamento de Fatura"
            transacao["estabelecimento"] = "Nubank"
    elif "compra aprovada" in assunto_lower:
        transacao["tipo"] = "Compra Cartao"
    elif "transferência enviada" in assunto_lower or "pix enviado" in assunto_lower:
        transacao["tipo"] = "Pix Enviado"
    elif "transferência recebida" in assunto_lower or "pix recebido" in assunto_lower:
        transacao["tipo"] = "Pix Recebido"

    return transacao

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
                ultimos_ids = ids_emails[-5:]
                print(f"Processando os ultimos {len(ultimos_ids)} e-mails...\n")
                
                for email_id in ultimos_ids:
                    status_fetch, dados_email = mail.fetch(email_id, "(RFC822)")
                    
                    for resposta in dados_email:
                        if isinstance(resposta, tuple):
                            msg = email.message_from_bytes(resposta[1])
                            
                            assunto, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(assunto, bytes):
                                assunto = assunto.decode(encoding if encoding else "utf-8")
                                
                            corpo = obter_corpo_email(msg)
                            data_email = msg.get("Date")
                            
                            dados_estruturados = extrair_dados_transacao(assunto, corpo, data_email)
                            
                            print(f"Assunto Original: {assunto}")
                            print(f"JSON Extraido: {dados_estruturados}")
                            print("-" * 50)
        
        mail.logout()

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    buscar_ultimos_emails_banco()