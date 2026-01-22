module.exports = {
  apps: [{
    name: 'bybit-trading-bot',
    script: 'main.py',
    interpreter: 'venv/bin/python3',
    cwd: process.cwd(), // Sử dụng thư mục hiện tại
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
    merge_logs: true,
    // Restart nếu crash
    min_uptime: '10s',
    max_restarts: 10,
    restart_delay: 4000
  }]
};
