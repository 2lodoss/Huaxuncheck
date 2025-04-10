@echo off
chcp 65001
echo 正在启动网络设备巡检系统...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请确保已安装Python并添加到系统环境变量中
    pause
    exit /b 1
)

REM 删除旧的数据库文件
if exist network_inspection.db (
    echo 正在删除旧的数据库文件...
    del network_inspection.db
)

REM 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误：依赖安装失败，请检查网络连接或手动运行 pip install -r requirements.txt
    pause
    exit /b 1
)

REM 启动后端服务
echo 正在启动后端服务...
start python app.py

REM 等待后端服务启动
echo 等待后端服务启动...
timeout /t 5

REM 检查后端服务是否正常运行
curl http://localhost:5000/api/devices >nul 2>&1
if errorlevel 1 (
    echo 错误：后端服务启动失败
    echo 请检查：
    echo 1. 端口5000是否被占用
    echo 2. 查看命令行窗口中的错误信息
    echo 3. 确保所有依赖都已正确安装
    pause
    exit /b 1
)

REM 启动前端页面
echo 正在启动前端页面...
start frontend/index.html

echo 系统已启动！
echo 后端服务运行在 http://localhost:5000
echo 前端页面已打开 