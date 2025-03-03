import network
import time
import uasyncio as asyncio

async def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect('iot', '1030210302')
        while not wlan.isconnected():
            print("正在连接...")
            await asyncio.sleep(1)  # 非阻塞等待
    print('network config: ', wlan.ifconfig())
