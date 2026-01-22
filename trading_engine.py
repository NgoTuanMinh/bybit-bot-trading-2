"""
Trading Engine
Executes trades via Bybit API
"""
import logging
import time
from typing import Dict, Optional
from pybit.unified_trading import HTTP
from position_manager import PositionManager, AccountManager
from config import config

logger = logging.getLogger(__name__)


class TradingEngine:
    """Handles trade execution via Bybit API"""
    
    def __init__(self, position_manager: PositionManager):
        self.position_manager = position_manager
        self.session = HTTP(
            testnet=config.TESTNET,
            api_key=config.API_KEY,
            api_secret=config.API_SECRET
        )
    
    def execute_order(self, order_params: Dict) -> bool:
        """
        Execute a market order and set SL/TP
        Returns True if successful
        """
        symbol = order_params["symbol"]
        side = order_params["side"]
        qty = order_params["qty"]
        sl_price = order_params["sl_price"]
        tp_price = order_params["tp_price"]
        
        try:
            logger.info(f"Executing {side} order for {symbol}: qty={qty}, SL={sl_price}, TP={tp_price}")
            
            # Step 1: Place market order
            order_response = self.session.place_order(
                category="linear",
                symbol=symbol,
                side=side,
                orderType="Market",
                qty=str(qty),
                leverage=str(config.LEVERAGE),
                reduceOnly=False
            )
            
            if order_response["retCode"] != 0:
                logger.error(f"Order failed for {symbol}: {order_response['retMsg']}")
                return False
            
            order_id = order_response["result"].get("orderId")
            logger.info(f"Order placed successfully: {order_id}")
            
            # Wait a bit for order to fill
            time.sleep(1)
            
            # Step 2: Set Stop Loss and Take Profit
            # Bybit v5 uses set_trading_stop endpoint
            sl_tp_response = self.session.set_trading_stop(
                category="linear",
                symbol=symbol,
                stopLoss=str(sl_price),
                takeProfit=str(tp_price),
                positionIdx=0  # 0 for one-way mode
            )
            
            if sl_tp_response["retCode"] != 0:
                logger.warning(f"Failed to set SL/TP for {symbol}: {sl_tp_response['retMsg']}")
                # Order was placed but SL/TP failed - still consider it successful
                # We can retry setting SL/TP later
            else:
                logger.info(f"SL/TP set successfully for {symbol}")
            
            # Step 3: Get position details and update position manager
            time.sleep(0.5)
            position_response = self.session.get_positions(
                category="linear",
                symbol=symbol,
                settleCoin="USDT"
            )
            
            if position_response["retCode"] == 0:
                positions = position_response["result"].get("list", [])
                for pos in positions:
                    if pos.get("symbol") == symbol and float(pos.get("size", 0)) > 0:
                        position_data = {
                            "symbol": symbol,
                            "side": pos.get("side"),
                            "size": float(pos.get("size", 0)),
                            "entry_price": float(pos.get("avgPrice", 0)),
                            "mark_price": float(pos.get("markPrice", 0)),
                            "unrealised_pnl": float(pos.get("unrealisedPnl", 0)),
                            "leverage": pos.get("leverage"),
                            "sl_price": float(pos.get("stopLoss", 0)) if pos.get("stopLoss") else sl_price,
                            "tp_price": float(pos.get("takeProfit", 0)) if pos.get("takeProfit") else tp_price,
                            "order_id": order_id
                        }
                        self.position_manager.add_position(symbol, position_data)
                        logger.info(f"Position tracked: {symbol} - {position_data}")
                        break
            
            return True
            
        except Exception as e:
            logger.error(f"Exception executing order for {symbol}: {e}", exc_info=True)
            return False
    
    def close_position(self, symbol: str, reason: str = "Manual") -> bool:
        """
        Close an existing position
        Returns True if successful
        """
        try:
            position = self.position_manager.get_position(symbol)
            if not position:
                logger.warning(f"No position found for {symbol}")
                return False
            
            side = position["side"]
            # Reverse the side to close
            close_side = "Sell" if side == "Buy" else "Buy"
            qty = position["size"]
            
            logger.info(f"Closing position for {symbol}: {reason}")
            
            response = self.session.place_order(
                category="linear",
                symbol=symbol,
                side=close_side,
                orderType="Market",
                qty=str(qty),
                reduceOnly=True
            )
            
            if response["retCode"] != 0:
                logger.error(f"Failed to close position for {symbol}: {response['retMsg']}")
                return False
            
            logger.info(f"Position closed successfully for {symbol}")
            self.position_manager.remove_position(symbol)
            return True
            
        except Exception as e:
            logger.error(f"Exception closing position for {symbol}: {e}", exc_info=True)
            return False
    
    def close_all_positions(self):
        """Close all active positions"""
        symbols = list(self.position_manager.active_positions.keys())
        logger.info(f"Closing all positions: {symbols}")
        
        for symbol in symbols:
            self.close_position(symbol, reason="Shutdown")
