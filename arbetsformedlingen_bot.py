#!/usr/bin/env python3
"""
Arbetsförmedlingen Job Search Automation
Automatiskt söker och sparar tre relevanta jobb från Arbetsförmedlingen.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Konfigurera logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/logs/arbetsformedlingen.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ArbetsformedlingenBot:
    """Bot för att söka jobb på Arbetsförmedlingen"""
    
    def __init__(self, config_path='/workspace/config.json'):
        """Initialisera bot med konfiguration"""
        self.config = self._load_config(config_path)
        self.base_url = "https://arbetsformedlingen.se"
        self.results_file = Path('/workspace/job_search_results.json')
        self.status_file = Path('/workspace/job_search_status.json')
        
    def _load_config(self, config_path):
        """Ladda konfiguration från fil"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Konfigurationsfil saknas: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Ogiltig JSON i konfigurationsfil: {e}")
            raise
    
    def _save_status(self, status, message, jobs_found=0):
        """Spara status för verifiering"""
        status_data = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'message': message,
            'jobs_found': jobs_found,
            'month': datetime.now().month,
            'year': datetime.now().year
        }
        
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Status sparad: {status} - {message}")
    
    def _save_jobs(self, jobs):
        """Spara hittade jobb till fil"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'jobs': jobs,
            'count': len(jobs)
        }
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Sparade {len(jobs)} jobb till {self.results_file}")
    
    def login(self, page):
        """Logga in på Arbetsförmedlingen"""
        try:
            logger.info("Försöker logga in på Arbetsförmedlingen...")
            
            # Navigera till inloggningssidan
            page.goto(f"{self.base_url}/platsbanken/logga-in")
            page.wait_for_load_state('networkidle')
            
            # Vänta på och klicka på inloggningsknapp (BankID eller annan metod)
            # OBS: Arbetsförmedlingen använder BankID - detta kräver manuell hantering
            # eller en annan autentiseringsmetod
            
            email = self.config.get('email')
            password = self.config.get('password')
            
            if not email or not password:
                logger.error("Email eller lösenord saknas i konfigurationen")
                return False
            
            # Försök hitta inloggningsformulär
            # Detta beror på Arbetsförmedlingens faktiska inloggningsmetod
            email_field = page.query_selector('input[type="email"], input[name="email"], input[id="email"]')
            if email_field:
                email_field.fill(email)
                
                password_field = page.query_selector('input[type="password"]')
                if password_field:
                    password_field.fill(password)
                    
                    # Klicka på inloggningsknapp
                    login_button = page.query_selector('button[type="submit"], input[type="submit"]')
                    if login_button:
                        login_button.click()
                        page.wait_for_load_state('networkidle')
                        logger.info("Inloggning genomförd")
                        return True
            
            logger.warning("Kunde inte hitta inloggningsformulär - kanske BankID krävs?")
            return False
            
        except PlaywrightTimeoutError:
            logger.error("Timeout vid inloggning")
            return False
        except Exception as e:
            logger.error(f"Fel vid inloggning: {e}")
            return False
    
    def search_jobs(self, page):
        """Sök efter relevanta jobb"""
        try:
            logger.info("Söker efter jobb...")
            
            # Navigera till jobbsökning
            page.goto(f"{self.base_url}/platsbanken")
            page.wait_for_load_state('networkidle')
            
            # Hämta sökord från konfiguration
            search_terms = self.config.get('search_terms', [])
            location = self.config.get('location', '')
            
            jobs_found = []
            
            for term in search_terms:
                logger.info(f"Söker efter: {term}")
                
                # Hitta sökfält
                search_field = page.query_selector('input[type="search"], input[name="q"], input[placeholder*="Sök"]')
                if search_field:
                    search_field.fill(term)
                    
                    # Fyll i plats om det finns
                    if location:
                        location_field = page.query_selector('input[name="location"], input[placeholder*="Plats"]')
                        if location_field:
                            location_field.fill(location)
                    
                    # Klicka sök
                    search_button = page.query_selector('button[type="submit"], button:has-text("Sök")')
                    if search_button:
                        search_button.click()
                        page.wait_for_load_state('networkidle')
                        
                        # Vänta lite för att resultaten ska laddas
                        page.wait_for_timeout(2000)
                        
                        # Hämta jobbresultat
                        job_elements = page.query_selector_all('[class*="job"], [class*="result"], article, [data-testid*="job"]')
                        
                        for job_elem in job_elements[:3]:  # Ta max 3 jobb per sökord
                            try:
                                title = job_elem.query_selector('h2, h3, [class*="title"]')
                                company = job_elem.query_selector('[class*="company"], [class*="employer"]')
                                link = job_elem.query_selector('a')
                                
                                job_data = {
                                    'title': title.inner_text() if title else 'N/A',
                                    'company': company.inner_text() if company else 'N/A',
                                    'url': link.get_attribute('href') if link else 'N/A',
                                    'search_term': term,
                                    'found_at': datetime.now().isoformat()
                                }
                                
                                jobs_found.append(job_data)
                                logger.info(f"Hittade jobb: {job_data['title']} @ {job_data['company']}")
                                
                                # Stoppa om vi har 3 jobb
                                if len(jobs_found) >= 3:
                                    break
                                    
                            except Exception as e:
                                logger.warning(f"Kunde inte extrahera jobbinfo: {e}")
                                continue
                        
                        # Stoppa om vi har 3 jobb
                        if len(jobs_found) >= 3:
                            break
                        
                        # Gå tillbaka för nästa sökning
                        page.goto(f"{self.base_url}/platsbanken")
                        page.wait_for_load_state('networkidle')
            
            return jobs_found[:3]  # Returnera max 3 jobb
            
        except Exception as e:
            logger.error(f"Fel vid jobbsökning: {e}")
            return []
    
    def run(self):
        """Kör hela processen"""
        logger.info("=== Startar Arbetsförmedlingen Bot ===")
        
        try:
            with sync_playwright() as p:
                # Starta browser
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                # Försök logga in (om konfigurerad)
                if self.config.get('login_required', False):
                    login_success = self.login(page)
                    if not login_success:
                        logger.warning("Inloggning misslyckades, fortsätter utan inloggning...")
                
                # Sök jobb
                jobs = self.search_jobs(page)
                
                # Spara resultat
                if jobs and len(jobs) >= 3:
                    self._save_jobs(jobs)
                    self._save_status('success', f'Hittade {len(jobs)} jobb', len(jobs))
                    logger.info(f"✓ Framgång! Hittade {len(jobs)} jobb")
                else:
                    self._save_status('partial', f'Hittade endast {len(jobs)} jobb (behöver 3)', len(jobs))
                    logger.warning(f"Hittade endast {len(jobs)} jobb (behöver 3)")
                
                # Stäng browser
                browser.close()
                
                return len(jobs) >= 3
                
        except Exception as e:
            logger.error(f"Kritiskt fel: {e}")
            self._save_status('error', str(e), 0)
            return False


def main():
    """Huvudfunktion"""
    # Skapa logs-mapp om den inte finns
    Path('/workspace/logs').mkdir(exist_ok=True)
    
    try:
        bot = ArbetsformedlingenBot()
        success = bot.run()
        
        if success:
            logger.info("✓ Jobbet är klart!")
            return 0
        else:
            logger.error("✗ Kunde inte hitta tillräckligt många jobb")
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
