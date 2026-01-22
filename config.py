"""
Configuration module for Bybit Trading Bot
Loads settings from .env file
"""
import os
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()


def load_symbols() -> List[str]:
    """
    Load symbols from BYBIT_SYMBOLS environment variable (CSV format)
    Returns list of symbol strings
    """
    symbols_str = os.getenv("BYBIT_SYMBOLS", "")
    if not symbols_str:
        raise ValueError("BYBIT_SYMBOLS environment variable is not set")
    
    symbols = [s.strip().upper() for s in symbols_str.split(",") if s.strip()]
    if len(symbols) != 50:
        print(f"Warning: Expected 50 symbols, got {len(symbols)}")
    
    return symbols


class Config:
    """Configuration class for trading bot"""
    
    # API Credentials
    API_KEY = os.getenv("BYBIT_API_KEY", "")
    API_SECRET = os.getenv("BYBIT_API_SECRET", "")
    
    # Testnet flag
    TESTNET = os.getenv("TESTNET", "true").lower() == "true"
    
    # Trading Symbols
    SYMBOLS = load_symbols()
    
    # Trading Parameters
    TIMEFRAME = os.getenv("TIMEFRAME", "15")  # M15 = 15 minutes
    EMA_PERIOD = int(os.getenv("EMA_PERIOD", "200"))
    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "5"))  # Percentage
    LEVERAGE = int(os.getenv("LEVERAGE", "10"))
    MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", "5"))
    STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "5"))  # Percentage
    TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "3"))  # Percentage
    
    # Optional features
    ENABLE_POSITION_TRACKER = os.getenv("ENABLE_POSITION_TRACKER", "true").lower() == "true"
    
    # Bybit API URLs
    @property
    def base_url(self) -> str:
        """Get base URL for Bybit API"""
        if self.TESTNET:
            return "https://api-testnet.bybit.com"
        return "https://api.bybit.com"
    
    @property
    def ws_public_url(self) -> str:
        """Get WebSocket public URL"""
        if self.TESTNET:
            return "wss://stream-testnet.bybit.com/v5/public/linear"
        return "wss://stream.bybit.com/v5/public/linear"
    
    @property
    def ws_private_url(self) -> str:
        """Get WebSocket private URL"""
        if self.TESTNET:
            return "wss://stream-testnet.bybit.com/v5/private"
        return "wss://stream.bybit.com/v5/private"
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.API_KEY or not self.API_SECRET:
            raise ValueError("BYBIT_API_KEY and BYBIT_API_SECRET must be set")
        if not self.SYMBOLS:
            raise ValueError("No symbols configured")
        return True


# Global config instance
config = Config()
