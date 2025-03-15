import urequests
import ujson

# 请根据你的 Home Assistant 实例地址进行修改
HA_URL = "http://192.168.101.246:8123"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzZmQ1ZDI1NGZhNTA0NTRhOTRhZDRjYzYyZGU5MWVkYyIsImlhdCI6MTc0MTY5NjI0NywiZXhwIjoyMDU3MDU2MjQ3fQ.dIc5ebY-FBbCApzPNKcfUweKxpdoKIx9EddOdGmbEV8"

def call_scene(scene_entity):
    """
    调用 Home Assistant API 触发指定场景
    """
    url = HA_URL + "/api/services/scene/turn_on"
    headers = {
        "Authorization": "Bearer " + API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {"entity_id": scene_entity}
    try:
        response = urequests.post(url, headers=headers, data=ujson.dumps(payload))
        print("状态码:", response.status_code)
#         print("响应内容:", response.text)
        response.close()
    except Exception as e:
        print("调用场景时发生异常:", str(e))

def start_movie_mode():
    call_scene("scene.kai_qi_guan_ying")

def stop_movie_mode():
    call_scene("scene.wan_cheng_guan_ying")

# 测试代码
if __name__ == "__main__":
#     print("开启观影模式：")
#     start_movie_mode()
    
    print("关闭观影模式：")
    stop_movie_mode()
