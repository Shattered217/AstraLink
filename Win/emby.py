import base64
import json
import requests
import subprocess
from flask import Flask, request, jsonify

# 配置参数
EMBY_URL = "http://192.168.101.236:8091"  # Emby 服务器地址
API_KEY = "43a6513adb44436e813f7fcb7c329143"  # Emby API 密钥
VLC_PATH = r"D:\VideoLAN\VLC\vlc.exe"  # VLC 可执行文件路径

app = Flask(__name__)

@app.route('/play', methods=['POST'])
def play_movie():
    try:
        raw_data = request.get_data(as_text=True)
        print(f"接收到的原始请求体: {raw_data}")

        if not request.is_json:
            return jsonify({"error": "请求头必须为 application/json"}), 400

        data = request.json
        encoded_data = data.get("encoded_data")
        if not encoded_data:
            return jsonify({"error": "缺少编码数据"}), 400

        try:
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            print(f"解码后的数据: {decoded_data}")
        except Exception as e:
            print(f"Base64 解码失败: {e}")
            return jsonify({"error": "Base64 解码失败"}), 400

        try:
            json_data = json.loads(decoded_data)
        except Exception as e:
            print(f"JSON 解析失败: {e}")
            return jsonify({"error": "JSON 解析失败"}), 400

        movie_name = json_data.get("movie_name")
        if not movie_name:
            return jsonify({"error": "影片名称不能为空"}), 400

        print(f"收到影片名称: {movie_name}")

        # 调用 Emby API 搜索影片 ID
        search_url = f"{EMBY_URL}/Items"
        params = {
            "searchTerm": movie_name,
            "api_key": API_KEY,
            "IncludeItemTypes": "Movie",
            "Recursive": "true"
        }
        response = requests.get(search_url, params=params)
        if response.status_code != 200:
            return jsonify({"error": "Emby API 请求失败"}), 500

        emby_data = response.json()
        if emby_data.get("TotalRecordCount", 0) == 0:
            return jsonify({"error": "未找到匹配的影片"}), 404

        movie_id = emby_data["Items"][0]["Id"]
        stream_url = f"{EMBY_URL}/Videos/{movie_id}/stream.mp4?api_key={API_KEY}"
        print(f"找到影片 ID: {movie_id}")
        print(f"播放链接: {stream_url}")

        # 调用 VLC 全屏播放
        try:
            subprocess.Popen([VLC_PATH, "--fullscreen", stream_url])
        except Exception as e:
            print(f"调用 VLC 失败: {e}")
            return jsonify({"error": "无法调用 VLC"}), 500

        return jsonify({"message": "播放成功", "movie_id": movie_id, "stream_url": stream_url}), 200

    except Exception as e:
        print(f"发生错误: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)