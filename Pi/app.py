from flask import Flask, jsonify, send_from_directory, render_template, request
import datetime
import threading
import time
import board
import adafruit_dht
import requests
from sensor import get_sensor_data 

app = Flask(__name__)

_thread_started = False
_start_lock = threading.Lock()

dht_device = adafruit_dht.DHT11(board.D4)
_data_lock = threading.Lock()
_current_data = {
    'temperature': None,
    'humidity': None,
    'last_update': None,
    'status': 'waiting'
}

def update_sensor_data():
    time.sleep(2)
    while True:
        try:
            t = dht_device.temperature
            h = dht_device.humidity
            if t is not None and h is not None:
                with _data_lock:
                    _current_data.update({
                        'temperature': round(t, 1),
                        'humidity': round(h, 1),
                        'last_update': time.time(),
                        'status': 'success'
                    })
            else:
                with _data_lock:
                    _current_data['status'] = 'error'
        except RuntimeError:
            with _data_lock:
                _current_data['status'] = 'error'
        except Exception:
            with _data_lock:
                _current_data['status'] = 'error'
        time.sleep(5)


@app.before_request
def start_sensor_thread_once():
    global _thread_started, _start_lock
    with _start_lock:
        if not _thread_started:
            from sensor import update_sensor_data
            threading.Thread(target=update_sensor_data, daemon=True).start()
            _thread_started = True

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
    from sensor import get_sensor_data
    return jsonify(get_sensor_data())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/emoji/<filename>')
def emoji(filename):
    return send_from_directory('emoji', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
