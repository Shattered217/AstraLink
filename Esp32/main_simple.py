from wifi_connect import do_connect
import uasyncio as asyncio
from mic import *
from baidu_audio import recongize, speech_tts
from silicon_deepseek import ask_question
from active import *
from load_config import *
import time
from ha_command import ha_action
from mood import send_mood
import random
from emby import send_movie_name

movie_name = None  # 清除电影记忆

async def handle_trigger_actions():
    global movie_name
    config = load_config()
    if config:
        BAIDU_API_KEY = config["baidu"]["api_key"]
        BAIDU_SECRET_KEY = config["baidu"]["secret_key"]
        SILICON_KEY = config["silicon"]["api_token"]

    print("检测到触发事件")
    # 唤醒语音合成
    active_words = [
        "你好，我在呢。",
        "你好，需要帮忙吗？",
        "你好，我已经准备好了。",
        "你好，随时为您服务。",
        "你好，请问需要做什么？"
    ]
    start_time = time.time()
    active_response = random.choice(active_words)
    try:
        await speech_tts(BAIDU_API_KEY, BAIDU_SECRET_KEY, active_response)
        print("唤醒语音已生成")
    except Exception as e:
        print(f"合成错误: {e}")
    print(f"语音合成耗时: {time.time() - start_time:.2f} 秒")

    # 录音
    print("开始录音...")
    recorder = None
    try:
        recorder = AudioRecorder()
        recorder.record_audio(5, "recording.wav")
        recorder.deinit()
        print("录音结束")
    except Exception as e:
        print("录音失败:", e)
        return

    # 语音识别
    start_time = time.time()
    try:
        text = recongize(BAIDU_API_KEY, BAIDU_SECRET_KEY, "recording.wav")
        print(f"识别结果: {text}")
    except ValueError as e:
        print(f"识别错误: {e}")
        text = "语音识别服务器错误"
        return
    print(f"语音识别耗时: {time.time() - start_time:.2f} 秒")

    # AI对话
    start_time = time.time()
    try:
        response = ask_question(text, SILICON_KEY, last_movie=movie_name)
    except Exception as e:
        print(f"AI对话错误: {e}")
        response = {"audio_content": "很抱歉，我刚刚有点短路了。", "command": "movie_off", "emoji": "thinking", "movie": 0}
    print(f"AI对话耗时: {time.time() - start_time:.2f} 秒")

    # 拆包
    audio_response = response["audio_content"]
    command_response = response["command"]
    emoji_response = response["emoji"]
    movie_name = response["movie"]
    print(f"Audio Content: {audio_response}")
    print(f"Command: {command_response}")
    print(f"Emoji: {emoji_response}")
    print(f"Movie: {movie_name}")

    # 并行执行所有后续任务
    tasks = []
    # 收集需要执行的任务
    if command_response:
        tasks.append(ha_action(command_response))
    if emoji_response:
        tasks.append(send_mood(emoji_response))
    if movie_name != 0:
        tasks.append(send_movie_name(movie_name))
    if audio_response:  # 语音合成任务
        tasks.append(speech_tts(BAIDU_API_KEY, BAIDU_SECRET_KEY, audio_response))

    # 并发执行所有任务并处理异常
    if tasks:
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f"并发任务执行出错: {repr(result)}")
        print(f"并发任务总耗时: {time.time() - start_time:.2f} 秒")

# 主函数保持不变
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

    print("触发事件循环运行中...")
    while True:
        await asyncio.sleep(1)  # 保持事件循环运行

if __name__ == '__main__':
    asyncio.run(main())
