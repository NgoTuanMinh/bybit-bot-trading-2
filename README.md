# Bybit Trading Bot - EMA200 Crossover Strategy

Bot trading futures trên Bybit sử dụng chiến lược EMA200 Crossover. Bot theo dõi 50 symbols trên khung thời gian M15 và tự động vào lệnh khi phát hiện tín hiệu crossover.

## Tính năng

- ✅ Theo dõi real-time 50 symbols trên khung M15
- ✅ Tính toán EMA200 tự động
- ✅ Phát hiện tín hiệu crossover (Bullish/Bearish)
- ✅ Quản lý rủi ro tự động (5% mỗi lệnh, đòn bẩy 10x)
- ✅ Giới hạn tối đa 5 positions cùng lúc
- ✅ Tự động set Stop Loss (5%) và Take Profit (3%)
- ✅ Theo dõi positions qua WebSocket
- ✅ Hỗ trợ Bybit Testnet để test

## Cấu trúc Project

```
BybitBotTrading2/
├── config.py              # Configuration và load env variables
├── kline_manager.py       # Quản lý dữ liệu nến và tính EMA
├── websocket_monitor.py   # WebSocket monitor cho kline data
├── position_manager.py    # Quản lý positions và account
├── signal_generator.py    # Phát hiện tín hiệu crossover
├── trading_engine.py      # Thực thi lệnh giao dịch
├── position_tracker.py    # Theo dõi positions qua WebSocket
├── main.py                # Entry point chính
├── requirements.txt       # Python dependencies
├── setup_server.sh        # Script tự động setup trên server
├── .env                   # Environment variables (tạo thủ công)
├── README.md             # File này
├── QUICKSTART.md         # Hướng dẫn nhanh
├── SETUP_GUIDE.md        # Hướng dẫn setup chi tiết
└── SERVER_SETUP.md       # Hướng dẫn setup trên server
```

## Hướng dẫn Setup

> **📚 Tài liệu hướng dẫn:**
> - **[QUICKSTART.md](QUICKSTART.md)** - Hướng dẫn nhanh để bắt đầu
> - **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Hướng dẫn setup chi tiết (local)
> - **[SERVER_SETUP.md](SERVER_SETUP.md)** - Hướng dẫn setup trên server Linux ⭐

### Setup trên Server (Khuyến nghị)

Nếu bạn muốn chạy bot trên server Linux, xem hướng dẫn chi tiết trong **[SERVER_SETUP.md](SERVER_SETUP.md)**.

**Quick setup trên server:**
```bash
# Upload code lên server, sau đó chạy:
bash setup_server.sh
```

### Setup Local (Development)

### Bước 1: Tạo tài khoản Bybit Testnet

1. Truy cập: https://testnet.bybit.com/
2. Đăng ký/Đăng nhập tài khoản
3. Vào **API Management** → **Create New Key**
4. Tạo API Key và API Secret
5. Lưu lại API Key và API Secret

### Bước 2: Cài đặt Python Dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Tạo file .env

Tạo file `.env` trong thư mục project với nội dung:

```env
# Bybit API Credentials
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here

# Bybit Testnet Settings
TESTNET=true

# Trading Symbols (comma-separated)
BYBIT_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,AVAXUSDT,DOGEUSDT,DOTUSDT,TRXUSDT,MATICUSDT,LINKUSDT,TONUSDT,ICPUSDT,SHIBUSDT,LTCUSDT,BCHUSDT,UNIUSDT,ATOMUSDT,XLMUSDT,FILUSDT,ETCUSDT,APTUSDT,NEARUSDT,OPUSDT,ARBUSDT,VETUSDT,AAVEUSDT,ALGOUSDT,MANAUSDT,EGLDUSDT,SANDUSDT,AXSUSDT,THETAUSDT,XTZUSDT,FTMUSDT,EOSUSDT,MKRUSDT,CRVUSDT,KAVAUSDT,RUNEUSDT,GALAUSDT,PEOPLEUSDT,WAVESUSDT,ZILUSDT,IOTAUSDT,ENJUSDT,ONEUSDT,CHZUSDT,BATUSDT

# Trading Configuration
TIMEFRAME=M15
EMA_PERIOD=200
RISK_PER_TRADE=5
LEVERAGE=10
MAX_POSITIONS=5
STOP_LOSS_PCT=5
TAKE_PROFIT_PCT=3
```

**Lưu ý:**
- Thay `your_api_key_here` và `your_api_secret_here` bằng API Key và Secret từ Bybit Testnet
- Để chạy trên mainnet, đặt `TESTNET=false` và dùng API credentials từ mainnet

### Bước 4: Chạy Bot

```bash
python main.py
```

Bot sẽ:
1. Load configuration từ `.env`
2. Fetch historical klines cho 50 symbols
3. Tính toán EMA200
4. Kết nối WebSocket để theo dõi real-time
5. Tự động phát hiện tín hiệu và vào lệnh

## Chiến lược Trading

### Tín hiệu LONG (Buy)
- Giá cắt từ trên xuống dưới EMA200
- Previous candle: Close > EMA200
- Current candle: Close < EMA200
- → Vào lệnh LONG

### Tín hiệu SHORT (Sell)
- Giá cắt từ dưới lên trên EMA200
- Previous candle: Close < EMA200
- Current candle: Close > EMA200
- → Vào lệnh SHORT

### Risk Management
- **Risk per trade**: 5% tài khoản
- **Leverage**: 10x
- **Stop Loss**: 5% từ entry price
- **Take Profit**: 3% từ entry price
- **Max positions**: 5 positions cùng lúc

## Cấu hình

Các thông số có thể điều chỉnh trong file `.env`:

| Thông số | Mô tả | Mặc định |
|----------|-------|----------|
| `TIMEFRAME` | Khung thời gian | M15 |
| `EMA_PERIOD` | Chu kỳ EMA | 200 |
| `RISK_PER_TRADE` | Rủi ro mỗi lệnh (%) | 5 |
| `LEVERAGE` | Đòn bẩy | 10 |
| `MAX_POSITIONS` | Số positions tối đa | 5 |
| `STOP_LOSS_PCT` | Stop Loss (%) | 5 |
| `TAKE_PROFIT_PCT` | Take Profit (%) | 3 |
| `TESTNET` | Chế độ testnet | true |

## Logging

Bot sẽ ghi log vào:
- Console (stdout)
- File `bot.log` trong thư mục project

## Lưu ý quan trọng

⚠️ **Cảnh báo rủi ro:**
- Trading có rủi ro, có thể mất tiền
- Luôn test trên Testnet trước khi dùng mainnet
- Không trade với số tiền bạn không thể mất
- Bot này chỉ là công cụ hỗ trợ, không đảm bảo lợi nhuận

## Troubleshooting

### Lỗi "BYBIT_API_KEY and BYBIT_API_SECRET must be set"
- Kiểm tra file `.env` đã được tạo chưa
- Đảm bảo API_KEY và API_SECRET đã được điền

### Lỗi kết nối WebSocket
- Kiểm tra kết nối internet
- Kiểm tra API credentials có đúng không
- Thử restart bot

### Không có tín hiệu
- Đảm bảo đã có đủ 1000 nến historical để tính EMA200
- Kiểm tra log để xem có lỗi gì không
- Crossover không phải lúc nào cũng xảy ra, cần kiên nhẫn

## License

MIT License - Sử dụng tự do nhưng tự chịu trách nhiệm về rủi ro.
