# Cách Chạy Bot Độc Lập (Không Bị Tắt Khi Đóng Terminal)

## ⚠️ Vấn đề

Nếu bạn chạy bot trực tiếp:
```bash
python3 main.py
```

Và đóng terminal → **Bot sẽ bị tắt!** ❌

## ✅ Giải pháp: 3 Cách Chạy Độc Lập

### ⭐ Cách 1: Systemd Service (KHUYẾN NGHỊ - Tốt nhất)

**Ưu điểm:**
- ✅ Bot chạy hoàn toàn độc lập, **KHÔNG BỊ TẮT** khi đóng terminal
- ✅ Tự động restart nếu bot crash
- ✅ Tự động chạy khi server khởi động lại
- ✅ Quản lý dễ dàng

**Cách setup:**

1. Tạo service file:
```bash
sudo nano /etc/systemd/system/bybit-trading-bot.service
```

2. Copy nội dung (điều chỉnh đường dẫn):
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

3. Kích hoạt và chạy:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bybit-trading-bot
sudo systemctl start bybit-trading-bot
```

4. Kiểm tra:
```bash
sudo systemctl status bybit-trading-bot
```

**✅ Với systemd, bạn có thể đóng terminal bình thường, bot vẫn chạy!**

---

### Cách 2: Screen (Cần detach trước khi đóng terminal)

**⚠️ Lưu ý:** Phải **detach** trước khi đóng terminal!

```bash
# Tạo screen session
screen -S trading-bot

# Chạy bot
source venv/bin/activate
python3 main.py

# ⚠️ QUAN TRỌNG: Detach TRƯỚC KHI ĐÓNG TERMINAL
# Nhấn: Ctrl+A, sau đó D (không nhấn Ctrl+C!)

# Sau khi detach, bạn có thể đóng terminal an toàn
```

**Reattach khi cần:**
```bash
screen -r trading-bot
```

**⚠️ Cảnh báo:** Nếu đóng terminal mà chưa detach → bot sẽ bị tắt!

---

### Cách 3: Tmux (Cần detach trước khi đóng terminal)

**⚠️ Lưu ý:** Phải **detach** trước khi đóng terminal!

```bash
# Tạo tmux session
tmux new -s trading-bot

# Chạy bot
source venv/bin/activate
python3 main.py

# ⚠️ QUAN TRỌNG: Detach TRƯỚC KHI ĐÓNG TERMINAL
# Nhấn: Ctrl+B, sau đó D (không nhấn Ctrl+C!)

# Sau khi detach, bạn có thể đóng terminal an toàn
```

**Reattach khi cần:**
```bash
tmux attach -t trading-bot
```

**⚠️ Cảnh báo:** Nếu đóng terminal mà chưa detach → bot sẽ bị tắt!

---

### Cách 4: PM2 (Khuyến nghị cho Node.js developers)

**Ưu điểm:**
- ✅ Bot chạy hoàn toàn độc lập, **KHÔNG BỊ TẮT** khi đóng terminal
- ✅ Tự động restart nếu bot crash
- ✅ Quản lý dễ dàng với CLI
- ✅ Web dashboard (optional)
- ✅ Log management tốt
- ✅ Không cần sudo

**Setup:**
```bash
# Cài Node.js và PM2
sudo npm install -g pm2

# Chạy bot
pm2 start ecosystem.config.js

# Setup tự động khởi động
pm2 startup
pm2 save
```

**✅ Với PM2, bạn có thể đóng terminal bình thường, bot vẫn chạy!**

Xem hướng dẫn chi tiết: **[PM2_SETUP.md](PM2_SETUP.md)**

---

## So sánh các cách

| Cách | Độc lập | Tự động restart | Tự động khởi động | Dễ quản lý | Web Dashboard |
|------|---------|-----------------|-------------------|------------|---------------|
| **Systemd** ⭐ | ✅ Hoàn toàn | ✅ Có | ✅ Có | ✅ Rất dễ | ❌ Không |
| **PM2** ⭐ | ✅ Hoàn toàn | ✅ Có | ✅ Có (cần setup) | ✅ Rất dễ | ✅ Có |
| Screen | ⚠️ Cần detach | ❌ Không | ❌ Không | ⚠️ Trung bình | ❌ Không |
| Tmux | ⚠️ Cần detach | ❌ Không | ❌ Không | ⚠️ Trung bình | ❌ Không |

## Kết luận

**⭐ KHUYẾN NGHỊ: Dùng Systemd Service**

- Bot chạy hoàn toàn độc lập
- Không cần lo về việc đóng terminal
- Tự động restart nếu crash
- Tự động chạy khi server khởi động lại

Xem hướng dẫn chi tiết trong **[SERVER_SETUP.md](SERVER_SETUP.md)**.
