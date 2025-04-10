import urequests
import ujson
import uasyncio as asyncio

# 请根据你的 Home Assistant 实例地址进行修改
HA_URL = "http://192.168.101.246:8123"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzZmQ1ZDI1NGZhNTA0NTRhOTRhZDRjYzYyZGU5MWVkYyIsImlhdCI6MTc0MTY5NjI0NywiZXhwIjoyMDU3MDU2MjQ3fQ.dIc5ebY-FBbCApzPNKcfUweKxpdoKIx9EddOdGmbEV8"

async def call_scene(scene_entity):
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

async def ha_action(command):
    """
    根据传入的命令执行相应的动作
    """
    if command == "movie_on":
        print("启动观影模式...")
        await call_scene("scene.kai_qi_guan_ying")  # 调用 perform_action 执行开启观影模式的场景
    elif command == "movie_off":
        print("停止观影模式...")
        await call_scene("scene.wan_cheng_guan_ying")  # 调用 perform_action 执行关闭观影模式的场景
    else:
        print(f"未知的命令: {command}")

# 测试代码
async def test():
    action = "movie_off"  # 可以替换为动态获取的动作
    await ha_action(action)

if __name__ == "__main__":
    asyncio.run(test())

