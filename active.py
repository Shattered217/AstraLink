from machine import Pin
import uasyncio as asyncio
import time

class TriggerManager:
    def __init__(self, debounce_ms=200):
        self.trigger_count = 0
        self.callbacks = []
        self._trigger_event = asyncio.Event()
        self.active_pin = Pin(7, Pin.IN, Pin.PULL_DOWN)
        self.debounce_ms = debounce_ms
        self._last_trigger = 0
        self.active_pin.irq(trigger=Pin.IRQ_RISING, handler=self._pin_handler)

    def _pin_handler(self, pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_trigger) > self.debounce_ms:
            self.trigger_count += 1
            self._trigger_event.set()
            self._last_trigger = now

    def register_callback(self, callback):
        """注册触发回调函数"""
        self.callbacks.append(callback)

    async def monitor_triggers(self):
        """监控触发事件并执行回调"""
        while True:
            await self._trigger_event.wait()  # 等待事件触发
            print(f"处理触发事件，当前计数：{self.trigger_count}")
            
            # 并行执行所有回调且等待完成
            tasks = [asyncio.create_task(cb()) for cb in self.callbacks]
            await asyncio.gather(*tasks)
            
            self._trigger_event.clear()  # 清除事件标志

# 创建单例实例
trigger_manager = TriggerManager()

# 导出模块接口
register_trigger_callback = trigger_manager.register_callback
monitor_triggers = trigger_manager.monitor_triggers
