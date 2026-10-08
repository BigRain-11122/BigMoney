# -*- coding: utf-8 -*-
"""r769 bm-c: O-20261008-1820 顺序改判令 style-sample batch (风格样图).
CEO gate order: style samples + storyboard for CEO review BEFORE any video.
Scenes per O-1820 spec: core three = 书库双影 / 刻字仪式 (kf1_carve is
candidate-a; this batch adds candidate-b) / 尾桥女神显影; optional fourth =
玻璃双时空叠印 (glass double-exposure, carries the 玻璃青 single cold accent).
best-of-2 per scene (two seeds each where a pair is required).
Mechanics reuses _r768bmc_kf_gen.py verbatim (single-source: wf/NEG/run_one,
SDXL base, 1024x576, warm amber monochrome, seed-locked). i2v video lane
FROZEN until CEO approves these samples (driver killed r769, seg1/seg2 parked).
Outputs to results/mv_work/style/, log results/mv_work/style_gen.log.
Pattern credit: Tools/_r768bmc_kf_gen.py (mechanics single-source) +
Tools/_r768bmc_kf_gen_rest.py (thin todo-driver shape)."""
import importlib.util
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\style"
LOGF = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\style_gen.log"

spec = importlib.util.spec_from_file_location(
    "kf_gen", os.path.join(HERE, "_r768bmc_kf_gen.py"))
kf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kf)

STYLES = [
    ("st1_library_a",
     "ancient mesopotamian library interior, tall wooden shelves stacked with "
     "clay tablets, a young man seated at a reading desk holding a small tablet, "
     "two long shadows cast side by side on the wall behind him, one modern "
     "silhouette and one robed scribe silhouette, single warm torch key light "
     "from the right, volumetric dust, 35mm medium wide shot, deep shadows, "
     "warm amber monochrome, 2001 music video still, 35mm film grain", 20011009),
    ("st1_library_b",
     "ancient mesopotamian library interior, tall wooden shelves stacked with "
     "clay tablets, a young man seated at a reading desk holding a small tablet, "
     "two long shadows cast side by side on the wall behind him, one modern "
     "silhouette and one robed scribe silhouette, single warm torch key light "
     "from the right, volumetric dust, 35mm medium wide shot, deep shadows, "
     "warm amber monochrome, 2001 music video still, 35mm film grain", 20011010),
    ("st2_carve_b",
     "wide shot of a robed scribe kneeling before a tall basalt stele at night, "
     "carving cuneiform signs with a reed stylus, torch fire behind him, rim "
     "light outlining his profile, monumental scale, hard torch key light from "
     "lower left, deep black background, 28mm wide lens, warm amber monochrome, "
     "2001 music video still, 35mm film grain, dust motes", 20011011),
    ("st3_goddess_a",
     "female deity manifesting from golden light and drifting dust on an "
     "ancient stone bridge at night, flowing robes forming out of mist, "
     "distinct human silhouette with one gently raised hand, warm torch glow "
     "from below the bridge, faint cool glass-cyan mist at the far edges, "
     "backlit volumetric rays, 50mm medium shot, warm amber monochrome with "
     "single cold cyan accent, 2001 music video still, 35mm film grain", 20011012),
    ("st3_goddess_b",
     "female deity manifesting from golden light and drifting dust on an "
     "ancient stone bridge at night, flowing robes forming out of mist, "
     "distinct human silhouette with one gently raised hand, warm torch glow "
     "from below the bridge, faint cool glass-cyan mist at the far edges, "
     "backlit volumetric rays, 50mm medium shot, warm amber monochrome with "
     "single cold cyan accent, 2001 music video still, 35mm film grain", 20011013),
    ("st4_glass_a",
     "double exposure through textured ancient glass, two overlapping eras in "
     "one frame, a modern reader silhouette and an ancient scribe silhouette "
     "merging into a single figure, clay tablet texture showing through the "
     "glass, warm torch light on one side, glass-cyan refraction on the other "
     "as the only cold accent, 50mm medium close shot, warm amber monochrome, "
     "2001 music video still, 35mm film grain", 20011014),
    ("st4_glass_b",
     "double exposure through textured ancient glass, two overlapping eras in "
     "one frame, a modern reader silhouette and an ancient scribe silhouette "
     "merging into a single figure, clay tablet texture showing through the "
     "glass, warm torch light on one side, glass-cyan refraction on the other "
     "as the only cold accent, 50mm medium close shot, warm amber monochrome, "
     "2001 music video still, 35mm film grain", 20011015),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    logf = open(LOGF, "a", encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    todo = [t for t in STYLES
            if not os.path.exists(os.path.join(OUT, t[0] + ".png"))]
    log("=== style gen start (O-1820 风格样图, todo=%s) ===" %
        [t[0] for t in todo])
    ok = True
    for name, prompt, seed in todo:
        try:
            ok = kf.run_one(name, prompt, seed, log) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    log("=== style gen done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
