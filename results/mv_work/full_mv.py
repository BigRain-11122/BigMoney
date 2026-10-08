# -*- coding: utf-8 -*-
"""MV-0001《爱在西元前》完整版草稿 v1——试生产直出成品（CEO 令「直接走工作流出成品」）
链：whisper 词位→逐词锁镜→程序化画面（三池）→zoompan→逐词切点→分级调色→2.35:1 遮幅→ASS 字幕→AIGC 标识→首尾闭环"""
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

F_T = font(84, True); F_S = font(40); F_XS = font(28)

# ---------- 画面基件（复用 pilots 已验函数族）----------
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

def stele(img, cx, top, w_, h_, line=(232, 200, 130)):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    r = w_ / 2
    dd.pieslice([cx-r, top, cx+r, top+2*r], 180, 360, fill=(44, 38, 32, 255))
    dd.rectangle([cx-r, top+r, cx+r, top+h_], fill=(40, 35, 29, 255))
    dd.polygon([(cx-r, top+r), (cx-r*0.72, top+r), (cx-r*0.86, top+h_), (cx-r, top+h_)], fill=(58, 50, 40, 255))
    dd.ellipse([cx-r*0.55, top+r*0.25, cx-r*0.15, top+r*0.75], fill=line+(120,))
    dd.ellipse([cx+r*0.18, top+r*0.30, cx+r*0.52, top+r*0.78], fill=line+(120,))
    dd.arc([cx-r, top, cx+r, top+2*r], 180, 360, fill=line+(230,), width=4)
    out = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(out, "RGBA")
    wedges(d, cx-r*0.78, top+r*1.35, r*1.56, 26, 9, line+(150,), random.Random(7), gap=max(14, int((h_-r*1.6)/26)))
    return out

def tablet(img, cx, cy, w_, h_, glow=True):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    dd.rounded_rectangle([cx-w_/2, cy-h_/2, cx+w_/2, cy+h_/2], radius=int(w_*0.07),
                          fill=(146, 108, 66, 255), outline=(96, 68, 38, 255), width=3)
    d = ImageDraw.Draw(ov, "RGBA")
    wedges(d, cx-w_*0.38, cy-h_*0.36, w_*0.76, 7, 8, (70, 46, 24, 235), random.Random(11), gap=int(h_*0.72/7))
    out = Image.alpha_composite(img, ov)
    if glow:
        d2 = ImageDraw.Draw(out, "RGBA")
        d2.rounded_rectangle([cx-w_/2-8, cy-h_/2-8, cx+w_/2+8, cy+h_/2+8],
                             radius=int(w_*0.08), outline=(255, 214, 140, 110), width=3)
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
        dd.line([(0, 520+i*72), (W, 520+i*72)], fill=(210, 176, 120, 70+i*26), width=3)
    for _ in range(160):
        dd.point((rng.uniform(0, W), rng.uniform(500, H)), fill=(226, 198, 148, rng.randint(60, 170)))
    return Image.alpha_composite(img, ov)

def couple(img, cx, y, s=1.0, color=(24, 20, 16, 255)):
    """双人剪影（凝视链）"""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    for dx in (-90, 90):
        x = cx + dx * s
        dd.ellipse([x-20*s, y-150*s, x+20*s, y-90*s], fill=color)
        dd.polygon([(x-34*s, y+90*s), (x+34*s, y+90*s), (x+24*s, y-90*s), (x-24*s, y-90*s)], fill=color)
    return Image.alpha_composite(img, ov)

def cap(img, text, y=120, f=None, alpha=230):
    d = ImageDraw.Draw(img, "RGBA")
    d.text((W//2, y), text, font=f or F_S, fill=(245, 240, 226, alpha), anchor="mm")

def mark(img):
    d = ImageDraw.Draw(img, "RGBA")
    d.text((56, 44), "AI 生成 · 改编致敬", font=F_XS, fill=(200, 196, 184, 120), anchor="lm")

# ---------- 画面原型（池·关键词→原型映射）----------
def A_dark_open(rng):          # 黑场→顶光
    img, d = base((10, 10, 12), (4, 4, 5)); return img
def A_stele(rng):              # 法典巨碑
    img, d = base((16, 15, 14), (6, 6, 5))
    img = stele(img, W//2, 130, 560, 700)
    for _ in range(26): ImageDraw.Draw(img, "RGBA").point(
        (rng.uniform(W*0.3, W*0.7), rng.uniform(110, 760)), fill=(255, 226, 168, rng.randint(40, 120)))
    return img
def A_stele_close(rng):        # 碑面下移
    img, d = base((14, 13, 12), (5, 5, 4))
    return stele(img, W//2, -320, 620, 1200)
def A_strata_years(rng):       # 三千七百多年
    img, d = base((18, 15, 12), (7, 6, 5))
    img = sand_strata(img, rng)
    cap(img, "距今已经三千七百多年")
    return img
def A_tablet_pair(rng):        # 王碑vs恋板
    img, d = base((16, 15, 14), (6, 6, 5))
    img = stele(img, W//2, 90, 470, 560)
    img = tablet(img, W//2, 740, 190, 130)
    cap(img, "王的石碑 · 恋人的泥板", y=852, f=F_XS, alpha=150)
    return img
def C_museum_vitrine(rng):     # 橱窗（时空之膜）
    img, d = base((26, 34, 42), (8, 12, 18))
    d.rectangle([W*0.28, 120, W*0.72, 700], outline=(215, 228, 245, 170), width=3)
    d.line([(W*0.5, 140), (W*0.5, 680)], fill=(215, 228, 245, 70), width=1)
    for i in range(5):
        d.line([(W*0.28+i*2, 120+i*4), (W*0.72-i*2, 120+i*4)], fill=(255, 255, 255, 8+i*3), width=1)
    img = tablet(img, W//2, 415, 300, 200)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(40): d.point((rng.uniform(W*0.3, W*0.7), rng.uniform(130, 690)),
                                fill=(255, 240, 210, rng.randint(20, 70)))
    cap(img, "橱窗 · 时空之膜", y=770, f=F_XS, alpha=150)
    return img
def C_gaze_couple(rng):       # 凝视链（她望字·他望她）
    img, d = base((24, 32, 40), (7, 10, 16))
    d.rectangle([W*0.30, 110, W*0.70, 690], outline=(210, 224, 242, 140), width=2)
    img = tablet(img, W*0.46, 400, 250, 170)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    for dx in (0, 150):
        x = W*0.62 - dx
        dd.ellipse([x-17, 470-150, x+17, 470-90], fill=(20, 16, 12, 255))
        dd.polygon([(x-30, 470+90), (x+30, 470+90), (x+21, 470-90), (x-21, 470-90)], fill=(20, 16, 12, 255))
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(W*0.5, 300), (W*0.62, 430)], fill=(255, 214, 140, 60), width=2)
    d.line([(W*0.66, 430), (W*0.7, 300)], fill=(255, 214, 140, 40), width=1)
    cap(img, "你凝视碑文 · 我凝视你", y=780, f=F_XS, alpha=150)
    return img
def B_temple_priests(rng):    # 祭司神殿（剪影）
    img, d = base((30, 22, 14), (10, 7, 5))
    img = ziggurat(img, W//2, 820, 1000, 4, (52, 40, 26, 255))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(7):
        x = W*0.18 + i * (W*0.64/6)
        d.polygon([(x-16, 700), (x+16, 700), (x+11, 560), (x-11, 560)], fill=(24, 18, 12, 255))
        d.ellipse([x-9, 530, x+9, 566], fill=(24, 18, 12, 255))
    d.line([(0, 740), (W, 740)], fill=(232, 200, 130, 60), width=2)
    for _ in range(20): d.point((rng.uniform(0, W), rng.uniform(300, 730)),
                                fill=(255, 210, 150, rng.randint(20, 80)))
    cap(img, "祭司 · 神殿 · 征战 · 弓箭", y=120)
    return img
def B_goddess_wish(rng):      # 苏美女神许愿
    img, d = base((34, 26, 16), (12, 9, 6))
    img = ziggurat(img, W*0.22, 850, 620, 5, (64, 50, 32, 235))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([W*0.66, 130, W*0.66+190, 320], fill=(232, 200, 130, 90))
    d.ellipse([W*0.66+40, 170, W*0.66+150, 280], fill=(255, 226, 168, 60))
    d.polygon([(W*0.5, 690), (W*0.56, 600), (W*0.62, 690)], fill=(24, 18, 12, 255))
    d.ellipse([W*0.53, 560, W*0.59, 616], fill=(24, 18, 12, 255))
    cap(img, "我以女神之名许愿", y=820, f=F_S)
    return img
def B_river_spread(rng):      # 底格里斯河漫延
    img, d = base((14, 30, 44), (4, 12, 20))
    for i in range(1, 9):
        r = 100 * i
        d.arc([W*0.5-r, 520-r*0.35, W*0.5+r, 520+r*0.35], 180, 360, fill=(150, 200, 240, max(30, 160-i*17)), width=3)
    img = ziggurat(img, W*0.2, 870, 380, 3, (40, 60, 90, 200))
    d = ImageDraw.Draw(img, "RGBA")
    cap(img, "思念像底格里斯河般的漫延", y=150)
    return img
def B_civilization(rng):      # 文明只剩语言
    img, d = base((22, 18, 12), (6, 5, 4))
    img = sand_strata(img, rng)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(4):
        d.rectangle([W*0.14+i*W*0.2, 380-((i%2)*46), W*0.14+i*W*0.2+150, 600-((i%2)*46)], fill=(70, 54, 34, 150))
        d.rectangle([W*0.14+i*W*0.2, 380-((i%2)*46), W*0.14+i*W*0.2+150, 600-((i%2)*46)], outline=(210, 176, 120, 90), width=2)
    cap(img, "当古文明只剩下难解的语言", y=200)
    return img
def C_carving_knife(rng):     # 刻字之手起刀
    img, d = base((20, 16, 12), (8, 6, 5))
    img = tablet(img, W//2, 560, 760, 470, glow=False)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(W//2-60, 300), (W//2+40, 420), (W//2-10, 452), (W//2-90, 340)], fill=(232, 200, 130, 220))
    d.line([(W//2-30, 386), (W//2+26, 560)], fill=(196, 158, 96, 200), width=6)
    cap(img, "我给你的爱写在西元前", y=120)
    return img
def A_wedge_macro(rng):       # 楔形笔画成形
    img, d = base((146, 108, 66), (54, 38, 24))
    wedges(d, W*0.2, 220, W*0.6, 8, 26, (58, 38, 20, 240), rng, gap=64)
    return img
def C_palm_press(rng):        # 掌心相覆（峰值帧）
    img, d = base((26, 20, 14), (10, 8, 6))
    img = tablet(img, W//2, 520, 700, 430)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    s = 700 * 0.30
    for dx, dy, a in [(-s*0.35, -s*0.18, 120), (s*0.35, -s*0.05, 235)]:
        dd.ellipse([W//2+dx-s*0.5, 520+dy-s*0.30, W//2+dx+s*0.5, 520+dy+s*0.42], fill=(24, 18, 12, 235))
        dd.polygon([(W//2+dx-s*0.5, 520+dy+s*0.05), (W//2+dx-s*0.1, 520+dy-s*0.55),
                    (W//2+dx+s*0.5, 520+dy+s*0.05)], fill=(24, 18, 12, 235))
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(36):
        d.point((rng.uniform(W*0.28, W*0.72), rng.uniform(300, 700)), fill=(255, 216, 150, rng.randint(50, 150)))
    cap(img, "用楔形文字刻下了永远", y=120, f=F_T)
    return img
def B_sand_bury(rng):         # 黄沙深埋
    img, d = base((36, 30, 22), (18, 14, 10))
    img = tablet(img, W//2, 430, 560, 340, glow=False)
    img = sand_strata(img, rng)
    cap(img, "深埋在美索不达米亚平原", y=810)
    return img
def C_excavation(rng):        # 出土
    img, d = base((30, 40, 48), (10, 14, 20))
    img = tablet(img, W//2, 500, 520, 330, glow=False)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(9):
        ang = i * 40
        d.line([(W//2, 500), (W//2 + 300*math.cos(math.radians(ang+205)), 500 + 200*math.sin(math.radians(ang+205)))],
               fill=(226, 198, 148, 90), width=3)
    cap(img, "几十个世纪后出土发现", y=150)
    return img
def C_repair_lamp(rng):       # 修复室·字迹清晰
    img, d = base((18, 26, 34), (6, 9, 14))
    img = tablet(img, W//2, 470, 640, 420)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(W*0.36, 0), (W*0.64, 0), (W*0.55, 190), (W*0.45, 190)], fill=(255, 236, 200, 26))
    cap(img, "泥板上的字迹依然清晰可见", y=790)
    return img
def C_glass_overlay(rng):     # 玻璃叠印（次峰）
    img, d = base((22, 30, 38), (7, 10, 16))
    d.rectangle([W*0.26, 110, W*0.74, 720], outline=(210, 224, 242, 150), width=2)
    img = tablet(img, W//2, 415, 280, 190)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    dd.pieslice([W*0.1, 250, W*0.5, 700], 180, 360, fill=(52, 40, 26, 60))
    img = Image.alpha_composite(img, ov)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(6):
        d.line([(W*0.26, 130+i*98), (W*0.74, 130+i*98)], fill=(255, 255, 255, 6+i*2), width=1)
    cap(img, "一切又重演", y=800, f=F_T)
    return img
def A_loop_end(rng):          # 尾帧·回环（与开场同构图）
    img, d = base((10, 10, 12), (4, 4, 5))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(60):
        d.point((rng.uniform(W*0.3, W*0.7), rng.uniform(120, 780)), fill=(255, 226, 168, rng.randint(10, 60)))
    cap(img, "一切又重演", y=H//2, f=F_T, alpha=210)
    return img

# ---------- 原型选择（关键词→原型·歌词锚锁镜）----------
ARCH_RULES = [
    ("法典|汉谟|颁布|哈姆|颁布", A_stele),
    ("三千七百|距今|年", A_strata_years),
    ("橱窗|出场|出场前|碑文|字眼|凝视|欣赏|深爱的脸", C_gaze_couple),
    ("石碑|泥板|碑", A_tablet_pair),
    ("祭司|神殿|征战|弓箭|从前", B_temple_priests),
    ("人潮|属于我|画面", C_gaze_couple),
    ("女神|许愿|身边", B_goddess_wish),
    ("河|漫|底格里斯|綠色|紛亂", B_river_spread),
    ("文明|语言|诗篇|難解|永垂|永水", B_civilization),
    ("爱|西元|心愿|寫在|写在", C_carving_knife),
    ("美索|达米|麦达|鸭皮|埋|深埋", B_sand_bury),
    ("世纪|出土|发现|詩", C_excavation),
    ("字迹|清晰|修复|静静可见|自己|和解", C_repair_lamp),
    ("楔形|永远|刻下|割下|拥戒", C_palm_press),
    ("誓言|花千|花钱|封花|风化|疲倦", B_sand_bury),
    ("重演|眼前|身邊|回到", C_glass_overlay),
]
INSTR_POOL = [A_stele_close, A_wedge_macro, C_museum_vitrine, B_river_spread, B_civilization]

def pick_arch(text, rng):
    for pat, fn in ARCH_RULES:
        if any(k in text for k in pat.split("|")):
            return fn
    return None

# ---------- 正典歌词字幕（顺序版·与 whisper 词位配对显示）----------
LYRIC_DISPLAY = [
    "古巴比伦王颁布了汉谟拉比法典", "刻在黑色的玄武岩", "距今已经三千七百多年",
    "你在橱窗前", "凝视碑文的字眼", "我却在旁静静欣赏你", "那张我深爱的脸",
    "祭司 神殿 征战 弓箭", "是谁的从前",
    "喜欢在人潮中", "你只属于我的画面", "经过苏美女神身边", "我以女神之名许愿",
    "思念像底格里斯河般的漫延", "当古文明只剩下难解的语言", "传说就成了永垂不朽的诗篇",
    "我给你的爱写在西元前", "深埋在美索不达米亚平原", "几十个世纪后出土发现",
    "泥板上的字迹依然清晰可见", "我给你的爱写在西元前", "深埋在美索不达米亚平原",
    "用楔形文字刻下了永远", "那已风化千年的誓言", "一切又重演",
]

def build_ass(path):
    """字幕：序列对齐法——whisper 行序=演唱序·按序消耗正典歌词行（字符重叠≥1 即配）"""
    evs = []
    di = 0  # LYRIC_DISPLAY 游标
    for l in LINES:
        if l["end"] - l["start"] < 1.2:
            continue
        best_i = -1
        # 向前看 3 个候选（容忍 ASR 乱序/插入行）
        for k in range(3):
            j = di + k
            if j >= len(LYRIC_DISPLAY):
                break
            if sum(1 for ch in set(LYRIC_DISPLAY[j][:5]) if ch in l["text"]) >= 1:
                best_i = j
                break
        if best_i >= 0:
            di = best_i + 1
            evs.append((l["start"], l["end"], LYRIC_DISPLAY[best_i]))
        # 无匹配=插行（哼唱/尾音）跳过不显示
    def ts(sec):
        h = int(sec // 3600); m = int(sec % 3600 // 60); s = sec % 60
        return f"{h}:{m:02d}:{s:05.2f}"
    rows = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1280", "PlayResY: 720", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: Def,Microsoft YaHei,46,&H00E8F2F6,&H00FFFFFF,&H00101010,&H80000000,-1,1,2,1,2,60,60,64,1",
            "", "[Events]",
            "Format: Layer, Start, End, Style, Text"]
    for a, b, t in evs:
        rows.append(f"Dialogue: 0,{ts(a)},{ts(b)},Def,{t}")
    path.write_text("\n".join(rows), encoding="utf-8")
    return len(evs)

# ---------- 镜表构建 ----------
def build_shots():
    """无缝镜表：每镜延至下一词起句（词间空隙由当前镜 hold 铺满全曲·零漂移）"""
    rng = random.Random(20261008)
    first_line = LINES[1]["start"] if len(LINES) > 1 else 30.0
    shots = [(0.0, first_line * 0.2, "title"),
             (first_line * 0.2, first_line * 0.55, A_dark_open),
             (first_line * 0.55, first_line, A_stele)]
    for i, l in enumerate(LINES[1:], start=1):
        t0 = l["start"]
        if i + 1 < len(LINES):
            t1 = LINES[i + 1]["start"]          # 延至下一词起句（铺空隙）
        else:
            t1 = l["end"]
        if t1 - t0 < 1.2:
            continue
        fn = pick_arch(l["text"], rng)
        if fn is None:
            fn = INSTR_POOL[len(shots) % len(INSTR_POOL)]
        shots.append((t0, t1, fn))
    last_end = LINES[-1]["end"] if LINES else DUR - 8
    if DUR - last_end > 1.0:
        shots.append((last_end, DUR, A_loop_end))
    # 合并超短镜头到前镜
    out = []
    for s in shots:
        if out and s[1] - s[0] < 1.4:
            prev = out[-1]
            out[-1] = (prev[0], s[1], prev[2])
        else:
            out.append(s)
    return out

def main():
    ass_n = build_ass(OUT / "lyrics.ass")
    print("ASS events", ass_n)
    shots = build_shots()
    print("SHOTS", len(shots))
    rng = random.Random(20261008)
    parts, inputs, idx = [], [], 0
    total_frames = int(DUR * FPS) + 1
    frame_counts = [max(int((t1 - t0) * FPS + 0.5), 2) for (t0, t1, fn) in shots]
    frame_counts[-1] = max(total_frames - sum(frame_counts[:-1]), 8)   # 末镜补差收口=零漂移
    for i, ((t0, t1, fn)) in enumerate(shots):
        p = OUT / f"s{i:03d}.png"
        if fn == "title":
            img, d = base((12, 12, 15), (5, 5, 7))
            cap(img, "爱在西元前", y=H//2-30, f=font(120, True))
            cap(img, "改编概念样片 · 全流程本地自动生产", y=H//2+80, f=F_S, alpha=180)
            img.convert("RGB").save(p)
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
    # 统一调色（三池差异已入画面·总链加胶片统一层）+遮幅+字幕+AIGC 角标
    final = (f"[vcat]eq=saturation=0.72:contrast=1.06,curves=all='0/0.03 0.5/0.52 1/0.98',"
             f"noise=alls=5:allf=t,vignette=PI/5,"
             f"crop=1280:546:0:87,pad=1280:720:0:87:black,"
             f"subtitles=lyrics.ass:fontsdir='C\:/Windows/Fonts',"
             f"drawtext=fontfile='C\:/Windows/Fonts/msyh.ttc':text='AI 生成 · 改编致敬原作':"
             f"fontsize=22:fontcolor=0xB8B4AC@0.6:x=36:y=676,format=yuv420p[vout]")
    fc = ";".join(parts + [cat, final])
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inputs + \
          ["-i", str(WAV), "-filter_complex", fc, "-map", "[vout]", "-map", f"{idx}:a",
           "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart", str(OUT / "MV0001_爱在西元前_样片v1.mp4")]
    cwd = subprocess.run(["cmd", "/c", "echo", "%CD%"], capture_output=True, text=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=str(OUT))
    if r.returncode != 0:
        print("FFMPEG_FAIL", r.stderr[-800:]); sys.exit(1)
    print("PRODUCT DONE:", OUT / "MV0001_爱在西元前_样片v1.mp4")

if __name__ == "__main__":
    main()
