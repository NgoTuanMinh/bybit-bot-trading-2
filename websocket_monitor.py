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

    def __init__(
        self,
        kline_manager: KlineDataManager,
        on_candle_close: Optional[Callable] = None,
        symbols: Optional[list] = None,
    ):
        self.kline_manager = kline_manager
        self.on_candle_close = on_candle_close
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_running = False
        self.reconnect_interval = 5
        self.thread: Optional[threading.Thread] = None
        # FIX_02: Exponential backoff
        self._reconnect_attempts = 0
        self._max_reconnect_delay = 60
        self.connected = False

        # Bybit topic: kline.{interval}.{symbol} — interval 1,3,5,15,30,...,D,W,M (no "15m")
        # https://bybit-exchange.github.io/docs/v5/websocket/public/kline
        interval = getattr(config, "kline_interval", None) or "15"
        syms = symbols if symbols is not None else config.SYMBOLS
        self.topics = [f"kline.{interval}.{s}" for s in syms]
        self._kline_prefix = f"kline.{interval}."
        logger.info(f"WebSocket kline topics: kline.{interval}.{{symbol}} ({len(self.topics)} topics)")
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages. FIX_03: debug log, robust processing."""
        try:
            data = json.loads(message)

            # FIX_03: Optional debug logging of raw kline messages
            if getattr(config, "DEBUG_WS_KLINE", False) and "topic" in data and "kline" in data.get("topic", ""):
                topic = data.get("topic", "")
                arr = data.get("data", [])
                last = arr[-1] if arr else {}
                logger.debug(f"WS kline: topic={topic} confirm={last.get('confirm')} data_len={len(arr)}")

            if "topic" in data:
                topic = data["topic"]
                if topic.startswith(getattr(self, "_kline_prefix", "kline.15.")):
                    symbol = topic.split(".")[-1]
                    kline_arr = data.get("data") or []
                    if not isinstance(kline_arr, list):
                        kline_arr = [kline_arr] if kline_arr else []
                    if kline_arr:
                        latest = kline_arr[-1] if isinstance(kline_arr[-1], dict) else {}
                        is_confirmed = latest.get("confirm", False)
                        self.kline_manager.add_new_kline(symbol, latest)
                        if is_confirmed and self.on_candle_close:
                            self.on_candle_close(symbol, latest)
                return

            if data.get("op") == "pong":
                logger.debug("WS pong received")
                return
            if "retMsg" in data:
                logger.info(f"WebSocket response: {data.get('retMsg')}")
            if "success" in data and not data.get("success") and "ret_msg" in data:
                logger.warning(f"WebSocket error: {data.get('ret_msg')}")

        except json.JSONDecodeError as e:
            logger.warning(f"WS message JSON error: {e}")
        except Exception as e:
            logger.warning(f"Error processing WebSocket message: {e}")
    
    def _on_error(self, ws, error):
        """FIX_02: Handle WebSocket errors, update connection state."""
        self.connected = False
        logger.warning(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """FIX_02: Handle close gracefully; do not set is_running=False (reconnect loop owns lifecycle)."""
        self.connected = False
        logger.warning(f"WebSocket connection closed (code={close_status_code}, msg={close_msg})")

    def _on_open(self, ws):
        """FIX_02: Set connected, reset backoff, log status. Subscribe in batches (max 10 per request)."""
        self.connected = True
        self._reconnect_attempts = 0
        logger.info("WebSocket connection opened; connection status: connected")

        # Bybit v5: {"op":"subscribe","args":["topic1",...]}; max 10 per subscribe
        batch_size = 10
        for i in range(0, len(self.topics), batch_size):
            batch = self.topics[i : i + batch_size]
            msg = {"op": "subscribe", "args": batch}
            try:
                ws.send(json.dumps(msg))
                logger.info(f"Subscribed to {len(batch)} kline topics (batch {i // batch_size + 1})")
            except Exception as e:
                logger.warning(f"Subscribe batch failed: {e}")
            time.sleep(0.15)
    
    def start(self):
        """Start WebSocket connection. FIX_02: ping/pong, exponential backoff, connection state."""
        if self.is_running:
            logger.warning("WebSocket monitor is already running")
            return
        self.is_running = True

        def run_websocket():
            while self.is_running:
                # FIX_02: Exponential backoff when reconnecting (skip delay on first connect)
                delay = min(
                    self.reconnect_interval * (2 ** self._reconnect_attempts),
                    self._max_reconnect_delay
                )
                if self._reconnect_attempts > 0:
                    logger.info(f"Reconnecting in {delay:.0f}s (attempt {self._reconnect_attempts})...")
                    time.sleep(delay)

                try:
                    logger.info(f"Connecting to WebSocket: {config.ws_public_url}")
                    self.ws = websocket.WebSocketApp(
                        config.ws_public_url,
                        on_message=self._on_message,
                        on_error=self._on_error,
                        on_close=self._on_close,
                        on_open=self._on_open,
                    )
                    # FIX_02: Ping/pong heartbeat (30s interval, 10s timeout)
                    self.ws.run_forever(ping_interval=30, ping_timeout=10)
                except Exception as e:
                    logger.warning(f"WebSocket exception: {e}")

                if self.is_running:
                    self._reconnect_attempts += 1
                    continue
                break

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
