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
    
    def __init__(self, period: int = 200, min_init_candles: int = 50):
        self.period = period
        self.min_init_candles = min_init_candles  # FIX_04: min candles to init with SMA seed
        self.value: Optional[float] = None
        self.prices: deque = deque(maxlen=period)
    
    def calculate(self, data: List[float], min_init: Optional[int] = None) -> Optional[float]:
        """
        Calculate EMA from a list of prices.
        FIX_04: If len(data) < period but >= min_init (default 50), use SMA of first min_init
        as seed and iterate to end. Otherwise standard: first EMA = SMA of first period values.
        """
        mi = min_init if min_init is not None else self.min_init_candles
        if len(data) < mi:
            return None
        
        multiplier = 2 / (self.period + 1)
        if len(data) >= self.period:
            # Standard: first EMA = SMA of first period
            sma = sum(data[:self.period]) / self.period
            ema = sma
            for price in data[self.period:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
        else:
            # FIX_04: Limited data - use SMA of first min_init as seed
            sma = sum(data[:mi]) / mi
            ema = sma
            for i in range(mi, len(data)):
                ema = (data[i] * multiplier) + (ema * (1 - multiplier))
        
        self.value = ema
        return ema
    
    def update(self, new_price: float) -> Optional[float]:
        """
        Update EMA with new price.
        FIX_04: Uses min_init_candles when computing initial EMA from buffered prices.
        """
        self.prices.append(new_price)
        if len(self.prices) < self.min_init_candles:
            return None
        if self.value is None:
            return self.calculate(list(self.prices), min_init=self.min_init_candles)
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
        self.klines: Dict[str, deque] = {}
        self.emas: Dict[str, EMAIndicator] = {}
        self.symbol_state: Dict[str, dict] = {}
        self._min_init = getattr(config, "EMA_MIN_INIT_CANDLES", 50)

    def _get_close_price(self, k) -> float:
        """Get close price from kline in list or dict format (FIX_03: WS sends dict)."""
        if isinstance(k, dict):
            return float(k.get("close", 0))
        return float(k[4])

    def validate_symbol(self, symbol: str) -> bool:
        """
        FIX_01: Validate symbol exists and is tradeable before fetch.
        Uses a lightweight get_kline(limit=1). Returns False on invalid or API error.
        """
        try:
            r = self.session.get_kline(
                category="linear",
                symbol=symbol,
                interval="15",
                limit=1
            )
            if r.get("retCode") != 0:
                logger.warning(f"Symbol {symbol} invalid or not available: {r.get('retMsg', 'unknown')}")
                return False
            return True
        except Exception as e:
            logger.warning(f"Symbol {symbol} validate failed: {e}")
            return False

    def get_valid_symbols(self) -> List[str]:
        """FIX_01: Symbols that have been successfully loaded (for WebSocket subscription)."""
        return list(self.klines.keys())

    def fetch_historical(self, symbol: str, limit: int = 1000) -> bool:
        """
        Fetch historical klines from Bybit.
        FIX_01: Wrapped in try-except; log.warning on failure; skip instead of crash.
        FIX_04: EMA init with min 50 candles; symbol marked ready only when EMA available.
        """
        try:
            logger.info(f"Fetching historical klines for {symbol} (limit={limit})")
            response = self.session.get_kline(
                category="linear",
                symbol=symbol,
                interval="15",
                limit=limit
            )
            if response.get("retCode") != 0:
                logger.warning(f"Fetch klines failed for {symbol}: {response.get('retMsg', 'unknown')}")
                return False

            kline_list = response.get("result", {}).get("list", [])
            if not kline_list:
                logger.warning(f"No kline data for {symbol}, skipping")
                return False

            kline_list = list(kline_list)
            kline_list.reverse()
            self.klines[symbol] = deque(kline_list, maxlen=limit)

            closes = [float(k[4]) for k in kline_list]
            ema_indicator = EMAIndicator(
                period=config.EMA_PERIOD,
                min_init_candles=getattr(config, "EMA_MIN_INIT_CANDLES", 50)
            )
            ema_value = ema_indicator.calculate(closes, min_init=self._min_init)

            if ema_value is not None:
                self.emas[symbol] = ema_indicator
                logger.info(f"EMA{config.EMA_PERIOD} for {symbol}: {ema_value:.2f}")
            else:
                logger.warning(f"Not enough data for EMA init for {symbol} (have {len(closes)}, need >={self._min_init})")

            ready = ema_value is not None
            cur = self._parse_kline(kline_list[-1])
            prev = self._parse_kline(kline_list[-2]) if len(kline_list) > 1 else None
            self.symbol_state[symbol] = {
                "current_candle": cur,
                "previous_candle": prev,
                "ema_200": ema_value,
                "last_cross": None,
                "is_above_ema": cur["close"] > ema_value if ema_value else None,
                "ready": ready,
            }
            return True

        except Exception as e:
            logger.warning(f"Exception fetching historical klines for {symbol}: {e}")
            return False
    
    def add_new_kline(self, symbol: str, kline_data: dict) -> bool:
        """
        Add new kline data and update EMA. kline_data from WebSocket (dict with open,close,confirm...).
        FIX_03: Use _get_close_price when reading from self.klines (mixed list/dict).
        FIX_04: Set ready=True only when ema_value is not None.
        """
        try:
            if symbol not in self.klines:
                logger.warning(f"Symbol {symbol} not initialized, skipping kline update")
                return False

            parsed_kline = self._parse_kline(kline_data)
            close_price = parsed_kline["close"]
            is_confirmed = kline_data.get("confirm", False)

            if is_confirmed:
                self.klines[symbol].append(kline_data)
                if symbol in self.emas:
                    ema_value = self.emas[symbol].update(close_price)
                else:
                    closes = [self._get_close_price(k) for k in self.klines[symbol]]
                    ema_indicator = EMAIndicator(
                        period=config.EMA_PERIOD,
                        min_init_candles=getattr(config, "EMA_MIN_INIT_CANDLES", 50)
                    )
                    ema_value = ema_indicator.calculate(closes, min_init=self._min_init)
                    self.emas[symbol] = ema_indicator

                ready = ema_value is not None
                if symbol in self.symbol_state:
                    s = self.symbol_state[symbol]
                    s["previous_candle"] = s["current_candle"]
                    s["current_candle"] = parsed_kline
                    s["ema_200"] = ema_value
                    s["is_above_ema"] = close_price > ema_value if ema_value else None
                    s["ready"] = ready

                ema_str = f"{ema_value:.2f}" if ema_value is not None else "n/a"
                logger.debug(f"Updated {symbol}: Close={close_price:.2f}, EMA={ema_str}, ready={ready}")
                return True
            else:
                if symbol in self.symbol_state:
                    self.symbol_state[symbol]["current_candle"] = parsed_kline
                return False

        except Exception as e:
            logger.warning(f"Exception adding new kline for {symbol}: {e}")
            return False
    
    def calculate_ema(self, symbol: str, period: int = 200) -> Optional[float]:
        """Calculate EMA for a symbol. Uses _get_close_price for mixed list/dict klines."""
        if symbol not in self.klines:
            return None
        closes = [self._get_close_price(k) for k in self.klines[symbol]]
        if len(closes) < max(period, self._min_init):
            return None
        ema_indicator = EMAIndicator(period=period, min_init_candles=self._min_init)
        return ema_indicator.calculate(closes, min_init=self._min_init)
    
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
