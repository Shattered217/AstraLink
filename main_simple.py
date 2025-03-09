from wifi_connect import do_connect
import uasyncio as asyncio
from audio import play_audio
from mic import *
from baidu_audio import recongize, speech_tts
from silicon_deepseek import ask_question
from active import *
from load_config import *

# 声明全局变量
AUDIO_URL = None
APK_KEY = None
SECRET_KEY = None
SILICON_KEY = None

AUDIO_URL = "http://192.168.101.164:6799/nihao.wav"

async def handle_trigger_actions():
    """异步处理完整的触发流程"""
    
    config = load_config()
    if config:
        BAIDU_API_KEY = config["baidu"]["api_key"]
        BAIDU_SECRET_KEY = config["baidu"]["secret_key"]
        AUDIO_URL = config["audio"]["audio_url"]
        SILICON_KEY = config["silicon"]["API_TOKEN"]

    print("\n--- 检测到触发事件 ---")
    # 播放音频
    try:
        print("播放提示音...")
        await play_audio(AUDIO_URL)
    except Exception as e:
        print("音频播放失败:", e)
        return
    
    # 录音
    print("开始录音...")
    recorder = None 
    try:
        recorder = AudioRecorder()
        recorder.record_audio(5, "recording.wav")
        recorder.deinit()  # 释放资源
        print("录音结束")
    except Exception as e:
        print("录音失败:", e)
        return 
    
    # 语音识别
    try:
        text = recongize(BAIDU_API_KEY, BAIDU_SECRET_KEY, "recording.wav")
        print(f"识别结果: {text}")
    except ValueError as e:
        print(f"识别错误: {e}")
        return
    
    # AI对话
    response = ask_question(text, SILICON_KEY)
    print(f"AI回复: {response}")
    
    # 语音合成
    try:
        speech_tts(BAIDU_API_KEY, BAIDU_SECRET_KEY, response)
        print("语音回复已生成")
    except Exception as e:
        print(f"合成错误: {e}")

#主函数
async def main():
    print("系统启动中...")
    
    config = load_config()
    if config:
        WIFI_SSID = config["wifi"]["ssid"]
        WIFI_PASSWORD = config["wifi"]["password"]
    else:
        print("未能加载配置文件，程序退出")
        exit()
    
    try:
        await do_connect(WIFI_SSID, WIFI_PASSWORD)
        print("WiFi 连接成功")
    except Exception as e:
        print("WiFi 连接失败:", e)
        return
    
    print("启动触发监控任务...")
    asyncio.create_task(trigger_manager.process_triggers())
    
    print("主事件循环运行中...")
    while True:
        await asyncio.sleep(1)  # 保持事件循环运行

if __name__ == '__main__':
    asyncio.run(main())
