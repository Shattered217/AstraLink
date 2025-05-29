# active.py
from machine import UART, Pin
import uasyncio as asyncio
import time

class TriggerManager:
    def __init__(self, handler, uart_num=1, baudrate=9600, rx_pin=9):
        self.uart = UART(uart_num, baudrate=baudrate)
        self.uart.init(rx=Pin(rx_pin), timeout=20)
        self._trigger_event = asyncio.Event()
        self.debounce_ms = 500
        self._last_trigger = 0
        self.handler = handler
        asyncio.create_task(self._uart_listener())

    async def _uart_listener(self):
        buffer = b''
        while True:
            while self.uart.any() > 0:
                buffer += self.uart.read(1)
                try:
                    message = buffer.decode('utf-8')
                    if '\n' in message:
                        line, rest = message.split('\n', 1)
                        await self._process_command(line.strip())
                        buffer = rest.encode('utf-8')  # 把剩下的部分重新转为 bytes
                except UnicodeError:
                    buffer = b''
            await asyncio.sleep_ms(10)

    async def _process_command(self, cmd):
        if cmd == "TRIGGER":
            now = time.ticks_ms()
            if time.ticks_diff(now, self._last_trigger) > self.debounce_ms:
                self._last_trigger = now
                self._trigger_event.set()
                print("收到有效触发指令")

    async def process_triggers(self):
        while True:
            await self._trigger_event.wait()
            try:
                await self.handler()
            except Exception as e:
                print(f"触发处理链错误: {e}")
            finally:
                self._trigger_event.clear()
