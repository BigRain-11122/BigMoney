# -*- coding: utf-8 -*-
"""MV-0001《爱在西元前》完整版 v2——修复式重映（D-BS-20261008-10 四项定谳）
底座=原版双线骨架（书房书写线×火把石室线）·暖橙一统+玻璃青唯一冷色·2001 胶片颗粒
十场=BRIEF-v2 正典：书房开场→书库发光碑双影（脑补成真）→石室神殿→刻字仪式→浮雕地层→
石室出土→书房读字→尾桥女神显影（补场8.5·173-188s）→玻璃双时空叠印→灯暗回环蚀刻字卡
v2.1 修正（三帧自验回执）：①全场景主体抬入 2.35:1 安全线（y≈150-750）+人物放大——遮幅裁切线下剪影全裁案修复；②女神镜重画（弱光晕强人形）；③字幕匹配改全字符集+尾桥拆三句+终副歌补行——ASR 噪声下尾桥/峰值行落空案修复。"""
import json, math, pathlib, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

DST = pathlib.Path(r"C:\Users\sjs20\Desktop\FluxGroup\media\BigStream\data\sources\mv001")
MV = DST.parent.parent / "storylines" / "drama" / "mv0001"
OUT = MV / "release"
OUT.mkdir(parents=True, exist_ok=True)
WAV = DST / "ai-zai-xi-yuan-qian.wav"
ST = json.loads((DST / "structure.json").read_text(encoding="utf-8"))
LINES = ST["lines"]
DUR = ST["duration"]
W, H, FPS = 1600, 900, 24

def font(size, bold=False):
    for c in (["C:\\Windows\\Fonts\\msyhbd.ttc", "C:\\Windows\\Fonts\\simhei.ttf"] if bold else []) + \
             ["C:\\Windows\\Fonts\\msyh.ttc", "C:\\Windows\\Fonts\\simhei.ttf"]:
        if pathlib.Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

F_T = font(96, True); F_S = font(40); F_XS = font(28); F_SEAL = font(300, True)

# ---------- 调色板（暖橙一统·玻璃青唯一冷色） ----------
AMBER_GLOW = (255, 196, 120); EMBER = (255, 168, 84); LINE = (232, 190, 130)
GOWN = (245, 236, 222); GLASS = (150, 196, 216)

def base(top, bot):
    img = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / H
        img.putpixel((0, y), tuple(int(top[i]*(1-t)+bot[i]*t) for i in range(3)))
    img = img.resize((W, H)).convert("RGBA")
    return img, ImageDraw.Draw(img, "RGBA")

def wedges(d, x0, y0, w_, rows, size, color, rng, gap=26):
    for r in range(rows):
        y = y0 + r * gap
        n = max(2, int(w_ / (size * 3.4)))
        for i in range(n):
            x = x0 + (i + rng.uniform(-0.15, 0.15)) * (w_ / n)
            a = rng.choice([0, 180]) + rng.uniform(-16, 16)
            rad = math.radians(a)
            d.line([(x, y), (x+math.cos(rad)*size*1.7, y+math.sin(rad)*size*1.7)],
                   fill=color, width=max(2, size//4))
            hx, hy = x+math.cos(rad)*size*1.7, y+math.sin(rad)*size*1.7
            px, py = -math.sin(rad)*size*0.5, math.cos(rad)*size*0.5
            d.polygon([(hx, hy), (hx+px, hy+py),
                       (hx+px*0.2-math.cos(rad)*size*0.45, hy+py*0.2-math.sin(rad)*size*0.45)], fill=color)

def seal(img, ch):
    """刻-写-刻字卡：大字低透明度衬底（不喧哗·300px/alpha16·防调色链放大抢戏）"""
    d = ImageDraw.Draw(img, "RGBA")
    d.text((W//2, H//2-40), ch, font=F_SEAL, fill=LINE+(16,), anchor="mm")

def stele(img, cx, top, w_, h_):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    r = w_ / 2
    dd.pieslice([cx-r, top, cx+r, top+2*r], 180, 360, fill=(44, 30, 18, 255))
    dd.rectangle([cx-r, top+r, cx+r, top+h_], fill=(38, 26, 16, 255))
    dd.polygon([(cx-r, top+r), (cx-r*0.72, top+r), (cx-r*0.86, top+h_), (cx-r, top+h_)], fill=(56, 38, 22, 255))
    dd.ellipse([cx-r*0.55, top+r*0.25, cx-r*0.15, top+r*0.75], fill=LINE+(120,))
    dd.ellipse([cx+r*0.18, top+r*0.30, cx+r*0.52, top+r*0.78], fill=LINE+(120,))
    dd.arc([cx-r, top, cx+r, top+2*r], 180, 360, fill=LINE+(230,), width=4)
    out = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(out, "RGBA")
    wedges(d, cx-r*0.78, top+r*1.35, r*1.56, 26, 9, LINE+(150,), random.Random(7), gap=max(14, int((h_-r*1.6)/26)))
    return out

def tablet(img, cx, cy, w_, h_, glow=False):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    dd.rounded_rectangle([cx-w_/2, cy-h_/2, cx+w_/2, cy+h_/2], radius=int(w_*0.07),
                          fill=(150, 108, 62, 255), outline=(104, 72, 40, 255), width=3)
    d = ImageDraw.Draw(ov, "RGBA")
    wedges(d, cx-w_*0.38, cy-h_*0.36, w_*0.76, 7, 8, (76, 50, 26, 235), random.Random(11), gap=int(h_*0.72/7))
    out = Image.alpha_composite(img, ov)
    if glow:
        d2 = ImageDraw.Draw(out, "RGBA")
        d2.rounded_rectangle([cx-w_/2-8, cy-h_/2-8, cx+w_/2+8, cy+h_/2+8],
                             radius=int(w_*0.08), outline=(255, 224, 160, 110), width=3)
    return out

def ziggurat(img, cx, base_y, w_, steps, color):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    sw, sh = w_, w_ * 0.14
    y = base_y
    for _ in range(steps):
        dd.rectangle([cx-sw/2, y-sh, cx+sw/2, y], fill=color)
        y -= sh
        sw *= 0.72
    return Image.alpha_composite(img, ov)

def sand_strata(img, rng):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    for i in range(5):
        dd.line([(0, 520+i*72), (W, 520+i*72)], fill=(216, 168, 104, 70+i*26), width=3)
    for _ in range(160):
        dd.point((rng.uniform(0, W), rng.uniform(500, H)), fill=(232, 188, 128, rng.randint(60, 170)))
    return Image.alpha_composite(img, ov)

def flame(d, x, y, s, rng):
    """火把火苗（暖橙核心+外焰）"""
    for i in range(3):
        fx = x + rng.uniform(-3, 3)*s
        dd_h = s*(1.15 - i*0.22)
        d.polygon([(fx-7*s, y), (fx+7*s, y), (fx+2*s, y-dd_h), (fx-2*s, y-dd_h)],
                  fill=(255, 170, 70, 120 - i*32))
    d.ellipse([x-4*s, y-9*s, x+4*s, y-2*s], fill=(255, 226, 170, 210))

def figure(d, x, y, s, color=(18, 11, 7, 255), hair=False):
    """人物剪影（y=脚底基准·须落在 2.35:1 安全线 y≈150-750 内）"""
    d.ellipse([x-15*s, y-140*s, x+15*s, y-100*s], fill=color)
    d.polygon([(x-26*s, y), (x+26*s, y), (x+18*s, y-100*s), (x-18*s, y-100*s)], fill=color)
    if hair:
        d.polygon([(x-15*s, y-138*s), (x+15*s, y-138*s), (x+20*s, y-60*s), (x-20*s, y-60*s)], fill=color)

def etched(d, x, y, text, f, main=(240, 205, 150)):
    d.text((x+7, y+7), text, font=f, fill=(120, 88, 50, 150), anchor="mm")
    d.text((x, y), text, font=f, fill=main+(238,), anchor="mm")

def mark(img):
    d = ImageDraw.Draw(img, "RGBA")
    d.text((56, 44), "AI 生成 · 改编致敬", font=F_XS, fill=(214, 186, 140, 130), anchor="lm")

# ---------- v2.1 画面原型（暖橙世界·主体全部位于 y≈150-750 安全线） ----------
def V_title(rng):
    img, d = base((22, 14, 8), (7, 5, 3))
    etched(d, W//2, H//2-40, "爱在西元前", F_T)
    etched(d, W//2, H//2+80, "修复式重映 · 概念样片", F_S)
    return img

def V_study_open(rng):       # 场1 书房线开场（原版帧位·书写者）
    img, d = base((46, 30, 15), (16, 10, 6))
    for row, sy in ((380, 760), (520, 820)):         # 书架两排（安全带内）
        d.rectangle([W*0.06, sy-26, W*0.94, sy], fill=(58, 38, 20, 255))
        for i in range(26):
            bx = W*0.07 + i*(W*0.86/26)
            bh = rng.randint(52, 96)
            d.rectangle([bx, sy-26-bh, bx+rng.randint(10, 18), sy-26], fill=(96+rng.randint(-18, 24), 62, 30, 235))
    d.polygon([(W*0.60, 760), (W*0.76, 320), (W*0.94, 380), (W*0.94, 760)], fill=(34, 22, 12, 255))  # 书桌
    d.polygon([(W*0.72, 0), (W*0.80, 0), (W*0.66, 760), (W*0.60, 760)], fill=(255, 216, 150, 22))   # 灯锥
    d.ellipse([W*0.76, -40, W*0.84, 40], fill=(255, 232, 180, 130))
    figure(d, W*0.70, 640, 1.25)                      # 伏案书写者剪影（安全带内）
    for _ in range(14): d.point((rng.uniform(0, W), rng.uniform(100, 740)), fill=EMBER+(rng.randint(16, 60),))
    return img

def V_stele_shadow(rng):     # 场1 法典碑巨影+字卡「刻」
    img, d = base((32, 21, 12), (10, 7, 4))
    d.polygon([(W*0.30, 0), (W*0.70, 0), (W*0.60, 520), (W*0.40, 520)], fill=(255, 220, 160, 20))
    img = stele(img, W//2, 100, 540, 640)
    d = ImageDraw.Draw(img, "RGBA")
    seal(img, "刻")
    for _ in range(26): d.point((rng.uniform(W*0.3, W*0.7), rng.uniform(100, 720)),
                                fill=EMBER+(rng.randint(40, 120),))
    return img

def V_glowcase(rng):         # 场2 书库过道·强发光碑物·双影凝视（脑补成真）
    img, d = base((40, 27, 15), (13, 9, 5))
    for side in (-1, 1):                             # 透视书架
        for k in range(4):
            x0 = W//2 + side*(90 + k*150)
            d.line([(x0, 80), (x0 + side*60, 760)], fill=(88, 58, 30, 160), width=14)
            for i in range(6):
                t = i/6
                bx = x0 + side*60*t
                d.rectangle([bx-10, 120+t*600, bx+6, 170+t*600], fill=(104, 68, 34, 120))
    cx = W//2
    d.rectangle([cx-150, 560, cx+150, 640], fill=(64, 42, 24, 255))                 # 基座
    d.rounded_rectangle([cx-120, 300, cx+120, 560], radius=10, fill=(255, 228, 170, 46))
    d.rectangle([cx-90, 335, cx+90, 540], fill=(255, 240, 205, 235))                 # 强发光碑物
    d.rounded_rectangle([cx-120, 300, cx+120, 560], radius=10, outline=GLASS+(150,), width=3)  # 玻璃青（唯一冷色）
    figure(d, cx-240, 610, 1.5)                                                      # 她：望碑文
    figure(d, cx-400, 625, 1.55)                                                      # 他：落后半步望她
    d.line([(cx-240, 460), (cx-60, 540)], fill=(255, 216, 150, 46), width=2)         # 凝视线①
    d.line([(cx-400, 475), (cx-265, 555)], fill=(255, 216, 150, 32), width=2)         # 凝视线②
    for _ in range(24): d.point((rng.uniform(W*0.3, W*0.7), rng.uniform(120, 720)),
                                fill=EMBER+(rng.randint(20, 70),))
    return img

def V_temple(rng):           # 场3 石室·火把·浮雕墙·祭司
    img, d = base((52, 34, 18), (18, 12, 7))
    img = ziggurat(img, W//2, 760, 980, 4, (56, 36, 20, 255))
    d = ImageDraw.Draw(img, "RGBA")
    flame(d, W*0.12, 560, 2.6, rng); flame(d, W*0.88, 560, 2.6, rng)
    for i in range(7):                               # 祭司列（安全带内）
        x = W*0.20 + i * (W*0.60/6)
        figure(d, x, 650, 0.95)
    d.rectangle([W*0.10, 480, W*0.90, 528], fill=(70, 46, 26, 200))                 # 浮雕带
    for i in range(12):                               # 浮雕剪影（战车·塔）
        x = W*0.12 + i*(W*0.76/11)
        d.polygon([(x, 528), (x+18, 494), (x+36, 528)], fill=(34, 22, 14, 255))
        d.rectangle([x+50, 498, x+60, 528], fill=(34, 22, 14, 255))
    for _ in range(20): d.point((rng.uniform(0, W), rng.uniform(200, 700)),
                                fill=EMBER+(rng.randint(20, 80),))
    return img

def V_goddess_bust(rng):     # 场3 苏美女神·香雾·许愿
    img, d = base((46, 30, 16), (14, 10, 6))
    cx = W*0.50
    d.ellipse([cx-170, 200, cx+170, 540], fill=(255, 216, 150, 26))                 # 光环
    d.ellipse([cx-110, 260, cx+110, 500], fill=(255, 224, 168, 34))
    figure(d, cx, 620, 1.30, color=(26, 17, 11, 235), hair=True)                     # 女神剪影（长发·安全带内）
    for i in range(5):                               # 香雾
        d.arc([cx-260+i*40, 320, cx+140+i*40, 700], 200+i*12, 340, fill=(255, 226, 170, 40), width=3)
    figure(d, W*0.22, 640, 1.05)                                                     # 许愿者
    d.polygon([(W*0.24, 500), (W*0.28, 488), (W*0.30, 528), (W*0.26, 540)], fill=(18, 11, 7, 255))  # 许愿双手
    return img

def V_river(rng):            # 场4 底格里斯·沙水漫延
    img, d = base((58, 38, 18), (20, 14, 8))
    for i in range(1, 9):
        r = 100 * i
        d.arc([W*0.5-r, 460-r*0.35, W*0.5+r, 460+r*0.35], 180, 360,
              fill=(255, 202, 130, max(30, 160-i*17)), width=3)
    img = ziggurat(img, W*0.2, 780, 380, 3, (46, 30, 16, 200))
    for _ in range(40): ImageDraw.Draw(img, "RGBA").point(
        (rng.uniform(W*0.3, W*0.7), rng.uniform(440, 740)), fill=(240, 200, 140, rng.randint(40, 110)))
    return img

def V_strata(rng):           # 场5 浮雕横移带·千年地层（元文本显题）
    img, d = base((50, 34, 18), (18, 12, 7))
    img = sand_strata(img, rng)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 330, W, 520], fill=(76, 50, 28, 150))
    for i in range(16):                               # 王朝剪影带：战车·塔楼·星
        x = i*(W/15)
        if i % 3 == 0:
            d.polygon([(x, 520), (x+26, 430), (x+52, 520)], fill=(30, 20, 12, 235))
        elif i % 3 == 1:
            d.rectangle([x, 460, x+16, 520], fill=(30, 20, 12, 235)); d.rectangle([x-4, 450, x+20, 460], fill=(30, 20, 12, 235))
        else:
            d.line([(x, 400), (x+20, 360)], fill=LINE+(160,), width=3); d.line([(x+20, 360), (x+40, 400)], fill=LINE+(160,), width=3)
    img = tablet(img, W//2, 640, 300, 170)            # 泥板静卧（安全带内）
    return img

def V_carve(rng):            # 场4 刻字仪式·字卡「写」
    img, d = base((44, 29, 15), (16, 11, 6))
    img = tablet(img, W//2, 500, 800, 440)
    d = ImageDraw.Draw(img, "RGBA")
    wedges(d, W*0.30, 380, W*0.40, 5, 30, (64, 42, 22, 245), rng, gap=52)
    d.polygon([(W//2-60, 260), (W//2+50, 380), (W//2+10, 412), (W//2-90, 298)], fill=LINE+(220,))   # 刻刀
    d.line([(W//2-30, 356), (W//2+30, 520)], fill=(200, 150, 90, 200), width=6)
    seal(img, "写")
    for _ in range(18): d.point((rng.uniform(W*0.3, W*0.7), rng.uniform(260, 700)),
                                fill=EMBER+(rng.randint(40, 130),))
    return img

def V_bury(rng):             # 场4 深埋·黄沙覆板
    img, d = base((62, 42, 22), (24, 16, 9))
    img = tablet(img, W//2, 430, 560, 330)
    img = sand_strata(img, rng)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(30): d.point((rng.uniform(0, W), rng.uniform(360, 620)), fill=(240, 198, 138, rng.randint(50, 140)))
    return img

def V_reveal(rng):           # 场6 石室火光·泥板出土显形（原版火炬帧位）
    img, d = base((42, 28, 15), (14, 10, 6))
    flame(d, W*0.10, 540, 2.2, rng); flame(d, W*0.90, 540, 2.2, rng)
    img = tablet(img, W//2, 520, 540, 330)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(9):
        ang = 205 + i * 40
        d.line([(W//2, 520), (W//2 + 320*math.cos(math.radians(ang)), 520 + 210*math.sin(math.radians(ang)))],
               fill=(240, 198, 138, 80), width=3)
    for _ in range(30): d.point((rng.uniform(W*0.3, W*0.7), rng.uniform(360, 700)),
                                fill=(240, 200, 140, rng.randint(40, 130)))
    return img

def V_reading(rng):          # 场7 书房读字·最清晰一帧
    img, d = base((34, 22, 12), (12, 8, 5))
    d.polygon([(W*0.36, 0), (W*0.64, 0), (W*0.55, 200), (W*0.45, 200)], fill=(255, 232, 180, 30))
    img = tablet(img, W//2, 460, 660, 380)
    d = ImageDraw.Draw(img, "RGBA")
    wedges(d, W*0.32, 380, W*0.36, 6, 24, (58, 38, 20, 250), rng, gap=58)           # 高锐大笔画=最清晰
    for i in range(4):                                # 书架暗影（书房线暗接）
        d.rectangle([W*0.02+i*30, 540, W*0.02+i*30+18, 700], fill=(70, 46, 26, 90))
    figure(d, W*0.82, 640, 1.15)                      # 读者剪影（安全带内）
    return img

def V_erosion(rng):          # 场7 风化誓言·字痕存留
    img, d = base((38, 25, 13), (13, 9, 5))
    img = tablet(img, W//2, 440, 760, 400)
    d = ImageDraw.Draw(img, "RGBA")
    wedges(d, W*0.28, 350, W*0.44, 6, 26, (66, 44, 24, 240), rng, gap=56)
    for _ in range(40):                               # 风化剥落（安全带内）
        d.point((rng.uniform(W*0.28, W*0.74), rng.uniform(640, 740)),
                fill=(214, 168, 110, rng.randint(60, 170)))
    for i in range(3):
        d.line([(W*0.30+i*160, 260), (W*0.34+i*160, 310)], fill=(120, 82, 44, 130), width=2)
    return img

def V_goddess_emerge(rng):   # 补场8.5 尾桥·白裙女神显影（人形分明·第二峰值）
    img, d = base((24, 15, 8), (6, 4, 2))
    for tx in (W*0.14, W*0.86):                      # 火把（火苗+柄）
        flame(d, tx, 520, 2.6, rng)
        d.line([(tx, 560), (tx, 650)], fill=(70, 46, 26, 255), width=7)
    cx = W//2
    d.ellipse([cx-115, 190, cx+115, 400], fill=(255, 210, 140, 12))                 # 弱光晕
    d.polygon([(cx-38, 250), (cx+38, 250), (cx+52, 470), (cx-52, 470)],           # 长发（乳褐）
              fill=(216, 204, 186, 235))
    d.ellipse([cx-30, 232, cx+30, 296], fill=GOWN+(252,))                          # 头
    d.polygon([(cx-15, 296), (cx+15, 296), (cx+42, 345), (cx-42, 345)],           # 肩
              fill=GOWN+(245,))
    d.polygon([(cx-42, 345), (cx+42, 345), (cx+30, 445), (cx-30, 445)],           # 上身收腰
              fill=GOWN+(240,))
    d.polygon([(cx-30, 445), (cx+30, 445), (cx+128, 710), (cx-128, 710)],          # 裙摆
              fill=GOWN+(238,))
    for _ in range(4):                               # 裙裾光丝
        d.line([(cx-150+rng.uniform(-20, 20), 420), (cx-95, 640)], fill=(255, 220, 160, 24), width=2)
    for _ in range(18): d.point((rng.uniform(W*0.12, W*0.88), rng.uniform(150, 740)),
                                fill=EMBER+(rng.randint(10, 56),))
    return img

def V_press(rng):            # 场4/8 掌心相覆·峰值·字卡「刻」（板面清底+经典掌形剪影=手可读）
    img, d = base((40, 26, 14), (14, 9, 5))
    img = tablet(img, W//2, 490, 700, 400)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([W//2-300, 490-160, W//2+300, 490+160], radius=26,
                        fill=(170, 122, 70, 240))                                   # 干净板面（去楔文噪）
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    for dx, dy in ((-95, -35), (95, 25)):                                           # 双掌相叠
        hx, hy = W//2 + dx, 500 + dy
        for k in range(5):                                                          # 五指短圆
            fx = hx - 104 + k*52
            dd.rounded_rectangle([fx-15, hy-165, fx+15, hy-45], radius=13,
                                 fill=(24, 15, 9, 246))
        dd.ellipse([hx-135, hy-80, hx+135, hy+110], fill=(30, 19, 11, 248))         # 掌
    wedges(dd, W*0.34, 640, W*0.32, 2, 22, (86, 56, 28, 220), rng, gap=40)         # 掌下三两刻痕（上下分离不互糊）
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img, "RGBA")
    seal(img, "刻")
    for _ in range(36):
        d.point((rng.uniform(W*0.28, W*0.72), rng.uniform(280, 700)), fill=EMBER+(rng.randint(50, 150),))
    return img

def V_glass(rng):            # 场8 玻璃双时空叠印（新奇全押·2001 拍不出）
    img, d = base((34, 23, 13), (11, 8, 5))
    d.rectangle([W*0.24, 90, W*0.76, 640], outline=GLASS+(160,), width=3)           # 玻璃青
    d.rectangle([W*0.24, 90, W*0.76, 640], fill=GLASS+(14,))
    img = tablet(img, W//2, 380, 300, 190)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    dd.rectangle([W*0.30, 460, W*0.44, 600], fill=(70, 46, 26, 60))                  # 玻璃内：古代神殿叠影
    for i in range(3):
        dd.rectangle([W*0.34+i*18, 440-i*24, W*0.40+i*18, 600], fill=(70, 46, 26, 50))
    for dx in (0, 120):                                                              # 玻璃外：双影倒映
        x = W*0.60 - dx
        dd.ellipse([x-16, 440, x+16, 488], fill=(20, 13, 9, 185))
        dd.polygon([(x-28, 620), (x+28, 620), (x+20, 488), (x-20, 488)], fill=(20, 13, 9, 185))
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(5):
        d.line([(W*0.24, 110+i*102), (W*0.76, 110+i*102)], fill=(255, 255, 255, 5+i*2), width=1)
    return img

def V_end(rng):              # 场9 灯暗回环·余烬·蚀刻字卡（与开场同构图族）
    img, d = base((14, 9, 5), (4, 3, 2))
    for _ in range(60):
        d.point((rng.uniform(W*0.3, W*0.7), rng.uniform(120, 780)), fill=EMBER+(rng.randint(10, 60),))
    etched(d, W//2, H//2, "爱在西元前", F_T)
    return img

# ---------- 原型选择（ASR 噪声关键词→原型·歌词锚锁镜） ----------
ARCH_RULES = [
    ("哈姆|颁布|法典|堡里", V_stele_shadow),
    ("三千七百|距今|记起", V_strata),
    ("橱窗|出场|碑文|字眼|悲欢|凝视|欣赏|深愛|深爱的脸", V_glowcase),
    ("人潮|属于|那画面", V_glowcase),
    ("祭司|神殿|征战|弓箭|从前|升天|占占", V_temple),
    ("女神|许愿|迷去夜|美丽山|身边|瞬间|冰雪烟", V_goddess_bust),
    ("紛亂|纷乱|皮革|河|漫", V_river),
    ("文明|语言|難解|难解|永垂|永水|詩|诗篇|成熟", V_strata),
    ("楔形|刻下|永远|割下|经文字|拥戒", V_press),
    ("风化|誓言|花千|花钱|道别", V_erosion),
    ("疲倦|家乡|害怕|身邊|假像|還是很遠|回到", V_goddess_emerge),
    ("深埋|美索|麦达|鸭皮|埋", V_bury),
    ("世纪|出土|发现|提前", V_reveal),
    ("字迹|清晰|可见|自己|和解|情绪|静静", V_reading),
    ("重演|尊严|眼前|一切", V_glass),
    ("西元|心愿|寫在|写在|愛|爱|心結|幸运", V_carve),
]
INSTR_POOL = [V_temple, V_strata, V_reveal, V_river]

def pick_arch(text, rng):
    for pat, fn in ARCH_RULES:
        if any(k in text for k in pat.split("|")):
            return fn
    return None

# ---------- 正典歌词字幕（v2.1=全字符集匹配+尾桥拆三句+终副歌补行） ----------
LYRIC_DISPLAY = [
    "古巴比伦王颁布了汉谟拉比法典", "刻在黑色的玄武岩", "距今已经三千七百多年",
    "你在橱窗前", "凝视碑文的字眼", "我却在旁静静欣赏你", "那张我深爱的脸",
    "祭司 神殿 征战 弓箭", "是谁的从前",
    "喜欢在人潮中", "你只属于我的画面", "经过苏美女神身边", "我以女神之名许愿",
    "思念像底格里斯河般的漫延", "当古文明只剩下难解的语言", "传说就成了永垂不朽的诗篇",
    "我给你的爱写在西元前", "深埋在美索不达米亚平原", "几十个世纪后出土发现",
    "泥板上的字迹依然清晰可见", "我给你的爱写在西元前", "深埋在美索不达米亚平原",
    "用楔形文字刻下了永远", "那已风化千年的誓言", "一切又重演",
    "祭司 神殿 征战 弓箭", "是谁的从前",
    "喜欢在人潮中", "你只属于我的画面", "经过苏美女神身边", "我以女神之名许愿",
    "思念像底格里斯河般的漫延", "当古文明只剩下难解的语言", "传说就成了永垂不朽的诗篇",
    "我给你的爱写在西元前", "深埋在美索不达米亚平原", "几十个世纪后出土发现",
    "泥板上的字迹依然清晰可见", "我给你的爱写在西元前", "深埋在美索不达米亚平原",
    "用楔形文字刻下了永远", "那已风化千年的誓言",
    "我感到很疲倦", "离家乡还是很远", "害怕再也不能回到你身边",
    "我给你的爱写在西元前", "深埋在美索不达米亚平原", "几十个世纪后出土发现",
    "泥板上的字迹依然清晰可见", "我给你的爱写在西元前", "用楔形文字刻下了永远",
    "那已风化千年的誓言", "一切又重演", "一切又重演", "爱在西元前",
]

def build_ass(path):
    """字幕：全字符集序列对齐+尾延展（ASR 噪声容错·尾桥三句入轨）"""
    evs = []
    di = 0
    for l in LINES:
        if l["end"] - l["start"] < 1.2:
            continue
        best_i = -1
        for k in range(3):
            j = di + k
            if j >= len(LYRIC_DISPLAY):
                break
            disp = LYRIC_DISPLAY[j]
            hits = len(set(disp) & set(l["text"]))
            if any(ch in l["text"] for ch in disp[:5]) or hits >= 3:   # 首5字命中 或 全句≥3字（ASR噪声容错·防错位抢行）
                best_i = j
                break
        if best_i >= 0:
            di = best_i + 1
            evs.append([l["start"], l["end"], LYRIC_DISPLAY[best_i]])
    for i in range(len(evs)-1):                       # 尾延展：铺演唱保持句
        if 0 < evs[i+1][0] - evs[i][1] <= 6:
            evs[i][1] = evs[i+1][0] - 0.12
    def ts(sec):
        h = int(sec // 3600); m = int(sec % 3600 // 60); s = sec % 60
        return f"{h}:{m:02d}:{s:05.2f}"
    rows = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1280", "PlayResY: 720", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: Def,Microsoft YaHei,46,&H00F2E8DC,&H00FFFFFF,&H00101010,&H80000000,-1,1,2,1,2,60,60,64,1",
            "", "[Events]",
            "Format: Layer, Start, End, Style, Text"]
    for a, b, t in evs:
        rows.append(f"Dialogue: 0,{ts(a)},{ts(b)},Def,{t}")
    path.write_text("\n".join(rows), encoding="utf-8")
    return len(evs)

# ---------- 镜表构建（书房开场→词锁镜→灯暗回环·无缝零漂移） ----------
def build_shots():
    rng = random.Random(20261008)
    first_line = LINES[1]["start"] if len(LINES) > 1 else 30.0
    t1, t2 = first_line * 0.23, first_line * 0.60     # 0-30s：字卡→书房→碑影
    shots = [(0.0, t1, "title"), (t1, t2, V_study_open), (t2, first_line, V_stele_shadow)]
    for i, l in enumerate(LINES[1:], start=1):
        t0 = l["start"]
        t1n = LINES[i+1]["start"] if i + 1 < len(LINES) else l["end"]
        if t1n - t0 < 1.2:
            continue
        fn = pick_arch(l["text"], rng)
        if fn is None:
            fn = INSTR_POOL[len(shots) % len(INSTR_POOL)]
        shots.append((t0, t1n, fn))
    last_end = LINES[-1]["end"] if LINES else DUR - 8
    if DUR - last_end > 1.0:
        shots.append((last_end, DUR, V_end))
    out = []
    for s in shots:
        if out and s[1] - s[0] < 1.4:
            prev = out[-1]
            out[-1] = (prev[0], s[1], prev[2])
        else:
            out.append(s)
    return out

def main():
    ass_n = build_ass(OUT / "lyrics_v2.ass")
    print("ASS events", ass_n)
    shots = build_shots()
    print("SHOTS", len(shots))
    rng = random.Random(20261008)
    parts, inputs, idx = [], [], 0
    total_frames = int(DUR * FPS) + 1
    frame_counts = [max(int((t1 - t0) * FPS + 0.5), 2) for (t0, t1, fn) in shots]
    frame_counts[-1] = max(total_frames - sum(frame_counts[:-1]), 8)   # 末镜补差收口=零漂移
    tmps = []
    for i, ((t0, t1, fn)) in enumerate(shots):
        p = OUT / f"s2_{i:03d}.png"
        tmps.append(p)
        if fn == "title":
            img = V_title(rng)
        else:
            img = fn(rng)
            mark(img)
        img.convert("RGB").save(p)
        frames = frame_counts[i]
        z = (f"z='min(1+0.0009*on,{1+0.0009*frames:.3f})'" if idx % 2 == 0
             else "z='max(1.10-0.001*on,1.001)'")
        parts.append(f"[{idx}:v]scale=1920:1080,zoompan={z}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                     f"d={frames}:s=1280x720:fps={FPS}[v{idx}]")
        inputs += ["-i", str(p)]
        idx += 1
    cat = "".join(f"[v{i}]" for i in range(idx)) + f"concat=n={idx}:v=1:a=0[vcat]"
    # 暖橙一统调色：色平衡偏暖+微降饱和+2001 胶片颗粒（保味律·反AI平滑）+遮幅+字幕+AIGC 角标
    final = (f"[vcat]colorbalance=rs=0.10:rm=0.06:bm=-0.08:bs=-0.10,"
             f"eq=saturation=0.80:contrast=1.07,"
             f"curves=all='0/0.02 0.5/0.55 1/0.97',"
             f"noise=alls=7:allf=t,vignette=PI/5,"
             f"crop=1280:546:0:87,pad=1280:720:0:87:black,"
             f"subtitles=lyrics_v2.ass:fontsdir='C\:/Windows/Fonts',"
             f"drawtext=fontfile='C\:/Windows/Fonts/msyh.ttc':text='AI 生成 · 改编致敬原作':"
             f"fontsize=22:fontcolor=0xC8A878@0.6:x=36:y=676,format=yuv420p[vout]")
    fc = ";".join(parts + [cat, final])
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inputs + \
          ["-i", str(WAV), "-filter_complex", fc, "-map", "[vout]", "-map", f"{idx}:a",
           "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart",
           str(OUT / "MV0001_爱在西元前_样片v2.mp4")]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=str(OUT))
    if r.returncode != 0:
        print("FFMPEG_FAIL", r.stderr[-800:]); sys.exit(1)
    for p in tmps:                                    # 批末自清律
        p.unlink(missing_ok=True)
    print("PRODUCT DONE:", OUT / "MV0001_爱在西元前_样片v2.mp4")

if __name__ == "__main__":
    main()
