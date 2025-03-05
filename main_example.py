from wifi_connect import do_connect
import active 
from audio import play_audio
import uasyncio as asyncio
from baidu_audio import *
from mic import *

async def audio_handler():
    print("检测到触发, 播放音频...")
    try:
        await play_audio("http://192.168.101.164:6799/nihao.wav")
    except Exception as e:
        print("播放失败:", e)
        
def trigger_callback():
    """回调函数，执行音频播放"""
    await audio_handler() 
    print("音频播放完成")
    
    # 创建 AudioRecorder 实例
    recorder = AudioRecorder()
    # 开始录音
    recorder.record_audio(3, "recording.wav")
    # 关闭 I2S 接口
    recorder.deinit()
    
    try:
        # 语音识别示例：从 PCM 文件识别文字
        recognized_text = recongize("recording.wav")
        print(f"识别结果: {recognized_text}")
    except ValueError as e:
        print(f"语音识别错误: {e}")
    
    try:
        # 语音合成示例：将文本转为语音并播放
        speech_tts(apikey, sercretkey, recognized_text)
    except Exception as e:
        print(f"语音合成错误: {e}")

async def main():
    print("Welcome to MicroPython!")
    
    # 注册触发回调
    active.register_trigger_callback(trigger_callback)
    
    # 连接WiFi
    await do_connect()
    
    # 启动触发监控任务
    asyncio.create_task(active.monitor_triggers())
    
    # 保持事件循环运行
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
