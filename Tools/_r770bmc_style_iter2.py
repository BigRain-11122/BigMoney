# -*- coding: utf-8 -*-
"""r770 bm-c: composite iteration-2 legs. v1 composite verdict: beat (b)(c)(d)
delivered BY CONSTRUCTION; FAIL causes = (i) Victorian glass-chimney lanterns
in base (v2-era frame lacked lamp negatives) + giant close-up face crowding
(overlay was a portrait). Fixes: (1) regen base with open-flame clay oil lamp
positives + lantern negatives; (2) regen overlay as wide-shot small full-body
figure. Then composite v2 in _r770bmc_style_composite2.py.
Pattern credit: Tools/_r770bmc_style_scribe_leg.py."""
import importlib.util
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOGF = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\style_gen.log"

spec = importlib.util.spec_from_file_location(
    "kf_gen", os.path.join(HERE, "_r768bmc_kf_gen.py"))
kf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kf)

kf.NEG = kf.NEG + (", flat illustration, vector art, poster art, watercolor, "
                   "ink wash, chinese ink painting, codex books, paper books, "
                   "paper sheets, parchment, glass chimney lamp, glass globe "
                   "lantern, hurricane lantern, kerosene lantern, metal "
                   "lantern, candlestick, hieroglyphs, egyptian, metal pen, "
                   "gray monochrome, deformed hand, close-up face portrait")

LEGS = [
    ("st1_library_base2",
     "cinematic photograph from a live-action film set, a young man seated at "
     "a wooden desk reading a clay tablet in an ancient mesopotamian archive "
     "room at night, lit by a single simple clay oil lamp with an open flame "
     "on the desk, shelf niches of stacked clay tablets on the walls, warm "
     "amber sepia monochrome grade, photographed on 35mm film, natural film "
     "grain, shallow depth of field, dust motes in lamplight, 50mm medium "
     "shot", 20011029),
    ("st1_scribe_overlay2",
     "wide shot, a robed ancient mesopotamian scribe standing full body in "
     "three-quarter view holding a clay tablet, the standing figure small in "
     "frame, dark shadowy background, warm torch light from the left, soft "
     "glow around the figure, wool kaunakes robe, bare head with rolled "
     "turban, warm amber sepia monochrome grade, 35mm film grain", 20011030),
]


def main():
    logf = open(LOGF, "a", encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    log("=== style gen v5-iter2 start (lamp-safe base + wide overlay) ===")
    ok = True
    for name, prompt, seed in LEGS:
        try:
            ok = kf.run_one(name, prompt, seed, log) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    log("=== style gen v5-iter2 done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
