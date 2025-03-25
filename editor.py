#这是前端程序
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import importlib.util
import sys
import numpy as np  # 使用 numpy 优化矩阵操作
from ampy.pyboard import Pyboard
from ampy.files import Files
import serial
import imgto3bit1 as it3
from fontopixels import font2pixels


class DotMatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("64x64 Dot Matrix")
        self.pixels = np.zeros((64, 64), dtype=int)  # 使用 numpy 数组
        self.history = []
        self.history_max = 10  # 限制历史记录深度

        self.colors = {
            "黑色": 0,
            "绿色": 1,
            "蓝色": 2,
            "青色": 3,
            "红色": 4,
            "黄色": 5,
            "洋红色": 6,
            "白色": 7,
        }
        self.color_hex_map = {
            0: "#1E1E1E",
            1: "#00FF00",
            2: "#0000FF",
            3: "#00FFFF",
            4: "#FF0000",
            5: "#FFFF00",
            6: "#F700F3",
            7: "#FFFFFF",
        }

        self.canvas = tk.Canvas(root, width=640, height=640, bg='black')
        self.canvas.pack()
        self.history.append(self.pixels.copy())
        self.draw_matrix()

        self.create_buttons()
        self.create_color_buttons()

        self.current_color = 0
        self.is_drawing = False
        self.has_changes = False
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_with_color)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        # 新增变量
        self.selection_start = None  # 框选起始位置 (x, y)
        self.selection_end = None  # 框选结束位置 (x, y)
        self.selected_area = None  # 存储选中的区域 (top, bottom, left, right)
        self.is_selecting = False  # 是否正在框选

        # 绑定右键事件
        self.canvas.bind("<Button-3>", self.start_selection)
        self.canvas.bind("<B3-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-3>", self.end_selection)

        # 绑定键盘事件
        self.root.bind("<Up>", self.move_selection)
        self.root.bind("<Down>", self.move_selection)
        self.root.bind("<Left>", self.move_selection)
        self.root.bind("<Right>", self.move_selection)

    def start_selection(self, event):
        """右键按下，开始框选"""
        self.is_selecting = True
        # 限制起始坐标在画布范围内
        x = max(0, min(event.x // 10, 63))
        y = max(0, min(event.y // 10, 63))
        self.selection_start = (x, y)
        self.selection_end = None
        # 删除旧的框选框线
        self.canvas.delete("selection")  # 清除之前的框选框线
        # 创建一个新的矩形框选区域
        self.selection_rect = self.canvas.create_rectangle(
            x * 10, y * 10, (x + 1) * 10, (y + 1) * 10,
            outline="yellow", tags="selection"
        )

    def update_selection(self, event):
        """右键拖动，更新框选区域"""
        if self.is_selecting:
            # 限制结束坐标在画布范围内
            x = max(0, min(event.x // 10, 63))
            y = max(0, min(event.y // 10, 63))
            self.selection_end = (x, y)
            # 更新矩形框选区域
            x1, y1 = self.selection_start
            # 删除旧的框选框线
            self.canvas.delete("selection")  # 清除之前的框选框线
            # 绘制新的框选框线
            self.selection_rect = self.canvas.create_rectangle(
                min(x1, x) * 10, min(y1, y) * 10,
                (max(x1, x) + 1) * 10, (max(y1, y) + 1) * 10,
                outline="yellow", tags="selection"
            )

    def end_selection(self, event):
        """右键释放，结束框选"""
        if self.is_selecting:
            self.is_selecting = False
            if self.selection_start and self.selection_end:
                # 计算选中的区域，并确保坐标在画布范围内
                x1, y1 = self.selection_start
                x2, y2 = self.selection_end
                self.selected_area = (
                    max(0, min(y1, y2)), min(63, max(y1, y2)),  # top, bottom
                    max(0, min(x1, x2)), min(63, max(x1, x2))  # left, right
                )
                #print(f"框选区域: 左上角=({self.selected_area[2]}, {self.selected_area[0]}), 右下角=({self.selected_area[3]}, {self.selected_area[1]})")

  
    def move_selection(self, event):
        if not self.selected_area:
            return

        top, bottom, left, right = self.selected_area
        height = bottom - top + 1
        width = right - left + 1

        # 计算移动方向
        delta_x, delta_y = 0, 0
        if event.keysym == "Up":
            delta_y = -1
        elif event.keysym == "Down":
            delta_y = 1
        elif event.keysym == "Left":
            delta_x = -1
        elif event.keysym == "Right":
            delta_x = 1

        # 检查边界
        new_top = top + delta_y
        new_bottom = bottom + delta_y
        new_left = left + delta_x
        new_right = right + delta_x

        if new_top < 0 or new_bottom >= 64 or new_left < 0 or new_right >= 64:
            return

        # 提取选中区域数据
        selected_pixels = self.pixels[top:bottom + 1, left:right + 1].copy()

        # --- 关键修改：直接操作像素数组和画布，不使用标签 ---
        # 清除旧位置的像素数据并更新画布
        self.pixels[top:bottom + 1, left:right + 1] = 0  # 旧位置置零
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                self.canvas.create_rectangle(
                    x * 10, y * 10, (x + 1) * 10, (y + 1) * 10,
                    fill=self.color_hex_map[0], outline="gray"  # 背景色覆盖
                )

        # 将数据写入新位置并更新画布
        self.pixels[new_top:new_top + height, new_left:new_left + width] = selected_pixels
        for y in range(height):
            for x in range(width):
                color = selected_pixels[y][x]
                self.canvas.create_rectangle(
                    (new_left + x) * 10, (new_top + y) * 10,
                    (new_left + x + 1) * 10, (new_top + y + 1) * 10,
                    fill=self.color_hex_map[color], outline="gray"  # 直接绘制新颜色
                )

        # 更新选中区域
        self.selected_area = (new_top, new_bottom, new_left, new_right)

        # 更新历史记录
        if len(self.history) >= self.history_max:
            self.history.pop(0)
        self.history.append(self.pixels.copy())

    def create_buttons(self):
        buttons = [
            ("保存为PY", self.save_as_py),
            ("读取PY", self.load_from_py),
            ("清除", self.clear_canvas),
            ("撤销", self.undo),
            ("图片转PY", self.imgto3bit),
            ("字符", self.font_pixels),
            ("发送到esp32", self.send2esp)
        ]
        for text, command in buttons:
            tk.Button(self.root, text=text, command=command).pack(side="left", padx=5, pady=5)

    def create_color_buttons(self):
        for color_name, color_num in self.colors.items():
            tk.Button(self.root, text=color_name, bg=self.color_hex_map[color_num],
                      command=lambda c=color_num: self.set_current_color(c)).pack(side="left", padx=5, pady=5)

    def send2esp(self):
        file_path = "map.py"
        if file_path:
            # 获取有效矩阵
            effective_matrix = self.get_effective_matrix()
            # 获取有效矩阵的起始位置
            top, bottom, left, right = self.calculate_effective_bounds()
            start_x, start_y = left, top  # 记录起始位置
            # 保存矩阵和起始位置到文件
            with open(file_path, 'w') as py_file:
                py_file.write(f'xy = [{start_x},{start_y}]\n')
                py_file.write('pixel = [\n')
                for i, row in enumerate(effective_matrix):
                    py_file.write('    ' + str(row.tolist()))  # 将 numpy 数组转换为列表
                    if i < len(effective_matrix) - 1:
                        py_file.write(',\n')
                    else:
                        py_file.write('\n')
                py_file.write(']\n')

        port = 'COM6'  # Windows
        board = Pyboard(port)
        files = Files(board)
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        files.put(file_path, file_content)
        print(f" {file_path} 文件已上传.")
        board.close()

        baudrate = 115200
        with serial.Serial(port, baudrate, timeout=0) as ser:
            command = "import main; main.set_restart_flag()\r\n"
            ser.write(command.encode('utf-8'))
            ser.flush()

    def font_pixels(self):
        user_input = simpledialog.askstring("输入", "请输入文本:", parent=self.root)
        if user_input:
            _, result = font2pixels(user_input,self.current_color)
            self.update_pixels(result)

    def draw_matrix(self):
        self.canvas.delete("all")
        for x in range(64):
            for y in range(64):
                color_num = self.pixels[y][x]
                color_hex = self.color_hex_map.get(color_num, "black")
                self.canvas.create_rectangle(x * 10, y * 10, (x + 1) * 10, (y + 1) * 10, fill=color_hex, outline="gray")

    def start_drawing(self, event):
        self.is_drawing = True
        x, y = event.x // 10, event.y // 10
        if 0 <= x < 64 and 0 <= y < 64:
            self.set_pixel_color(x, y, self.current_color)

    def imgto3bit(self):
        image_path = filedialog.askopenfilename(title="选择图片", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not image_path:
            messagebox.showerror("错误", "未选择任何图片")
            return

        try:
            configs = it3.Configs()
            img_matrix = it3.ConvertImage(image_path, configs)
            self.pixels = np.array(img_matrix)  # 转换为 numpy 数组
            self.draw_matrix()
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {e}")

    def draw_with_color(self, event):
        if self.is_drawing:
            x, y = event.x // 10, event.y // 10
            if 0 <= x < 64 and 0 <= y < 64:
                if hasattr(self, 'last_x') and hasattr(self, 'last_y'):
                    self.bresenham_line(self.last_x, self.last_y, x, y, self.current_color)
                else:
                    self.set_pixel_color(x, y, self.current_color)
                self.last_x, self.last_y = x, y

    def bresenham_line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx, sy = 1 if x0 < x1 else -1, 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set_pixel_color(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def stop_drawing(self, event):
        self.is_drawing = False
        if hasattr(self, 'last_x'):
            del self.last_x
        if hasattr(self, 'last_y'):
            del self.last_y
        if self.has_changes:
            self.history.append(self.pixels.copy())
            self.has_changes = False

    def set_pixel_color(self, x, y, color_num):
        if self.pixels[y][x] != color_num:
            self.pixels[y][x] = color_num
            self.has_changes = True
            color_hex = self.color_hex_map.get(color_num, "black")
            self.canvas.create_rectangle(x * 10, y * 10, (x + 1) * 10, (y + 1) * 10, fill=color_hex, outline="gray")

    def set_current_color(self, color_num):
        self.current_color = color_num

    def clear_canvas(self):
        self.history.clear()
        self.pixels = np.zeros((64, 64), dtype=int)  # 重置为全零矩阵
        self.history.append(self.pixels.copy())
        self.draw_matrix()

    def undo(self):
        if len(self.history) > 1:
            self.history.pop()
            self.pixels = self.history[-1].copy()
            self.draw_matrix()
        else:
            messagebox.showinfo("Info", "没有更多可撤销的操作！")

    def save_as_py(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            # 获取有效矩阵
            effective_matrix = self.get_effective_matrix()
            # 获取有效矩阵的起始位置
            top, bottom, left, right = self.calculate_effective_bounds()
            start_x, start_y = left, top  # 记录起始位置

            # 保存矩阵和起始位置到文件
            with open(file_path, 'w') as py_file:
                py_file.write(f'xy = [{start_x},{start_y}]\n')
                py_file.write('pixel = [\n')
                for i, row in enumerate(effective_matrix):
                    py_file.write('    ' + str(row.tolist()))  # 将 numpy 数组转换为列表
                    if i < len(effective_matrix) - 1:
                        py_file.write(',\n')
                    else:
                        py_file.write('\n')
                py_file.write(']\n')
            messagebox.showinfo("Info", "保存成功！")

    def get_effective_matrix(self):
        top, bottom, left, right = self.calculate_effective_bounds()
        return self.pixels[top:bottom + 1, left:right + 1]

    def calculate_effective_bounds(self):
        # 找到矩阵的有效区域
        rows = np.any(self.pixels != 0, axis=1)
        cols = np.any(self.pixels != 0, axis=0)
        if not np.any(rows) or not np.any(cols):
            return 0, 63, 0, 63  # 如果没有有效区域，返回整个矩阵

        top = np.where(rows)[0][0]
        bottom = np.where(rows)[0][-1]
        left = np.where(cols)[0][0]
        right = np.where(cols)[0][-1]
        return top, bottom, left, right

    def load_from_py(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file_path:
            try:
                # 动态加载 Python 文件
                module_name = "pixel_data"
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None:
                    messagebox.showerror("Error", "无法加载文件")
                    return
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                # 检查是否包含 pixel 变量和起始位置
                if hasattr(module, 'pixel') and hasattr(module, 'xy'):
                    pixel_data = module.pixel
                    xy = module.xy

                    if isinstance(pixel_data, list) and all(isinstance(row, list) for row in pixel_data):
                        # 清空当前画布
                        self.clear_canvas()
                        # 将加载的矩阵放置到 (start_x, start_y) 位置
                        for y, row in enumerate(pixel_data):
                            for x, value in enumerate(row):
                                target_x = xy[0] + x
                                target_y = xy[1] + y
                                if 0 <= target_x < 64 and 0 <= target_y < 64:  # 确保坐标在范围内
                                    self.pixels[target_y][target_x] = value

                        # 更新历史记录并重新绘制
                        self.history.append(self.pixels.copy())
                        self.draw_matrix()
                    else:
                        messagebox.showerror("Error", "文件中的 'pixel' 列表格式不正确")
                else:
                    messagebox.showerror("Error", "文件中未找到 'pixel' 列表或起始位置")
            except Exception as e:
                messagebox.showerror("Error", f"加载失败: {str(e)}")

    def update_pixels(self, pixel_data):
        self.pixels = np.array(pixel_data)  # 转换为 numpy 数组
        self.history.append(self.pixels.copy())
        self.draw_matrix()


if __name__ == "__main__":
    root = tk.Tk()
    app = DotMatrixApp(root)
    root.mainloop()
