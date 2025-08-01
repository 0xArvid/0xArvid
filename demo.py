#!/usr/bin/env python3
"""
Demo av Mail Access Checker
Visar hur olika typer av email-adresser verifieras
"""

from mail_access_checker import MailAccessChecker, print_result
import time

def main():
    print("=" * 70)
    print("           MAIL ACCESS CHECKER - DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Skapa checker instans
    checker = MailAccessChecker(timeout=5)
    
    # Test emails - olika typer för att visa olika resultat
    test_emails = [
        "test@gmail.com",           # Troligen ogiltig Gmail
        "admin@example.com",        # Role account på example domän
        "user@10minutemail.com",    # Disposable email
        "info@google.com",          # Troligen giltig corporate email
        "invalid.email.format",     # Ogiltig syntax
    ]
    
    for email in test_emails:
        print(f"\n🔍 Kontrollerar: {email}")
        print("-" * 50)
        
        start_time = time.time()
        result = checker.check_email(email)
        
        # Visa resultat i kompakt format
        print(f"✓ Syntax: {'OK' if result.is_valid_syntax else 'FEL'}")
        
        if result.is_valid_syntax:
            print(f"✓ Domän: {'OK' if result.domain_exists else 'FEL'}")
            print(f"✓ SMTP: {'OK' if result.smtp_valid else 'FEL'}")
            print(f"⚠ Disposable: {'JA' if result.is_disposable else 'NEJ'}")
            print(f"⚠ Role account: {'JA' if result.is_role_account else 'NEJ'}")
            
            if result.mx_records:
                print(f"📧 Mail servrar: {len(result.mx_records)} st")
        
        if result.error_message:
            print(f"❌ Fel: {result.error_message}")
        
        print(f"⏱ Tid: {result.check_duration:.2f}s")
        
        # Vänta lite mellan requests för att vara snäll mot servrar
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print("                    DEMONSTRATION KLAR")
    print("=" * 70)
    print("\nFör att köra fullständiga tester:")
    print("python3 mail_access_checker.py test@example.com")
    print("python3 mail_access_checker.py -f test_emails.txt --export csv")
    print("python3 mail_checker_gui.py  # För grafiskt gränssnitt")

if __name__ == "__main__":
    main()