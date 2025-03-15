#!/bin/bash
# 激活虚拟环境
source /home/Shattered/AstraLink/AstraLink/bin/activate

# 启动 main.py 和 display.py
python /home/Shattered/AstraLink/mood.py &
python /home/Shattered/AstraLink/display.py &
