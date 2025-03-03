from machine import I2S, Pin
import time
import uos

# 配置I2S引脚
sck_pin = Pin(4)  # 串行时钟
ws_pin = Pin(5)   # 字选择
sd_pin = Pin(6)   # 串行数据

# 音频参数配置
sampleRate = 16000       # 采样率：16kHz
bitsPerSample = 16       # 位深度：16-bit
num_channels = 1         # 声道数：单声道
bufSize = 4096           # 缓冲区大小：4KB
file_duration = 5        # 录音时长：5秒

def create_wav_header(sample_rate, bits_per_sample, num_channels, data_size):
    """生成WAV文件头"""
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    
    header = bytes()
    header += b'RIFF'
    header += (data_size + 36).to_bytes(4, 'little')  # 文件总大小
    header += b'WAVE'
    header += b'fmt '
    header += (16).to_bytes(4, 'little')             # fmt块大小
    header += (1).to_bytes(2, 'little')              # PCM格式
    header += num_channels.to_bytes(2, 'little')     # 声道数
    header += sample_rate.to_bytes(4, 'little')      # 采样率
    header += byte_rate.to_bytes(4, 'little')        # 字节率
    header += block_align.to_bytes(2, 'little')      # 块对齐
    header += bits_per_sample.to_bytes(2, 'little')  # 位深度
    header += b'data'
    header += data_size.to_bytes(4, 'little')        # 数据大小
    return header

def record_audio(filename, duration):
    """录制音频并保存为WAV文件"""
    # 初始化I2S音频输入
    audioInI2S = I2S(
        0,  # 设备ID
        sck=sck_pin,
        ws=ws_pin,
        sd=sd_pin,
        mode=I2S.RX,
        bits=bitsPerSample,
        format=I2S.MONO if num_channels == 1 else I2S.STEREO,
        rate=sampleRate,
        ibuf=bufSize
    )
    
    # 检查文件是否存在，若存在则删除
    if filename in uos.listdir():
        print(f"删除已存在的文件: {filename}")
        uos.remove(filename)
        time.sleep(0.5)
    
    # 打开文件并写入WAV头
    with open(filename, 'wb') as f:
        # 预计算数据大小
        total_data_size = sampleRate * num_channels * (bitsPerSample // 8) * duration
        header = create_wav_header(sampleRate, bitsPerSample, num_channels, total_data_size)
        f.write(header)
        
        # 开始录音
        print("开始录音...")
        start_time = time.time()
        while time.time() - start_time < duration:
            read_buf = bytearray(bufSize)  # 读取缓冲区
            bytes_read = audioInI2S.readinto(read_buf)
            f.write(read_buf[:bytes_read])  # 写入文件
            print(f"已录制 {bytes_read} 字节")
        
        print("录音结束")
    
    # 关闭I2S设备
    audioInI2S.deinit()

# 测试录音功能
if __name__ == '__main__':
    output_file = '/recording.wav'  # 保存路径
    record_duration = 5  # 录音时长（秒）
    
    print(f"开始录制 {record_duration} 秒音频...")
    record_audio(output_file, record_duration)
    print(f"音频已保存至 {output_file}")
