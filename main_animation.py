import hub75
import matrixdata
from animation import AnimationPlayer
from flame_32_data import frames

ROW_SIZE = 64
COL_SIZE = 64

config = hub75.Hub75SpiConfiguration()
matrix = matrixdata.MatrixData(ROW_SIZE, COL_SIZE)
hub75spi = hub75.Hub75Spi(matrix, config)

flame_player = AnimationPlayer(matrix, hub75spi, frames, 0, 26)
flame_player.run_loop()
