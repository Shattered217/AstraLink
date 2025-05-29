import machine
import uos
import utime

class AudioRecorder:
    def __init__(self, sample_rate=16000, sample_size_in_bits=16, channels=1, buffer_length_in_bytes=4096):
        self.SAMPLE_RATE = sample_rate
        self.SAMPLE_SIZE_IN_BITS = sample_size_in_bits
        self.CHANNELS = channels
        self.BUFFER_LENGTH_IN_BYTES = buffer_length_in_bytes

        # 配置 I2S 引脚
        self.WS_PIN = 5
        self.SCK_PIN = 4
        self.SD_PIN = 6

        # 初始化 I2S 对象
        self.i2s = machine.I2S(
            0,
            sck=machine.Pin(self.SCK_PIN),
            ws=machine.Pin(self.WS_PIN),
            sd=machine.Pin(self.SD_PIN),
            mode=machine.I2S.RX,
            bits=self.SAMPLE_SIZE_IN_BITS,
            format=machine.I2S.MONO if self.CHANNELS == 1 else machine.I2S.STEREO,
            rate=self.SAMPLE_RATE,
            ibuf=self.BUFFER_LENGTH_IN_BYTES
        )

    def generate_wav_header(self, sample_rate, sample_size_in_bits, channels, num_samples):
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

    def record_audio(self, duration, filename):
        num_samples = self.SAMPLE_RATE * duration
        buffer = bytearray(self.BUFFER_LENGTH_IN_BYTES)
        samples_written = 0

        # 生成 WAV 文件头
        header = self.generate_wav_header(self.SAMPLE_RATE, self.SAMPLE_SIZE_IN_BITS, self.CHANNELS, num_samples)

        # 打开文件以写入模式
        with open(filename, 'wb') as f:
            # 写入 WAV 文件头
            f.write(header)

            start_time = utime.ticks_ms()
            while samples_written < num_samples * (self.SAMPLE_SIZE_IN_BITS // 8):
                num_read = self.i2s.readinto(buffer)
                if num_read > 0:
                    f.write(buffer[:num_read])
                    samples_written += num_read
                elapsed_time = utime.ticks_diff(utime.ticks_ms(), start_time)
                if elapsed_time >= duration * 1000:
                    break

        print(f"录音完成，文件已保存为 {filename}")

    def deinit(self):
        self.i2s.deinit()

# def main():
# 
#     # 创建 AudioRecorder 实例
#     recorder = AudioRecorder()
# 
#     # 开始录音
#     recorder.record_audio(3, "recording.wav")
# 
#     # 关闭 I2S 接口
#     recorder.deinit()
# 
# if __name__ == "__main__":
#     main()
