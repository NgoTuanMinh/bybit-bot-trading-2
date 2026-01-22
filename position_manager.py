"""
Position Manager and Account Manager
Handles position tracking, risk management, and account balance
"""
import logging
from typing import Dict, Optional, Tuple
from pybit.unified_trading import HTTP
from config import config

logger = logging.getLogger(__name__)


class AccountManager:
    """Manages account balance and margin"""
    
    def __init__(self, session: HTTP):
        self.session = session
        self._balance: Optional[float] = None
        self._available_margin: Optional[float] = None
    
    def get_balance(self) -> float:
        """Get current wallet balance"""
        try:
            response = self.session.get_wallet_balance(
                category="linear",
                accountType="UNIFIED"
            )
            
            if response["retCode"] == 0:
                result = response["result"]
                if result.get("list"):
                    account = result["list"][0]
                    total_equity = float(account.get("totalEquity", 0))
                    self._balance = total_equity
                    logger.debug(f"Account balance: {total_equity:.2f} USDT")
                    return total_equity
            else:
                logger.error(f"Error getting balance: {response['retMsg']}")
            
            return self._balance or 0.0
            
        except Exception as e:
            logger.error(f"Exception getting balance: {e}", exc_info=True)
            return self._balance or 0.0
    
    def update_balance(self, pnl: float):
        """Update balance after position close (for tracking)"""
        if self._balance is not None:
            self._balance += pnl
            logger.info(f"Balance updated: {self._balance:.2f} USDT (PnL: {pnl:+.2f})")
    
    def get_available_margin(self) -> float:
        """Get available margin for new positions"""
        try:
            response = self.session.get_wallet_balance(
                category="linear",
                accountType="UNIFIED"
            )
            
            if response["retCode"] == 0:
                result = response["result"]
                if result.get("list"):
                    account = result["list"][0]
                    available_balance = float(account.get("availableBalance", 0))
                    self._available_margin = available_balance
                    return available_balance
            else:
                logger.error(f"Error getting available margin: {response['retMsg']}")
            
            return self._available_margin or 0.0
            
        except Exception as e:
            logger.error(f"Exception getting available margin: {e}", exc_info=True)
            return self._available_margin or 0.0


class PositionManager:
    """Manages active positions and risk calculations"""
    
    def __init__(self, account_manager: AccountManager, session: HTTP):
        self.account_manager = account_manager
        self.session = session
        self.active_positions: Dict[str, dict] = {}
        self.max_positions = config.MAX_POSITIONS
    
    def can_open_position(self, symbol: str) -> bool:
        """Check if we can open a new position"""
        # Check if position already exists for this symbol
        if symbol in self.active_positions:
            logger.debug(f"Position already exists for {symbol}")
            return False
        
        # Check max positions limit
        if len(self.active_positions) >= self.max_positions:
            logger.debug(f"Max positions reached ({self.max_positions})")
            return False
        
        return True
    
    def calculate_position_size(self, account_balance: float, entry_price: float) -> float:
        """
        Calculate position size based on risk per trade
        Position Size = (Account Balance × RISK_PER_TRADE%) × Leverage / Entry Price
        """
        risk_amount = account_balance * (config.RISK_PER_TRADE / 100)
        position_value = risk_amount * config.LEVERAGE
        position_size = position_value / entry_price
        
        logger.debug(f"Position size calculation: Balance={account_balance:.2f}, "
                    f"Risk={risk_amount:.2f}, Value={position_value:.2f}, Size={position_size:.6f}")
        
        return position_size
    
    def calculate_sl_tp(self, entry_price: float, side: str) -> Tuple[float, float]:
        """
        Calculate Stop Loss and Take Profit prices
        LONG: SL = Entry × (1 - STOP_LOSS_PCT%), TP = Entry × (1 + TAKE_PROFIT_PCT%)
        SHORT: SL = Entry × (1 + STOP_LOSS_PCT%), TP = Entry × (1 - TAKE_PROFIT_PCT%)
        """
        if side.upper() == "BUY" or side.upper() == "LONG":
            # Long position
            sl_price = entry_price * (1 - config.STOP_LOSS_PCT / 100)
            tp_price = entry_price * (1 + config.TAKE_PROFIT_PCT / 100)
        else:
            # Short position
            sl_price = entry_price * (1 + config.STOP_LOSS_PCT / 100)
            tp_price = entry_price * (1 - config.TAKE_PROFIT_PCT / 100)
        
        return sl_price, tp_price
    
    def add_position(self, symbol: str, position_data: dict):
        """Add a new position to tracking"""
        self.active_positions[symbol] = position_data
        logger.info(f"Added position: {symbol} - {position_data}")
    
    def remove_position(self, symbol: str):
        """Remove position from tracking"""
        if symbol in self.active_positions:
            removed = self.active_positions.pop(symbol)
            logger.info(f"Removed position: {symbol} - {removed}")
    
    def get_position(self, symbol: str) -> Optional[dict]:
        """Get position data for a symbol"""
        return self.active_positions.get(symbol)
    
    def sync_positions(self):
        """Sync positions from Bybit API"""
        try:
            response = self.session.get_positions(
                category="linear",
                settleCoin="USDT"
            )
            
            if response["retCode"] == 0:
                positions = response["result"].get("list", [])
                active_symbols = set()
                
                for pos in positions:
                    size = float(pos.get("size", 0))
                    if size > 0:  # Active position
                        symbol = pos.get("symbol")
                        active_symbols.add(symbol)
                        
                        # Update or add position
                        self.active_positions[symbol] = {
                            "symbol": symbol,
                            "side": pos.get("side"),
                            "size": size,
                            "entry_price": float(pos.get("avgPrice", 0)),
                            "mark_price": float(pos.get("markPrice", 0)),
                            "unrealised_pnl": float(pos.get("unrealisedPnl", 0)),
                            "leverage": pos.get("leverage"),
                            "sl_price": float(pos.get("stopLoss", 0)) if pos.get("stopLoss") else None,
                            "tp_price": float(pos.get("takeProfit", 0)) if pos.get("takeProfit") else None
                        }
                
                # Remove positions that are no longer active
                for symbol in list(self.active_positions.keys()):
                    if symbol not in active_symbols:
                        self.remove_position(symbol)
                
                logger.debug(f"Synced positions: {len(self.active_positions)} active")
            else:
                logger.error(f"Error syncing positions: {response['retMsg']}")
                
        except Exception as e:
            logger.error(f"Exception syncing positions: {e}", exc_info=True)
