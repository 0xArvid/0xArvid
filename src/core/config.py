"""
Konfigurationshantering för Mail Access Checker
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """Hanterar konfiguration för Mail Access Checker"""
    
    def __init__(self):
        # Standard konfiguration
        self.timeout = 30
        self.max_threads = 5
        self.retry_attempts = 3
        self.ssl_verify = True
        self.default_ports = {
            'imap': {'ssl': 993, 'plain': 143},
            'smtp': {'ssl': 465, 'starttls': 587, 'plain': 25},
            'pop3': {'ssl': 995, 'plain': 110}
        }
        
        # Output inställningar
        self.output_file = None
        self.verbose = False
        self.quiet = False
        
        # Protokoll inställningar
        self.protocol = 'imap'
        self.test_all_protocols = False
        
        # Input inställningar
        self.target_email = None
        self.target_password = None
        self.input_file = None
        
        # Avancerade inställningar
        self.user_agent = "Mail-Access-Checker/1.0"
        self.delay_between_attempts = 1
        self.proxy_list = []
        self.use_proxy = False
        
        # Provider-specifika inställningar
        self.email_providers = {}
        self._load_default_providers()
        
        # Email forwarding inställningar
        self.forward_to_email = None
        self.forward_from_email = None
        self.forward_password = None
        self.forward_smtp_server = None
        self.enable_forwarding = False
    
    def _load_default_providers(self):
        """Laddar standard e-postleverantörer"""
        self.email_providers = {
            'gmail.com': {
                'imap': {'host': 'imap.gmail.com', 'port': 993, 'ssl': True},
                'smtp': {'host': 'smtp.gmail.com', 'port': 587, 'tls': True}
            },
            'outlook.com': {
                'imap': {'host': 'outlook.office365.com', 'port': 993, 'ssl': True},
                'smtp': {'host': 'smtp-mail.outlook.com', 'port': 587, 'tls': True}
            },
            'hotmail.com': {
                'imap': {'host': 'outlook.office365.com', 'port': 993, 'ssl': True},
                'smtp': {'host': 'smtp-mail.outlook.com', 'port': 587, 'tls': True}
            },
            'yahoo.com': {
                'imap': {'host': 'imap.mail.yahoo.com', 'port': 993, 'ssl': True},
                'smtp': {'host': 'smtp.mail.yahoo.com', 'port': 587, 'tls': True}
            },
            'icloud.com': {
                'imap': {'host': 'imap.mail.me.com', 'port': 993, 'ssl': True},
                'smtp': {'host': 'smtp.mail.me.com', 'port': 587, 'tls': True}
            },
            'engineer.com': {
                'imap': {'host': 'imap.mail.com', 'port': 993, 'ssl': True},
                'smtp': {'host': 'smtp.mail.com', 'port': 587, 'tls': True}
            },
            'mail.com': {
                'imap': {'host': 'imap.mail.com', 'port': 993, 'ssl': True},
                'smtp': {'host': 'smtp.mail.com', 'port': 587, 'tls': True}
            }
        }
    
    def load_from_file(self, config_path: str) -> None:
        """Laddar konfiguration från YAML-fil"""
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                raise FileNotFoundError(f"Konfigurationsfil hittades inte: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if config_data:
                self._update_from_dict(config_data)
                
        except Exception as e:
            raise Exception(f"Fel vid läsning av konfigurationsfil: {e}")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Uppdaterar konfiguration från dictionary"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_from_args(self, args) -> None:
        """Uppdaterar konfiguration från CLI-argument"""
        if args.threads:
            self.max_threads = args.threads
        if args.timeout:
            self.timeout = args.timeout
        if args.output:
            self.output_file = args.output
        if args.verbose:
            self.verbose = args.verbose
        if args.quiet:
            self.quiet = args.quiet
        if args.protocol:
            self.protocol = args.protocol
            if args.protocol == 'all':
                self.test_all_protocols = True
        if args.target:
            self.target_email = args.target
        if args.password:
            self.target_password = args.password
        if args.file:
            self.input_file = args.file
        
        # Forwarding inställningar
        if hasattr(args, 'forward_to') and args.forward_to:
            self.forward_to_email = args.forward_to
        if hasattr(args, 'forward_from') and args.forward_from:
            self.forward_from_email = args.forward_from
        if hasattr(args, 'forward_password') and args.forward_password:
            self.forward_password = args.forward_password
        if hasattr(args, 'forward_smtp') and args.forward_smtp:
            self.forward_smtp_server = args.forward_smtp
            
        # Aktivera forwarding om alla nödvändiga parametrar finns
        if all([self.forward_to_email, self.forward_from_email, self.forward_password]):
            self.enable_forwarding = True
    
    def get_provider_config(self, email: str, protocol: str) -> Optional[Dict[str, Any]]:
        """Hämtar konfiguration för specifik e-postleverantör"""
        domain = email.split('@')[-1].lower()
        
        if domain in self.email_providers:
            provider = self.email_providers[domain]
            if protocol in provider:
                return provider[protocol]
        
        return None
    
    def save_to_file(self, config_path: str) -> None:
        """Sparar konfiguration till YAML-fil"""
        config_dict = {
            'timeout': self.timeout,
            'max_threads': self.max_threads,
            'retry_attempts': self.retry_attempts,
            'ssl_verify': self.ssl_verify,
            'default_ports': self.default_ports,
            'user_agent': self.user_agent,
            'delay_between_attempts': self.delay_between_attempts,
            'email_providers': self.email_providers
        }
        
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
    
    def validate(self) -> bool:
        """Validerar konfiguration"""
        if self.max_threads <= 0:
            raise ValueError("max_threads måste vara större än 0")
        
        if self.timeout <= 0:
            raise ValueError("timeout måste vara större än 0")
        
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts kan inte vara negativ")
        
        return True
    
    def __str__(self) -> str:
        """Returnerar strängrepresentation av konfiguration"""
        return f"""Mail Access Checker Configuration:
- Timeout: {self.timeout}s
- Max Threads: {self.max_threads}
- Retry Attempts: {self.retry_attempts}
- SSL Verify: {self.ssl_verify}
- Protocol: {self.protocol}
- Verbose: {self.verbose}
- Output File: {self.output_file or 'None'}
"""