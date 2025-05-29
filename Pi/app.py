from flask import Flask, jsonify, send_from_directory, render_template, request
import datetime
import threading
import time
import requests

app = Flask(__name__)

# Home Assistant配置
HA_BASE_URL = "http://192.168.101.246:8123"
HA_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzZmQ1ZDI1NGZhNTA0NTRhOTRhZDRjYzYyZGU5MWVkYyIsImlhdCI6MTc0MTY5NjI0NywiZXhwIjoyMDU3MDU2MjQ3fQ.dIc5ebY-FBbCApzPNKcfUweKxpdoKIx9EddOdGmbEV8"
HA_HEADERS = {
    "Authorization": f"Bearer {HA_API_KEY}",
    "Content-Type": "application/json"
}

_data_lock = threading.Lock()
_current_data = {
    'temperature': None,
    'humidity': None,
    'last_update': None,
    'status': 'waiting'
}

# 添加对话历史变量
_conversation = {
    'message': None,
    'response': None
}

# 添加WiFi信号和状态变量
_wifi_quality = 0
_status = 0

def get_ha_sensor_data():
    try:
        # 获取温度数据
        temp_response = requests.get(
            f"{HA_BASE_URL}/api/states/sensor.temperature_humidity_sensor_12a5_temperature",
            headers=HA_HEADERS,
            timeout=5
        )
        temp_data = temp_response.json()
        
        # 获取湿度数据
        humidity_response = requests.get(
            f"{HA_BASE_URL}/api/states/sensor.temperature_humidity_sensor_12a5_humidity",
            headers=HA_HEADERS,
            timeout=5
        )
        humidity_data = humidity_response.json()
        
        if temp_response.status_code == 200 and humidity_response.status_code == 200:
            return {
                'temperature': round(float(temp_data['state']), 1),
                'humidity': round(float(humidity_data['state']), 1),
                'last_update': time.time(),
                'status': 'success'
            }
        else:
            return {'status': 'error'}
    except Exception as e:
        print(f"Error fetching HA data: {e}")
        return {'status': 'error'}

def update_sensor_data():
    time.sleep(2)
    while True:
        try:
            sensor_data = get_ha_sensor_data()
            with _data_lock:
                _current_data.update(sensor_data)
        except Exception as e:
            print(f"Error in update_sensor_data: {e}")
            with _data_lock:
                _current_data['status'] = 'error'
        time.sleep(5)

# 启动传感器数据更新线程
sensor_thread = threading.Thread(target=update_sensor_data, daemon=True)
sensor_thread.start()

current_mood = 'default'

@app.route('/api/time')
def get_time():
    now = datetime.datetime.now()
    return jsonify({
        'time': now.strftime('%H:%M:%S'),
        'date': now.strftime('%Y-%m-%d')
    })

@app.route('/api/yiyan')
def get_yiyan():
    try:
        resp = requests.get('http://192.168.101.129:8000/?encode=text&c=i', timeout=2)
        return jsonify({'yiyan': resp.text.strip()})
    except:
        return jsonify({'yiyan': '获取失败'})

@app.route('/api/mood', methods=['GET', 'POST'])
def api_mood():
    if request.method == 'POST':
        data = request.get_json() or request.form
        mood = data.get('mood')
        if mood:
            global current_mood
            current_mood = mood
            return jsonify({'status': 'ok', 'mood': mood})
        return jsonify({'status': 'error', 'msg': 'No mood provided'}), 400
    else:
        return jsonify({'mood': current_mood})

@app.route('/api/sensor')
def get_sensor():
    with _data_lock:
        return jsonify(_current_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/emoji/<filename>')
def emoji(filename):
    return send_from_directory('emoji', filename)

@app.route('/api/add_history', methods=['POST'])
def add_history():
    data = request.get_json() or request.form
    message = data.get('message')
    response = data.get('response')
    
    if message and response:
        global _conversation
        _conversation = {
            'message': message,
            'response': response
        }
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error', 'msg': 'Missing message or response'}), 400

@app.route('/api/conversation')
def get_conversation():
    return jsonify(_conversation)

@app.route('/api/wifi_quality', methods=['GET', 'POST'])
def wifi_quality():
    global _wifi_quality
    if request.method == 'POST':
        data = request.get_json() or request.form
        quality = data.get('wifi_quality')
        if quality is not None:
            _wifi_quality = int(quality)
            return jsonify({'status': 'ok'})
        return jsonify({'status': 'error', 'msg': 'No quality value provided'}), 400
    return jsonify({'quality': _wifi_quality})

@app.route('/api/status', methods=['GET', 'POST'])
def status():
    global _status
    if request.method == 'POST':
        data = request.get_json() or request.form
        status = data.get('status')
        if status is not None:
            _status = int(status)
            return jsonify({'status': 'ok'})
        return jsonify({'status': 'error', 'msg': 'No status value provided'}), 400
    return jsonify({'status': _status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
