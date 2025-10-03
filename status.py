#!/usr/bin/env python3
"""
Snabb status-checker för Arbetsförmedlingen automation
Visar aktuell status och senaste resultat
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def print_box(title, content, status="info"):
    """Print en fin box med information"""
    colors = {
        "success": "\033[92m",  # Grön
        "warning": "\033[93m",  # Gul
        "error": "\033[91m",    # Röd
        "info": "\033[94m"      # Blå
    }
    reset = "\033[0m"
    
    color = colors.get(status, colors["info"])
    
    width = 60
    print(f"\n{color}{'═' * width}{reset}")
    print(f"{color}║{reset} {title.ljust(width-2)} {color}║{reset}")
    print(f"{color}{'═' * width}{reset}")
    for line in content:
        print(f"{color}║{reset} {line.ljust(width-2)} {color}║{reset}")
    print(f"{color}{'═' * width}{reset}\n")


def check_system_status():
    """Kontrollera systemstatus"""
    
    print("\n" + "▓" * 60)
    print("▓" + " ARBETSFÖRMEDLINGEN AUTOMATION - STATUS ".center(58) + "▓")
    print("▓" * 60 + "\n")
    print(f"Tidpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Kontrollera konfiguration
    config_file = Path('/workspace/config.json')
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            search_terms = config.get('search_terms', [])
            location = config.get('location', 'Ej angiven')
            
            print_box("⚙ KONFIGURATION", [
                f"Status: ✓ OK",
                f"Sökord: {', '.join(search_terms) if search_terms else 'SAKNAS'}",
                f"Plats: {location}",
                f"Inloggning: {'Ja' if config.get('login_required') else 'Nej'}"
            ], "success")
        except Exception as e:
            print_box("⚙ KONFIGURATION", [
                f"Status: ✗ FEL",
                f"Meddelande: {str(e)}"
            ], "error")
    else:
        print_box("⚙ KONFIGURATION", [
            "Status: ✗ SAKNAS",
            "config.json hittades inte"
        ], "error")
    
    # Kontrollera senaste sökning
    status_file = Path('/workspace/job_search_status.json')
    if status_file.exists():
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            timestamp = status.get('timestamp', 'Okänd')
            search_status = status.get('status', 'unknown')
            message = status.get('message', 'Ingen information')
            jobs_found = status.get('jobs_found', 0)
            month = status.get('month', 0)
            year = status.get('year', 0)
            
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            is_current_month = (month == current_month and year == current_year)
            
            box_status = "success" if search_status == "success" else "warning"
            if not is_current_month:
                box_status = "error"
            
            print_box("📊 SENASTE SÖKNING", [
                f"Tidpunkt: {timestamp}",
                f"Status: {search_status.upper()}",
                f"Jobb hittade: {jobs_found}/3",
                f"Period: {year}-{month:02d}",
                f"Aktuell månad: {'Ja ✓' if is_current_month else 'Nej ✗'}",
                f"Meddelande: {message}"
            ], box_status)
            
        except Exception as e:
            print_box("📊 SENASTE SÖKNING", [
                f"Status: ✗ FEL",
                f"Kunde inte läsa status: {str(e)}"
            ], "error")
    else:
        print_box("📊 SENASTE SÖKNING", [
            "Status: Ingen sökning utförd än",
            "Kör: ./arbetsformedlingen_bot.py"
        ], "warning")
    
    # Visa hittade jobb
    results_file = Path('/workspace/job_search_results.json')
    if results_file.exists():
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            jobs = results.get('jobs', [])
            timestamp = results.get('timestamp', 'Okänd')
            
            print_box("💼 HITTADE JOBB", [
                f"Antal: {len(jobs)}",
                f"Tidpunkt: {timestamp}",
                ""
            ] + [
                f"{i+1}. {job.get('title', 'N/A')} @ {job.get('company', 'N/A')}"
                for i, job in enumerate(jobs[:3])
            ], "info")
            
        except Exception as e:
            print_box("💼 HITTADE JOBB", [
                f"Kunde inte läsa resultat: {str(e)}"
            ], "error")
    
    # Kontrollera cron
    import subprocess
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            cron_lines = [line for line in result.stdout.split('\n') 
                         if 'arbetsformedlingen' in line.lower()]
            
            if cron_lines:
                print_box("⏰ CRON-JOBB", [
                    f"Status: ✓ AKTIVA ({len(cron_lines)} jobb)",
                    ""
                ] + [line.strip() for line in cron_lines[:3]], "success")
            else:
                print_box("⏰ CRON-JOBB", [
                    "Status: ⚠ INGA JOBB",
                    "Kör: ./setup_cron.sh för att aktivera"
                ], "warning")
        else:
            print_box("⏰ CRON-JOBB", [
                "Status: ? OKÄND",
                "Kunde inte kontrollera crontab"
            ], "warning")
    except FileNotFoundError:
        print_box("⏰ CRON-JOBB", [
            "Status: ✗ CRON EJ INSTALLERAD",
            "Installera cron först"
        ], "error")
    
    # Nästa körning
    now = datetime.now()
    next_run_day = 15
    next_run_month = now.month if now.day < 15 else (now.month % 12) + 1
    next_run_year = now.year if now.day < 15 else (now.year + (1 if now.month == 12 else 0))
    
    from datetime import datetime
    next_run = datetime(next_run_year, next_run_month, next_run_day, 7, 0)
    days_until = (next_run - now).days
    
    print_box("📅 NÄSTA KÖRNING", [
        f"Datum: {next_run.strftime('%Y-%m-%d kl 07:00')}",
        f"Om: {days_until} dagar",
        f"Verifiering: {next_run.strftime('%Y-%m-%d kl 21:00')}"
    ], "info")
    
    print("─" * 60)
    print("\nKommandon:")
    print("  ./arbetsformedlingen_bot.py  - Kör jobbsökning manuellt")
    print("  ./verify_job_search.py       - Verifiera status")
    print("  ./test_manual.py             - Kör fullständigt test")
    print("  tail -f logs/*.log           - Visa loggar")
    print()


if __name__ == '__main__':
    try:
        check_system_status()
    except KeyboardInterrupt:
        print("\n\nAvbrutet.")
        sys.exit(0)
