"""
OpenBullet 2-inspirerad HTTP automation för Parakey.com
Fokuserar på snabba HTTP-requests utan full browser rendering
"""

import asyncio
import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from fake_useragent import UserAgent
import httpx
import requests
from loguru import logger
from urllib.parse import urljoin, urlparse


@dataclass
class ProxyConfig:
    """Proxy configuration för rotation"""
    protocol: str  # http, https, socks4, socks5
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    
    @property
    def url(self) -> str:
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"


@dataclass
class RequestConfig:
    """Konfiguration för requests (OpenBullet-stil)"""
    method: str = "GET"
    headers: Dict[str, str] = None
    data: Dict[str, Any] = None
    json_data: Dict[str, Any] = None
    cookies: Dict[str, str] = None
    timeout: int = 10
    follow_redirects: bool = True
    verify_ssl: bool = True


class OpenBulletStyleAutomation:
    """
    OpenBullet 2-inspirerad automation klass
    Fokuserar på snabba HTTP-operationer utan full browser
    """
    
    def __init__(self, base_url: str = "https://www.parakey.co"):
        self.base_url = base_url
        self.session = requests.Session()
        self.ua = UserAgent()
        self.proxies: List[ProxyConfig] = []
        self.current_proxy_index = 0
        
        # Default headers för att simulera riktig browser
        self._setup_default_headers()
        
        logger.info("OpenBullet-style automation initialized")
    
    def _setup_default_headers(self):
        """Setup default headers för att undvika detektion"""
        self.session.headers.update({
            'User-Agent': self.ua.chrome,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
    
    def add_proxy(self, proxy: ProxyConfig):
        """Lägg till proxy för rotation"""
        self.proxies.append(proxy)
        logger.info(f"Added proxy: {proxy.host}:{proxy.port}")
    
    def rotate_proxy(self):
        """Rotera till nästa proxy"""
        if not self.proxies:
            return
        
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        current_proxy = self.proxies[self.current_proxy_index]
        
        self.session.proxies = {
            'http': current_proxy.url,
            'https': current_proxy.url
        }
        
        logger.info(f"Rotated to proxy: {current_proxy.host}:{current_proxy.port}")
    
    def rotate_user_agent(self):
        """Rotera User-Agent för att undvika detektion"""
        new_ua = self.ua.chrome
        self.session.headers['User-Agent'] = new_ua
        logger.debug(f"Rotated User-Agent: {new_ua}")
    
    def add_human_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Lägg till mänsklig delay för att undvika rate limiting"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        logger.debug(f"Human delay: {delay:.2f}s")
    
    def make_request(self, 
                    endpoint: str, 
                    config: RequestConfig = None,
                    use_proxy_rotation: bool = False,
                    use_ua_rotation: bool = False) -> requests.Response:
        """
        Gör HTTP request med OpenBullet-stil konfiguration
        """
        if config is None:
            config = RequestConfig()
        
        # Rotera proxy och UA om specificerat
        if use_proxy_rotation:
            self.rotate_proxy()
        if use_ua_rotation:
            self.rotate_user_agent()
        
        # Bygg full URL
        url = urljoin(self.base_url, endpoint)
        
        # Förbered request parameters
        request_kwargs = {
            'method': config.method,
            'url': url,
            'timeout': config.timeout,
            'allow_redirects': config.follow_redirects,
            'verify': config.verify_ssl
        }
        
        # Lägg till headers, data, etc.
        if config.headers:
            request_kwargs['headers'] = {**self.session.headers, **config.headers}
        
        if config.data:
            request_kwargs['data'] = config.data
        
        if config.json_data:
            request_kwargs['json'] = config.json_data
        
        if config.cookies:
            request_kwargs['cookies'] = config.cookies
        
        try:
            logger.info(f"Making {config.method} request to {url}")
            response = self.session.request(**request_kwargs)
            
            logger.info(f"Response: {response.status_code} ({len(response.content)} bytes)")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def discover_endpoints(self) -> Dict[str, int]:
        """
        Upptäck tillgängliga endpoints (reconnaissance)
        OpenBullet-stil endpoint discovery
        """
        common_endpoints = [
            "/",
            "/login",
            "/api/",
            "/api/v1/",
            "/portal/",
            "/admin/",
            "/dashboard/",
            "/auth/",
            "/oauth/",
            "/api/auth/",
            "/.well-known/",
            "/robots.txt",
            "/sitemap.xml"
        ]
        
        results = {}
        
        for endpoint in common_endpoints:
            try:
                response = self.make_request(endpoint, use_ua_rotation=True)
                results[endpoint] = response.status_code
                
                # Log intressanta fynd
                if response.status_code == 200:
                    logger.success(f"Found accessible endpoint: {endpoint}")
                elif response.status_code == 401:
                    logger.warning(f"Authentication required: {endpoint}")
                elif response.status_code == 403:
                    logger.warning(f"Forbidden access: {endpoint}")
                
                self.add_human_delay(0.5, 2.0)
                
            except Exception as e:
                logger.error(f"Error checking {endpoint}: {e}")
                results[endpoint] = -1
        
        return results
    
    def analyze_login_form(self, login_endpoint: str = "/login") -> Dict[str, Any]:
        """
        Analysera login-formulär för att förstå autentiseringsmekanismen
        """
        try:
            response = self.make_request(login_endpoint)
            
            if response.status_code != 200:
                logger.error(f"Could not access login page: {response.status_code}")
                return {}
            
            # Enkel parsing av login-formulär
            content = response.text.lower()
            
            analysis = {
                'has_csrf_token': 'csrf' in content or '_token' in content,
                'has_captcha': 'captcha' in content or 'recaptcha' in content,
                'has_mfa': '2fa' in content or 'mfa' in content or 'totp' in content,
                'form_action': None,
                'input_fields': [],
                'javascript_heavy': '<script' in content and content.count('<script') > 5
            }
            
            logger.info(f"Login form analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing login form: {e}")
            return {}
    
    def attempt_login(self, 
                     username: str, 
                     password: str,
                     login_endpoint: str = "/login") -> bool:
        """
        Försök logga in med OpenBullet-stil HTTP requests
        """
        try:
            # Först, hämta login-sidan för tokens/cookies
            login_page = self.make_request(login_endpoint)
            
            if login_page.status_code != 200:
                logger.error("Could not access login page")
                return False
            
            # Extrahera CSRF token om det finns (enkel regex)
            csrf_token = None
            import re
            csrf_match = re.search(r'name=["\']_token["\'] value=["\']([^"\']+)["\']', login_page.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                logger.info("Found CSRF token")
            
            # Förbered login data
            login_data = {
                'username': username,
                'email': username,  # Backup om de använder email
                'password': password
            }
            
            if csrf_token:
                login_data['_token'] = csrf_token
            
            # Gör login request
            login_config = RequestConfig(
                method="POST",
                data=login_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': urljoin(self.base_url, login_endpoint)
                }
            )
            
            self.add_human_delay(1, 3)
            
            response = self.make_request(login_endpoint, login_config)
            
            # Analysera response för att se om login lyckades
            success_indicators = [
                'dashboard' in response.url.lower(),
                'portal' in response.url.lower(),
                'welcome' in response.text.lower(),
                response.status_code == 302,  # Redirect efter lyckad login
            ]
            
            failure_indicators = [
                'error' in response.text.lower(),
                'invalid' in response.text.lower(),
                'incorrect' in response.text.lower(),
                'failed' in response.text.lower(),
            ]
            
            if any(success_indicators) and not any(failure_indicators):
                logger.success("Login appears successful!")
                return True
            else:
                logger.warning("Login appears to have failed")
                return False
                
        except Exception as e:
            logger.error(f"Login attempt failed: {e}")
            return False


class AsyncOpenBulletStyle:
    """
    Async version för bättre prestanda (mer OpenBullet 2-likt)
    """
    
    def __init__(self, base_url: str = "https://www.parakey.co"):
        self.base_url = base_url
        self.ua = UserAgent()
        self.proxies: List[ProxyConfig] = []
        
    async def make_concurrent_requests(self, 
                                     endpoints: List[str], 
                                     max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """
        Gör flera requests samtidigt (OpenBullet-stil concurrency)
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def make_single_request(endpoint: str) -> Dict[str, Any]:
            async with semaphore:
                async with httpx.AsyncClient() as client:
                    try:
                        url = urljoin(self.base_url, endpoint)
                        headers = {
                            'User-Agent': self.ua.chrome,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                        }
                        
                        response = await client.get(url, headers=headers, timeout=10)
                        
                        return {
                            'endpoint': endpoint,
                            'status_code': response.status_code,
                            'size': len(response.content),
                            'headers': dict(response.headers),
                            'success': True
                        }
                        
                    except Exception as e:
                        return {
                            'endpoint': endpoint,
                            'error': str(e),
                            'success': False
                        }
        
        # Kör alla requests samtidigt
        tasks = [make_single_request(endpoint) for endpoint in endpoints]
        results = await asyncio.gather(*tasks)
        
        return results


# Exempel på användning
if __name__ == "__main__":
    # Skapa automation instance
    automation = OpenBulletStyleAutomation()
    
    # Lägg till några proxies (exempel)
    # automation.add_proxy(ProxyConfig("http", "proxy1.example.com", 8080))
    
    # Upptäck endpoints
    logger.info("Starting endpoint discovery...")
    endpoints = automation.discover_endpoints()
    
    # Analysera login
    logger.info("Analyzing login form...")
    login_analysis = automation.analyze_login_form()
    
    # Testa login (med dummy credentials)
    # result = automation.attempt_login("test@example.com", "password123")
    
    logger.info("OpenBullet-style automation complete!")