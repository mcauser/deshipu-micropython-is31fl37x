import utime


class _Base:
    def __init__(self, i2c, address=80):
        self.address = address
        self.i2c = i2c
        self._i2c_buffer = bytearray(1)
        self._brightness = 0
        self._active = False

    def _page(self, page):
        self.i2c.writeto_mem(self.address, 0xfe, b'\xc5')
        self._i2c_buffer[0] = page
        self.i2c.writeto_mem(self.address, 0xfd, self._i2c_buffer)

    def _config(self, register, value):
        self._page(3)
        self._i2c_buffer[0] = value
        self.i2c.writeto_mem(self.address, register, self._i2c_buffer)

    def active(self, value):
        if value is None:
            return self._active
        self._config(0x00, 0x01 if value else 0x00)
        self._active = bool(value)

    def _pixel(self, x, y, color):
        self._page(1)
        self._i2c_buffer[0] = color
        self.i2c.writeto_mem(self.address, x + y * 8, self._i2c_buffer)

    def brightness(self, value=None):
        if value is None:
            return self._brightness
        if not 0 <= value <= 255:
            raise ValueError()
        self._config(0x01, value)
        self._brightness = value


class Matrix8x8x2(_Base):
    def __init__(self, i2c, address=80):
        super().__init__(i2c, address)
        self.active(1)
        self.brightness(127)
        self._page(0)
        self.i2c.writeto_mem(self.address, 0, b'\xff' * 16 )

    def pixel(self, x, y, color):
        if not (0 <= x <= 7 and 0 <= y <= 7):
            return
        self._pixel(x, y * 2, color & 0xff)
        self._pixel(7 - x, y * 2 + 1, (color >> 8) & 0xff)


class PewPew(Matrix8x8x2):
    def __init__(self, i2c, address=80):
        super().__init__(i2c, address)
        self._page(0)
        self.i2c.writeto_mem(self.address, 0x12, b'\x3f')


class Matrix7x11(_Base):
    _COLS = (0, 5, 1, 6, 4, 2, 3)
    _ROWS = (6, 7, 5, 8, 4, 3, 9, 2, 10, 1, 0)

    def __init__(self, i2c, address=80):
        super().__init__(i2c, address)
        self.active(1)
        self.brightness(127)
        self._page(0)
        self.i2c.writeto_mem(self.address, 0, b'\x55\x15' * 11 )

    def pixel(self, x, y, color):
        if not (0 <= x <= 6 and 0 <= y <= 10):
            return
        self._pixel(self._COLS[x] * 2, self._ROWS[y] * 2, color & 0xff)


class Matrix14x11(_Base):
    _COLS = (8, 4, 9, 2, 7, 3, 5, 0, 6, 1, 11, 13, 10, 12)

    def __init__(self, i2c, address=80):
        super().__init__(i2c, address)
        self.active(1)
        self.brightness(127)
        self._page(0)
        self.i2c.writeto_mem(self.address, 0, b'\xff\x3f' * 11)

    def pixel(self, x, y, color):
        if not (0 <= x <= 13 and 0 <= y <= 10):
            return
        self._pixel(self._COLS[x], 20 - y * 2, color & 0xff)
