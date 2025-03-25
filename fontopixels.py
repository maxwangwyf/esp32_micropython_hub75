def font2pixels(character,color):
    character_data = {}
    all_matrix = [[0 for _ in range(64)] for _ in range(64)]  # 初始化 64x64 矩阵
    current_row = 0  # 当前行
    current_col = 0  # 当前列

    for index, char in enumerate(character):
        # 判断字符是否为 ASCII 字符
        if ord(char) < 128:
            # ASCII 字符处理
            try:
                with open("font/asc16", "rb") as asc_file:
                    # ASCII 字符的偏移量计算
                    offset = ord(char) * 16  # 每个 ASCII 字符占 16 字节
                    asc_file.seek(offset)
                    mat = asc_file.read(16)  # 读取 16 字节的点阵数据
                    if len(mat) != 16:
                        print(f"无法读取字符 '{char}' 的点阵数据（数据长度不足）")
                        continue

                    # 显示点阵图形
                    matrix = []
                    for j in range(16):  # 16 行
                        row = []
                        for k in range(8):  # 每行 8 个像素
                            flag = mat[j] & (0x80 >> k)
                            row.append(color if flag else 0)
                        matrix.append(row)
                    character_data[f"char{index + 1}"] = matrix

                    # 将当前字符的点阵数据拼接到总矩阵中
                    char_width = len(matrix[0])  # 字符宽度
                    char_height = len(matrix)     # 字符高度

                    # 检查是否需要换行
                    if current_col + char_width > 64:
                        current_row += char_height  # 换行
                        current_col = 0  # 重置列

                    # 检查是否超出矩阵高度
                    if current_row + char_height > 64:
                        print("矩阵已满，无法继续添加字符。")
                        break

                    # 将字符点阵数据复制到总矩阵中
                    for i in range(char_height):
                        for j in range(char_width):
                            all_matrix[current_row + i][current_col + j] = matrix[i][j]

                    # 更新当前列
                    current_col += char_width
            except FileNotFoundError:
                print("错误: 无法打开 asc16 文件，请确保路径正确且文件存在。")
                return
            except Exception as e:
                print(f"错误: {e}")
                return
        else:
            # 汉字处理
            try:
                incode = char.encode('gb2312')
            except UnicodeEncodeError:
                print(f"字符 '{char}' 不是有效的GB2312字符")
                continue

            if len(incode) != 2:
                print(f"字符 '{char}' 的编码长度不是2")
                continue

            # 获取区位码
            qh = incode[0] - 0xa0
            wh = incode[1] - 0xa0
            offset = (94 * (qh - 1) + (wh - 1)) * 24  # hzk12-->24,hzk14-->28,hzk16-->32

            try:
                with open("font/hzk12", "rb") as hzk_file:
                    hzk_file.seek(offset)
                    mat = hzk_file.read(24)  # 读取 24 字节的点阵数据
                    if len(mat) != 24:
                        print(f"无法读取字符 '{char}' 的点阵数据（数据长度不足）")
                        continue

                    # 显示点阵图形
                    matrix = []
                    for j in range(12):  # 12 行
                        row = []
                        for i in range(2):  # 每行 2 字节
                            for k in range(8):  # 每字节 8 个像素
                                flag = mat[j * 2 + i] & (0x80 >> k)
                                row.append(1 if flag else 0)
                        matrix.append(row)
                    character_data[f"char{index + 1}"] = matrix

                    # 将当前字符的点阵数据拼接到总矩阵中
                    char_width = len(matrix[0])  # 字符宽度
                    char_height = len(matrix)     # 字符高度

                    # 检查是否需要换行
                    if current_col + char_width > 64:
                        current_row += char_height  # 换行
                        current_col = 0  # 重置列

                    # 检查是否超出矩阵高度
                    if current_row + char_height > 64:
                        print("矩阵已满，无法继续添加字符。")
                        break

                    # 将字符点阵数据复制到总矩阵中
                    for i in range(char_height):
                        for j in range(char_width):
                            all_matrix[current_row + i][current_col + j] = matrix[i][j]

                    # 更新当前列
                    current_col += char_width
            except FileNotFoundError:
                print("错误: 无法打开 hzk12 文件，请确保路径正确且文件存在。")
                return
            except Exception as e:
                print(f"错误: {e}")
                return

    return character_data, all_matrix  # 返回字符数据和总矩阵

def savetopy(character_data, all_matrix):
    # 将点阵数据保存到 character_map.py 文件中
    with open("character_map.py", "w", encoding="utf-8") as f:
        f.write("# 自动生成的字符点阵数据\n\n")
        for var_name, matrix in character_data.items():
            f.write(f"{var_name} = [\n")
            for row in matrix:
                f.write(f"    {row},\n")
            f.write("]\n\n")
        f.write("all_matrix = [\n")
        for row in all_matrix:
            f.write(f"    {row},\n")
        f.write("]\n")
        print("点阵数据已保存到 character_map.py 文件中。")

if __name__ == "__main__":
    character_data, all_matrix = font2pixels(" 2025/3\n2")
    if character_data:
        savetopy(character_data, all_matrix)
