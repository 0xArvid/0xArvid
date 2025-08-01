"""
Headless Browser automation för Parakey.com med avancerade stealth-tekniker
Fokuserar på att undvika detektion genom att simulera riktig browser
"""

import random
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from loguru import logger


@dataclass
class BrowserConfig:
    """Konfiguration för browser setup"""
    headless: bool = True
    use_stealth: bool = True
    window_size: tuple = (1920, 1080)
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    disable_images: bool = True
    disable_javascript: bool = False
    timeout: int = 30


class StealthHeadlessBrowser:
    """
    Avancerad headless browser med stealth-tekniker för att undvika detektion
    """
    
    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self.driver = None
        self.ua = UserAgent()
        self.setup_driver()
        
        logger.info("Stealth headless browser initialized")
    
    def setup_driver(self):
        """Setup Chrome driver med stealth-konfiguration"""
        try:
            if self.config.use_stealth:
                # Använd undetected-chromedriver för bättre stealth
                options = uc.ChromeOptions()
            else:
                options = Options()
            
            # Grundläggande options
            if self.config.headless:
                options.add_argument("--headless=new")  # Nya headless mode
            
            # Anti-detection arguments
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-component-extensions-with-background-pages")
            
            # Performance optimizations
            if self.config.disable_images:
                prefs = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", prefs)
            
            # Window size
            options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
            
            # User agent
            if self.config.user_agent:
                options.add_argument(f"--user-agent={self.config.user_agent}")
            elif not self.config.use_stealth:  # undetected-chromedriver hanterar UA automatiskt
                options.add_argument(f"--user-agent={self.ua.chrome}")
            
            # Proxy
            if self.config.proxy:
                options.add_argument(f"--proxy-server={self.config.proxy}")
            
            # Exclude automation switches
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Skapa driver
            if self.config.use_stealth:
                self.driver = uc.Chrome(options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            
            # Appliera ytterligare stealth-åtgärder
            self._apply_stealth_measures()
            
            # Set timeout
            self.driver.implicitly_wait(self.config.timeout)
            
            logger.success("Chrome driver setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            raise
    
    def _apply_stealth_measures(self):
        """Appliera avancerade stealth-åtgärder via JavaScript"""
        try:
            # Ta bort webdriver property
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # Fake chrome object
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            # Mock languages
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['sv-SE', 'sv', 'en-US', 'en']
                });
            """)
            
            # Canvas fingerprint randomization
            self.driver.execute_script("""
                const getContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type) {
                    if (type === '2d') {
                        const context = getContext.call(this, type);
                        const originalFillRect = context.fillRect;
                        context.fillRect = function(x, y, width, height) {
                            const randomOffset = Math.random() * 0.1;
                            originalFillRect.call(this, x + randomOffset, y + randomOffset, width, height);
                        };
                        return context;
                    }
                    return getContext.call(this, type);
                };
            """)
            
            # WebGL fingerprint protection
            self.driver.execute_script("""
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';  // UNMASKED_VENDOR_WEBGL
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';  // UNMASKED_RENDERER_WEBGL
                    }
                    return getParameter.call(this, parameter);
                };
            """)
            
            # Screen resolution consistency
            self.driver.execute_script(f"""
                Object.defineProperty(screen, 'width', {{
                    get: () => {self.config.window_size[0]}
                }});
                Object.defineProperty(screen, 'height', {{
                    get: () => {self.config.window_size[1]}
                }});
            """)
            
            logger.info("Stealth measures applied successfully")
            
        except Exception as e:
            logger.warning(f"Some stealth measures failed: {e}")
    
    def navigate_to(self, url: str) -> bool:
        """Navigera till URL med human-like beteende"""
        try:
            logger.info(f"Navigating to: {url}")
            
            # Random delay före navigation
            self._human_delay(0.5, 2.0)
            
            self.driver.get(url)
            
            # Vänta på att sidan laddas
            WebDriverWait(self.driver, self.config.timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Simulera mänskligt scroll-beteende
            self._simulate_human_scroll()
            
            logger.success(f"Successfully navigated to {url}")
            return True
            
        except TimeoutException:
            logger.error(f"Timeout loading {url}")
            return False
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False
    
    def _human_delay(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Mänsklig delay för att undvika detektion"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _simulate_human_scroll(self):
        """Simulera mänskligt scroll-beteende"""
        try:
            # Random scroll för att simulera användare som läser sidan
            scroll_actions = random.randint(1, 3)
            
            for _ in range(scroll_actions):
                scroll_amount = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                self._human_delay(0.5, 1.5)
            
            # Scrolla tillbaka till toppen
            self.driver.execute_script("window.scrollTo(0, 0);")
            self._human_delay(0.3, 1.0)
            
        except Exception as e:
            logger.debug(f"Scroll simulation failed: {e}")
    
    def find_element_safe(self, by: By, value: str, timeout: int = 10) -> Optional[Any]:
        """Säker element-finding med timeout"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
    
    def human_type(self, element, text: str):
        """Simulera mänsklig typning"""
        try:
            element.clear()
            
            for char in text:
                element.send_keys(char)
                # Random delay mellan tangenttryckningar
                delay = random.uniform(0.05, 0.2)
                time.sleep(delay)
            
            # Extra delay efter typning
            self._human_delay(0.5, 1.0)
            
        except Exception as e:
            logger.error(f"Typing error: {e}")
    
    def human_click(self, element):
        """Simulera mänskligt klick med mouse movement"""
        try:
            # Scrolla till element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self._human_delay(0.3, 0.8)
            
            # Använd ActionChains för mer naturlig mouse movement
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.pause(random.uniform(0.1, 0.3))
            actions.click()
            actions.perform()
            
            self._human_delay(0.5, 1.5)
            
        except Exception as e:
            logger.error(f"Click error: {e}")
    
    def analyze_page_structure(self) -> Dict[str, Any]:
        """Analysera sidans struktur för att förstå layout"""
        try:
            # Grundläggande sidinformation
            page_info = {
                'title': self.driver.title,
                'url': self.driver.current_url,
                'has_forms': len(self.driver.find_elements(By.TAG_NAME, "form")) > 0,
                'has_login_fields': False,
                'has_captcha': False,
                'javascript_heavy': False,
                'security_headers': {},
                'meta_info': {}
            }
            
            # Kontrollera för login-fält
            login_indicators = [
                "input[type='password']",
                "input[name*='password']",
                "input[name*='email']",
                "input[name*='username']",
                "button[type='submit']"
            ]
            
            for indicator in login_indicators:
                elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                if elements:
                    page_info['has_login_fields'] = True
                    break
            
            # Kontrollera för CAPTCHA
            captcha_indicators = [
                ".captcha",
                ".recaptcha",
                "#captcha",
                "[data-captcha]",
                "iframe[src*='recaptcha']"
            ]
            
            for indicator in captcha_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements:
                        page_info['has_captcha'] = True
                        break
                except:
                    continue
            
            # Kontrollera JavaScript-intensivitet
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            page_info['javascript_heavy'] = len(scripts) > 10
            
            # Hämta meta-information
            try:
                meta_elements = self.driver.find_elements(By.TAG_NAME, "meta")
                for meta in meta_elements:
                    name = meta.get_attribute("name")
                    content = meta.get_attribute("content")
                    if name and content:
                        page_info['meta_info'][name] = content
            except:
                pass
            
            logger.info(f"Page analysis complete: {page_info}")
            return page_info
            
        except Exception as e:
            logger.error(f"Page analysis error: {e}")
            return {}
    
    def attempt_login(self, username: str, password: str, 
                     login_url: str = None) -> Dict[str, Any]:
        """
        Försök logga in med mänskligt beteende
        """
        result = {
            'success': False,
            'error': None,
            'redirect_url': None,
            'took_seconds': 0
        }
        
        start_time = time.time()
        
        try:
            # Navigera till login-sida om specificerad
            if login_url:
                if not self.navigate_to(login_url):
                    result['error'] = "Failed to navigate to login page"
                    return result
            
            # Analysera sidan
            page_structure = self.analyze_page_structure()
            
            if not page_structure.get('has_login_fields'):
                result['error'] = "No login fields detected on page"
                return result
            
            if page_structure.get('has_captcha'):
                result['error'] = "CAPTCHA detected - manual intervention required"
                return result
            
            # Hitta login-fält
            username_field = None
            password_field = None
            
            # Försök olika selectors för användarnamn
            username_selectors = [
                "input[type='email']",
                "input[name*='email']",
                "input[name*='username']",
                "input[name*='user']",
                "input[id*='email']",
                "input[id*='username']",
                "input[placeholder*='email']",
                "input[placeholder*='username']"
            ]
            
            for selector in username_selectors:
                username_field = self.find_element_safe(By.CSS_SELECTOR, selector, 2)
                if username_field:
                    logger.info(f"Found username field with selector: {selector}")
                    break
            
            # Hitta lösenordsfält
            password_field = self.find_element_safe(By.CSS_SELECTOR, "input[type='password']", 2)
            
            if not username_field or not password_field:
                result['error'] = "Could not locate username or password fields"
                return result
            
            # Simulera mänsklig interaktion
            logger.info("Starting human-like login process...")
            
            # Klicka på användarnamn-fält och skriv
            self.human_click(username_field)
            self.human_type(username_field, username)
            
            # Kort paus som en människa skulle göra
            self._human_delay(0.8, 2.0)
            
            # Klicka på lösenord-fält och skriv
            self.human_click(password_field)
            self.human_type(password_field, password)
            
            # Längre paus innan submit
            self._human_delay(1.0, 3.0)
            
            # Hitta och klicka submit-knapp
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[name*='login']",
                "button[id*='login']",
                ".login-button",
                ".btn-login"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                submit_button = self.find_element_safe(By.CSS_SELECTOR, selector, 2)
                if submit_button:
                    break
            
            if not submit_button:
                # Fallback: tryck Enter på lösenordsfält
                password_field.send_keys("\n")
            else:
                self.human_click(submit_button)
            
            # Vänta på response
            self._human_delay(2.0, 5.0)
            
            # Kontrollera om login lyckades
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Success indicators
            success_indicators = [
                'dashboard' in current_url.lower(),
                'portal' in current_url.lower(),
                'profile' in current_url.lower(),
                'welcome' in page_source,
                'logout' in page_source,
                'dashboard' in page_source
            ]
            
            # Error indicators
            error_indicators = [
                'error' in page_source,
                'invalid' in page_source,
                'incorrect' in page_source,
                'failed' in page_source,
                'login' in current_url.lower() and 'error' in current_url.lower()
            ]
            
            if any(success_indicators) and not any(error_indicators):
                result['success'] = True
                result['redirect_url'] = current_url
                logger.success("Login appears successful!")
            else:
                result['error'] = "Login appears to have failed"
                logger.warning("Login appears to have failed")
            
        except Exception as e:
            result['error'] = f"Login process error: {str(e)}"
            logger.error(f"Login process error: {e}")
        
        finally:
            result['took_seconds'] = time.time() - start_time
        
        return result
    
    def take_screenshot(self, filename: str = None) -> str:
        """Ta screenshot för debugging"""
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return ""
    
    def get_page_source(self) -> str:
        """Hämta sidans källkod"""
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Error getting page source: {e}")
            return ""
    
    def close(self):
        """Stäng browser"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")


# Exempel på användning
if __name__ == "__main__":
    # Skapa browser med stealth-konfiguration
    config = BrowserConfig(
        headless=True,
        use_stealth=True,
        disable_images=True
    )
    
    browser = StealthHeadlessBrowser(config)
    
    try:
        # Navigera till Parakey
        browser.navigate_to("https://www.parakey.co")
        
        # Analysera sidan
        analysis = browser.analyze_page_structure()
        
        # Ta screenshot för debugging
        browser.take_screenshot("parakey_homepage.png")
        
        logger.info("Browser automation complete!")
        
    finally:
        browser.close()