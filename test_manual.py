#!/usr/bin/env python3
"""
Manuellt testscript för att verifiera att systemet fungerar
Kör detta innan du aktiverar cron-jobben
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def check_config():
    """Kontrollera konfiguration"""
    print_header("1. KONTROLLERAR KONFIGURATION")
    
    config_file = Path('/workspace/config.json')
    
    if not config_file.exists():
        print("❌ config.json saknas!")
        print("   Kopiera config.example.json till config.json och fyll i dina uppgifter")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("✓ config.json hittad")
        print(f"  Email: {config.get('email', 'SAKNAS')}")
        print(f"  Inloggning krävs: {config.get('login_required', False)}")
        print(f"  Sökord: {', '.join(config.get('search_terms', []))}")
        print(f"  Plats: {config.get('location', 'Inte angiven')}")
        
        if not config.get('search_terms'):
            print("⚠ VARNING: Inga sökord angivna!")
            return False
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Ogiltig JSON i config.json: {e}")
        return False


def check_dependencies():
    """Kontrollera Python-beroenden"""
    print_header("2. KONTROLLERAR BEROENDEN")
    
    try:
        import playwright
        print("✓ Playwright installerad")
        print(f"  Version: {playwright.__version__}")
    except ImportError:
        print("❌ Playwright SAKNAS!")
        print("   Kör: pip install -r requirements.txt")
        return False
    
    # Kontrollera om Playwright browsers är installerade
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        print("✓ Playwright browsers installerade")
    except Exception as e:
        print(f"❌ Playwright browsers saknas: {e}")
        print("   Kör: python -m playwright install chromium")
        return False
    
    return True


def check_scripts():
    """Kontrollera att scripts finns"""
    print_header("3. KONTROLLERAR SCRIPTS")
    
    scripts = {
        'arbetsformedlingen_bot.py': 'Huvudscript',
        'verify_job_search.py': 'Verifieringsscript',
        'setup_cron.sh': 'Cron setup script'
    }
    
    all_ok = True
    for script, desc in scripts.items():
        path = Path(f'/workspace/{script}')
        if path.exists():
            is_executable = path.stat().st_mode & 0o111
            status = "✓" if is_executable else "⚠"
            exec_note = "" if is_executable else " (inte körbar)"
            print(f"{status} {script} - {desc}{exec_note}")
            if not is_executable:
                print(f"   Kör: chmod +x /workspace/{script}")
        else:
            print(f"❌ {script} SAKNAS!")
            all_ok = False
    
    return all_ok


def check_directories():
    """Kontrollera och skapa nödvändiga mappar"""
    print_header("4. KONTROLLERAR MAPPAR")
    
    logs_dir = Path('/workspace/logs')
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
        print("✓ Skapade logs/ mapp")
    else:
        print("✓ logs/ mapp finns")
    
    return True


def run_test():
    """Kör testjobb"""
    print_header("5. KÖR TESTJOBB")
    
    try:
        from arbetsformedlingen_bot import ArbetsformedlingenBot
        
        print("Startar bot (detta kan ta några sekunder)...")
        bot = ArbetsformedlingenBot()
        success = bot.run()
        
        if success:
            print("\n✓ Testjobb KLART!")
            print("\nKontrollera resultat:")
            
            # Visa resultat
            results_file = Path('/workspace/job_search_results.json')
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results = json.load(f)
                
                print(f"\nHittade {results['count']} jobb:")
                for i, job in enumerate(results['jobs'], 1):
                    print(f"\n  {i}. {job['title']}")
                    print(f"     Företag: {job['company']}")
                    print(f"     URL: {job['url']}")
        else:
            print("\n⚠ Testjobb genomfört men hittade inte tillräckligt många jobb")
            print("   Kontrollera logs/arbetsformedlingen.log för detaljer")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Fel vid testjobb: {e}")
        print("\nKontrollera logs/arbetsformedlingen.log för mer information")
        return False


def run_verification():
    """Kör verifieringsscript"""
    print_header("6. KÖR VERIFIERING")
    
    try:
        from verify_job_search import check_job_search_status
        
        success = check_job_search_status()
        
        if success:
            print("\n✓ Verifiering OK!")
        else:
            print("\n⚠ Verifiering visar problem")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Fel vid verifiering: {e}")
        return False


def main():
    """Huvudfunktion"""
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#  ARBETSFÖRMEDLINGEN BOT - MANUELLT TEST".center(60) + "#")
    print("#" + " "*58 + "#")
    print("#"*60)
    
    print(f"\nDatum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Kör alla checks
    checks = [
        ("Konfiguration", check_config),
        ("Beroenden", check_dependencies),
        ("Scripts", check_scripts),
        ("Mappar", check_directories),
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            all_passed = False
            print(f"\n❌ {name} check misslyckades!")
    
    if not all_passed:
        print("\n" + "="*60)
        print("SYSTEMET ÄR INTE REDO")
        print("="*60)
        print("\nÅtgärda problemen ovan innan du fortsätter.")
        return 1
    
    # Fråga om användaren vill köra test
    print("\n" + "="*60)
    print("ALLA CHECKS OK!")
    print("="*60)
    
    try:
        response = input("\nVill du köra ett testjobb nu? (j/n): ").strip().lower()
        if response in ['j', 'ja', 'y', 'yes']:
            run_test()
            run_verification()
        else:
            print("\nTest hoppades över. Kör manuellt med:")
            print("  python3 arbetsformedlingen_bot.py")
    except (EOFError, KeyboardInterrupt):
        print("\n\nTest hoppades över.")
    
    print("\n" + "="*60)
    print("NÄSTA STEG:")
    print("="*60)
    print("""
1. Kontrollera att allt fungerar:
   python3 arbetsformedlingen_bot.py

2. Installera cron-jobb:
   ./setup_cron.sh

3. Verifiera cron-jobb:
   crontab -l

4. Övervaka loggar:
   tail -f logs/arbetsformedlingen.log
""")
    
    return 0


if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nAvbrutet av användare.")
        exit(1)
