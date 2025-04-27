import network
import time
import uasyncio as asyncio

wlan = network.WLAN(network.STA_IF)

async def do_connect(WIFI_SSID, WIFI_PASSWORD):
    global wlan
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        print("WiFi名称: "+WIFI_SSID+"  WiFi密码: "+WIFI_PASSWORD)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print("正在连接...")
            await asyncio.sleep(1)  # 非阻塞等待
    print('network config: ', wlan.ifconfig())
    
def get_wifi_quality():
    global wlan
    rssi = wlan.status('rssi')
    quality = min(max(2 * (rssi + 100), 0), 100)
    return int(quality)

if __name__ == "__main__":
    get_wifi_quality()

