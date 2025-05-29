# main.py
from wifi_connect import *
import uasyncio as asyncio
from mic import *
from baidu_audio import recongize, speech_tts
from silicon_deepseek import ask_question
from active import TriggerManager
from load_config import *
from ha_command import ha_action
from send_data import send_data
import random
from emby import send_movie_name

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
            await send_data("wifi_quality", get_wifi_quality())
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
        await send_data("status", 1)
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
            
            print(f"AI响应: {response}")  # 添加调试输出
            
            if not response or not isinstance(response, dict) or not all(key in response for key in ["audio_content", "command", "emoji", "movie"]):
                print("AI处理失败，返回默认响应")
                response = {
                    "audio_content": "抱歉，我现在有点累，能换个方式说吗？",
                    "command": "",
                    "emoji": "thinking",
                    "movie": "0"
                }

            # 响应处理
            tasks = []
            try:
                if response.get("command"):
                    tasks.append(ha_action(response["command"]))
                if response.get("emoji"):
                    tasks.append(send_data("emoji", response["emoji"]))
                if response.get("movie") != "0":
                    tasks.append(send_movie_name(response["movie"]))
                if response.get("audio_content"):
                    tasks.append(speech_tts(
                        self.config["baidu"]["api_key"],
                        self.config["baidu"]["secret_key"],
                        response["audio_content"]
                    ))            

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                else:
                    print("没有需要执行的任务")
            except Exception as e:
                print(f"任务执行异常: {e}")
                await send_data("ai_chat", "任务执行异常", str(e))
        finally:
            await send_data("ai_chat", text, response["audio_content"])
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

