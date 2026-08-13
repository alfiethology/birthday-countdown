from machine import Pin, I2C
from time import sleep_ms

# ------------------------------------------------------------
# Raspberry Pi Pico 2 + DFRobot I2C LCD1602
#
# Wiring:
# LCD VCC -> Pico VBUS / 5V
# LCD GND -> Pico GND
# LCD SDA -> Pico GP4
# LCD SCL -> Pico GP5
# ------------------------------------------------------------

# I2C setup
i2c = I2C(
    0,
    sda=Pin(4),
    scl=Pin(5),
    freq=100000
)

# DFRobot LCD1602 default address
LCD_ADDR = 0x20

# PCF8574 bit mapping commonly used by this DFRobot module
LCD_RS = 0x01
LCD_RW = 0x02
LCD_EN = 0x04
LCD_BACKLIGHT = 0x08

# LCD commands
LCD_CLEAR = 0x01
LCD_HOME = 0x02
LCD_ENTRY_MODE = 0x04
LCD_DISPLAY_CONTROL = 0x08
LCD_FUNCTION_SET = 0x20
LCD_SET_DDRAM = 0x80


class LCD1602:

    def __init__(self, i2c, address=0x20):
        self.i2c = i2c
        self.address = address
        self.backlight = LCD_BACKLIGHT

        sleep_ms(50)

        # HD44780 4-bit initialization sequence
        self._write4(0x30)
        sleep_ms(5)

        self._write4(0x30)
        sleep_ms(1)

        self._write4(0x30)
        sleep_ms(1)

        self._write4(0x20)
        sleep_ms(1)

        # 4-bit mode, 2 lines, 5x8 font
        self.command(LCD_FUNCTION_SET | 0x08)

        # Display on, cursor off, blink off
        self.command(LCD_DISPLAY_CONTROL | 0x04)

        self.clear()

        # Entry mode: increment cursor
        self.command(LCD_ENTRY_MODE | 0x02)

    def _write_raw(self, value):
        self.i2c.writeto(
            self.address,
            bytes([value | self.backlight])
        )

    def _pulse_enable(self, value):
        self._write_raw(value | LCD_EN)
        sleep_ms(1)

        self._write_raw(value & ~LCD_EN)
        sleep_ms(1)

    def _write4(self, value):
        self._write_raw(value)
        self._pulse_enable(value)

    def _send(self, value, mode=0):
        high = (value & 0xF0) | mode
        low = ((value << 4) & 0xF0) | mode

        self._write4(high)
        self._write4(low)

    def command(self, command):
        self._send(command, 0)

    def write_char(self, char):
        self._send(ord(char), LCD_RS)

    def write(self, text):
        for char in str(text):
            self.write_char(char)

    def clear(self):
        self.command(LCD_CLEAR)
        sleep_ms(2)

    def home(self):
        self.command(LCD_HOME)
        sleep_ms(2)

    def set_cursor(self, column, row):
        # LCD1602 DDRAM row offsets
        row_offsets = [0x00, 0x40]

        if row > 1:
            row = 1

        if column > 15:
            column = 15

        self.command(
            LCD_SET_DDRAM |
            (column + row_offsets[row])
        )

    def backlight_on(self):
        self.backlight = LCD_BACKLIGHT
        self._write_raw(0)

    def backlight_off(self):
        self.backlight = 0
        self._write_raw(0)


# ------------------------------------------------------------
# First scan the I2C bus
# ------------------------------------------------------------

devices = i2c.scan()

print("I2C devices found:")

if not devices:
    print("None")
    print("Check wiring.")
else:
    for device in devices:
        print("  ", hex(device))


# ------------------------------------------------------------
# Start LCD
# ------------------------------------------------------------

if LCD_ADDR not in devices:
    print()
    print("WARNING:")
    print("LCD not detected at", hex(LCD_ADDR))
    print("Detected addresses:", [hex(x) for x in devices])

else:
    print()
    print("LCD detected at", hex(LCD_ADDR))

    lcd = LCD1602(i2c, LCD_ADDR)

    lcd.clear()

    lcd.set_cursor(0, 0)
    lcd.write("ground control")

    lcd.set_cursor(0, 1)
    lcd.write("to major Tom")

    print("Message written to LCD.")
