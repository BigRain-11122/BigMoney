# r955 verification strips: (a) C07 sink-vs-pullback base-line pair
# (b) R06 cuneiform 100% tiling-probe crops
import os
from PIL import Image, ImageDraw

FRAMES = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r955bmc_qcframes"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results"

def crop_bottom(path, frac=0.45):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    return im.crop((0, int(h * (1 - frac)), w, h))

def crop_zoom(path, boxes):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    return [im.crop((int(x * w), int(y * h), int((x + bw) * w), int((y + bh) * h))) for x, y, bw, bh in boxes]

# (a) C07 first vs last, bottom 45% (base contact zone), side by side
a1 = crop_bottom(os.path.join(FRAMES, "C07_stele_sink_v2_f5.png"))
a2 = crop_bottom(os.path.join(FRAMES, "C07_stele_sink_v2_f45.png"))
W = a1.size[0] + a2.size[0] + 12
H = max(a1.size[1], a2.size[1]) + 60
strip = Image.new("RGB", (W, H), (24, 24, 24))
d = ImageDraw.Draw(strip)
d.text((6, 4), "== C07 t=0.5s bottom45% | t=4.5s bottom45% ==", fill=(255, 210, 80))
strip.paste(a1, (0, 28))
strip.paste(a2, (a1.size[0] + 12, 28))
strip.save(os.path.join(OUT, "_r955bmc_c07_basline.png"), quality=90)
print("C07 strip", strip.size)

# (b) R06 f29 three 100% crops spread across the inscription area
boxes = [(0.15, 0.30, 0.22, 0.22), (0.45, 0.45, 0.22, 0.22), (0.70, 0.28, 0.22, 0.22)]
crops = crop_zoom(os.path.join(FRAMES, "R06_museum_verse_f29.png"), boxes)
cw = max(c.size[0] for c in crops)
ch = sum(c.size[1] for c in crops) + 40
z = Image.new("RGB", (cw, ch), (24, 24, 24))
d = ImageDraw.Draw(z)
y = 0
d.text((6, 4), "== R06 f29 100% crops x3 (inscription tiling probe) ==", fill=(255, 210, 80))
y = 26
for c in crops:
    z.paste(c, (0, y))
    y += c.size[1] + 6
z.save(os.path.join(OUT, "_r955bmc_r06_zoom.png"), quality=92)
print("R06 zoom", z.size)
