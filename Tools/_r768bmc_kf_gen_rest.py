# -*- coding: utf-8 -*-
"""r768 bm-c continuation: generate remaining keyframes kf2_strata/kf3_unearth/
kf4_palms (kf1_carve already done by predecessor tick, 16:29). Reuses the exact
workflow/prompt/negative/seed of _r768bmc_kf_gen.py verbatim (single-source).
Detached pythonw run, own log tail in results/mv_work/kf_gen.log."""
import importlib.util
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\kf"
LOGF = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\kf_gen.log"

spec = importlib.util.spec_from_file_location(
    "kf_gen", os.path.join(HERE, "_r768bmc_kf_gen.py"))
kf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kf)


def main():
    os.makedirs(OUT, exist_ok=True)
    logf = open(LOGF, "a", encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    todo = [t for t in kf.KFS
            if not os.path.exists(os.path.join(OUT, t[0] + ".png"))]
    log("=== kf gen rest start (todo=%s) ===" % [t[0] for t in todo])
    ok = True
    for name, prompt, seed in todo:
        try:
            ok = kf.run_one(name, prompt, seed, log) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    log("=== kf gen rest done ok=%s ===" % ok)


if __name__ == "__main__":
    main()
