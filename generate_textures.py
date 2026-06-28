import struct
import zlib
import random

def make_chunk(type, data):
    length = struct.pack('>I', len(data))
    crc = struct.pack('>I', zlib.crc32(type + data) & 0xffffffff)
    return length + type + data + crc

class ProArtist:
    def __init__(self, width, height, bg=(0, 0, 0, 0)):
        self.width = width
        self.height = height
        self.pixels = [[bg for _ in range(width)] for _ in range(height)]

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            if len(color) == 3:
                self.pixels[y][x] = (*color, 255)
            else:
                self.pixels[y][x] = color

    def brush_stroke(self, x, y, w, h, color, density=0.5):
        for i in range(y, y + h):
            for j in range(x, x + w):
                if random.random() < density:
                    # Randomize color slightly
                    n = random.randint(-15, 15)
                    c = tuple(max(0, min(255, channel + n)) for channel in color[:3])
                    a = color[3] if len(color) == 4 else 255
                    self.set_pixel(j, i, (*c, a))

    def paint_uv_box(self, u, v, w, h, d, color):
        # Top
        self.brush_stroke(u + d, v, w, d, tuple(min(255, c + 30) for c in color), 0.9)
        # Bottom
        self.brush_stroke(u + d + w, v, w, d, tuple(max(0, c - 40) for c in color), 0.9)
        # West
        self.brush_stroke(u, v + d, d, h, color, 0.9)
        # North
        self.brush_stroke(u + d, v + d, w, h, tuple(max(0, c - 10) for c in color), 0.9)
        # East
        self.brush_stroke(u + d + w, v + d, d, h, color, 0.9)
        # South
        self.brush_stroke(u + d + w + d, v + d, w, h, tuple(max(0, c - 20) for c in color), 0.9)

    def save(self, filename):
        png_header = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', self.width, self.height, 8, 6, 0, 0, 0)
        ihdr_chunk = make_chunk(b'IHDR', ihdr_data)
        all_rows = b''
        for row in self.pixels:
            row_bytes = b'\x00'
            for p in row:
                row_bytes += struct.pack('BBBB', *p)
            all_rows += row_bytes
        idat_data = zlib.compress(all_rows)
        idat_chunk = make_chunk(b'IDAT', idat_data)
        iend_chunk = make_chunk(b'IEND', b'')
        with open(filename, 'wb') as f:
            f.write(png_header + ihdr_chunk + idat_chunk + iend_chunk)

# --- Forest Guardian ---
fg = ProArtist(128, 128)
bark = (80, 50, 30)
leaf = (34, 100, 34)
fg.paint_uv_box(0, 0, 8, 10, 8, bark)
fg.brush_stroke(9, 10, 2, 2, (0, 255, 255), 1.0) # Eyes
fg.brush_stroke(13, 10, 2, 2, (0, 255, 255), 1.0)
fg.paint_uv_box(0, 40, 18, 12, 11, bark)
fg.brush_stroke(11, 51, 18, 12, leaf, 0.6) # Mossy front
fg.paint_uv_box(60, 21, 4, 28, 6, bark)
fg.paint_uv_box(60, 58, 4, 28, 6, bark)
fg.paint_uv_box(37, 0, 6, 12, 5, bark)
fg.paint_uv_box(60, 0, 6, 12, 5, bark)
fg.save('RP/textures/entity/forest_guardian.png')

# --- Desert Stinger ---
ds = ProArtist(64, 64, (210, 180, 140, 255))
chitin = (110, 60, 20)
ds.paint_uv_box(0, 0, 6, 6, 6, chitin)
ds.paint_uv_box(0, 12, 10, 8, 12, chitin)
ds.paint_uv_box(32, 4, 8, 8, 8, (30, 30, 30)) # Head
ds.brush_stroke(41, 13, 1, 1, (255, 0, 0), 1.0) # Red eyes
ds.brush_stroke(46, 13, 1, 1, (255, 0, 0), 1.0)
ds.paint_uv_box(18, 0, 16, 2, 2, chitin)
ds.save('RP/textures/entity/desert_stinger.png')

# --- Cloud Ray ---
cr = ProArtist(64, 64)
cloud = (240, 240, 255, 220)
cr.paint_uv_box(0, 0, 8, 2, 8, cloud)
cr.paint_uv_box(0, 10, 6, 1, 3, cloud)
cr.paint_uv_box(0, 14, 8, 1, 6, cloud)
cr.paint_uv_box(0, 21, 8, 1, 6, cloud)
cr.paint_uv_box(28, 0, 2, 1, 8, cloud)
cr.save('RP/textures/entity/cloud_ray.png')

# Icon
icon = ProArtist(64, 64, (34, 139, 34, 255))
icon.brush_stroke(16, 16, 32, 32, (101, 67, 33), 0.8)
icon.save('BP/pack_icon.png')
icon.save('RP/pack_icon.png')
