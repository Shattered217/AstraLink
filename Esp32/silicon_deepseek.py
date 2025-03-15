import urequests
import ujson
import time

def ask_question(question, SILICON_KEY):
    API_TOKEN = SILICON_KEY 
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + API_TOKEN,
        "Content-Type": "application/json"
    }

    # 定义人格内容
    prompt = """你是一个AI观影助手，请严格按照以下要求回答：
    回复必须简短、风趣幽默，语言轻松俏皮。
    每次回复必须返回一个Python可拆包的字典，格式如下：
    {"audio_content": "回答文本", "command": "指令", "emoji": ["心情"]}
    可用表情包括: ["cool", "laughing", "smiling", "kissing", "tasty", "thinking", "smirking", "shushing", "surprised" , "tasty", "laughing"]
    指令（command）字段只能有两个值："movie_on" 或 "movie_off"。
    如果用户表示要观影或询问电影推荐，则返回 "movie_on"。
    如果用户明确表示不想观影或拒绝推荐，则返回 "movie_off"。
    不允许输出除上述字段之外的任何内容或格式。
    请根据用户的提问灵活回答，避免每次都推荐相同的电影。"""
    
    payload = {
        "model": "Qwen/QwQ-32B",
        "messages": [
            {
                "role": "system", 
                "content": prompt
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
        "response_format": {"type": "text"},
        "cache_buster": str(time.time())  # 避免缓存
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
        
        # 将 content 解析为字典
        if content:
            try:
                # 去除可能的换行符和多余空格
                content = content.strip()
                # 将字符串解析为字典
                content_dict = ujson.loads(content)
                return content_dict
            except Exception as e:
                print("解析 content 为字典失败:", str(e))
                return None
        else:
            print("未获取到 Content。")
            return None
        
    except Exception as e:
        print("请求异常:", str(e))
        return None

if __name__ == "__main__":
    question = "开启观影模式"
    content = ask_question(question, "")
    
    if content:
        print("\n提取的 Content:", content)
        print("Audio Content:", content.get("audio_content"))
        print("Command:", content.get("command"))
        print("Emoji:", content.get("emoji"))
    else:
        print("未获取到 Content。")