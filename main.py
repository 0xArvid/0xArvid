#!/usr/bin/env python3
"""
Mail Access Checker - Ett verktyg för att testa e-postkontos tillgänglighet
Utvecklat för utbildningsändamål och säkerhetstestning
"""

import argparse
import sys
import os
from pathlib import Path

# Lägg till src-mappen till Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.config import Config
from core.logger import setup_logger
from ui.cli import CLI

def main():
    """Huvudfunktion för Mail Access Checker"""
    parser = argparse.ArgumentParser(
        description="Mail Access Checker - Testa e-postkontos tillgänglighet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exempel:
  python main.py --target email@example.com --password secret123
  python main.py --file accounts.txt --threads 5
  python main.py --config custom_config.yaml
        """
    )
    
    # Grundläggande argument
    parser.add_argument('--target', '-t', help='Enskild e-postadress att testa')
    parser.add_argument('--password', '-p', help='Lösenord för enskild e-post')
    parser.add_argument('--file', '-f', help='Fil med e-post:lösenord kombinationer')
    
    # Konfigurationsargument
    parser.add_argument('--config', '-c', help='Konfigurationsfil', default='config/settings.yaml')
    parser.add_argument('--threads', type=int, help='Antal trådar att använda', default=5)
    parser.add_argument('--timeout', type=int, help='Timeout i sekunder', default=30)
    
    # Output argument
    parser.add_argument('--output', '-o', help='Utdatafil för resultat')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Tyst läge')
    
    # Protokollargument
    parser.add_argument('--protocol', choices=['imap', 'smtp', 'pop3', 'all'], 
                       default='imap', help='Protokoll att testa')
    
    args = parser.parse_args()
    
    # Validera argument
    if not args.target and not args.file:
        parser.error("Du måste ange antingen --target eller --file")
    
    if args.target and not args.password:
        parser.error("När du använder --target måste du också ange --password")
    
    try:
        # Ladda konfiguration
        config = Config()
        if os.path.exists(args.config):
            config.load_from_file(args.config)
        
        # Uppdatera config med CLI-argument
        config.update_from_args(args)
        
        # Setup logger
        logger = setup_logger(verbose=args.verbose, quiet=args.quiet)
        
        # Starta CLI
        cli = CLI(config, logger)
        cli.run()
        
    except KeyboardInterrupt:
        print("\n[!] Avbrutet av användare")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Fel: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()