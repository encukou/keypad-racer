import struct

def hex2rgb(s):
    return tuple(i/255 for i in struct.unpack('<3B', bytes.fromhex(s)))

COLORS = (
    hex2rgb('e92d36'),  # apple
    hex2rgb('f09333'),  # firetruck
    hex2rgb('ffff2a'),  # sun
    hex2rgb('96ff32'),  # lime
    hex2rgb('1cc74f'),  # grass
    hex2rgb('4ac1f0'),  # sky
    hex2rgb('2839f1'),  # lake
    hex2rgb('93338f'),  # deep-prism
    hex2rgb('e9468d'),  # love
)

class Palette:
    def player_color(self, i):
        return COLORS[i % len(COLORS)]
