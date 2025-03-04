import json
import gc
import binascii
import urequests
from machine import unique_id
from machine import I2S, Pin
import time

# 配置音频采样率与设备ID
audiorate = 8000
dev_cuid = binascii.hexlify(unique_id()).decode("utf-8")
print(dev_cuid)

# 百度语音识别和语音合成 API 密钥（填入你自己的）
apikey = ''  # 语音识别API Key
sercretkey = ''  # 语音识别Secret Key

# 获取访问令牌（token）
def fetch_token(API_Key, Secret_Key):
    url = f'http://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_Key}&client_secret={Secret_Key}'
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = urequests.request("POST", url, headers=headers, data=payload)
    return str(response.json().get("access_token"))

# 语音识别（STT）
import time

def recongize(audiofile, dev_pid=80001):
    """语音识别（STT）"""
    _token = fetch_token(apikey, sercretkey)
    url = f'http://vop.baidu.com/pro_api?dev_pid={dev_pid}&cuid={dev_cuid}&token={_token}'

    # 逐块读取音频数据，避免一次性加载整个文件
    chunk_size = 48000  # 每次读取的数据块大小
    with open(audiofile, 'rb') as f:
        while True:
            speech_data = f.read(chunk_size)
            if not speech_data:
                break  # 文件读取完成
            
            # 将每块数据发送到百度语音识别API
            headers = {
                'Content-Type': f'audio/pcm; rate={audiorate}'
            }
            try:
                response = urequests.post(url, data=speech_data, headers=headers)
                results = json.loads(response.text)
                if results["err_no"] != 0:
                    raise ValueError(results["err_msg"], results["err_no"])
                elif results["err_msg"] == "success.":
                    gc.collect()  # 清理内存
                    return results["result"][0]
                time.sleep(1)  # 添加延时，减少请求频率
            except Exception as e:
                print(f"请求失败，错误：{e}")
                gc.collect()  # 出现错误时清理内存
                time.sleep(1)  # 异常情况下也添加延时
    return "未识别到语音"


# 语音合成（TTS）
def speech_tts(API_Key, Secret_Key, text_tts):
    _token = fetch_token(apikey, sercretkey)
    text = binascii.hexlify(text_tts.encode('utf-8')).decode("utf-8")  # 对文字进行转码
    text_urlencode = ''
    for i in range(0, len(text)):
        if i % 2 == 0:
            text_urlencode += '%'
        text_urlencode += text[i]
    
    tts_url = f'http://tsn.baidu.com/text2audio?tex={text_urlencode}&tok={_token}&cuid={dev_cuid}&ctp=1&lan=zh&spd=5&vol=5&per=111&aue=6'
    
    # 创建音频输出对象
    i2s = I2S(1, sck=Pin(5), ws=Pin(14), sd=Pin(11), mode=I2S.TX, bits=16, format=I2S.MONO, rate=16000, ibuf=20000)
    response = urequests.get(tts_url, stream=True)
    response.raw.read(44)  # 跳过WAV头
    
    while True:
        try:
            content_byte = response.raw.read(1024)
            if len(content_byte) == 0:
                time.sleep_ms(100)
                break
            i2s.write(content_byte)
        except Exception as ret:
            print("产生的异常为", ret)
            i2s.deinit()
            break
    
    time.sleep_ms(100)
    i2s.deinit()

# 示例：语音识别与语音合成
# if __name__ == "__main__":
#     try:
#         # 语音识别示例：从 PCM 文件识别文字
#         recognized_text = recongize("s.pcm")
#         print(f"识别结果: {recognized_text}")
#     except ValueError as e:
#         print(f"语音识别错误: {e}")
#     
#     try:
#         # 语音合成示例：将文本转为语音并播放
#         speech_tts(apikey, sercretkey, "欢迎使用语音合成功能！")
#     except Exception as e:
#         print(f"语音合成错误: {e}")

