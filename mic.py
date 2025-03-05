import machine
import uos
import utime

# 配置 I2S 参数
SAMPLE_RATE = 16000  # 采样率，单位：Hz
SAMPLE_SIZE_IN_BITS = 16  # 采样位深度，单位：位
CHANNELS = 1  # 声道数
BUFFER_LENGTH_IN_BYTES = 4096  # 缓冲区长度

# 配置 I2S 引脚
WS_PIN = 4
SCK_PIN = 5
SD_PIN = 6

# 初始化 I2S 对象
i2s = machine.I2S(
    0,
    sck=machine.Pin(SCK_PIN),
    ws=machine.Pin(WS_PIN),
    sd=machine.Pin(SD_PIN),
    mode=machine.I2S.RX,
    bits=SAMPLE_SIZE_IN_BITS,
    format=machine.I2S.MONO if CHANNELS == 1 else machine.I2S.STEREO,
    rate=SAMPLE_RATE,
    ibuf=BUFFER_LENGTH_IN_BYTES
)

# 定义 WAV 文件头生成函数
def generate_wav_header(sample_rate, sample_size_in_bits, channels, num_samples):
    file_size = 36 + num_samples * channels * (sample_size_in_bits // 8)
    header = bytearray()

    # 构建 RIFF 块
    header.extend(b'RIFF')
    header.extend(file_size.to_bytes(4, 'little'))
    header.extend(b'WAVE')

    # 构建 fmt 子块
    header.extend(b'fmt ')
    header.extend(16 .to_bytes(4, 'little'))  # 子块 1 大小
    header.extend(1 .to_bytes(2, 'little'))  # 音频格式（PCM = 1）
    header.extend(channels.to_bytes(2, 'little'))
    header.extend(sample_rate.to_bytes(4, 'little'))
    byte_rate = sample_rate * channels * (sample_size_in_bits // 8)
    header.extend(byte_rate.to_bytes(4, 'little'))
    block_align = channels * (sample_size_in_bits // 8)
    header.extend(block_align.to_bytes(2, 'little'))
    header.extend(sample_size_in_bits.to_bytes(2, 'little'))

    # 构建 data 子块
    header.extend(b'data')
    data_size = num_samples * channels * (sample_size_in_bits // 8)
    header.extend(data_size.to_bytes(4, 'little'))

    return header

# 录音函数
def record_audio(duration, filename):
    num_samples = SAMPLE_RATE * duration
    buffer = bytearray(BUFFER_LENGTH_IN_BYTES)
    samples_written = 0

    # 生成 WAV 文件头
    header = generate_wav_header(SAMPLE_RATE, SAMPLE_SIZE_IN_BITS, CHANNELS, num_samples)

    # 打开文件以写入模式
    with open(filename, 'wb') as f:
        # 写入 WAV 文件头
        f.write(header)

        start_time = utime.ticks_ms()
        while samples_written < num_samples * (SAMPLE_SIZE_IN_BITS // 8):
            num_read = i2s.readinto(buffer)
            if num_read > 0:
                f.write(buffer[:num_read])
                samples_written += num_read
            elapsed_time = utime.ticks_diff(utime.ticks_ms(), start_time)
            if elapsed_time >= duration * 1000:
                break

    print(f"录音完成，文件已保存为 {filename}")

# 录音时长（秒）
RECORD_DURATION = 10
# 保存的文件名
RECORD_FILENAME = "recording.wav"

# 开始录音
record_audio(RECORD_DURATION, RECORD_FILENAME)

# 关闭 I2S 接口
i2s.deinit()
