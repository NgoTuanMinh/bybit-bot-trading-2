# Hướng dẫn Setup Bot Trading Bybit

## Bước 1: Tạo API Key trên Bybit Testnet

1. **Truy cập Bybit Testnet:**
   - Vào https://testnet.bybit.com/
   - Đăng ký hoặc đăng nhập tài khoản

2. **Tạo API Key:**
   - Vào **API Management** (hoặc **API Key Management**)
   - Click **Create New Key**
   - Đặt tên cho API Key (ví dụ: "Trading Bot")
   - Chọn quyền: **Read** và **Trade** (quan trọng!)
   - **Lưu lại API Key và API Secret ngay lập tức** (Secret chỉ hiển thị 1 lần)

3. **Kiểm tra IP Whitelist:**
   - Nếu có IP Whitelist, để trống hoặc thêm IP của bạn
   - Hoặc bỏ chọn IP Whitelist để cho phép từ mọi nơi (chỉ dùng cho testnet)

## Bước 2: Cài đặt Python và Dependencies

1. **Kiểm tra Python version:**
   ```bash
   python --version
   ```
   Cần Python 3.7 trở lên

2. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Hoặc nếu dùng pip3:
   ```bash
   pip3 install -r requirements.txt
   ```

## Bước 3: Tạo file .env

1. **Tạo file `.env` trong thư mục project:**
   ```bash
   touch .env
   ```

2. **Copy nội dung sau vào file `.env` và điền thông tin:**

```env
# Bybit API Credentials
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here

# Bybit Testnet Settings (true = testnet, false = mainnet)
TESTNET=true

# Trading Symbols (50 symbols, comma-separated)
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

3. **Thay thế:**
   - `your_api_key_here` → API Key từ Bybit Testnet
   - `your_api_secret_here` → API Secret từ Bybit Testnet

## Bước 4: Nạp tiền vào Testnet Account

1. Vào Bybit Testnet
2. Vào **Assets** → **Deposit**
3. Nạp testnet USDT (miễn phí, chỉ để test)
4. Cần ít nhất 100-200 USDT để test bot

## Bước 5: Chạy Bot

1. **Chạy bot:**
   ```bash
   python main.py
   ```

2. **Bot sẽ:**
   - Load configuration
   - Fetch historical data cho 50 symbols (có thể mất vài phút)
   - Tính toán EMA200
   - Kết nối WebSocket
   - Bắt đầu monitor và trading

3. **Theo dõi log:**
   - Log hiển thị trên console
   - Log cũng được lưu vào file `bot.log`

## Bước 6: Kiểm tra Bot hoạt động

1. **Kiểm tra log:**
   - Xem có lỗi gì không
   - Xem đã fetch historical data thành công chưa
   - Xem WebSocket đã kết nối chưa

2. **Kiểm tra trên Bybit:**
   - Vào **Positions** để xem có positions nào không
   - Vào **Order History** để xem các lệnh đã đặt

3. **Chờ tín hiệu:**
   - Bot sẽ tự động phát hiện crossover
   - Khi có tín hiệu, bot sẽ tự động vào lệnh
   - Có thể mất vài giờ hoặc vài ngày mới có tín hiệu

## Chuyển sang Mainnet (Sản xuất)

⚠️ **CẢNH BÁO: Chỉ chuyển sang mainnet khi đã test kỹ trên testnet!**

1. **Tạo API Key trên Mainnet:**
   - Vào https://www.bybit.com/
   - Tạo API Key tương tự như testnet
   - **CẨN THẬN với quyền và IP Whitelist!**

2. **Cập nhật file .env:**
   ```env
   TESTNET=false
   BYBIT_API_KEY=your_mainnet_api_key
   BYBIT_API_SECRET=your_mainnet_api_secret
   ```

3. **Kiểm tra lại:**
   - Đảm bảo đã test kỹ trên testnet
   - Bắt đầu với số tiền nhỏ
   - Monitor bot cẩn thận

## Troubleshooting

### Lỗi: "BYBIT_API_KEY and BYBIT_API_SECRET must be set"
- Kiểm tra file `.env` đã được tạo chưa
- Kiểm tra tên biến có đúng không (không có khoảng trắng)
- Kiểm tra API Key và Secret đã được điền chưa

### Lỗi: "Authentication failed"
- Kiểm tra API Key và Secret có đúng không
- Kiểm tra API Key có quyền Trade chưa
- Kiểm tra IP Whitelist (nếu có)

### Lỗi: "Not enough balance"
- Nạp thêm USDT vào tài khoản testnet
- Giảm `RISK_PER_TRADE` trong `.env`

### Bot không vào lệnh
- Crossover không phải lúc nào cũng xảy ra
- Kiểm tra log xem có tín hiệu không
- Đảm bảo đã có đủ 1000 nến historical
- Kiểm tra `MAX_POSITIONS` - có thể đã đạt giới hạn

### WebSocket disconnect
- Bot sẽ tự động reconnect
- Kiểm tra kết nối internet
- Nếu vẫn lỗi, restart bot

## Các thông số quan trọng

| Thông số | Mô tả | Khuyến nghị |
|----------|-------|-------------|
| `RISK_PER_TRADE` | % tài khoản risk mỗi lệnh | 1-5% |
| `LEVERAGE` | Đòn bẩy | 5-10x (cẩn thận!) |
| `STOP_LOSS_PCT` | Stop Loss % | 3-5% |
| `TAKE_PROFIT_PCT` | Take Profit % | 2-5% |
| `MAX_POSITIONS` | Số positions tối đa | 3-5 |

## Liên hệ và Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra log file `bot.log`
2. Kiểm tra lại các bước setup
3. Đảm bảo API credentials đúng
4. Test trên testnet trước

**Lưu ý:** Bot này chỉ là công cụ hỗ trợ. Trading có rủi ro, tự chịu trách nhiệm về quyết định của mình.
