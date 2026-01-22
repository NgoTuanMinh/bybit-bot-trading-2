# Quick Start Guide - Bot Trading Bybit

## Bước nhanh để chạy bot

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Tạo file .env
Tạo file `.env` với nội dung:

```env
BYBIT_API_KEY=your_testnet_api_key
BYBIT_API_SECRET=your_testnet_api_secret
TESTNET=true
BYBIT_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,AVAXUSDT,DOGEUSDT,DOTUSDT,TRXUSDT,MATICUSDT,LINKUSDT,TONUSDT,ICPUSDT,SHIBUSDT,LTCUSDT,BCHUSDT,UNIUSDT,ATOMUSDT,XLMUSDT,FILUSDT,ETCUSDT,APTUSDT,NEARUSDT,OPUSDT,ARBUSDT,VETUSDT,AAVEUSDT,ALGOUSDT,MANAUSDT,EGLDUSDT,SANDUSDT,AXSUSDT,THETAUSDT,XTZUSDT,FTMUSDT,EOSUSDT,MKRUSDT,CRVUSDT,KAVAUSDT,RUNEUSDT,GALAUSDT,PEOPLEUSDT,WAVESUSDT,ZILUSDT,IOTAUSDT,ENJUSDT,ONEUSDT,CHZUSDT,BATUSDT
TIMEFRAME=M15
EMA_PERIOD=200
RISK_PER_TRADE=5
LEVERAGE=10
MAX_POSITIONS=5
STOP_LOSS_PCT=5
TAKE_PROFIT_PCT=3
```

### 3. Lấy API Key từ Bybit Testnet
- Vào https://testnet.bybit.com/
- API Management → Create New Key
- Copy API Key và Secret vào file .env

### 4. Chạy bot
```bash
python main.py
```

## Các file quan trọng

- `.env` - Cấu hình (API keys, settings)
- `main.py` - Chạy bot
- `bot.log` - Log file (tự động tạo)
- `SETUP_GUIDE.md` - Hướng dẫn chi tiết
- `README.md` - Tài liệu đầy đủ

## Lưu ý

- ⚠️ Luôn test trên Testnet trước
- ⚠️ Trading có rủi ro
- ⚠️ Bot cần thời gian để fetch historical data (vài phút)
- ⚠️ Tín hiệu không phải lúc nào cũng có, cần kiên nhẫn

## Xem thêm

- `SETUP_GUIDE.md` - Hướng dẫn setup chi tiết
- `README.md` - Tài liệu đầy đủ về bot
