"""
Command Line Interface för Mail Access Checker
"""

import time
from typing import List, Dict, Any
from pathlib import Path

from core.config import Config
from core.logger import MailAccessLogger
from core.exceptions import MailAccessException

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
            
            # Starta testning
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
    
    def _test_account(self, account: Dict[str, str]):
        """Testar ett enskilt konto (placeholder implementation)"""
        email = account['email']
        password = account['password']
        
        try:
            self.logger.debug(f"Testar {email}")
            
            # TODO: Implementera riktig protokolltestning här
            # För nu: simulera resultat baserat på e-post
            if email.endswith('@example.com'):
                result = 'valid'
                self.logger.success(f"VALID: {email}")
            elif email.endswith('@invalid.com'):
                result = 'invalid'
                self.logger.error(f"INVALID: {email}")
            else:
                result = 'unknown'
                self.logger.warning(f"UNKNOWN: {email}")
            
            self.results[result] += 1
            
            # Spara resultat om konfigurerat
            if self.config.output_file:
                self._save_result(email, result)
                
        except Exception as e:
            self.logger.error(f"Fel vid testning av {email}: {e}")
            self.results['error'] += 1
    
    def _save_result(self, email: str, result: str):
        """Sparar testresultat till fil"""
        try:
            output_path = Path(self.config.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Skapa resultatrad
            result_line = f"{email}:{result}\n"
            
            # Skriv till fil (append mode)
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(result_line)
                
        except Exception as e:
            self.logger.error(f"Fel vid sparande av resultat: {e}")
    
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