# Hướng dẫn Chạy Bot với PM2

PM2 là một process manager mạnh mẽ, dễ sử dụng hơn systemd và không cần sudo để quản lý.

## Ưu điểm của PM2

- ✅ Bot chạy hoàn toàn độc lập, **KHÔNG BỊ TẮT** khi đóng terminal
- ✅ Tự động restart nếu bot crash
- ✅ Quản lý dễ dàng với CLI
- ✅ Web dashboard (optional)
- ✅ Log management tốt
- ✅ Không cần sudo (chạy với user thường)
- ✅ Monitor CPU, Memory real-time

## Cài đặt PM2

### Bước 1: Cài đặt Node.js

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

**CentOS/RHEL:**
```bash
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
```

**Kiểm tra:**
```bash
node --version
npm --version
```

### Bước 2: Cài đặt PM2

```bash
sudo npm install -g pm2
```

**Kiểm tra:**
```bash
pm2 --version
```

## Setup Bot với PM2

### Cách 1: Dùng Ecosystem File (KHUYẾN NGHỊ)

1. Tạo file `ecosystem.config.js` trong thư mục project:

```bash
nano ecosystem.config.js
```

2. Copy nội dung sau (điều chỉnh đường dẫn):

```javascript
module.exports = {
  apps: [{
    name: 'bybit-trading-bot',
    script: 'main.py',
    interpreter: 'venv/bin/python3',
    cwd: '/home/your-username/BybitBotTrading2',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    error_file: './bot_error.log',
    out_file: './bot.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true
  }]
};
```

**Thay thế:**
- `your-username` → username của bạn
- Điều chỉnh đường dẫn `cwd` nếu project ở vị trí khác

3. Chạy bot:

```bash
pm2 start ecosystem.config.js
```

### Cách 2: Chạy trực tiếp

```bash
# Vào thư mục project
cd /home/your-username/BybitBotTrading2

# Chạy với PM2
pm2 start venv/bin/python3 --name bybit-trading-bot -- main.py
```

### Cách 3: Chạy với working directory

```bash
pm2 start main.py \
  --name bybit-trading-bot \
  --interpreter venv/bin/python3 \
  --cwd /home/your-username/BybitBotTrading2
```

## Quản lý Bot với PM2

### Các lệnh cơ bản

```bash
# Xem danh sách tất cả processes
pm2 list

# Xem log real-time
pm2 logs bybit-trading-bot

# Xem log chỉ output (100 dòng cuối)
pm2 logs bybit-trading-bot --lines 100

# Xem log chỉ errors
pm2 logs bybit-trading-bot --err

# Restart bot
pm2 restart bybit-trading-bot

# Stop bot
pm2 stop bybit-trading-bot

# Start bot (nếu đã stop)
pm2 start bybit-trading-bot

# Delete bot (xóa khỏi PM2)
pm2 delete bybit-trading-bot

# Xem thông tin chi tiết
pm2 show bybit-trading-bot

# Monitor (CPU, Memory real-time)
pm2 monit

# Flush logs (xóa logs cũ)
pm2 flush
```

### Xem thống kê

```bash
# Xem thống kê chi tiết
pm2 status

# Xem thông tin process
pm2 info bybit-trading-bot

# Xem process tree
pm2 prettylist
```

## Setup Tự động Chạy Khi Server Khởi Động

1. Tạo startup script:

```bash
pm2 startup
```

Lệnh này sẽ hiển thị một lệnh cần chạy, ví dụ:
```bash
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u your-username --hp /home/your-username
```

2. Copy và chạy lệnh đó (thay `your-username` bằng username của bạn)

3. Save current PM2 processes:

```bash
pm2 save
```

Bây giờ bot sẽ tự động chạy khi server khởi động lại!

## Web Dashboard (Optional)

PM2 có thể cung cấp web dashboard để monitor:

```bash
# Cài đặt PM2 web interface
pm2 install pm2-server-monit

# Hoặc dùng PM2 Plus (cloud)
pm2 link
```

Truy cập: `http://your-server-ip:9615`

## So sánh PM2 vs Systemd

| Tính năng | PM2 | Systemd |
|-----------|-----|---------|
| Độc lập khi đóng terminal | ✅ | ✅ |
| Tự động restart | ✅ | ✅ |
| Tự động khởi động | ✅ (cần setup) | ✅ |
| Quản lý dễ dàng | ✅ Rất dễ | ⚠️ Trung bình |
| Web dashboard | ✅ Có | ❌ Không |
| Cần sudo | ❌ Không | ✅ Có |
| Cần Node.js | ✅ Có | ❌ Không |
| Log management | ✅ Tốt | ⚠️ Trung bình |
| Monitor real-time | ✅ Có | ❌ Không |

## Troubleshooting

### Lỗi: "pm2: command not found"
```bash
# Cài lại PM2
sudo npm install -g pm2

# Hoặc thêm vào PATH
export PATH=$PATH:/usr/lib/node_modules/pm2/bin
```

### Lỗi: "Cannot find interpreter"
```bash
# Kiểm tra đường dẫn Python
which python3
# Đảm bảo ecosystem.config.js có đường dẫn đúng
```

### Bot không tự động restart
```bash
# Kiểm tra ecosystem.config.js có autorestart: true
# Hoặc restart thủ công
pm2 restart bybit-trading-bot
```

### Xem log lỗi chi tiết
```bash
pm2 logs bybit-trading-bot --err --lines 50
```

## Kết luận

PM2 là lựa chọn tốt nếu:
- ✅ Bạn quen với Node.js ecosystem
- ✅ Bạn muốn quản lý dễ dàng hơn systemd
- ✅ Bạn muốn web dashboard
- ✅ Bạn không muốn dùng sudo

**Sau khi setup PM2, bạn có thể đóng terminal bình thường, bot vẫn chạy!** ✅
