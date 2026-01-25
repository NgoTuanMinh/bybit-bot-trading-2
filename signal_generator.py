"""
Trading Signal Generator
Detects EMA200 crossover signals and generates trading orders
"""
import logging
from typing import Optional, Dict
from kline_manager import KlineDataManager
from position_manager import PositionManager

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generates trading signals based on EMA200 crossover"""
    
    def __init__(self, kline_manager: KlineDataManager, position_manager: PositionManager):
        self.kline_manager = kline_manager
        self.position_manager = position_manager
    
    def check_crossover(self, symbol: str) -> Optional[Dict]:
        """
        Check for EMA200 crossover and generate signal if conditions are met
        Returns signal dict or None
        """
        try:
            state = self.kline_manager.get_symbol_state(symbol)
            if not state:
                return None
            # FIX_04: Skip signals for symbols not ready (e.g. insufficient candles for EMA)
            if not state.get("ready", False):
                logger.debug(f"Symbol {symbol} not ready for trading (insufficient EMA data), skipping")
                return None

            current_candle = state.get("current_candle")
            previous_candle = state.get("previous_candle")
            ema_200 = state.get("ema_200")
            if not current_candle or not previous_candle or not ema_200:
                return None
            
            current_close = current_candle["close"]
            previous_close = previous_candle["close"]
            
            # Check for crossover
            signal = None
            
            # BEARISH CROSSOVER (SHORT signal)
            # Previous: close < EMA200, Current: close > EMA200
            if previous_close < ema_200 and current_close > ema_200:
                signal = {
                    "type": "BEARISH_CROSSOVER",
                    "side": "Sell",  # Short position
                    "symbol": symbol,
                    "entry_price": current_close,
                    "previous_close": previous_close,
                    "current_close": current_close,
                    "ema_200": ema_200
                }
                logger.info(f"BEARISH crossover detected for {symbol}: "
                          f"Price crossed above EMA200 ({current_close:.2f} > {ema_200:.2f})")
            
            # BULLISH CROSSOVER (LONG signal)
            # Previous: close > EMA200, Current: close < EMA200
            elif previous_close > ema_200 and current_close < ema_200:
                signal = {
                    "type": "BULLISH_CROSSOVER",
                    "side": "Buy",  # Long position
                    "symbol": symbol,
                    "entry_price": current_close,
                    "previous_close": previous_close,
                    "current_close": current_close,
                    "ema_200": ema_200
                }
                logger.info(f"BULLISH crossover detected for {symbol}: "
                          f"Price crossed below EMA200 ({current_close:.2f} < {ema_200:.2f})")
            
            # If signal detected, validate conditions
            if signal:
                # Check if we can open position
                if not self.position_manager.can_open_position(symbol):
                    logger.debug(f"Cannot open position for {symbol} (already exists or max positions reached)")
                    return None
                
                # Get account balance
                account_balance = self.position_manager.account_manager.get_balance()
                if account_balance <= 0:
                    logger.warning(f"Insufficient balance: {account_balance:.2f}")
                    return None
                
                # Calculate position size
                position_size = self.position_manager.calculate_position_size(
                    account_balance, 
                    signal["entry_price"]
                )
                
                # Calculate SL and TP
                sl_price, tp_price = self.position_manager.calculate_sl_tp(
                    signal["entry_price"],
                    signal["side"]
                )
                
                # Build order parameters
                order_params = {
                    "symbol": symbol,
                    "side": signal["side"],
                    "order_type": "Market",
                    "qty": round(position_size, 6),
                    "sl_price": round(sl_price, 2),
                    "tp_price": round(tp_price, 2),
                    "signal_type": signal["type"],
                    "entry_price": signal["entry_price"],
                    "ema_200": ema_200
                }
                
                logger.info(f"Signal generated for {symbol}: {order_params}")
                return order_params
            
            return None
            
        except Exception as e:
            logger.error(f"Exception checking crossover for {symbol}: {e}", exc_info=True)
            return None
