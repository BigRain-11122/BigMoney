# -*- coding: utf-8 -*-
"""r770 bm-c: O-1820 style-sample v4 targeted regen. v3 verdict: all 4 FAIL --
(a) library second-figure beat: separate-figure/shadow-transform both
unrenderable; the PROVEN pass formula is st4_glass silhouette-merge
(transplant it to the archive scene); (b) carve wedge readability: human-scale
shots always mush; fix = macro texture shot (wedge geometry, no anatomy, no
'readable text' demand) + backlit silhouette writing shot.
Outputs (via kf_gen OUT binding) to results/mv_work/kf/, same lane log.
Pattern credit: Tools/_r769bmc_style_regen3.py (v3 driver)."""
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

kf.NEG = kf.NEG + (", flat illustration, vector art, paper cutout, poster art, "
                   "watercolor, ink wash, chinese ink painting, brush stroke "
                   "texture, codex books, leather bound books, paper books, "
                   "paper sheets, parchment, glass chimney lamp, "
                   "hieroglyphs, egyptian, metal pen, ballpoint pen, fountain "
                   "pen, marker, gray monochrome, cold gray grade, desaturated, "
                   "deformed hand, extra fingers, melted fingers, gibberish "
                   "squiggles")

STYLES_V4 = [
    ("st1_library_g",
     "double exposure of two overlapping eras in one frame, a young modern "
     "reader silhouette and an ancient robed scribe silhouette merging into "
     "a single seated figure at the same wooden desk in an ancient "
     "mesopotamian archive at night, clay tablet on the desk showing "
     "through both eras, single warm oil lamp flame as the only light "
     "source, warm amber sepia monochrome grade, 50mm medium shot, 2001 "
     "music video still, 35mm film grain, dust motes in lamplight", 20011024),
    ("st1_library_h",
     "double exposure of two overlapping eras in one frame, a modern reader "
     "silhouette and an ancient robed scribe silhouette merging into one "
     "seated figure reading a clay tablet by warm oil lamp light in a "
     "mesopotamian archive, shelf of clay tablets behind, warm amber sepia "
     "monochrome grade, medium shot, 2001 music video still, 35mm film "
     "grain", 20011025),
    ("st2_carve_g",
     "extreme macro photograph of a wet clay tablet surface, deep fresh "
     "triangular wedge-shaped cuneiform impressions pressed in neat "
     "horizontal rows, the cut tip of a reed stylus pressed into the clay "
     "leaving a fresh wedge mark, warm amber torchlight raking across the "
     "surface casting tiny crisp shadows inside each wedge impression, warm "
     "amber sepia monochrome grade, razor sharp macro focus, 35mm film "
     "grain, 2001 music video still", 20011026),
    ("st2_carve_h",
     "a robed scribe in full silhouette bent over a clay tablet on a low "
     "wooden desk, backlit by a single warm torch, the lit tablet surface "
     "facing the camera showing rows of wedge marks, cut reed stylus in "
     "the silhouetted hand touching the clay, warm amber sepia monochrome "
     "grade, 50mm medium shot, shallow depth of field, 35mm film grain, "
     "2001 music video still", 20011027),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    logf = open(LOGF, "a", encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    todo = [t for t in STYLES_V4
            if not os.path.exists(os.path.join(OUT, t[0] + ".png"))]
    log("=== style gen v4 start (silhouette-merge + macro-wedge, todo=%s) ===" %
        [t[0] for t in todo])
    ok = True
    for name, prompt, seed in todo:
        try:
            ok = kf.run_one(name, prompt, seed, log) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    log("=== style gen v4 done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
