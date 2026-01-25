"""
Configuration module for Bybit Trading Bot
Loads settings from .env file
"""
import os
from dotenv import load_dotenv
from typing import List, Set

# Load environment variables
load_dotenv()

# FIX_01: Symbols known to be available on Bybit Testnet (linear perpetual)
# SHIBUSDT and some others may not exist on testnet - exclude or validate at runtime
TESTNET_AVAILABLE_SYMBOLS: Set[str] = frozenset([
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "TRXUSDT",
    "MATICUSDT", "LINKUSDT", "TONUSDT", "LTCUSDT", "BCHUSDT",
    "UNIUSDT", "ATOMUSDT", "XLMUSDT", "FILUSDT", "ETCUSDT",
    "APTUSDT", "NEARUSDT", "OPUSDT", "ARBUSDT", "VETUSDT",
    "AAVEUSDT", "ALGOUSDT", "MANAUSDT", "EGLDUSDT", "SANDUSDT",
    "AXSUSDT", "THETAUSDT", "XTZUSDT", "FTMUSDT", "EOSUSDT",
    "MKRUSDT", "CRVUSDT", "KAVAUSDT", "RUNEUSDT", "GALAUSDT",
    "WAVESUSDT", "ZILUSDT", "IOTAUSDT", "ENJUSDT", "ONEUSDT",
    "CHZUSDT", "BATUSDT",
    # May not be on testnet - include for validate to filter: ICPUSDT, SHIBUSDT, PEOPLEUSDT
])


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
    EMA_MIN_INIT_CANDLES = int(os.getenv("EMA_MIN_INIT_CANDLES", "50"))  # FIX_04: min candles to init EMA
    RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "5"))  # Percentage
    LEVERAGE = int(os.getenv("LEVERAGE", "10"))
    MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", "5"))
    STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "5"))  # Percentage
    TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "3"))  # Percentage
    
    # Optional features
    ENABLE_POSITION_TRACKER = os.getenv("ENABLE_POSITION_TRACKER", "true").lower() == "true"
    DEBUG_WS_KLINE = os.getenv("DEBUG_WS_KLINE", "false").lower() == "true"  # FIX_03: log raw kline messages
    
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


def get_symbols_to_fetch() -> List[str]:
    """FIX_01: When TESTNET, return only symbols in TESTNET_AVAILABLE_SYMBOLS. Otherwise all."""
    if not config.TESTNET:
        return list(config.SYMBOLS)
    return [s for s in config.SYMBOLS if s in TESTNET_AVAILABLE_SYMBOLS]
