import urequests
import ujson

def ask_question(question, SILICON_KEY):
    
    API_TOKEN = SILICON_KEY 
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + API_TOKEN,
        "Content-Type": "application/json"
    }

    # 定义人格内容
    system_message = "你是一个幽默风趣的AI观影助手，喜欢用轻松的语气回答问题。请注意，时刻保持精炼且较少的回复，并且不要询问，请直接回复。"

    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {
                "role": "system", 
                "content": system_message
            },
            {
                "role": "user", 
                "content": question
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "response_format": {"type": "text"}
    }

    try:
        json_payload = ujson.dumps(payload)
        json_payload_bytes = json_payload.encode('utf-8')
        response = urequests.post(url, headers=headers, data=json_payload_bytes)
        
        if response.status_code != 200:
            print("API请求失败，状态码:", response.status_code)
            return None
            
        json_data = response.json()
        response.close() 
        
        content = None
        for choice in json_data.get("choices", []):
            message = choice.get("message", {})
            content = message.get("content", "")
            break
        
#         if content:
#             print("\n提取的 Content:", content)
#         else:
#             print("未获取到 Content。")
        
        return content
        
    except Exception as e:
        print("请求异常:", str(e))
        return None

if __name__ == "__main__":
    question = "给我推荐一部电影"
    content = ask_question(question)
    
    if content:
        print("\n提取的 Content:", content)
    else:
        print("未获取到 Content。")
