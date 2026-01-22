"""
Main entry point for Bybit Trading Bot
EMA200 Crossover Strategy
"""
import signal
import sys
import time
import logging
from pybit.unified_trading import HTTP
from config import config
from kline_manager import KlineDataManager
from websocket_monitor import WebSocketMonitor
from position_manager import AccountManager, PositionManager
from signal_generator import SignalGenerator
from trading_engine import TradingEngine
from position_tracker import PositionTracker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)


class TradingBot:
    """Main bot orchestrator"""
    
    def __init__(self):
        self.running = False
        self.session = HTTP(
            testnet=config.TESTNET,
            api_key=config.API_KEY,
            api_secret=config.API_SECRET
        )
        
        # Initialize components
        self.kline_manager = KlineDataManager()
        self.account_manager = AccountManager(self.session)
        self.position_manager = PositionManager(self.account_manager, self.session)
        self.signal_generator = SignalGenerator(self.kline_manager, self.position_manager)
        self.trading_engine = TradingEngine(self.position_manager)
        self.ws_monitor = None
        self.position_tracker = None
    
    def on_candle_close(self, symbol: str, kline_data: dict):
        """Callback when a candle closes"""
        try:
            logger.info(f"Candle closed for {symbol}")
            
            # Check for crossover signal
            signal = self.signal_generator.check_crossover(symbol)
            
            if signal:
                logger.info(f"Trading signal detected for {symbol}: {signal['signal_type']}")
                
                # Execute order
                success = self.trading_engine.execute_order(signal)
                if success:
                    logger.info(f"Order executed successfully for {symbol}")
                else:
                    logger.error(f"Failed to execute order for {symbol}")
            else:
                logger.debug(f"No signal for {symbol}")
                
        except Exception as e:
            logger.error(f"Exception in candle close handler for {symbol}: {e}", exc_info=True)
    
    def on_position_closed(self, symbol: str, position_data: dict):
        """Callback when a position is closed"""
        try:
            logger.info(f"Position closed for {symbol}: {position_data}")
            # Additional cleanup or logging can be added here
        except Exception as e:
            logger.error(f"Exception in position close handler: {e}", exc_info=True)
    
    def initialize(self):
        """Initialize all components"""
        logger.info("Initializing bot components...")
        
        # Step 1: Fetch historical klines for all symbols
        logger.info("Fetching historical klines...")
        for symbol in config.SYMBOLS:
            success = self.kline_manager.fetch_historical(symbol, limit=1000)
            if success:
                logger.info(f"✓ {symbol} historical data loaded")
            else:
                logger.warning(f"✗ Failed to load {symbol} historical data")
            time.sleep(0.1)  # Rate limiting
        
        # Step 2: Sync existing positions
        logger.info("Syncing existing positions...")
        self.position_manager.sync_positions()
        logger.info(f"Active positions: {len(self.position_manager.active_positions)}")
        
        # Step 3: Get account balance
        balance = self.account_manager.get_balance()
        logger.info(f"Account balance: {balance:.2f} USDT")
        
        # Step 4: Initialize WebSocket monitors
        logger.info("Initializing WebSocket connections...")
        self.ws_monitor = WebSocketMonitor(
            self.kline_manager,
            on_candle_close=self.on_candle_close
        )
        
        self.position_tracker = PositionTracker(
            self.position_manager,
            on_position_closed=self.on_position_closed
        )
        
        logger.info("Initialization complete!")
    
    def start(self):
        """Start the bot"""
        if self.running:
            logger.warning("Bot is already running")
            return
        
        self.running = True
        logger.info("Starting trading bot...")
        
        # Start WebSocket connections
        self.ws_monitor.start()
        self.position_tracker.start()
        
        # Wait a bit for connections to establish
        time.sleep(3)
        
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Main loop - keep running until interrupted
        try:
            while self.running:
                # Periodic tasks
                time.sleep(60)  # Check every minute
                
                # Sync positions periodically
                self.position_manager.sync_positions()
                
                # Log status
                if self.position_manager.active_positions:
                    logger.info(f"Active positions: {len(self.position_manager.active_positions)}")
                    for symbol, pos in self.position_manager.active_positions.items():
                        logger.info(f"  {symbol}: {pos['side']} {pos['size']} @ {pos['entry_price']:.2f} "
                                  f"(PnL: {pos['unrealised_pnl']:+.2f})")
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        if not self.running:
            return
        
        logger.info("Stopping bot...")
        self.running = False
        
        # Stop WebSocket connections
        if self.ws_monitor:
            self.ws_monitor.stop()
        if self.position_tracker:
            self.position_tracker.stop()
        
        # Close all positions (optional - comment out if you want to keep positions open)
        # logger.info("Closing all positions...")
        # self.trading_engine.close_all_positions()
        
        logger.info("Bot stopped")


def main():
    """Main function to start the bot"""
    try:
        # Validate configuration
        config.validate()
        logger.info("=" * 60)
        logger.info("Bybit Trading Bot - EMA200 Crossover Strategy")
        logger.info("=" * 60)
        logger.info(f"Testnet mode: {config.TESTNET}")
        logger.info(f"Monitoring {len(config.SYMBOLS)} symbols")
        logger.info(f"EMA Period: {config.EMA_PERIOD}")
        logger.info(f"Risk per trade: {config.RISK_PER_TRADE}%")
        logger.info(f"Leverage: {config.LEVERAGE}x")
        logger.info(f"Max positions: {config.MAX_POSITIONS}")
        logger.info(f"Stop Loss: {config.STOP_LOSS_PCT}%")
        logger.info(f"Take Profit: {config.TAKE_PROFIT_PCT}%")
        logger.info("=" * 60)
        
        # Create and start bot
        bot = TradingBot()
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Received interrupt signal")
            bot.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize and start
        bot.initialize()
        bot.start()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
