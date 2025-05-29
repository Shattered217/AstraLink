#!/bin/bash

# --- 配置 ---
FLASK_APP_PATH="/home/Shattered/AstraLink/app.py"
VENV_ACTIVATE_SCRIPT="/home/Shattered/AstraLink/env/bin/activate"
FLASK_PORT="5000" # 假设 Flask 运行在 5000 端口
BROWSER_URL="http://127.0.0.1:$FLASK_PORT"
BROWSER_START_DELAY_SECONDS=3

# --- 捕获 SIGINT (CTRL+C) 以优雅地退出 ---
# 当按下 CTRL+C 时，这个函数会被执行
cleanup_on_exit() {
    echo -e "\n捕获到 CTRL+C。正在关闭..."

    # 停止 Flask 应用
    if [ -n "$APP_PID" ]; then
        echo "正在终止 Flask 应用 (PID: $APP_PID)..."
        kill "$APP_PID" 2>/dev/null # 发送 SIGTERM 信号
        wait "$APP_PID" 2>/dev/null # 等待进程终止
        echo "Flask 应用已终止。"
    fi

    # 停止 Chromium 浏览器
    # 注意：Chromium 可能不会直接响应 kill，因为它可能有多个子进程。
    # 更可靠的方法是杀死所有与该 URL 相关的 Chromium 进程。
    # 这里我们尝试通过其进程 ID 终止，但如果有多个实例或子进程，可能需要更复杂的逻辑。
    if [ -n "$BROWSER_PID" ]; then
        echo "正在终止 Chromium 浏览器 (PID: $BROWSER_PID)..."
        kill "$BROWSER_PID" 2>/dev/null # 发送 SIGTERM 信号
        wait "$BROWSER_PID" 2>/dev/null # 等待进程终止
        echo "Chromium 浏览器已终止。"
    fi

    # 退出脚本
    exit 0
}

# 设置陷阱，当接收到 SIGINT 信号时执行 cleanup_on_exit 函数
trap cleanup_on_exit SIGINT

# --- 启动 Flask 服务（后台运行）---
echo "正在启动 Flask 服务..."
source "$VENV_ACTIVATE_SCRIPT" # 激活虚拟环境
python3 "$FLASK_APP_PATH" &
APP_PID=$! # 获取 Flask 进程的 PID
echo "Flask 服务已启动 (PID: $APP_PID)。"

# --- 延迟启动浏览器 ---
echo "等待 ${BROWSER_START_DELAY_SECONDS} 秒后启动浏览器..."
sleep "$BROWSER_START_DELAY_SECONDS"

echo "正在启动 Chromium 浏览器..."
chromium-browser --kiosk "$BROWSER_URL" &
BROWSER_PID=$! # 获取浏览器进程的 PID
echo "Chromium 浏览器已启动 (PID: $BROWSER_PID)。"


# --- 阻塞脚本，直到 Flask 程序退出 ---
# 这会等待 Flask 进程。当它被 kill -SIGTERM 或自身退出时，wait 也会结束。
# 由于我们设置了 trap，如果用户按 CTRL+C，trap 会先被触发，然后 kill Flask 进程。
echo "脚本正在等待 Flask 应用退出。请按 CTRL+C 终止。"
wait "$APP_PID"

echo "Flask 应用已自行终止。正在执行清理..."
cleanup_on_exit # 确保在 Flask 正常退出时也执行清理（尽管浏览器可能还在）

# 如果 Flask 在按下 CTRL+C 之前就退出了，我们仍然会执行清理。