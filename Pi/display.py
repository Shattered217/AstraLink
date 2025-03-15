import requests
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import os

class GIFPlayer:
    def __init__(self, root):
        self.root = root
        # 设置全屏
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda event: self.root.attributes("-fullscreen", False))  # 按Esc退出全屏
        
        # 设置窗口背景为黑色
        self.root.configure(bg="black")
        
        # 创建标签用于显示GIF
        self.label = tk.Label(root, bg="black")  # 设置标签背景为黑色
        self.label.pack(expand=True, fill=tk.BOTH)  # 让标签填充整个窗口
        
        self.current_mood = None
        self.gif_frames = []  # 当前GIF的帧数据
        self.delays = []      # 当前GIF的帧延迟数据
        self.frame_idx = 0
        self.after_id = None
        
        self.check_interval = 500  # 检查心情间隔（毫秒）
        self.check_mood()

    def check_mood(self):
        """检查当前心情并更新GIF"""
        try:
            response = requests.get('http://localhost:5000/get_mood')
            if response.ok:
                new_mood = response.json()['mood']
                if new_mood != self.current_mood:
                    self.current_mood = new_mood
                    self.load_and_play_gif()
        except Exception as e:
            print(f"Error checking mood: {e}")
        
        self.root.after(self.check_interval, self.check_mood)

    def load_and_play_gif(self):
        """加载并播放当前心情对应的GIF"""
        # 取消正在播放的动画
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        # 释放之前加载的GIF资源
        self.gif_frames.clear()
        self.delays.clear()

        # 加载新GIF
        gif_path = os.path.join("emoji", f"{self.current_mood}.gif")
        if not os.path.exists(gif_path):
            print(f"GIF file not found: {gif_path}")
            return

        try:
            with Image.open(gif_path) as im:
                try:
                    while True:
                        # 保持比例缩放GIF
                        screen_width = self.root.winfo_screenwidth()
                        screen_height = self.root.winfo_screenheight()
                        resized_frame = self._resize_with_aspect_ratio(im.copy(), screen_width, screen_height)
                        frame = ImageTk.PhotoImage(resized_frame)
                        self.gif_frames.append(frame)
                        self.delays.append(im.info.get('duration', 100))
                        im.seek(len(self.gif_frames))
                except EOFError:
                    pass
        except Exception as e:
            print(f"Error loading GIF: {e}")
            return

        # 开始播放
        self.frame_idx = 0
        self.update_frame()

    def _resize_with_aspect_ratio(self, image, target_width, target_height):
        """保持比例缩放图像，并用黑色填充剩余区域"""
        original_width, original_height = image.size
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height

        # 计算缩放后的尺寸
        if original_ratio > target_ratio:
            # 以宽度为准
            new_width = target_width
            new_height = int(target_width / original_ratio)
        else:
            # 以高度为准
            new_height = target_height
            new_width = int(target_height * original_ratio)

        # 缩放图像
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 创建黑色背景图像
        background = Image.new("RGB", (target_width, target_height), "black")
        # 将缩放后的图像居中放置
        offset = ((target_width - new_width) // 2, (target_height - new_height) // 2)
        background.paste(resized_image, offset)

        return background

    def update_frame(self):
        """更新GIF帧"""
        if self.frame_idx < len(self.gif_frames):
            self.label.config(image=self.gif_frames[self.frame_idx])
            self.frame_idx += 1
            self.after_id = self.root.after(
                self.delays[self.frame_idx-1], 
                self.update_frame
            )
        else:
            self.after_id = None

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Emoji Display")
    player = GIFPlayer(root)
    root.mainloop()