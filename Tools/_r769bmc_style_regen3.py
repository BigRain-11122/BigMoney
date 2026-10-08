# -*- coding: utf-8 -*-
"""r769 bm-c: O-1820 style-sample v3 regen. v2 gate verdict: photographic +
amber-grade fixes LANDED (filmic 7-8, zero style leaks) but scene requirements
still absent: (a) library double-shadow — single-lamp physics means SDXL will
not paint a second different-person shadow; fix = double-exposure ghost (the
technique that PASSED for the glass scene, and a stronger rendering of the
scene's essence 脑补成真) + one wall-shadow-transform variant;
(b) carve ritual — macro hand anatomy is beyond SDXL-base and wedge-forming
is unreadable at macro; fix = medium close-up with the cuneiform tablet
prominent (fresh wedge rows readable, hands at low-risk scale).
Outputs (via kf_gen OUT binding) to results/mv_work/kf/, same lane log.
Pattern credit: Tools/_r769bmc_style_regen.py (v2 driver)."""
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
                   "glass lamp, modern objects, hieroglyphs, egyptian, "
                   "metal pen, ballpoint pen, fountain pen, marker, "
                   "gray monochrome, cold gray grade, desaturated, "
                   "deformed hand, extra fingers, melted fingers")

STYLES_V3 = [
    ("st1_library_e",
     "cinematic double exposure photograph from a live-action film set, "
     "ancient mesopotamian archive room at night, a young man seated at a "
     "wooden desk reading a clay tablet lit by a single warm oil lamp, "
     "overlaid in the same frame with the translucent glowing figure of a "
     "robed ancient scribe standing beside the desk, the scribe's silhouette "
     "shining softly through the scene beside the modern reader, both "
     "figures readable in one frame, imagination becoming real, warm amber "
     "sepia monochrome grade, photographed on 35mm film, natural film grain, "
     "2001 music video still, shallow depth of field, dust motes in lamplight",
     20011020),
    ("st1_library_f",
     "cinematic photograph from a live-action film set, a young man reading "
     "a clay tablet at a wooden desk in an ancient mesopotamian archive at "
     "night, his own huge shadow cast on the wall behind him has transformed "
     "into the distinct silhouette of a robed ancient scribe holding a "
     "stylus, the shadow shape clearly different from the seated man, "
     "imagination becoming real, single warm torchlight source, warm amber "
     "sepia monochrome grade, photographed on 35mm film, natural film grain, "
     "2001 music video still", 20011021),
    ("st2_carve_e",
     "cinematic photograph from a live-action film set, an ancient scribe's "
     "two hands holding a wet clay tablet covered in neat rows of fresh "
     "wedge-shaped cuneiform inscriptions, a simple cut reed pen resting "
     "across the tablet edge, warm torch light from the left bathing the "
     "scene in amber, medium close-up, sharp focus on the rows of cuneiform "
     "wedge marks, warm amber sepia monochrome grade, photographed on 35mm "
     "film, natural film grain, 2001 music video still, dust motes", 20011022),
    ("st2_carve_f",
     "cinematic photograph from a live-action film set, a robed scribe "
     "seated at a low wooden desk writing with a cut reed stylus on a wet "
     "clay tablet, fresh wedge-shaped cuneiform marks visible on the tablet "
     "surface, warm torchlight key from the left, warm amber sepia "
     "monochrome grade, 50mm medium shot, shallow depth of field, "
     "photographed on 35mm film, natural film grain, 2001 music video still",
     20011023),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    logf = open(LOGF, "a", encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    todo = [t for t in STYLES_V3
            if not os.path.exists(os.path.join(OUT, t[0] + ".png"))]
    log("=== style gen v3 start (composition redesign, todo=%s) ===" %
        [t[0] for t in todo])
    ok = True
    for name, prompt, seed in todo:
        try:
            ok = kf.run_one(name, prompt, seed, log) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    log("=== style gen v3 done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
