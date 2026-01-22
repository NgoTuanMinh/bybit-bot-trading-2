# Hướng dẫn Cài đặt Bot trên Server Linux

Hướng dẫn chi tiết để cài đặt và chạy bot trading trên server Linux (Ubuntu/Debian/CentOS).

## Bước 1: Cài đặt Python 3

### Ubuntu/Debian:
```bash
# Cập nhật package list
sudo apt update

# Cài đặt Python 3 và pip
sudo apt install -y python3 python3-pip python3-venv

# Kiểm tra version
python3 --version
# Nên là Python 3.7 trở lên
```

### CentOS/RHEL:
```bash
# Cài đặt Python 3
sudo yum install -y python3 python3-pip

# Hoặc với dnf (CentOS 8+)
sudo dnf install -y python3 python3-pip

# Kiểm tra version
python3 --version
```

## Bước 2: Upload Code lên Server

### Cách 1: Sử dụng Git (Khuyến nghị)
```bash
# Cài đặt git nếu chưa có
sudo apt install -y git  # Ubuntu/Debian
# hoặc
sudo yum install -y git  # CentOS

# Clone project (nếu có git repo)
git clone <your-repo-url> BybitBotTrading2
cd BybitBotTrading2
```

### Cách 2: Sử dụng SCP/SFTP
```bash
# Từ máy local, upload toàn bộ thư mục lên server
scp -r /path/to/BybitBotTrading2 user@your-server-ip:/home/user/

# SSH vào server
ssh user@your-server-ip
cd /home/user/BybitBotTrading2
```

### Cách 3: Sử dụng rsync
```bash
rsync -avz /path/to/BybitBotTrading2 user@your-server-ip:/home/user/
```

## Bước 3: Tạo Virtual Environment (Khuyến nghị)

```bash
# Vào thư mục project
cd BybitBotTrading2

# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
source venv/bin/activate

# Bạn sẽ thấy (venv) ở đầu dòng prompt
```

## Bước 4: Cài đặt Dependencies

```bash
# Đảm bảo đang trong virtual environment
# (venv) sẽ hiển thị ở đầu dòng

# Cài đặt dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Bước 5: Tạo file .env

```bash
# Tạo file .env
nano .env
# hoặc
vi .env
```

**Copy nội dung sau vào file .env:**

```env
# Bybit API Credentials
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here

# Bybit Testnet Settings
TESTNET=true

# Trading Symbols (50 symbols)
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

**Lưu file:**
- Nano: `Ctrl+X`, sau đó `Y`, sau đó `Enter`
- Vi: `Esc`, sau đó `:wq`, sau đó `Enter`

**Thay thế:**
- `your_api_key_here` → API Key từ Bybit
- `your_api_secret_here` → API Secret từ Bybit

## Bước 6: Test chạy Bot

```bash
# Đảm bảo đang trong virtual environment
source venv/bin/activate

# Chạy bot để test
python3 main.py
```

Nếu chạy thành công, bạn sẽ thấy log. Nhấn `Ctrl+C` để dừng.

## Bước 7: Chạy Bot ở Background (Screen/Tmux)

### Cách 1: Sử dụng Screen

```bash
# Cài đặt screen (nếu chưa có)
sudo apt install -y screen  # Ubuntu/Debian
# hoặc
sudo yum install -y screen  # CentOS

# Tạo screen session mới
screen -S trading-bot

# Kích hoạt virtual environment
source venv/bin/activate

# Chạy bot
python3 main.py

# Detach khỏi screen: Nhấn Ctrl+A, sau đó D
# Reattach vào screen: screen -r trading-bot
# Xem danh sách screen: screen -ls
# Kill screen: screen -X -S trading-bot quit
```

### Cách 2: Sử dụng Tmux

```bash
# Cài đặt tmux (nếu chưa có)
sudo apt install -y tmux  # Ubuntu/Debian
# hoặc
sudo yum install -y tmux  # CentOS

# Tạo tmux session mới
tmux new -s trading-bot

# Kích hoạt virtual environment
source venv/bin/activate

# Chạy bot
python3 main.py

# Detach khỏi tmux: Nhấn Ctrl+B, sau đó D
# Reattach vào tmux: tmux attach -t trading-bot
# Xem danh sách tmux: tmux ls
# Kill tmux: tmux kill-session -t trading-bot
```

## Bước 8: Tạo Systemd Service (Tự động chạy khi khởi động)

### Tạo service file:

```bash
sudo nano /etc/systemd/system/bybit-trading-bot.service
```

**Copy nội dung sau (điều chỉnh đường dẫn):**

```ini
[Unit]
Description=Bybit Trading Bot - EMA200 Crossover Strategy
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/BybitBotTrading2
Environment="PATH=/home/your-username/BybitBotTrading2/venv/bin"
ExecStart=/home/your-username/BybitBotTrading2/venv/bin/python3 /home/your-username/BybitBotTrading2/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/your-username/BybitBotTrading2/bot.log
StandardError=append:/home/your-username/BybitBotTrading2/bot_error.log

[Install]
WantedBy=multi-user.target
```

**Thay thế:**
- `your-username` → username của bạn trên server
- Điều chỉnh đường dẫn nếu project ở vị trí khác

**Lưu file và kích hoạt service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (tự động chạy khi khởi động)
sudo systemctl enable bybit-trading-bot

# Start service
sudo systemctl start bybit-trading-bot

# Kiểm tra status
sudo systemctl status bybit-trading-bot

# Xem log
sudo journalctl -u bybit-trading-bot -f

# Stop service
sudo systemctl stop bybit-trading-bot

# Restart service
sudo systemctl restart bybit-trading-bot
```

## Bước 9: Cấu hình Firewall (Nếu cần)

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 22/tcp  # SSH
# Bot không cần mở port vì chỉ kết nối ra ngoài

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## Bước 10: Monitoring và Logs

### Xem log real-time:

```bash
# Nếu dùng systemd
sudo journalctl -u bybit-trading-bot -f

# Hoặc xem file log
tail -f /home/your-username/BybitBotTrading2/bot.log
```

### Kiểm tra bot có đang chạy:

```bash
# Nếu dùng systemd
sudo systemctl status bybit-trading-bot

# Hoặc kiểm tra process
ps aux | grep main.py

# Hoặc nếu dùng screen
screen -ls

# Hoặc nếu dùng tmux
tmux ls
```

## Các lệnh hữu ích

### Quản lý Virtual Environment:
```bash
# Kích hoạt
source venv/bin/activate

# Deactivate
deactivate
```

### Cập nhật code:
```bash
# Nếu dùng git
cd /home/your-username/BybitBotTrading2
git pull

# Cài đặt dependencies mới (nếu có)
source venv/bin/activate
pip install -r requirements.txt

# Restart bot
sudo systemctl restart bybit-trading-bot
```

### Backup .env:
```bash
# Backup file .env (quan trọng!)
cp .env .env.backup
```

## Troubleshooting

### Lỗi "python3: command not found"
```bash
# Cài đặt Python 3
sudo apt install -y python3 python3-pip
```

### Lỗi "pip: command not found"
```bash
# Cài đặt pip
sudo apt install -y python3-pip
# hoặc
python3 -m ensurepip --upgrade
```

### Lỗi "Permission denied"
```bash
# Kiểm tra quyền file
chmod +x main.py
# Hoặc chạy với quyền user thích hợp
```

### Bot không chạy sau khi restart server
```bash
# Kiểm tra service có enable chưa
sudo systemctl is-enabled bybit-trading-bot

# Nếu chưa, enable lại
sudo systemctl enable bybit-trading-bot
sudo systemctl start bybit-trading-bot
```

### Kiểm tra log lỗi:
```bash
# Systemd logs
sudo journalctl -u bybit-trading-bot -n 100

# File log
tail -n 100 bot.log
cat bot_error.log
```

## Checklist Setup

- [ ] Python 3.7+ đã cài đặt
- [ ] Code đã upload lên server
- [ ] Virtual environment đã tạo và kích hoạt
- [ ] Dependencies đã cài đặt (`pip install -r requirements.txt`)
- [ ] File `.env` đã tạo và điền đầy đủ thông tin
- [ ] Bot đã test chạy thành công
- [ ] Bot đã setup chạy background (screen/tmux hoặc systemd)
- [ ] Service đã enable tự động khởi động (nếu dùng systemd)
- [ ] Đã test restart server và bot tự động chạy lại

## Lưu ý bảo mật

1. **Bảo vệ file .env:**
   ```bash
   chmod 600 .env  # Chỉ owner đọc được
   ```

2. **Không commit .env lên git:**
   - File `.gitignore` đã có `.env`
   - Luôn backup `.env` ở nơi an toàn

3. **API Keys:**
   - Chỉ dùng trên server
   - Không chia sẻ với ai
   - Rotate keys định kỳ

4. **SSH Security:**
   - Dùng SSH key thay vì password
   - Disable root login
   - Đổi port SSH mặc định

## Kết luận

Sau khi hoàn thành các bước trên, bot sẽ:
- ✅ Tự động chạy khi server khởi động (nếu dùng systemd)
- ✅ Tự động restart nếu bị crash
- ✅ Log được lưu vào file để theo dõi
- ✅ Chạy ổn định trên server

Chúc bạn trading thành công! 🚀
