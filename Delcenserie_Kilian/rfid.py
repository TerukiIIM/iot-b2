import time
from machine import Pin, SPI
from mfrc522 import MFRC522
import random

spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
rfid1 = MFRC522(spi, Pin(5), Pin(7))  # Lecteur 1
rfid2 = MFRC522(spi, Pin(6), Pin(8))  # Lecteur 2

def scan_rfid(reader):
    """Lit un badge RFID."""
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.anticoll()
        if stat == reader.OK:
            return "-".join([str(i) for i in uid])
    return None
