from wifi_connect import do_connect
import active 
from audio import play_audio
import uasyncio as asyncio

async def audio_handler():
    print("检测到触发, 播放音频...")
    try:
        await play_audio("http://192.168.101.164:6799/nihao.wav")
    except Exception as e:
        print("播放失败:", e)

async def main():
    print("Welcome to MicroPython!")
    
    # 注册触发回调
    active.register_trigger_callback(audio_handler)
    
    # 连接WiFi
    await do_connect()
    
    # 启动触发监控任务
    asyncio.create_task(active.monitor_triggers())
    
    # 保持事件循环运行（替代 sleep_forever）
    while True:
        await asyncio.sleep(1)  # 每秒检查一次

if __name__ == '__main__':
    asyncio.run(main())
