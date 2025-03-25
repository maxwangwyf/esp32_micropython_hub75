import hub75
import matrixdata
from map import pixel,xy

# 全局变量，控制是否重新运行
restart_flag = False
# 设置重启标志
def set_restart_flag():
    global restart_flag
    restart_flag = True

def start():
    global restart_flag
    config = hub75.Hub75SpiConfiguration()
    matrix = matrixdata.MatrixData(64, 64)
    hub75spi = hub75.Hub75Spi(matrix, config)
    matrix.set_pixels(xy[1], xy[0], pixel)
    while True:
        hub75spi.display_data()
        # 检查是否需要重新运行
        if restart_flag:
            print("Restarting start() function...")
            restart_flag = False
            break  # 退出循环，重新运行 start() 函数

# 调用 start 函数
start()
