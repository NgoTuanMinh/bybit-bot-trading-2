# Troubleshooting Guide

## Lỗi WebSocket Position Tracker

### Lỗi: "Connection to remote host was lost"

**Nguyên nhân:**
- Authentication thất bại
- API Key/Secret không đúng
- WebSocket connection bị timeout
- Network issues

**Giải pháp:**

#### 1. Kiểm tra API Credentials

Đảm bảo trong file `.env`:
```env
BYBIT_API_KEY=your_correct_api_key
BYBIT_API_SECRET=your_correct_api_secret
TESTNET=true  # hoặc false
```

#### 2. Kiểm tra API Key Permissions

API Key phải có:
- ✅ Quyền **Read** (để đọc positions)
- ✅ Quyền **Trade** (để trade)
- ✅ Cho phép **WebSocket Private Stream**

Kiểm tra trên Bybit:
- Testnet: https://testnet.bybit.com/app/user/api-management
- Mainnet: https://www.bybit.com/app/user/api-management

#### 3. Tạm thời Disable Position Tracker

Nếu vẫn lỗi, bạn có thể tạm thời disable position tracker. Bot vẫn hoạt động bình thường, chỉ không có real-time position updates (sẽ sync qua API định kỳ).

Thêm vào file `.env`:
```env
ENABLE_POSITION_TRACKER=false
```

Sau đó restart bot.

#### 4. Kiểm tra Network/Firewall

```bash
# Test kết nối đến Bybit WebSocket
curl -I https://stream-testnet.bybit.com

# Hoặc test với telnet
telnet stream-testnet.bybit.com 443
```

#### 5. Xem Log Chi Tiết

Thêm vào `main.py` để xem log chi tiết:
```python
logging.basicConfig(level=logging.DEBUG)
```

Hoặc xem log file:
```bash
tail -f bot.log | grep -i "websocket\|position\|auth\|error"
```

### Bot vẫn hoạt động không?

**Có!** Position Tracker là tính năng **optional**. Bot vẫn hoạt động bình thường:
- ✅ Vẫn fetch klines và tính EMA
- ✅ Vẫn phát hiện signals
- ✅ Vẫn vào lệnh
- ✅ Vẫn sync positions qua API (mỗi phút)
- ❌ Chỉ không có real-time position updates qua WebSocket

### Các lỗi khác

#### Lỗi: "BYBIT_API_KEY and BYBIT_API_SECRET must be set"
- Kiểm tra file `.env` đã tạo chưa
- Kiểm tra tên biến có đúng không (không có khoảng trắng)

#### Lỗi: "Not enough balance"
- Nạp thêm USDT vào tài khoản
- Hoặc giảm `RISK_PER_TRADE` trong `.env`

#### Lỗi: "Authentication failed"
- Kiểm tra API Key và Secret có đúng không
- Kiểm tra API Key có quyền WebSocket chưa
- Kiểm tra IP Whitelist (nếu có)

#### Bot không vào lệnh
- Crossover không phải lúc nào cũng xảy ra
- Kiểm tra log xem có tín hiệu không
- Kiểm tra `MAX_POSITIONS` - có thể đã đạt giới hạn

## Liên hệ

Nếu vẫn gặp vấn đề, kiểm tra:
1. Log file `bot.log` và `bot_error.log`
2. API credentials có đúng không
3. Network connection
4. Bybit API status
