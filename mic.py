import time
import uos
from machine import I2S, Pin

# 配置I2S音频接口参数
sck_pin = Pin(4)  # SCK接4
ws_pin = Pin(5)   # WS接5
sd_pin = Pin(6)   # SD接6

# 采样率和每个样本的位数
sampleRate = 8000  # 采样率
bitsPerSample = 16  # 采样位深
num_channels = 1  
bufSize = 32000    # 缓冲区大小，单位字节
file_duration = 5  # 录音时长（秒）

# 创建音频对象，开始录音
audioInI2S = I2S(
    0,  # 设备ID，0代表第一个I2S设备
    sck=sck_pin,
    ws=ws_pin,
    sd=sd_pin,
    mode=I2S.RX,
    bits=bitsPerSample,
    format=I2S.MONO,
    rate=sampleRate,
    ibuf=bufSize
)

# 读取音频数据并写入文件
def createWavHeader(sampleRate, bitsPerSample, num_channels, data_size):
    # WAV文件头的构造，适用于16位深、单通道或立体声
    header = bytearray()
    
    # RIFF头
    header.extend(b'RIFF')
    header.extend((36 + data_size).to_bytes(4, 'little'))  # 总大小 = 36 + 数据大小
    header.extend(b'WAVE')
    
    # fmt块
    header.extend(b'fmt ')
    header.extend((16).to_bytes(4, 'little'))  # fmt块的大小
    header.extend((1).to_bytes(2, 'little'))  # 编码方式 (1为PCM)
    header.extend((num_channels).to_bytes(1, 'little'))  # 声道数
    header.extend((sampleRate).to_bytes(4, 'little'))  # 采样率
    header.extend((sampleRate * num_channels * bitsPerSample // 8).to_bytes(4, 'little'))  # 每秒字节数
    header.extend((num_channels * bitsPerSample // 8).to_bytes(2, 'little'))  # 每个采样的字节数
    header.extend((bitsPerSample).to_bytes(2, 'little'))  # 采样位数
    
    # data块
    header.extend(b'data')
    header.extend((data_size).to_bytes(4, 'little'))  # 数据块大小
    
    return header

# 开始录音并保存音频数据到文件
def record_audio():
    # 创建读取缓冲区
    readBuf = bytearray(bufSize)
    recoder = True
    start_time = time.time()
    
    # 输出文件
    sfile = 's.pcm'
    
    # 检查文件是否存在，存在则删除
    if sfile in uos.listdir():
        print('删除旧文件:', sfile)
        uos.remove(sfile)
        time.sleep(0.5)
    
    fin = open(sfile, 'wb')
    
    # 写入WAV文件头
    head = createWavHeader(sampleRate, bitsPerSample, num_channels, bufSize * file_duration)
    fin.write(head)
    
    print('开始录音...')
    
    while recoder:
        # 读取音频数据
        currByteCount = audioInI2S.readinto(readBuf)
        print('读取字节数:', currByteCount)
        
        # 将读取的数据写入文件
        audio_data = bytearray()
        audio_data.extend(readBuf)
        fin.write(audio_data)
        
        # 检查是否到达设定的录音时长
        if time.time() - start_time >= file_duration:
            recoder = False
    
    fin.close()
    print('录音结束')
    print('准备进行识别')

# 执行录音
try:
    record_audio()
except Exception as e:
    print("录音过程中出错:", e)

# 清理资源
audioInI2S.deinit()

