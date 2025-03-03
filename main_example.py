# main.py
from wifi_connect import do_connect
import active 
from audio import play_audio
import uasyncio as asyncio

async def main():
    print("Welcome to MicroPython!")
    print(f"初始触发状态: {active.active_triggered}") 
    await do_connect()

    asyncio.create_task(active.active_way()) 
    
    while True:
        if active.active_triggered: 
            print("检测到触发, 播放音频...")
            await play_audio("http://192.168.101.164:6799/nihao.wav")
            active.active_triggered = False 
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())