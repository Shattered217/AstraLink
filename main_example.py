from wifi_connect import do_connect
import active 
from audio import play_audio
import uasyncio as asyncio
from baidu_audio import *
from mic import *
from silicon_deepseek import *

async def audio_handler():
    print("检测到触发, 播放音频...")
    try:
        await play_audio("http://192.168.101.164:6799/nihao.wav")
    except Exception as e:
        print("播放失败:", e)
        
def trigger_callback():
    """回调函数，执行音频播放"""
    await audio_handler() 
    print("开始录音")
                                      
    recorder = AudioRecorder()
    recorder.record_audio(5, "recording.wav")
    recorder.deinit()
    print("录音结束")
    
    try:
        recognized_text = recongize("recording.wav")
        print(f"识别结果: {recognized_text}")
    except ValueError as e:
        print(f"语音识别错误: {e}")
    
    ai_text = ask_question(recognized_text)
    
    try:
        speech_tts(apikey, sercretkey, ai_text)
    except Exception as e:
        print(f"语音合成错误: {e}")

async def main():
    print("Welcome to MicroPython!")
     
    # 注册触发回调
    active.register_trigger_callback(trigger_callback)
    
    await do_connect()
    
    # 启动触发监控任务
    asyncio.create_task(active.monitor_triggers())
    
    # 保持事件循环运行
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
