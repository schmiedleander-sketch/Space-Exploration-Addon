import struct
import zlib
import random

def make_chunk(type, data):
    length = struct.pack('>I', len(data))
    crc = struct.pack('>I', zlib.crc32(type + data) & 0xffffffff)
    return length + type + data + crc

class TextureGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

    def fill_rect(self, x, y, w, h, color):
        for i in range(y, min(y + h, self.height)):
            for j in range(x, min(x + w, self.width)):
                # Add slight noise for texture
                r = max(0, min(255, color[0] + random.randint(-10, 10)))
                g = max(0, min(255, color[1] + random.randint(-10, 10)))
                b = max(0, min(255, color[2] + random.randint(-10, 10)))
                self.pixels[i][j] = (r, g, b)

    def draw_pattern(self, x, y, w, h, color1, color2, vertical=True):
        for i in range(y, min(y + h, self.height)):
            for j in range(x, min(x + w, self.width)):
                choice = color1 if (i if vertical else j) % 2 == 0 else color2
                r = max(0, min(255, choice[0] + random.randint(-5, 5)))
                g = max(0, min(255, choice[1] + random.randint(-5, 5)))
                b = max(0, min(255, choice[2] + random.randint(-5, 5)))
                self.pixels[i][j] = (r, g, b)

    def save(self, filename):
        png_header = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', self.width, self.height, 8, 2, 0, 0, 0)
        ihdr_chunk = make_chunk(b'IHDR', ihdr_data)

        all_rows = b''
        for row in self.pixels:
            row_bytes = b'\x00'
            for p in row:
                row_bytes += struct.pack('BBB', *p)
            all_rows += row_bytes

        idat_data = zlib.compress(all_rows)
        idat_chunk = make_chunk(b'IDAT', idat_data)
        iend_chunk = make_chunk(b'IEND', b'')

        with open(filename, 'wb') as f:
            f.write(png_header + ihdr_chunk + idat_chunk + iend_chunk)

# --- Forest Guardian (128x128) ---
# UVs: head [0,0], body [0,40], body2 [0,70], arms [60,21], [60,58], legs [37,0], [60,0]
fg = TextureGenerator(128, 128)
# Base mossy green
fg.fill_rect(0, 0, 128, 128, (45, 90, 45))
# Head (Woody/Mossy)
fg.draw_pattern(0, 0, 32, 32, (80, 60, 40), (100, 80, 60), vertical=False) # Wood grain
# Body (Thick Bark)
fg.draw_pattern(0, 40, 60, 30, (60, 40, 20), (80, 60, 40))
# Arms/Legs
fg.fill_rect(60, 21, 40, 40, (100, 120, 100)) # Vines
fg.fill_rect(37, 0, 20, 20, (50, 30, 10)) # Roots
fg.save('RP/textures/entity/forest_guardian.png')

# --- Desert Stinger (64x64) ---
# UVs: head [32,4], body0 [0,0], body1 [0,12], legs [18,0]
ds = TextureGenerator(64, 64)
# Sandy Base
ds.fill_rect(0, 0, 64, 64, (194, 178, 128))
# Head (Black eyes/Red patterns)
ds.fill_rect(32, 4, 16, 16, (30, 30, 30))
ds.fill_rect(34, 6, 4, 4, (200, 0, 0)) # Eye spot
# Body Segments
ds.draw_pattern(0, 0, 32, 12, (100, 80, 40), (130, 110, 70), vertical=True)
ds.draw_pattern(0, 12, 32, 20, (100, 80, 40), (130, 110, 70), vertical=True)
# Legs (Darker)
ds.fill_rect(18, 0, 14, 14, (60, 50, 30))
ds.save('RP/textures/entity/desert_stinger.png')

# --- Cloud Ray (64x64) ---
# UVs: head [0,10], body [0,0], wings [0,14], [0,21], tail [28,0]
cr = TextureGenerator(64, 64)
# Ethereal Blue Base
cr.fill_rect(0, 0, 64, 64, (200, 230, 255))
# Body (Soft Cloud)
cr.draw_pattern(0, 0, 20, 10, (255, 255, 255), (220, 240, 255), vertical=False)
# Wings (Wispy)
cr.draw_pattern(0, 14, 32, 7, (180, 210, 255), (210, 240, 255))
cr.draw_pattern(0, 21, 32, 7, (180, 210, 255), (210, 240, 255))
# Head/Tail (Glowy bits)
cr.fill_rect(0, 10, 10, 4, (255, 255, 255))
cr.fill_rect(28, 0, 10, 16, (220, 240, 255))
cr.save('RP/textures/entity/cloud_ray.png')
