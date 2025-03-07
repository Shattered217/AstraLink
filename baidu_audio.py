import json
import gc
import binascii
import urequests
from machine import unique_id
from machine import I2S, Pin
import time

# 配置音频采样率与设备ID
audiorate = 16000
dev_cuid = binascii.hexlify(unique_id()).decode("utf-8")
print(dev_cuid)

# 百度语音识别和语音合成 API 密钥（填入你自己的）
apikey = "fsgLPOlFX0aW1xSJAk3oiS0p"
sercretkey = "YYw6JdIJLe4aAoksgy19YraYisgHZCFP"

def fetch_token(API_Key, Secret_Key):
    url = f'http://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_Key}&client_secret={Secret_Key}'
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = urequests.request("POST", url, headers=headers, data=payload)
    return str(response.json().get("access_token"))

def recongize(audiofile, dev_pid=80001, chunk_size=4096):
    """使用 RAW 方式，分块上传音频数据"""
    token = fetch_token(apikey, sercretkey)
    url = f'http://vop.baidu.com/pro_api?dev_pid={dev_pid}&cuid={dev_cuid}&token={token}'

    headers = {
        'Content-Type': 'audio/pcm;rate=16000',
    }

    with open(audiofile, 'rb') as f:
        uresponse = urequests.post(url, data=f, headers=headers)

    results = uresponse.json()
    
    if results.get("err_no") == 0:
        return "".join(results["result"])
    else:
        raise ValueError(f"识别错误: {results.get('err_msg')}, 错误码: {results.get('err_no')}")

def speech_tts(API_Key, Secret_Key, text_tts):
    _token = fetch_token(apikey, sercretkey)
    text = binascii.hexlify(text_tts.encode('utf-8')).decode("utf-8") 
    text_urlencode = ''
    for i in range(0, len(text)):
        if i % 2 == 0:
            text_urlencode += '%'
        text_urlencode += text[i]
    
    tts_url = f'http://tsn.baidu.com/text2audio?tex={text_urlencode}&tok={_token}&cuid={dev_cuid}&ctp=1&lan=zh&spd=5&vol=5&per=111&aue=6'
    
    i2s = I2S(1, sck=Pin(18), ws=Pin(8), sd=Pin(17), mode=I2S.TX, bits=16, format=I2S.MONO, rate=16000, ibuf=20000)
    response = urequests.get(tts_url, stream=True)
    response.raw.read(44) 
    
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
#         recognized_text = recongize("16k.wav")
#         print(f"识别结果: {recognized_text}")
#     except ValueError as e:
#         print(f"语音识别错误: {e}")
#     
#     try:
#         # 语音合成示例：将文本转为语音并播放
#         speech_tts(apikey, sercretkey, recognized_text)
#     except Exception as e:
#         print(f"语音合成错误: {e}")

