from machine import Pin, SoftSPI, freq
from time import sleep_us

#freq(160000000)  # default NodeMCU ESP-32S v1.1
freq(240000000)
class Hub75SpiConfiguration:
    def __init__(self):
        self.spi_baud_rate = 20000000
        self.illumination_time_microseconds = 10  # 基准显示时间（微秒）
        
        # 行选择引脚配置（32扫需要5个引脚）
        self.line_select_a_pin_number = 23
        self.line_select_b_pin_number = 19
        self.line_select_c_pin_number = 5
        self.line_select_d_pin_number = 17
        self.line_select_e_pin_number = 18
        
        # 数据引脚配置
        self.red1_pin_number = 25
        self.blue1_pin_number = 27
        self.green1_pin_number = 26
        self.red2_pin_number = 14
        self.blue2_pin_number = 13
        self.green2_pin_number = 12
        
        # 控制引脚
        self.clock_pin_number = 16
        self.latch_pin_number = 4
        self.output_enable_pin_number = 15
        self.spi_miso_pin_number = 35


class Hub75Spi:
    '''
    HUB75 RGB LED matrix communication.
    '''
    def __init__(self, matrix_data, config):
        '''
        Parameters
        ----------
        matrix_data : MatrixData object
        config : Hub75SpiConfiguration
            Pin configuration.
        '''
        self.config = config
        self.matrix_data = matrix_data
        self.half_row_size = matrix_data.row_size // 2

        self.latch_pin = Pin(config.latch_pin_number, Pin.OUT)
        self.output_enable_pin = Pin(config.output_enable_pin_number, Pin.OUT)
        self.line_select_a_pin = Pin(config.line_select_a_pin_number, Pin.OUT)
        self.line_select_b_pin = Pin(config.line_select_b_pin_number, Pin.OUT)
        self.line_select_c_pin = Pin(config.line_select_c_pin_number, Pin.OUT)
        self.line_select_d_pin = Pin(config.line_select_d_pin_number, Pin.OUT)
        self.line_select_e_pin = Pin(config.line_select_e_pin_number, Pin.OUT)

        self.line_select_a_pin.off()
        self.line_select_b_pin.off()
        self.line_select_c_pin.off()
        self.line_select_d_pin.off()
        self.line_select_e_pin.off()

        self.red1_mosi_pin = Pin(config.red1_pin_number)
        self.red2_mosi_pin = Pin(config.red2_pin_number)
        self.green1_mosi_pin = Pin(config.green1_pin_number)
        self.green2_mosi_pin = Pin(config.green2_pin_number)
        self.blue1_mosi_pin = Pin(config.blue1_pin_number)
        self.blue2_mosi_pin = Pin(config.blue2_pin_number)

        self.red1_spi = SoftSPI(baudrate=config.spi_baud_rate, polarity=1, phase=0, sck=Pin(config.clock_pin_number), mosi=self.red1_mosi_pin, miso=Pin(config.spi_miso_pin_number))
        self.red2_spi = SoftSPI(baudrate=config.spi_baud_rate, polarity=1, phase=0, sck=Pin(config.clock_pin_number), mosi=self.red2_mosi_pin, miso=Pin(config.spi_miso_pin_number))
        self.green1_spi = SoftSPI(baudrate=config.spi_baud_rate, polarity=1, phase=0, sck=Pin(config.clock_pin_number), mosi=self.green1_mosi_pin, miso=Pin(config.spi_miso_pin_number))
        self.green2_spi = SoftSPI(baudrate=config.spi_baud_rate, polarity=1, phase=0, sck=Pin(config.clock_pin_number), mosi=self.green2_mosi_pin, miso=Pin(config.spi_miso_pin_number))
        self.blue1_spi = SoftSPI(baudrate=config.spi_baud_rate, polarity=1, phase=0, sck=Pin(config.clock_pin_number), mosi=self.blue1_mosi_pin, miso=Pin(config.spi_miso_pin_number))
        self.blue2_spi = SoftSPI(baudrate=config.spi_baud_rate, polarity=1, phase=0, sck=Pin(config.clock_pin_number), mosi=self.blue2_mosi_pin, miso=Pin(config.spi_miso_pin_number))

    def set_row_select(self, row):
        '''
        Set data for row select pins.

        Parameters
        ----------
        row : int
            current row for serial color data.

        Returns
        -------
        None.
        '''
        self.line_select_a_pin.value(row & 1)
        self.line_select_b_pin.value(row & 2)
        self.line_select_c_pin.value(row & 4)
        self.line_select_d_pin.value(row & 8)
        self.line_select_e_pin.value(row & 16)

    def display_top_half(self):
        '''
        Write top half of display, see display_data().

        Returns
        -------
        None.
        '''
        for row in range(self.half_row_size):
            # shift in data
            row_data = self.matrix_data.red_matrix_data[row]
            self.red1_spi.write(row_data)
            self.red1_mosi_pin.off()
            self.output_enable_pin.on() # disable

            self.set_row_select(row)

            self.latch_pin.on()
            self.latch_pin.off()
            self.output_enable_pin.off() # enable
            sleep_us(self.config.illumination_time_microseconds)

            # shift in data
            row_data = self.matrix_data.green_matrix_data[row]
            self.green1_spi.write(row_data)
            self.green1_mosi_pin.off()
            self.output_enable_pin.on() # disable
            self.latch_pin.on()
            self.latch_pin.off()
            self.output_enable_pin.off() # enable
            sleep_us(self.config.illumination_time_microseconds)

            # shift in data
            row_data = self.matrix_data.blue_matrix_data[row]
            self.blue1_spi.write(row_data)
            self.blue1_mosi_pin.off()
            self.output_enable_pin.on() # disable
            self.latch_pin.on()
            self.latch_pin.off()
            self.output_enable_pin.off() # enable
            sleep_us(self.config.illumination_time_microseconds)

    def display_bottom_half(self):
        '''
        Write bottom half of display, see display_data().

        Returns
        -------
        None.
        '''
        for row in range(self.half_row_size, self.matrix_data.row_size):
            # shift in data
            row_data = self.matrix_data.red_matrix_data[row]
            self.red2_spi.write(row_data)
            self.red2_mosi_pin.off()
            self.output_enable_pin.on() # disable

            self.set_row_select(row % self.half_row_size)

            self.latch_pin.on()
            self.latch_pin.off()
            self.output_enable_pin.off() # enable
            sleep_us(self.config.illumination_time_microseconds)

            row_data = self.matrix_data.green_matrix_data[row]
            self.green2_spi.write(row_data)
            self.green2_mosi_pin.off()
            self.output_enable_pin.on() # disable
            self.latch_pin.on()
            self.latch_pin.off()
            self.output_enable_pin.off() # enable
            sleep_us(self.config.illumination_time_microseconds)

            row_data = self.matrix_data.blue_matrix_data[row]
            self.blue2_spi.write(row_data)
            self.blue2_mosi_pin.off()
            self.output_enable_pin.on() # disable
            self.latch_pin.on()
            self.latch_pin.off()
            self.output_enable_pin.off() # enable
            sleep_us(self.config.illumination_time_microseconds)

        # flush out last blue line
        self.blue2_spi.write(bytearray(self.matrix_data.col_bytes))
        self.output_enable_pin.on()
        self.latch_pin.on()
        self.latch_pin.off()

    def display_data(self):
        '''
        Write pixel data to LED matrix.

        Returns
        -------
        None.
        '''
        self.display_top_half()
        self.display_bottom_half()
