from machine import Pin
import uasyncio as asyncio

active_triggered = False
i = 1

active_pin = Pin(7, Pin.IN, Pin.PULL_DOWN)

def pin_handler(pin):
    global i, active_triggered
    i += 1
    print("唤醒已触发{}次".format(i))
    active_triggered = True

async def active_way():
    global active_triggered
    # 中断，监听上升沿
    active_pin.irq(trigger=Pin.IRQ_RISING, handler=pin_handler)

    while True:
        await asyncio.sleep(0.1) 
        if active_triggered:
            print("触发了{}次".format(i))
    #        active_triggered = False

