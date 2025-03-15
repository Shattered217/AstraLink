import network
import time
import uasyncio as asyncio

async def do_connect(WIFI_SSID, WIFI_PASSWORD):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        print("WiFi名称: "+WIFI_SSID+"  WiFi密码: "+WIFI_PASSWORD)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print("正在连接...")
            await asyncio.sleep(1)  # 非阻塞等待
    print('network config: ', wlan.ifconfig())
