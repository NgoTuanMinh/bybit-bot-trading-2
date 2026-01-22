#!/bin/bash

# Script tự động setup bot trading trên server Linux
# Chạy: bash setup_server.sh

set -e  # Dừng nếu có lỗi

echo "=========================================="
echo "Bybit Trading Bot - Server Setup Script"
echo "=========================================="
echo ""

# Kiểm tra OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Không thể xác định OS. Thoát."
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Cài đặt Python và dependencies
echo "Bước 1: Cài đặt Python 3 và pip..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv git
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    if command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip git
    else
        sudo yum install -y python3 python3-pip git
    fi
else
    echo "OS không được hỗ trợ tự động. Vui lòng cài đặt Python 3 thủ công."
    exit 1
fi

# Kiểm tra Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
echo ""

# Tạo virtual environment
echo "Bước 2: Tạo virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment đã tạo"
else
    echo "✓ Virtual environment đã tồn tại"
fi
echo ""

# Kích hoạt virtual environment và cài dependencies
echo "Bước 3: Cài đặt Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies đã cài đặt"
echo ""

# Kiểm tra file .env
echo "Bước 4: Kiểm tra file .env..."
if [ ! -f ".env" ]; then
    echo "⚠ File .env chưa tồn tại!"
    echo "Vui lòng tạo file .env với nội dung từ SETUP_GUIDE.md"
    echo ""
    echo "Bạn có muốn tạo file .env template không? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cat > .env << 'EOF'
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
EOF
        chmod 600 .env
        echo "✓ File .env template đã tạo"
        echo "⚠ VUI LÒNG CHỈNH SỬA FILE .env VÀ ĐIỀN API KEY/SECRET!"
    fi
else
    echo "✓ File .env đã tồn tại"
    chmod 600 .env  # Bảo vệ file .env
fi
echo ""

# Cài đặt screen và tmux (optional)
echo "Bước 5: Cài đặt screen và tmux (optional)..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt install -y screen tmux 2>/dev/null || echo "Screen/tmux đã cài hoặc không thể cài"
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    if command -v dnf &> /dev/null; then
        sudo dnf install -y screen tmux 2>/dev/null || echo "Screen/tmux đã cài hoặc không thể cài"
    else
        sudo yum install -y screen tmux 2>/dev/null || echo "Screen/tmux đã cài hoặc không thể cài"
    fi
fi
echo ""

# Tạo systemd service (optional)
echo "Bước 6: Tạo systemd service (optional)..."
echo "Bạn có muốn tạo systemd service để bot tự động chạy khi khởi động? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    CURRENT_USER=$(whoami)
    CURRENT_DIR=$(pwd)
    
    SERVICE_FILE="/etc/systemd/system/bybit-trading-bot.service"
    
    sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Bybit Trading Bot - EMA200 Crossover Strategy
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python3 $CURRENT_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$CURRENT_DIR/bot.log
StandardError=append:$CURRENT_DIR/bot_error.log

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable bybit-trading-bot
    echo "✓ Systemd service đã tạo và enable"
    echo ""
    echo "Các lệnh quản lý service:"
    echo "  Start:   sudo systemctl start bybit-trading-bot"
    echo "  Stop:    sudo systemctl stop bybit-trading-bot"
    echo "  Status:  sudo systemctl status bybit-trading-bot"
    echo "  Logs:    sudo journalctl -u bybit-trading-bot -f"
else
    echo "Bỏ qua tạo systemd service"
fi
echo ""

# Tóm tắt
echo "=========================================="
echo "Setup hoàn tất!"
echo "=========================================="
echo ""
echo "Các bước tiếp theo:"
echo "1. Chỉnh sửa file .env và điền API Key/Secret"
echo "2. Test chạy bot:"
echo "   source venv/bin/activate"
echo "   python3 main.py"
echo ""
echo "3. Chạy bot ở background:"
echo "   - Dùng screen: screen -S trading-bot"
echo "   - Dùng tmux:  tmux new -s trading-bot"
echo "   - Hoặc dùng systemd service (nếu đã tạo)"
echo ""
echo "Xem thêm hướng dẫn chi tiết trong SERVER_SETUP.md"
echo ""
