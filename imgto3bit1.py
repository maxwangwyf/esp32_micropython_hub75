import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from PIL import Image  # 使用Pillow代替OpenCV

class Configs:
    def __init__(self):
        self.RED_THRESHOLD = 127
        self.GREEN_THRESHOLD = 127
        self.BLUE_THRESHOLD = 127
        self.RED_BIT = 0b100
        self.GREEN_BIT = 0b010
        self.BLUE_BIT = 0b001
        self.MAX_ROW_SIZE = 64
        self.MAX_COL_SIZE = 64
        self.variable_name = "pixel"
        self.output_file = "img_data.py"

def GetReducedImageSize(img, configs):
    """计算保持比例的缩放尺寸"""
    orig_width, orig_height = img.size
    if configs.MAX_ROW_SIZE and configs.MAX_COL_SIZE:
        # 计算缩放比例，保持宽高比
        width_ratio = configs.MAX_COL_SIZE / orig_width
        height_ratio = configs.MAX_ROW_SIZE / orig_height
        ratio = min(width_ratio, height_ratio)
        new_width = int(orig_width * ratio)
        new_height = int(orig_height * ratio)
    elif configs.MAX_ROW_SIZE:
        # 仅限制高度
        ratio = configs.MAX_ROW_SIZE / orig_height
        new_width = int(orig_width * ratio)
        new_height = configs.MAX_ROW_SIZE
    elif configs.MAX_COL_SIZE:
        # 仅限制宽度
        ratio = configs.MAX_COL_SIZE / orig_width
        new_width = configs.MAX_COL_SIZE
        new_height = int(orig_height * ratio)
    else:
        # 不缩放
        new_width, new_height = orig_width, orig_height
    return new_width, new_height

def ConvertImageTo3BitList(img, configs):
    """将图像转换为3位颜色列表"""
    img_array = np.array(img)  # 将Pillow图像转换为NumPy数组
    return ((img_array[:, :, 0] >= configs.RED_THRESHOLD) * configs.RED_BIT |
           (img_array[:, :, 1] >= configs.GREEN_THRESHOLD) * configs.GREEN_BIT |
           (img_array[:, :, 2] >= configs.BLUE_THRESHOLD) * configs.BLUE_BIT)

def FillMatrix(img, target_shape):
    """将图像填充到目标形状"""
    filled_img = np.zeros(target_shape, dtype=np.uint8)
    filled_img[:img.shape[0], :img.shape[1]] = img  # 将原始图像放置在新图像区域
    return filled_img

def PrintImageList(img, out):
    """将图像数据写入文件"""
    out.write(f"{app.configs.variable_name} = [\n")
    for row in img:
        out.write("    [" + ", ".join(map(str, row)) + "],\n")
    out.write("]\n")

def ConvertImage(image, configs):
    """使用Pillow加载和处理图像"""
    try:
        img = Image.open(image)  # 使用Pillow打开图像
    except Exception as e:
        raise ValueError(f"无法读取图像: {e}")

    # 计算缩放后的尺寸并调整图像大小
    new_width, new_height = GetReducedImageSize(img, configs)
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)  # 保持比例缩放

    # 将图像转换为3位颜色列表
    img_3bit = ConvertImageTo3BitList(img_resized, configs)

    # 确保填充到目标形状（64x64）
    img_filled = FillMatrix(img_3bit, (configs.MAX_ROW_SIZE, configs.MAX_COL_SIZE))
    print(img_filled)
    return img_filled

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to 3-Bit Converter")
        self.configs = Configs()
        self.image_path = None

        self.select_button = tk.Button(root, text="选择图片", command=self.convert_and_save)
        self.select_button.pack(pady=10)

        self.status_label = tk.Label(root, text="请选择图片")
        self.status_label.pack(pady=10)

 
    def convert_and_save(self):
        self.image_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not self.image_path:
            messagebox.showerror("错误", "请先选择图片！")
            return

        try:
            img_out = ConvertImage(self.image_path, self.configs)
            with open(self.configs.output_file, "w") as out_file:
                PrintImageList(img_out, out_file)
            messagebox.showinfo("成功", f"图片已转换并保存为 {self.configs.output_file}")
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()
