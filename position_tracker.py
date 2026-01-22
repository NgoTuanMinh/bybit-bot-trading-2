"""
Position Tracker
Monitors position updates via private WebSocket
"""
import json
import logging
import threading
import time
import websocket
import hmac
import hashlib
from typing import Callable, Optional
from position_manager import PositionManager
from config import config

logger = logging.getLogger(__name__)


class PositionTracker:
    """Tracks positions via private WebSocket"""
    
    def __init__(self, position_manager: PositionManager, on_position_closed: Optional[Callable] = None):
        self.position_manager = position_manager
        self.on_position_closed = on_position_closed
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_running = False
        self.reconnect_interval = 5
        self.thread: Optional[threading.Thread] = None
    
    def _generate_signature(self, expires: int) -> str:
        """Generate signature for WebSocket authentication"""
        signature = hmac.new(
            config.API_SECRET.encode("utf-8"),
            f"GET/realtime{expires}".encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            # Handle authentication response
            if "op" in data and data["op"] == "auth":
                if data.get("success"):
                    logger.info("WebSocket authenticated successfully")
                    # Subscribe to position and execution channels
                    subscribe_msg = {
                        "op": "subscribe",
                        "args": ["position", "execution"]
                    }
                    ws.send(json.dumps(subscribe_msg))
                    logger.info("Subscribed to position and execution channels")
                else:
                    logger.error(f"WebSocket authentication failed: {data.get('ret_msg')}")
                return
            
            # Handle position updates
            if "topic" in data:
                topic = data["topic"]
                
                if topic == "position":
                    self._handle_position_update(data.get("data", []))
                elif topic == "execution":
                    self._handle_execution_update(data.get("data", []))
            
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}", exc_info=True)
    
    def _handle_position_update(self, positions: list):
        """Handle position update from WebSocket"""
        try:
            for pos_data in positions:
                symbol = pos_data.get("symbol")
                size = float(pos_data.get("size", 0))
                
                if size == 0:
                    # Position closed
                    if symbol in self.position_manager.active_positions:
                        logger.info(f"Position closed for {symbol} (size = 0)")
                        position = self.position_manager.get_position(symbol)
                        
                        # Calculate PnL
                        if position:
                            pnl = float(pos_data.get("unrealisedPnl", 0))
                            self.position_manager.account_manager.update_balance(pnl)
                        
                        # Remove from tracking
                        self.position_manager.remove_position(symbol)
                        
                        # Trigger callback
                        if self.on_position_closed:
                            self.on_position_closed(symbol, position)
                else:
                    # Position updated
                    position_data = {
                        "symbol": symbol,
                        "side": pos_data.get("side"),
                        "size": size,
                        "entry_price": float(pos_data.get("avgPrice", 0)),
                        "mark_price": float(pos_data.get("markPrice", 0)),
                        "unrealised_pnl": float(pos_data.get("unrealisedPnl", 0)),
                        "leverage": pos_data.get("leverage"),
                        "sl_price": float(pos_data.get("stopLoss", 0)) if pos_data.get("stopLoss") else None,
                        "tp_price": float(pos_data.get("takeProfit", 0)) if pos_data.get("takeProfit") else None
                    }
                    
                    # Update or add position
                    self.position_manager.add_position(symbol, position_data)
                    logger.debug(f"Position updated: {symbol} - PnL: {position_data['unrealised_pnl']:.2f}")
                    
        except Exception as e:
            logger.error(f"Exception handling position update: {e}", exc_info=True)
    
    def _handle_execution_update(self, executions: list):
        """Handle execution update (order fills, closes)"""
        try:
            for exec_data in executions:
                symbol = exec_data.get("symbol")
                exec_type = exec_data.get("execType")
                side = exec_data.get("side")
                qty = float(exec_data.get("execQty", 0))
                price = float(exec_data.get("execPrice", 0))
                
                if exec_type == "Trade":
                    logger.info(f"Execution: {symbol} {side} {qty} @ {price}")
                
                # Check if this is a close (reduceOnly)
                if exec_data.get("reduceOnly"):
                    logger.info(f"Position reduced for {symbol}: {qty} @ {price}")
                    
        except Exception as e:
            logger.error(f"Exception handling execution update: {e}", exc_info=True)
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        logger.warning("Private WebSocket connection closed")
        self.is_running = False
        
        # Attempt to reconnect
        if self.is_running:
            logger.info(f"Attempting to reconnect in {self.reconnect_interval} seconds...")
            time.sleep(self.reconnect_interval)
            self.start()
    
    def _on_open(self, ws):
        """Handle WebSocket open - authenticate"""
        logger.info("Private WebSocket connection opened")
        
        # Authenticate
        expires = int((time.time() + 10000) * 1000)  # 10 seconds from now
        signature = self._generate_signature(expires)
        
        auth_msg = {
            "op": "auth",
            "args": [config.API_KEY, expires, signature]
        }
        ws.send(json.dumps(auth_msg))
        logger.info("Sent authentication request")
    
    def start(self):
        """Start WebSocket connection"""
        if self.is_running:
            logger.warning("Position tracker is already running")
            return
        
        self.is_running = True
        
        def run_websocket():
            while self.is_running:
                try:
                    logger.info(f"Connecting to private WebSocket: {config.ws_private_url}")
                    self.ws = websocket.WebSocketApp(
                        config.ws_private_url,
                        on_message=self._on_message,
                        on_error=self._on_error,
                        on_close=self._on_close,
                        on_open=self._on_open
                    )
                    self.ws.run_forever()
                    
                    if self.is_running:
                        logger.info(f"Reconnecting in {self.reconnect_interval} seconds...")
                        time.sleep(self.reconnect_interval)
                except Exception as e:
                    logger.error(f"WebSocket exception: {e}", exc_info=True)
                    if self.is_running:
                        time.sleep(self.reconnect_interval)
        
        self.thread = threading.Thread(target=run_websocket, daemon=True)
        self.thread.start()
        logger.info("Position tracker thread started")
    
    def stop(self):
        """Stop WebSocket connection"""
        logger.info("Stopping position tracker...")
        self.is_running = False
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Position tracker stopped")
