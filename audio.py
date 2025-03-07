from machine import I2S, Pin
import urequests
import uasyncio as asyncio

sck_pin = Pin(18)
ws_pin = Pin(8)
sd_pin = Pin(17)

async def play_audio(url):
    try:
        # 初始化 I2S
        audio_out = I2S(1, sck=sck_pin, ws=ws_pin, sd=sd_pin, mode=I2S.TX, bits=16, format=I2S.MONO, rate=44100, ibuf=40000)
        
        response = urequests.get(url)
        response.raw.read(44)
        print("音频开始播放...")

        while True:
            content_byte = response.raw.read(4096)
            if len(content_byte) == 0:
                print("音频播放完毕.")
                break
            
            audio_out.write(content_byte)
            await asyncio.sleep(0)
    
    except Exception as e:
        print("播放音频时发生异常: ", e)
    finally:
        response.close()

