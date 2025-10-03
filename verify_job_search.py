#!/usr/bin/env python3
"""
Verifieringsskript för att kontrollera att jobbsökning är klar
Körs kl 21:00 för att säkerställa att sökningen är gjord innan deadline
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_job_search_status():
    """Kontrollera om jobbsökningen är genomförd"""
    
    status_file = Path('/workspace/job_search_status.json')
    
    if not status_file.exists():
        logger.error("❌ VARNING: Ingen jobbsökning har körts denna månad!")
        return False
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        # Kontrollera om sökningen är från denna månad
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        status_month = status.get('month')
        status_year = status.get('year')
        
        if status_month != current_month or status_year != current_year:
            logger.error(f"❌ VARNING: Jobbsökning är inte från denna månad ({current_year}-{current_month:02d})")
            logger.error(f"   Senaste sökning: {status_year}-{status_month:02d}")
            return False
        
        # Kontrollera status
        if status.get('status') == 'success' and status.get('jobs_found', 0) >= 3:
            logger.info(f"✓ Jobbsökning är genomförd!")
            logger.info(f"  Tidpunkt: {status.get('timestamp')}")
            logger.info(f"  Antal jobb: {status.get('jobs_found')}")
            logger.info(f"  Status: {status.get('message')}")
            return True
        else:
            logger.warning(f"⚠ Jobbsökning är ofullständig:")
            logger.warning(f"  Status: {status.get('status')}")
            logger.warning(f"  Meddelande: {status.get('message')}")
            logger.warning(f"  Jobb hittade: {status.get('jobs_found', 0)}/3")
            return False
            
    except json.JSONDecodeError as e:
        logger.error(f"❌ Kunde inte läsa statusfil: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Fel vid verifiering: {e}")
        return False


def send_notification(success):
    """Skicka notifiering (kan utökas med email/SMS)"""
    
    notification_file = Path('/workspace/notification.txt')
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if success:
        message = f"""
VERIFIERING KLAR - {timestamp}
================================
Status: ✓ GENOMFÖRD
Jobbsökningen för denna månad är genomförd och 3 jobb har hittats.
"""
    else:
        message = f"""
VERIFIERING KLAR - {timestamp}
================================
Status: ❌ EJ GENOMFÖRD
VARNING: Jobbsökningen är inte genomförd innan deadline!
Deadline: Kl 07:00 den 15:e varje månad
Aktuell tid: {timestamp}

Åtgärder krävs omedelbart!
"""
    
    with open(notification_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    logger.info(f"Notifiering sparad till {notification_file}")


def main():
    """Huvudfunktion"""
    logger.info("=== Startar verifiering av jobbsökning ===")
    logger.info(f"Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = check_job_search_status()
    send_notification(success)
    
    if success:
        logger.info("✓ Verifiering klar - allt är OK!")
        return 0
    else:
        logger.error("✗ Verifiering klar - åtgärd krävs!")
        return 1


if __name__ == '__main__':
    exit(main())
