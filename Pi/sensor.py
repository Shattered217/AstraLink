import time
import board
import adafruit_dht
import threading

# 初始化 DHT11 传感器，连接到 GPIO4，禁用 pulseio
dht_device = adafruit_dht.DHT11(board.D4)

# 用于存储最新的温湿度数据
_current_data = {
    'temperature': None,
    'humidity': None,
    'last_update': None,
    'status': 'waiting'  
}

_data_lock = threading.Lock()

def update_sensor_data():
    global _current_data
    last_success = True 
    while True:
        try:
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity
            
            if temperature_c is not None and humidity is not None:
                temp = round(temperature_c, 1)
                hum = round(humidity, 1)
                current_time = time.time()
                
                with _data_lock:
                    _current_data = {
                        'temperature': temp,
                        'humidity': hum,
                        'last_update': current_time,
                        'status': 'success'
                    }
                
                if not last_success:
                    print("传感器读取恢复正常")
                last_success = True
                time.sleep(5.0) 
            else:
                with _data_lock:
                    _current_data['status'] = 'error'
                last_success = False
                time.sleep(2.0)
        except RuntimeError as error:
            with _data_lock:
                _current_data['status'] = 'error'
            last_success = False
            time.sleep(2.0) 
        except Exception as e:
            with _data_lock:
                _current_data['status'] = 'error'
            last_success = False
            time.sleep(2.0)

def get_sensor_data():
    global _current_data
    with _data_lock:
        return dict(_current_data)

update_thread = threading.Thread(target=update_sensor_data, daemon=True)
update_thread.start()

# 测试代码
if __name__ == '__main__':
    print("开始测试DHT11传感器...")
    print("按Ctrl+C退出")
    try:
        while True:
            data = get_sensor_data()
            if data['temperature'] is not None and data['humidity'] is not None:
                print(f"温度: {data['temperature']}°C  湿度: {data['humidity']}% 状态: {data['status']}")
            else:
                print(f"等待数据... 状态: {data['status']}")
            time.sleep(2) 
    except KeyboardInterrupt:
        print("\n测试结束") 