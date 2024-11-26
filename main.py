import cv2
import numpy as np
import pyautogui
import os
import time
import keyboard  # 导入 keyboard 库
import threading  # 导入 threading 库
from queue import Queue  # 导入队列模块

def get_image_files(image_directory):
    """获取目录中的所有图片文件"""
    return [f for f in os.listdir(image_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

def capture_screenshot():
    """获取固定窗口的截图"""
    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def load_template(image_path):
    """加载模板图像"""
    if os.path.exists(image_path):
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            template = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_UNCHANGED)
            if template is None:
                print(f"无法读取模板: {image_path}")
                return None
            return template
        except Exception as e:
            print(f"读取模板时发生错误: {e}")
            return None
    else:
        print(f"文件不存在: {image_path}")
        return None

def match_template(screenshot, template):
    """进行模板匹配"""
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    return np.where(result >= 0.8)  # 设置匹配阈值

def click_image(image_file, image_directory, screenshot):
    """点击匹配的图片"""
    image_path = os.path.join(image_directory, image_file)
    template = load_template(image_path)

    if template is not None:
        loc = match_template(screenshot, template)

        # 如果找到匹配，模拟点击
        for pt in zip(*loc[::-1]):
            pyautogui.click(pt[0] + template.shape[1] // 2, pt[1] + template.shape[0] // 2)
            print(f"找到目标: {image_file}，进行点击！！！")
            break  # 只点击第一个匹配

def main(max_threads=5):  # 设置最大线程数，默认值为5
    # 设置图片目录
    image_directory = './assets/image'
    
    print("按 'Esc' 键退出程序。")
    
    while True:  # 循环查找和点击
        if keyboard.is_pressed('esc'):  # 检查是否按下 'Esc' 键
            print("程序已退出。")
            break
        
        # 获取目录中的所有图片文件
        image_files = get_image_files(image_directory)
        
        # 获取固定窗口的截图
        screenshot = capture_screenshot()

        threads = []  # 存储线程

        for image_file in image_files:
            # 创建并启动线程
            thread = threading.Thread(target=click_image, args=(image_file, image_directory, screenshot))
            thread.start()
            threads.append(thread)

            # 控制同时运行的线程数
            if len(threads) >= max_threads:
                for thread in threads:
                    thread.join()  # 等待所有线程完成
                threads = []  # 清空线程列表

        # 等待所有剩余线程完成
        for thread in threads:
            thread.join()

        # 等待一段时间后重试
        print("未找到匹配的模板，等待一段时间后重试...")
        time.sleep(0.1)  # 等待0.1秒后重试

if __name__ == "__main__":
    main(max_threads=5)  # 可以在这里调整最大线程数