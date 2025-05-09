from flask import Flask, jsonify, send_from_directory, render_template, request
import datetime
import requests
import os

app = Flask(__name__)

# 用于存储当前mood
current_mood = 'default'

def get_current_mood():
    global current_mood
    return current_mood

def set_current_mood(mood):
    global current_mood
    current_mood = mood

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
            set_current_mood(mood)
            return jsonify({'status': 'ok', 'mood': mood})
        return jsonify({'status': 'error', 'msg': 'No mood provided'}), 400
    else:
        mood = get_current_mood()
        return jsonify({'mood': mood})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/emoji/<filename>')
def emoji(filename):
    return send_from_directory('emoji', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)