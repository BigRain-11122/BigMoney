# Master 节点初始化（Windows PowerShell）
# 1. 安装依赖
python -m pip install -r requirements.txt

# 2. 启动 Redis（需要先装 Redis for Windows，或用 WSL）
# 本脚本不负责安装 Redis，假设 redis-server 已在 PATH
Start-Process redis-server -WindowStyle Hidden

# 3. 初始化目录
New-Item -ItemType Directory -Force -Path data\daily, data\basic, results, logs | Out-Null

Write-Host "[master] setup complete. Next: pull data, then start Celery workers."
