import urequests
import ujson
import re
import time
from load_config import *


def format_response(audio_content: str, command: str, emoji: str, movie: str):
    return {
        "audio_content": audio_content,
        "command": command,
        "emoji": emoji,
        "movie": movie,
    }


def safe_extract_args(args_str):
    """从字符串中提取合法 JSON 并解析为字典"""
    try:
        match = re.search(r'({.*})', args_str)  # 去掉 re.DOTALL
        if match:
            clean_args_str = match.group(1)
            args = ujson.loads(clean_args_str)
            if isinstance(args, dict) and all(k in args for k in ["audio_content", "command", "emoji", "movie"]):
#                 print(f"成功从 JSON 中提取参数: {args}")
                return args
    except Exception as e:
        print(f"解析 JSON 失败: {e}")

    print("尝试手动提取字段...")
    try:
        def extract_field(key):
            pattern = f'"{key}":\\s*"([^"]*?)"'
            match = re.search(pattern, args_str)
            return match.group(1) if match else ""

        args = {
            "audio_content": extract_field("audio_content") or args_str.strip()[:100],
            "command": extract_field("command") or "movie_on",
            "emoji": extract_field("emoji") or "thinking",
            "movie": extract_field("movie") or "0",
        }
        print(f"手动提取成功: {args}")
        return args
    except Exception as e:
        print(f"手动提取失败: {e}")
        return {
            "audio_content": args_str.strip()[:100],
            "command": "movie_on",
            "emoji": "thinking",
            "movie": "0",
        }



def ask_question(question, SILICON_KEY, last_movie=None):
    API_TOKEN = SILICON_KEY
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + API_TOKEN,
        "Content-Type": "application/json",
    }

    movie_context = f"用户刚刚看完电影《{last_movie}》。\n" if last_movie else ""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "format_response",
                "description": "格式化观影助手的响应，返回音频内容、指令、表情和电影名称",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "audio_content": {"type": "string", "description": "简短风趣的回答文本"},
                        "command": {
                            "type": "string",
                            "enum": ["movie_on", "movie_off"],
                            "description": "控制电影播放的指令",
                        },
                        "emoji": {
                            "type": "string",
                            "enum": [
                                "cool", "laughing", "smiling", "kissing", "tasty",
                                "thinking", "smirking", "shushing", "surprised",
                            ],
                            "description": "表情状态",
                        },
                        "movie": {"type": "string", "description": "推荐或停止的电影名称，0表示不推荐"},
                    },
                    "required": ["audio_content", "command", "emoji", "movie"],
                },
            },
        }
    ]

    prompt = f"""你是一个AI观影助手，请严格按照以下要求回答：
    回复必须简短、风趣幽默，语言轻松俏皮。
    当用户表示要观影或询问推荐时返回"movie_on"并推荐电影；
    当用户明确拒绝或结束观影时返回"movie_off"；
    根据上下文选择合适表情，推荐电影时使用正确命名格式。
    当前电影上下文：{movie_context}"""

    payload = {
        "model": "THUDM/GLM-4-32B-0414",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
        "tools": tools,
        "tool_choice": {"type": "function", "function": {"name": "format_response"}},
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 1024,
    }

    try:
        json_payload = ujson.dumps(payload)
        response = urequests.post(url, headers=headers, data=json_payload.encode("utf-8"))

        if response.status_code != 200:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"API响应: {response.text}")
            return None

        json_data = response.json()
        message = json_data.get("choices", [{}])[0].get("message", {})

        if "tool_calls" in message:
            tool_call = message["tool_calls"][0]
            if tool_call["function"]["name"] == "format_response":
                args_str = tool_call["function"].get("arguments", "")
#                 print(f"原始工具参数字符串: {args_str}")
                args = safe_extract_args(args_str)
                return args

        print("未获取到有效的工具调用响应")
        return None

    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None
    finally:
        if 'response' in locals():
            response.close()

if __name__ == "__main__":
    config = load_config()
    SILICON_KEY = config["silicon"]["api_token"]
    question = "刚刚那部电影怎么样"
    content = ask_question(question, SILICON_KEY, "疾速追杀4")

    if content:
#         print("\n提取的 Content:", content)
        print("Audio Content:", content.get("audio_content"))
        print("Command:", content.get("command"))
        print("Emoji:", content.get("emoji"))
        print("Movie:", content.get("movie"))
    else:
        print("未获取到 Content。")

