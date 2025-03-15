import json
import time
import binascii
import urequests
from machine import unique_id, I2S, Pin

# 配置音频采样率与设备ID
audiorate = 16000
dev_cuid = binascii.hexlify(unique_id()).decode("utf-8")

# 全局变量用于存储 token 及其过期时间
global_token = None
token_expiration_time = 0

def fetch_token(API_Key, Secret_Key):
    """从百度 API 获取 access_token"""
    start_time = time.time()
    url = f'http://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_Key}&client_secret={Secret_Key}'
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = urequests.request("POST", url, headers=headers, data=payload)
    print(f"获取 token 耗时: {time.time() - start_time:.2f} 秒")
    
    response_data = response.json()
    access_token = response_data.get("access_token")
    expires_in = response_data.get("expires_in", 0)  # 默认过期时间为 0
    
    expiration_time = time.time() + expires_in
    
    return access_token, expiration_time

def get_token(API_Key, Secret_Key):
    global global_token, token_expiration_time
    
    if not global_token or time.time() >= token_expiration_time:
        print("Token 不存在或已过期，正在重新获取...")
        global_token, token_expiration_time = fetch_token(API_Key, Secret_Key)
    
    return global_token

def recongize(apikey, sercretkey, audiofile, dev_pid=80001, chunk_size=4096):
    """语音识别函数"""
    token = get_token(apikey, sercretkey) 
    url = f'http://vop.baidu.com/pro_api?dev_pid={dev_pid}&cuid={dev_cuid}&token={token}'

    headers = {
        'Content-Type': 'audio/pcm;rate=16000',
    }

    start_time = time.time()
    with open(audiofile, 'rb') as f:
        uresponse = urequests.post(url, data=f, headers=headers)
    print(f"上传音频耗时: {time.time() - start_time:.2f} 秒")

    start_time = time.time()
    results = uresponse.json()
    print(f"解析返回数据耗时: {time.time() - start_time:.2f} 秒")
    
    if results.get("err_no") == 0:
        return "".join(results["result"])
    else:
        raise ValueError(f"识别错误: {results.get('err_msg')}, 错误码: {results.get('err_no')}")

def speech_tts(apikey, sercretkey, text_tts):
    """语音合成函数"""
    token = get_token(apikey, sercretkey)  
    text = binascii.hexlify(text_tts.encode('utf-8')).decode("utf-8") 
    text_urlencode = ''
    for i in range(0, len(text)):
        if i % 2 == 0:
            text_urlencode += '%'
        text_urlencode += text[i]
    
    tts_url = f'http://tsn.baidu.com/text2audio?tex={text_urlencode}&tok={token}&cuid={dev_cuid}&ctp=1&lan=zh&spd=5&vol=5&per=111&aue=6'
    
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
if __name__ == "__main__":
    apikey = "your_api_key"
    sercretkey = "your_secret_key"
    
    try:
        # 语音识别示例：从 PCM 文件识别文字
        recognized_text = recongize(apikey, sercretkey, "recording.wav")
        print(f"识别结果: {recognized_text}")
    except ValueError as e:
        print(f"语音识别错误: {e}")
    
    try:
        # 语音合成示例：将文本转为语音并播放
        speech_tts(apikey, sercretkey, "你好，世界！")
    except Exception as e:
        print(f"语音合成错误: {e}")