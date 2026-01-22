"""
Kline Data Manager and EMA Indicator
Handles historical kline data fetching and EMA calculation
"""
import logging
from typing import Dict, List, Optional
from collections import deque
from pybit.unified_trading import HTTP
from config import config

logger = logging.getLogger(__name__)


class EMAIndicator:
    """EMA (Exponential Moving Average) Indicator"""
    
    def __init__(self, period: int = 200):
        self.period = period
        self.value: Optional[float] = None
        self.prices: deque = deque(maxlen=period)
    
    def calculate(self, data: List[float]) -> float:
        """
        Calculate EMA from a list of prices
        EMA = Price(t) × k + EMA(y) × (1 – k)
        where k = 2 / (N + 1), N = period
        """
        if len(data) < self.period:
            return None
        
        # Start with SMA for first value
        sma = sum(data[:self.period]) / self.period
        multiplier = 2 / (self.period + 1)
        
        ema = sma
        for price in data[self.period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        self.value = ema
        return ema
    
    def update(self, new_price: float) -> float:
        """
        Update EMA with new price
        """
        self.prices.append(new_price)
        
        if len(self.prices) < self.period:
            return None
        
        if self.value is None:
            # Calculate initial EMA from all prices
            return self.calculate(list(self.prices))
        
        # Update EMA incrementally
        multiplier = 2 / (self.period + 1)
        self.value = (new_price * multiplier) + (self.value * (1 - multiplier))
        return self.value
    
    def get_value(self) -> Optional[float]:
        """Get current EMA value"""
        return self.value


class KlineDataManager:
    """Manages kline data and EMA calculations for multiple symbols"""
    
    def __init__(self):
        self.session = HTTP(
            testnet=config.TESTNET,
            api_key=config.API_KEY,
            api_secret=config.API_SECRET
        )
        self.klines: Dict[str, deque] = {}  # symbol -> deque of klines
        self.emas: Dict[str, EMAIndicator] = {}  # symbol -> EMAIndicator
        
        # Symbol state tracking
        self.symbol_state: Dict[str, dict] = {}
    
    def fetch_historical(self, symbol: str, limit: int = 1000) -> bool:
        """
        Fetch historical klines from Bybit
        Returns True if successful
        """
        try:
            logger.info(f"Fetching {limit} historical klines for {symbol}")
            
            response = self.session.get_kline(
                category="linear",
                symbol=symbol,
                interval="15",  # M15
                limit=limit
            )
            
            if response["retCode"] != 0:
                logger.error(f"Error fetching klines for {symbol}: {response['retMsg']}")
                return False
            
            kline_list = response["result"]["list"]
            # Reverse to get chronological order (oldest first)
            kline_list.reverse()
            
            # Store klines
            self.klines[symbol] = deque(kline_list, maxlen=limit)
            
            # Calculate EMA
            closes = [float(k[4]) for k in kline_list]  # close price is index 4
            ema_indicator = EMAIndicator(period=config.EMA_PERIOD)
            ema_value = ema_indicator.calculate(closes)
            
            if ema_value:
                self.emas[symbol] = ema_indicator
                logger.info(f"EMA200 for {symbol}: {ema_value:.2f}")
            else:
                logger.warning(f"Not enough data to calculate EMA200 for {symbol}")
            
            # Initialize symbol state
            if kline_list:
                current_candle = self._parse_kline(kline_list[-1])
                self.symbol_state[symbol] = {
                    "current_candle": current_candle,
                    "previous_candle": self._parse_kline(kline_list[-2]) if len(kline_list) > 1 else None,
                    "ema_200": ema_value,
                    "last_cross": None,
                    "is_above_ema": current_candle["close"] > ema_value if ema_value else None
                }
            
            return True
            
        except Exception as e:
            logger.error(f"Exception fetching historical klines for {symbol}: {e}", exc_info=True)
            return False
    
    def add_new_kline(self, symbol: str, kline_data: dict) -> bool:
        """
        Add new kline data and update EMA
        kline_data should be from WebSocket
        """
        try:
            if symbol not in self.klines:
                logger.warning(f"Symbol {symbol} not initialized, fetching historical first")
                self.fetch_historical(symbol)
                return False
            
            parsed_kline = self._parse_kline(kline_data)
            close_price = parsed_kline["close"]
            
            # Check if this is a confirmed (closed) candle
            is_confirmed = kline_data.get("confirm", False)
            
            if is_confirmed:
                # Add to klines deque
                self.klines[symbol].append(kline_data)
                
                # Update EMA
                if symbol in self.emas:
                    ema_value = self.emas[symbol].update(close_price)
                else:
                    # Recalculate from all klines
                    closes = [float(k[4]) for k in self.klines[symbol]]
                    ema_indicator = EMAIndicator(period=config.EMA_PERIOD)
                    ema_value = ema_indicator.calculate(closes)
                    self.emas[symbol] = ema_indicator
                
                # Update symbol state
                if symbol in self.symbol_state:
                    previous_candle = self.symbol_state[symbol]["current_candle"]
                    self.symbol_state[symbol]["previous_candle"] = previous_candle
                    self.symbol_state[symbol]["current_candle"] = parsed_kline
                    self.symbol_state[symbol]["ema_200"] = ema_value
                    self.symbol_state[symbol]["is_above_ema"] = close_price > ema_value if ema_value else None
                
                logger.debug(f"Updated {symbol}: Close={close_price:.2f}, EMA={ema_value:.2f if ema_value else None}")
                return True
            else:
                # Update current candle (not confirmed yet)
                if symbol in self.symbol_state:
                    self.symbol_state[symbol]["current_candle"] = parsed_kline
                return False
                
        except Exception as e:
            logger.error(f"Exception adding new kline for {symbol}: {e}", exc_info=True)
            return False
    
    def calculate_ema(self, symbol: str, period: int = 200) -> Optional[float]:
        """Calculate EMA for a symbol"""
        if symbol not in self.klines:
            return None
        
        closes = [float(k[4]) for k in self.klines[symbol]]
        if len(closes) < period:
            return None
        
        ema_indicator = EMAIndicator(period=period)
        return ema_indicator.calculate(closes)
    
    def get_current_ema(self, symbol: str) -> Optional[float]:
        """Get current EMA value for a symbol"""
        if symbol in self.emas:
            return self.emas[symbol].get_value()
        return None
    
    def get_symbol_state(self, symbol: str) -> Optional[dict]:
        """Get current state for a symbol"""
        return self.symbol_state.get(symbol)
    
    def _parse_kline(self, kline: list) -> dict:
        """
        Parse kline data from Bybit format
        [startTime, open, high, low, close, volume, turnover]
        """
        if isinstance(kline, dict):
            return {
                "start_time": int(kline.get("start", kline.get("startTime", 0))),
                "open": float(kline.get("open", 0)),
                "high": float(kline.get("high", 0)),
                "low": float(kline.get("low", 0)),
                "close": float(kline.get("close", 0)),
                "volume": float(kline.get("volume", 0)),
                "turnover": float(kline.get("turnover", 0)),
                "confirm": kline.get("confirm", False)
            }
        else:
            # List format
            return {
                "start_time": int(kline[0]),
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
                "turnover": float(kline[6]),
                "confirm": False
            }
