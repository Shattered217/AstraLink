import ujson as json
import urequests
import time
import uasyncio as asyncio

ENDPOINTS = {
    "wifi_quality": "/api/wifi_quality",
    "ai_chat":     "/api/add_history",
    "status":      "/api/status",
    "emoji":       "/api/mood"  # 添加 emoji endpoint
}

HOST = "http://192.168.101.246:5000"

async def send_data(attr, content1, content2="", timeout=5):
    path = ENDPOINTS.get(attr)
    if not path:
        print('Error: Unknown attribute "{}"'.format(attr))
        return None

    url = HOST + path

    # 根据不同属性，构造不同payload
    if attr == "ai_chat":
        payload = {
            "message": content1,
            "response": content2
        }
    elif attr == "emoji":
        payload = {
            "mood": content1
        }
    else:
        payload = {attr: content1}

    try:
        headers = {
            "Content-Type": "application/json"
        }
        json_str = json.dumps(payload)
        json_bytes = json_str.encode('utf-8') 
        resp = urequests.post(url, data=json_bytes, headers=headers, timeout=timeout)
        print(attr+"发送完成")
        resp.close()
        return resp
    except Exception as e:
        print("Exception during send_data:", e)
        return None

# 测试代码
async def test():    
    # 发送 WiFi 质量
    await send_data("wifi_quality", 70)

    # 发送 AI 对话文本
    await send_data("ai_chat", "你好，今天的天气如何？", "123")

    # 发送状态
    await send_data("status", 1)
    
    # 发送表情
    await send_data("emoji", "cool")

if __name__ == "__main__":
    asyncio.run(test())
