#!/usr/bin/env python3
"""
Mail Access Checker - Ett program för att verifiera e-postadresser
Skapad som ett exempel på hur man bygger ett eget mail access checker verktyg.

Funktioner:
- Syntax validering
- DNS MX record kontroll
- SMTP server verifiering
- Disposable email detektion
- Bulk verifiering
- Export av resultat
"""

import re
import socket
import smtplib
import dns.resolver
import json
import csv
import sys
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from datetime import datetime

@dataclass
class EmailCheckResult:
    """Resultat från email verifiering"""
    email: str
    is_valid_syntax: bool = False
    domain_exists: bool = False
    mx_records: List[str] = None
    smtp_valid: bool = False
    is_disposable: bool = False
    is_role_account: bool = False
    is_catch_all: Optional[bool] = None
    error_message: str = ""
    check_duration: float = 0.0
    
    def __post_init__(self):
        if self.mx_records is None:
            self.mx_records = []

class MailAccessChecker:
    """Huvudklass för email verifiering"""
    
    def __init__(self, timeout: int = 10, from_email: str = "test@example.com"):
        self.timeout = timeout
        self.from_email = from_email
        
        # Lista över kända disposable email providers
        self.disposable_domains = {
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'yopmail.com', 'temp-mail.org',
            'throwaway.email', 'getnada.com', 'maildrop.cc'
        }
        
        # Lista över role accounts
        self.role_accounts = {
            'admin', 'administrator', 'postmaster', 'hostmaster',
            'webmaster', 'www', 'abuse', 'noreply', 'no-reply',
            'support', 'help', 'info', 'contact', 'sales', 'security'
        }
    
    def validate_syntax(self, email: str) -> bool:
        """Validerar email syntax enligt RFC 5322"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None
    
    def check_mx_records(self, domain: str) -> Tuple[bool, List[str]]:
        """Kontrollerar MX records för domänen"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_list = [str(mx.exchange).rstrip('.') for mx in mx_records]
            return True, mx_list
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception):
            # Fallback till A record
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                return True, [domain]  # Använd domänen själv som mail server
            except Exception:
                return False, []
    
    def check_smtp_server(self, email: str, mx_servers: List[str]) -> Tuple[bool, Optional[bool]]:
        """Kontrollerar SMTP server tillgänglighet och email deliverability"""
        if not mx_servers:
            return False, None
            
        for mx_server in mx_servers:
            try:
                # Anslut till SMTP server
                with smtplib.SMTP(mx_server, 25, timeout=self.timeout) as server:
                    server.helo('localhost')
                    
                    # Testa MAIL FROM
                    code, response = server.mail(self.from_email)
                    if code != 250:
                        continue
                    
                    # Testa RCPT TO
                    code, response = server.rcpt(email)
                    
                    if code == 250:
                        return True, False  # Valid, not catch-all
                    elif code == 550:
                        return False, None  # Invalid
                    elif code in [451, 452, 421]:
                        # Temporary failure - antagligen valid
                        return True, None
                    
                    # Testa catch-all genom att testa en random adress
                    random_email = f"nonexistent{int(time.time())}@{email.split('@')[1]}"
                    server.rset()
                    server.mail(self.from_email)
                    code, response = server.rcpt(random_email)
                    
                    if code == 250:
                        return True, True  # Catch-all domain
                    else:
                        return True, False  # Valid specific email
                        
            except (socket.timeout, socket.gaierror, smtplib.SMTPException, ConnectionRefusedError):
                continue
                
        return False, None
    
    def is_disposable_email(self, domain: str) -> bool:
        """Kontrollerar om domänen är en disposable email provider"""
        return domain.lower() in self.disposable_domains
    
    def is_role_account(self, email: str) -> bool:
        """Kontrollerar om email är ett role account"""
        local_part = email.split('@')[0].lower()
        return local_part in self.role_accounts
    
    def check_email(self, email: str) -> EmailCheckResult:
        """Utför komplett verifiering av en email adress"""
        start_time = time.time()
        result = EmailCheckResult(email=email.strip().lower())
        
        try:
            # 1. Syntax validering
            result.is_valid_syntax = self.validate_syntax(result.email)
            if not result.is_valid_syntax:
                result.error_message = "Invalid email syntax"
                return result
            
            # Extrahera domän
            domain = result.email.split('@')[1]
            
            # 2. Kontrollera role account
            result.is_role_account = self.is_role_account(result.email)
            
            # 3. Kontrollera disposable email
            result.is_disposable = self.is_disposable_email(domain)
            
            # 4. MX record kontroll
            result.domain_exists, result.mx_records = self.check_mx_records(domain)
            if not result.domain_exists:
                result.error_message = "Domain does not exist or has no mail servers"
                return result
            
            # 5. SMTP validering
            result.smtp_valid, result.is_catch_all = self.check_smtp_server(result.email, result.mx_records)
            
        except Exception as e:
            result.error_message = f"Unexpected error: {str(e)}"
        
        finally:
            result.check_duration = time.time() - start_time
            
        return result
    
    def check_bulk_emails(self, emails: List[str], max_workers: int = 5) -> List[EmailCheckResult]:
        """Verifierar flera email adresser parallellt"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Starta alla jobs
            future_to_email = {executor.submit(self.check_email, email): email for email in emails}
            
            # Samla resultat
            for future in as_completed(future_to_email):
                email = future_to_email[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✓ Checked: {email}")
                except Exception as e:
                    error_result = EmailCheckResult(email=email, error_message=str(e))
                    results.append(error_result)
                    print(f"✗ Error checking {email}: {e}")
        
        return results
    
    def export_results(self, results: List[EmailCheckResult], format: str = 'csv', filename: str = None):
        """Exporterar resultat till fil"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_check_results_{timestamp}.{format}"
        
        if format.lower() == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'email', 'is_valid_syntax', 'domain_exists', 'smtp_valid',
                    'is_disposable', 'is_role_account', 'is_catch_all',
                    'mx_records', 'error_message', 'check_duration'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    writer.writerow({
                        'email': result.email,
                        'is_valid_syntax': result.is_valid_syntax,
                        'domain_exists': result.domain_exists,
                        'smtp_valid': result.smtp_valid,
                        'is_disposable': result.is_disposable,
                        'is_role_account': result.is_role_account,
                        'is_catch_all': result.is_catch_all,
                        'mx_records': ';'.join(result.mx_records),
                        'error_message': result.error_message,
                        'check_duration': round(result.check_duration, 3)
                    })
        
        elif format.lower() == 'json':
            data = []
            for result in results:
                data.append({
                    'email': result.email,
                    'is_valid_syntax': result.is_valid_syntax,
                    'domain_exists': result.domain_exists,
                    'smtp_valid': result.smtp_valid,
                    'is_disposable': result.is_disposable,
                    'is_role_account': result.is_role_account,
                    'is_catch_all': result.is_catch_all,
                    'mx_records': result.mx_records,
                    'error_message': result.error_message,
                    'check_duration': result.check_duration
                })
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Results exported to: {filename}")

def print_result(result: EmailCheckResult):
    """Skriver ut resultatet på ett snyggt sätt"""
    print(f"\n{'='*60}")
    print(f"Email: {result.email}")
    print(f"{'='*60}")
    print(f"✓ Valid syntax: {result.is_valid_syntax}")
    print(f"✓ Domain exists: {result.domain_exists}")
    print(f"✓ SMTP valid: {result.smtp_valid}")
    print(f"✓ Is disposable: {result.is_disposable}")
    print(f"✓ Is role account: {result.is_role_account}")
    print(f"✓ Is catch-all: {result.is_catch_all}")
    
    if result.mx_records:
        print(f"MX Records: {', '.join(result.mx_records)}")
    
    if result.error_message:
        print(f"❌ Error: {result.error_message}")
    
    print(f"Check duration: {result.check_duration:.3f}s")

def main():
    parser = argparse.ArgumentParser(description='Mail Access Checker - Verifiera email adresser')
    parser.add_argument('email', nargs='?', help='Email adress att kontrollera')
    parser.add_argument('-f', '--file', help='Fil med email adresser (en per rad)')
    parser.add_argument('--export', choices=['csv', 'json'], help='Exportformat för resultat')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout för SMTP anslutningar (sekunder)')
    parser.add_argument('--workers', type=int, default=5, help='Antal parallella workers för bulk kontroll')
    parser.add_argument('--from-email', default='test@example.com', help='Email att använda i MAIL FROM kommando')
    
    args = parser.parse_args()
    
    if not args.email and not args.file:
        parser.print_help()
        return
    
    checker = MailAccessChecker(timeout=args.timeout, from_email=args.from_email)
    
    if args.email:
        # Kontrollera en enda email
        print(f"Checking email: {args.email}")
        result = checker.check_email(args.email)
        print_result(result)
        
        if args.export:
            checker.export_results([result], args.export)
    
    elif args.file:
        # Kontrollera emails från fil
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                emails = [line.strip() for line in f if line.strip()]
            
            print(f"Checking {len(emails)} emails from {args.file}")
            results = checker.check_bulk_emails(emails, max_workers=args.workers)
            
            # Visa sammanfattning
            valid_count = sum(1 for r in results if r.smtp_valid)
            invalid_count = sum(1 for r in results if not r.smtp_valid and r.is_valid_syntax)
            syntax_errors = sum(1 for r in results if not r.is_valid_syntax)
            
            print(f"\n{'='*60}")
            print(f"SAMMANFATTNING")
            print(f"{'='*60}")
            print(f"Totalt kontrollerade: {len(results)}")
            print(f"✓ Giltiga emails: {valid_count}")
            print(f"✗ Ogiltiga emails: {invalid_count}")
            print(f"❌ Syntax fel: {syntax_errors}")
            print(f"📧 Disposable emails: {sum(1 for r in results if r.is_disposable)}")
            print(f"🏢 Role accounts: {sum(1 for r in results if r.is_role_account)}")
            
            if args.export:
                checker.export_results(results, args.export)
                
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
        except Exception as e:
            print(f"Error reading file: {e}")

if __name__ == "__main__":
    main()