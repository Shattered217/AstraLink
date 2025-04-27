from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)

CONFIG_FILE = 'config.json'

# 初始化数据
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            esp32_data = json.load(f)
    except Exception as e:
        print(f"加载配置失败: {e}")
        esp32_data = {
            "wifi_quality": "未连接",
            "history_conversation": [],
            "status": "待机"
        }
else:
    esp32_data = {
        "wifi_quality": "未连接",
        "history_conversation": [],
        "status": "待机"
    }

# 启动时清空历史记录
first_request = True

@app.before_request
def clear_history():
    global first_request
    if first_request:
        esp32_data['history_conversation'] = []
        first_request = False  # 只在第一次请求时清空历史记录

# 存储历史对话的文件路径
HISTORY_FILE = 'conversation_history.json'

# 如果历史文件存在，加载历史对话
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            esp32_data['history_conversation'] = json.load(f)
    except Exception as e:
        print(f"加载历史对话失败: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/wifi', methods=['GET', 'POST'])
def wifi():
    if request.method == 'POST':
        data = request.get_json()
        if 'wifi_quality' in data:
            esp32_data['wifi_quality'] = data['wifi_quality']
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "缺少wifi_quality参数"})
    return jsonify({"wifi_quality": esp32_data['wifi_quality']})

@app.route('/api/status', methods=['GET', 'POST'])
def status():
    if request.method == 'POST':
        data = request.get_json()
        if 'status' in data:
            esp32_data['status'] = data['status']
            try:
                # 写入配置文件，保存最新状态
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(esp32_data, f, ensure_ascii=False, indent=2)
                return jsonify({"status": "success", "message": "状态更新成功"})
            except Exception as e:
                print(f"保存状态失败: {e}")
                return jsonify({"status": "error", "message": "保存状态失败"})
        else:
            return jsonify({"status": "error", "message": "缺少status参数"})
    
    
    return jsonify({"status": esp32_data['status']})


@app.route('/api/history', methods=['GET'])
def history():
    return jsonify({"history": esp32_data['history_conversation']})

@app.route('/api/add_history', methods=['POST'])
def add_history():
    data = request.get_json()
    if 'message' in data and 'response' in data:
        esp32_data['history_conversation'].append({
            "message": data['message'],
            "response": data['response'],
            "timestamp": datetime.now().isoformat()
        })
        
        # 只需要确保数据正确地写入到 config.json 文件
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(esp32_data, f, ensure_ascii=False, indent=2)
            print("数据已写入 config.json")
        except Exception as e:
            print(f"保存配置失败: {e}")
        
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "缺少message或response参数"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
