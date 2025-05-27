# main.py
from wifi_connect import *
import uasyncio as asyncio
from mic import *
from baidu_audio import recongize, speech_tts
from silicon_deepseek import ask_question
from active import TriggerManager
from load_config import *
from ha_command import ha_action
from mood import send_mood
import random
from emby import send_movie_name
from send_data import send_data

movie_name = None

class Application:
    def __init__(self):
        self.trigger_manager = None
        self.config = None

    async def initialize(self):
        self.config = load_config()
        if not self.config:
            raise RuntimeError("配置加载失败")
        
        await self.connect_wifi()
        self.init_trigger_manager()
        print("系统初始化完成")

    async def connect_wifi(self):
        try:
            await do_connect(
                self.config["wifi"]["ssid"],
                self.config["wifi"]["password"]
            )
            print(f"WiFi连接成功，质量: {get_wifi_quality()}")
        except Exception as e:
            print(f"WiFi连接失败: {e}")
            raise

    def init_trigger_manager(self):
        self.trigger_manager = TriggerManager(
            handler=self.handle_trigger_actions,
            uart_num=1,
            baudrate=9600,
            rx_pin=9
        )
        asyncio.create_task(self.trigger_manager.process_triggers())
        print("串口触发器已初始化")

    async def handle_trigger_actions(self):
        send_data("status", 1)
        global movie_name
        
        try:
            # 唤醒语音合成
            active_response = random.choice([
                "你好，我在呢。",
                "你好，需要帮忙吗？",
                "你好，我已经准备好了。",
                "你好，随时为您服务。",
                "你好，请问需要做什么？"
            ])
            await speech_tts(
                self.config["baidu"]["api_key"],
                self.config["baidu"]["secret_key"],
                active_response
            )

            # 录音处理
            recorder = AudioRecorder()
            recorder.record_audio(5, "recording.wav")
            recorder.deinit()

            # 语音识别
            text = recongize(
                self.config["baidu"]["api_key"],
                self.config["baidu"]["secret_key"],
                "recording.wav"
            )

            # AI处理
            response = ask_question(
                text,
                self.config["silicon"]["api_token"],
                last_movie=movie_name
            )

            # 响应处理
            tasks = []
            if response.get("command"):
                tasks.append(ha_action(response["command"]))
            if response.get("emoji"):
                tasks.append(send_mood(response["emoji"]))
            if response.get("movie") != "0":
                tasks.append(send_movie_name(response["movie"]))
            if response.get("audio_content"):
                tasks.append(speech_tts(
                    self.config["baidu"]["api_key"],
                    self.config["baidu"]["secret_key"],
                    response["audio_content"]
                ))

            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            print(f"处理流程异常: {e}")
            await send_data("error", str(e))
        finally:
            await send_data("status", 0)

async def main():
    app = Application()
    try:
        await app.initialize()
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        print(f"系统崩溃: {e}")
        # 执行紧急恢复操作

if __name__ == '__main__':
    asyncio.run(main())
