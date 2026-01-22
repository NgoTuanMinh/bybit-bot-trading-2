# Các Bước Setup Nhanh trên Server

## Checklist nhanh cho server trống

### 1. Cài đặt Python (1 lệnh)
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install -y python3 python3-pip git
```

### 2. Upload code lên server
```bash
# Cách 1: Dùng SCP (từ máy local)
scp -r BybitBotTrading2 user@server-ip:/home/user/

# Cách 2: Dùng Git (nếu có repo)
git clone <repo-url> BybitBotTrading2
cd BybitBotTrading2
```

### 3. Chạy script tự động setup
```bash
cd BybitBotTrading2
bash setup_server.sh
```

Script sẽ tự động:
- ✓ Cài đặt Python dependencies
- ✓ Tạo virtual environment
- ✓ Cài đặt Python packages
- ✓ Tạo file .env template
- ✓ Cài đặt screen/tmux
- ✓ Tạo systemd service (optional)

### 4. Chỉnh sửa file .env
```bash
nano .env
# Điền API_KEY và API_SECRET từ Bybit Testnet
```

### 5. Test chạy bot
```bash
source venv/bin/activate
python3 main.py
# Nhấn Ctrl+C để dừng
```

### 6. Chạy bot ở background

**Option A: Dùng Screen**
```bash
screen -S trading-bot
source venv/bin/activate
python3 main.py
# Nhấn Ctrl+A, sau đó D để detach
```

**Option B: Dùng Systemd (nếu đã tạo service)**
```bash
sudo systemctl start bybit-trading-bot
sudo systemctl status bybit-trading-bot
```

## Các lệnh quản lý thường dùng

### Xem log
```bash
# Nếu dùng systemd
sudo journalctl -u bybit-trading-bot -f

# Hoặc xem file log
tail -f bot.log
```

### Kiểm tra bot có chạy không
```bash
# Systemd
sudo systemctl status bybit-trading-bot

# Hoặc
ps aux | grep main.py
```

### Restart bot
```bash
# Systemd
sudo systemctl restart bybit-trading-bot

# Hoặc nếu dùng screen
screen -r trading-bot
# Nhấn Ctrl+C để dừng, sau đó chạy lại
```

### Stop bot
```bash
# Systemd
sudo systemctl stop bybit-trading-bot

# Hoặc
pkill -f main.py
```

## Xem thêm

- **[SERVER_SETUP.md](SERVER_SETUP.md)** - Hướng dẫn chi tiết đầy đủ
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Hướng dẫn setup local
- **[README.md](README.md)** - Tài liệu tổng quan
