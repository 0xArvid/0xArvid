"""
Loggningssystem för Mail Access Checker
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

# Färgkoder för terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class ColoredFormatter(logging.Formatter):
    """Formatter som lägger till färger baserat på log-nivå"""
    
    COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD
    }
    
    def format(self, record):
        # Lägg till färg baserat på nivå
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Colors.END}"
        
        # Formatera meddelandet
        formatted = super().format(record)
        return formatted

class MailAccessLogger:
    """Anpassad logger för Mail Access Checker"""
    
    def __init__(self, name: str = "MailAccessChecker", verbose: bool = False, quiet: bool = False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Rensa befintliga handlers
        self.logger.handlers.clear()
        
        # Sätt log-nivå baserat på parametrar
        if quiet:
            console_level = logging.ERROR
        elif verbose:
            console_level = logging.DEBUG
        else:
            console_level = logging.INFO
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        
        # Formatera för console (med färger)
        console_format = '[%(asctime)s] [%(levelname)s] %(message)s'
        console_formatter = ColoredFormatter(console_format, datefmt='%H:%M:%S')
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
        
        # File handler (utan färger)
        self.file_handler = None
    
    def add_file_handler(self, log_file: str):
        """Lägger till fil-handler för att spara loggar"""
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self.file_handler.setLevel(logging.DEBUG)
        
        # Formatera för fil (utan färger)
        file_format = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
        file_formatter = logging.Formatter(file_format, datefmt='%Y-%m-%d %H:%M:%S')
        self.file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(self.file_handler)
    
    def info(self, message: str):
        """Loggar info-meddelande"""
        self.logger.info(message)
    
    def success(self, message: str):
        """Loggar framgångsmeddelande (grön)"""
        self.logger.info(f"{Colors.GREEN}[SUCCESS]{Colors.END} {message}")
    
    def warning(self, message: str):
        """Loggar varningsmeddelande"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Loggar felmeddelande"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Loggar kritiskt meddelande"""
        self.logger.critical(message)
    
    def debug(self, message: str):
        """Loggar debug-meddelande"""
        self.logger.debug(message)
    
    def banner(self, text: str):
        """Visar banner med text"""
        banner_width = 60
        border = "=" * banner_width
        
        lines = text.split('\n')
        max_line_length = max(len(line) for line in lines)
        
        self.info(f"\n{Colors.CYAN}{border}{Colors.END}")
        for line in lines:
            padding = (banner_width - len(line) - 2) // 2
            padded_line = " " * padding + line + " " * padding
            if len(padded_line) < banner_width - 2:
                padded_line += " "
            self.info(f"{Colors.CYAN}|{Colors.END}{Colors.BOLD}{padded_line}{Colors.END}{Colors.CYAN}|{Colors.END}")
        self.info(f"{Colors.CYAN}{border}{Colors.END}")
    
    def progress(self, current: int, total: int, message: str = ""):
        """Visar progress information"""
        percentage = (current / total) * 100 if total > 0 else 0
        progress_bar_length = 30
        filled_length = int(progress_bar_length * current // total) if total > 0 else 0
        
        bar = "█" * filled_length + "░" * (progress_bar_length - filled_length)
        
        progress_msg = f"\r{Colors.BLUE}[{bar}]{Colors.END} {percentage:.1f}% ({current}/{total})"
        if message:
            progress_msg += f" - {message}"
        
        print(progress_msg, end='', flush=True)
    
    def result_summary(self, results: dict):
        """Visar sammanfattning av resultat"""
        total = sum(results.values())
        
        self.info(f"\n{Colors.BOLD}=== RESULTATSAMMANFATTNING ==={Colors.END}")
        
        for status, count in results.items():
            percentage = (count / total * 100) if total > 0 else 0
            color = self._get_status_color(status)
            self.info(f"{color}{status.upper():<12}{Colors.END}: {count:>5} ({percentage:>5.1f}%)")
        
        self.info(f"{Colors.BOLD}{'TOTALT':<12}: {total:>5}{Colors.END}")
    
    def _get_status_color(self, status: str) -> str:
        """Hämtar färg baserat på status"""
        status_colors = {
            'valid': Colors.GREEN,
            'invalid': Colors.RED,
            'timeout': Colors.YELLOW,
            'error': Colors.RED,
            'rate_limited': Colors.YELLOW,
            'unknown': Colors.PURPLE
        }
        return status_colors.get(status.lower(), Colors.WHITE)

def setup_logger(name: str = "MailAccessChecker", 
                verbose: bool = False, 
                quiet: bool = False,
                log_file: Optional[str] = None) -> MailAccessLogger:
    """
    Skapar och konfigurerar logger
    
    Args:
        name: Namn på logger
        verbose: Om verbose output ska användas
        quiet: Om endast errors ska visas
        log_file: Filnamn för att spara loggar
    
    Returns:
        Konfigurerad MailAccessLogger instans
    """
    logger = MailAccessLogger(name, verbose, quiet)
    
    if log_file:
        logger.add_file_handler(log_file)
    
    return logger