# -*- coding: utf-8 -*-
"""r769 bm-c: O-1820 style-sample v2 regen for the two scenes that FAILED the
three-law human-eye gate (r769 blind review): 书库双影 (both v1 candidates
failed: double-shadow absent, flat vector look, ink leak on b) and 刻字仪式
(kf1_carve: modern metal pen + gray grade; st2_carve_b: hieroglyphs + gray
grade + no carving action). Fixes: photographic live-action vocabulary
upfront, warm-amber grade upfront, extended negatives (flat illustration /
vector / ink-wash family / hieroglyphs / metal pen / codex books), scene
requirements restated as the central subject. best-of-2 per scene.
Mechanics reuses _r768bmc_kf_gen.py verbatim (single-source) with NEG
extended via module attribute (append-only, disclosed).
Outputs (via kf_gen OUT binding) to results/mv_work/kf/, log
results/mv_work/style_gen.log (same lane log).
Pattern credit: Tools/_r769bmc_style_gen.py (v1 batch driver)."""
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
                   "texture, codex books, modern books, paperbacks, "
                   "hieroglyphs, egyptian, cartouche, winged sun disc, "
                   "metal pen, ballpoint pen, fountain pen, marker, "
                   "gray monochrome, cold gray grade, desaturated")

STYLES_V2 = [
    ("st1_library_c",
     "cinematic photograph from a live-action film set, ancient mesopotamian "
     "archive room at night, wooden shelves stacked with clay tablets, a "
     "young man seated at a reading desk holding a small clay tablet, lit by "
     "a single warm oil lamp, TWO large distinct human shadows cast side by "
     "side on the wall behind him, one shadow of a modern young man and one "
     "shadow of a robed ancient scribe, the two shadows clearly separated "
     "and both readable, whole frame bathed in warm amber sepia tones, "
     "torchlit amber monochrome grade, photographed on 35mm film, kodak "
     "film stock, natural film grain, candid documentary photograph, 2001 "
     "music video still, shallow depth of field, dust motes in the lamp "
     "light", 20011016),
    ("st1_library_d",
     "cinematic photograph from a live-action film set, ancient mesopotamian "
     "archive room at night, wooden shelves stacked with clay tablets, a "
     "young man seated at a reading desk holding a small clay tablet, lit by "
     "a single warm oil lamp, TWO large distinct human shadows cast side by "
     "side on the wall behind him, one shadow of a modern young man and one "
     "shadow of a robed ancient scribe, the two shadows clearly separated "
     "and both readable, whole frame bathed in warm amber sepia tones, "
     "torchlit amber monochrome grade, photographed on 35mm film, kodak "
     "film stock, natural film grain, candid documentary photograph, 2001 "
     "music video still, shallow depth of field, dust motes in the lamp "
     "light", 20011017),
    ("st2_carve_c",
     "cinematic photograph from a live-action film set, extreme close-up of "
     "an ancient scribe's hand pressing a simple cut reed stylus, a plain "
     "wooden tapered reed pen, into a wet clay tablet, clear wedge-shaped "
     "cuneiform marks forming under the stylus tip, torch key light from "
     "the left bathing the whole frame in warm amber sepia tones, amber "
     "monochrome grade, photographed on 35mm film, kodak film stock, macro "
     "100mm lens feel, razor-thin depth of field, dust motes floating in "
     "the torch light, natural film grain, candid documentary photograph, "
     "2001 music video still", 20011018),
    ("st2_carve_d",
     "cinematic photograph from a live-action film set, extreme close-up of "
     "an ancient scribe's hand pressing a simple cut reed stylus, a plain "
     "wooden tapered reed pen, into a wet clay tablet, clear wedge-shaped "
     "cuneiform marks forming under the stylus tip, torch key light from "
     "the left bathing the whole frame in warm amber sepia tones, amber "
     "monochrome grade, photographed on 35mm film, kodak film stock, macro "
     "100mm lens feel, razor-thin depth of field, dust motes floating in "
     "the torch light, natural film grain, candid documentary photograph, "
     "2001 music video still", 20011019),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    logf = open(LOGF, "a", encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    todo = [t for t in STYLES_V2
            if not os.path.exists(os.path.join(OUT, t[0] + ".png"))]
    log("=== style gen v2 start (O-1820 gate-fail regen, todo=%s) ===" %
        [t[0] for t in todo])
    ok = True
    for name, prompt, seed in todo:
        try:
            ok = kf.run_one(name, prompt, seed, log) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    log("=== style gen v2 done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
