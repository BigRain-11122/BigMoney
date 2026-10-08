# -*- coding: utf-8 -*-
"""r770 bm-c: O-1820 library double-shadow composite legs.
Leg-1: generate a single standing-scribe frame (single figure = SDXL-proven
easy) to serve as the overlay layer.
Leg-2 (separate script): PIL composite base=st1_library_c (v2 clean filmic
archive frame) + overlay=scribe frame at screen/soft-light blend = the
double-shadow beat guaranteed BY CONSTRUCTION (no model capability demanded).
Pattern credit: Tools/_r770bmc_style_regen4.py (driver mechanics)."""
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
                   "paper sheets, parchment, glass chimney lamp, hieroglyphs, "
                   "egyptian, metal pen, gray monochrome, deformed hand")

PROMPT = ("a robed ancient mesopotamian scribe standing and holding a clay "
          "tablet, seen in three-quarter view, warm torch light from the "
          "left, dark shadowy archive background, wool kaunakes robe with "
          "fringed hem, bare head with rolled turban, warm amber sepia "
          "monochrome grade, 50mm full shot, 2001 music video still, 35mm "
          "film grain, soft glow around the figure")

NAME = "st1_scribe_overlay"
SEED = 20011028


def main():
    logf = open(LOGF, "a", encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    log("=== style gen v5-composite-leg start (single scribe overlay frame) ===")
    try:
        ok = kf.run_one(NAME, PROMPT, SEED, log)
    except Exception as exc:
        log("EXC %s: %r" % (NAME, exc))
        ok = False
    log("=== style gen v5-composite-leg done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
