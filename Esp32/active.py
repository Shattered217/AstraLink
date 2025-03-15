from machine import Pin
import uasyncio as asyncio
import time
from main_simple import handle_trigger_actions

class TriggerManager:
    def __init__(self, pin_number=7, debounce_ms=200):
        self.trigger_count = 0
        self._trigger_event = asyncio.Event()
        self.active_pin = Pin(pin_number, Pin.IN, Pin.PULL_DOWN)
        self.debounce_ms = debounce_ms
        self._last_trigger = 0
        self.active_pin.irq(trigger=Pin.IRQ_RISING, handler=self._pin_handler)

    def _pin_handler(self, pin):
        print("IRQ 触发检测到")  # 调试信息
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_trigger) > self.debounce_ms:
            self.trigger_count += 1
            self._trigger_event.set()
            self._last_trigger = now

    async def process_triggers(self):
        """异步处理触发事件"""
        while True:
            print("等待触发事件...")  # 调试信息
            await self._trigger_event.wait()
            print(f"触发事件 (总计: {self.trigger_count})")

            # 触发 `handle_trigger_actions()` 并捕获异常
            asyncio.create_task(self._safe_handle_trigger())

            self._trigger_event.clear()

    async def _safe_handle_trigger(self):
        global AUDIO_SCK_PIN, AUDIO_WS_PIN, AUDIO_SD_PIN, AUDIO_URL, APK_KEY, SECRET_KEY, SILICON_KEY
        """安全执行 handle_trigger_actions，防止未捕获异常"""
        try:
            await handle_trigger_actions()
        except Exception as e:
            print(f"触发处理失败: {e}")
            
# 单例模式
trigger_manager = TriggerManager()

# 主程序
# async def main():
#     print("启动触发监控任务...")
#     asyncio.create_task(trigger_manager.process_triggers())
#     
#     print("主事件循环运行中...")
#     while True:
#         await asyncio.sleep(1)  # 保持事件循环运行
# 
# if __name__ == '__main__':
#     print("程序启动")
#     asyncio.run(main())
