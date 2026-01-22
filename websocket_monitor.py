"""
WebSocket Monitor for Multi-Symbol Kline Tracking
Monitors M15 klines for 50 symbols in real-time
"""
import json
import logging
import threading
import time
import websocket
from typing import Dict, Callable, Optional
from kline_manager import KlineDataManager
from config import config

logger = logging.getLogger(__name__)


class WebSocketMonitor:
    """WebSocket monitor for real-time kline data"""
    
    def __init__(self, kline_manager: KlineDataManager, on_candle_close: Optional[Callable] = None):
        self.kline_manager = kline_manager
        self.on_candle_close = on_candle_close
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_running = False
        self.reconnect_interval = 5
        self.thread: Optional[threading.Thread] = None
        
        # Build subscription topics
        self.topics = [f"kline.15.{symbol}" for symbol in config.SYMBOLS]
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            if "topic" in data:
                topic = data["topic"]
                if topic.startswith("kline.15."):
                    symbol = topic.split(".")[-1]
                    kline_data = data.get("data", [])
                    
                    if kline_data:
                        # Get the latest kline
                        latest_kline = kline_data[-1]
                        is_confirmed = latest_kline.get("confirm", False)
                        
                        # Add to kline manager
                        self.kline_manager.add_new_kline(symbol, latest_kline)
                        
                        # If candle is confirmed (closed), trigger callback
                        if is_confirmed and self.on_candle_close:
                            self.on_candle_close(symbol, latest_kline)
            
            elif "retMsg" in data:
                # Response message
                logger.info(f"WebSocket response: {data.get('retMsg')}")
            
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}", exc_info=True)
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        logger.warning("WebSocket connection closed")
        self.is_running = False
        
        # Attempt to reconnect
        if self.is_running:
            logger.info(f"Attempting to reconnect in {self.reconnect_interval} seconds...")
            time.sleep(self.reconnect_interval)
            self.start()
    
    def _on_open(self, ws):
        """Handle WebSocket open"""
        logger.info("WebSocket connection opened")
        
        # Subscribe to kline topics
        # Bybit v5 requires subscription in format: {"op": "subscribe", "args": ["topic1", "topic2", ...]}
        # We need to subscribe in batches (max 10 topics per subscription)
        batch_size = 10
        for i in range(0, len(self.topics), batch_size):
            batch = self.topics[i:i + batch_size]
            subscribe_msg = {
                "op": "subscribe",
                "args": batch
            }
            ws.send(json.dumps(subscribe_msg))
            logger.info(f"Subscribed to {len(batch)} topics (batch {i // batch_size + 1})")
            time.sleep(0.1)  # Small delay between batches
    
    def start(self):
        """Start WebSocket connection"""
        if self.is_running:
            logger.warning("WebSocket monitor is already running")
            return
        
        self.is_running = True
        
        def run_websocket():
            while self.is_running:
                try:
                    logger.info(f"Connecting to WebSocket: {config.ws_public_url}")
                    self.ws = websocket.WebSocketApp(
                        config.ws_public_url,
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
        logger.info("WebSocket monitor thread started")
    
    def stop(self):
        """Stop WebSocket connection"""
        logger.info("Stopping WebSocket monitor...")
        self.is_running = False
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("WebSocket monitor stopped")
