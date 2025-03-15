import ujson as json

def load_config(filename="config.json"):
    """加载 JSON 配置文件"""
    try:
        with open(filename, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return None 