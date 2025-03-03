from machine import I2S, Pin

# 配置I2S音频接口参数
sck_pin = Pin(4)  # SCK接4
ws_pin = Pin(5)   # WS接5
sd_pin = Pin(6)   # SD接6

# 初始化I2S输入（麦克风）
audio_in = I2S(
    0,  # 设备ID，0代表第一个I2S设备
    sck=sck_pin,
    ws=ws_pin,
    sd=sd_pin,
    mode=I2S.RX,
    bits=16,
    format=I2S.MONO,
    rate=16000,  # 可根据需要调整采样率
    ibuf=20000   # 输入缓冲区大小
)

# 录制一些音频数据，并逐块处理
def record_audio(seconds):
    chunk_size = 32000  # 每次读取的数据块大小
    total_samples = seconds * 16000  # 总样本数，假设采样率为16kHz
    recorded_bytes = 0
    
    print("开始录音...")
    
    while recorded_bytes < total_samples * 2:  # 每个样本占2字节
        buf = bytearray(chunk_size)
        audio_in.readinto(buf)
        recorded_bytes += len(buf)
        
        # 在这里处理每一块数据，例如打印数据长度或保存到文件
        print("已录制 {} 字节".format(recorded_bytes))
        
        # 如果你想保存录音数据，可以在这里写入文件
        # with open('recording.raw', 'ab') as f:
        #     f.write(buf)
    
    print("录音结束")

# 示例：录制并检查音频数据
try:
    record_audio(3)  # 录制3秒的音频
except MemoryError as e:
    print("内存不足:", e)

# 清理资源
audio_in.deinit()