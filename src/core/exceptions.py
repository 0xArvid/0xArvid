"""
Anpassade exceptions för Mail Access Checker
"""

class MailAccessException(Exception):
    """Bas-exception för Mail Access Checker"""
    pass

class ConfigurationError(MailAccessException):
    """Exception för konfigurationsfel"""
    pass

class ConnectionError(MailAccessException):
    """Exception för anslutningsfel"""
    def __init__(self, message: str, host: str = None, port: int = None):
        super().__init__(message)
        self.host = host
        self.port = port

class AuthenticationError(MailAccessException):
    """Exception för autentiseringsfel"""
    def __init__(self, message: str, email: str = None):
        super().__init__(message)
        self.email = email

class ProtocolError(MailAccessException):
    """Exception för protokollspecifika fel"""
    def __init__(self, message: str, protocol: str = None):
        super().__init__(message)
        self.protocol = protocol

class TimeoutError(MailAccessException):
    """Exception för timeout-fel"""
    def __init__(self, message: str, timeout_duration: int = None):
        super().__init__(message)
        self.timeout_duration = timeout_duration

class RateLimitError(MailAccessException):
    """Exception när rate limit nås"""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after

class SSLError(MailAccessException):
    """Exception för SSL/TLS-relaterade fel"""
    pass

class InvalidCredentialsError(AuthenticationError):
    """Exception för ogiltiga inloggningsuppgifter"""
    pass

class AccountLockedError(AuthenticationError):
    """Exception när konto är låst"""
    pass

class TwoFactorAuthRequired(AuthenticationError):
    """Exception när tvåfaktor-autentisering krävs"""
    pass

class ProviderNotSupportedError(MailAccessException):
    """Exception när e-postleverantör inte stöds"""
    def __init__(self, message: str, provider: str = None):
        super().__init__(message)
        self.provider = provider

class FileNotFoundError(MailAccessException):
    """Exception när fil inte hittas"""
    pass

class InvalidFileFormatError(MailAccessException):
    """Exception för ogiltigt filformat"""
    pass