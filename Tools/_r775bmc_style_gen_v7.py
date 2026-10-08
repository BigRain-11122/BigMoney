# -*- coding: utf-8 -*-
"""r775 bm-c: MV-0001 A-direction rolling continuation batch v7 (next-ptr
item-3: glass cyan-silver retry seed family + goddess white-robe second-seed
pick-of-two + z4 ghost-transparency one-notch-down tweak). O-1715 self-decision
authority, CEO picks later, products reusable either way. Reuses existing
r774 base3/overlay3 for the z4 composite (alpha 0.6 -> 0.45, ghost one notch
more transparent; brightness-split side logic identical to z3). Mechanics
reuses Tools/_r768bmc_kf_gen.py verbatim (single-source: run_one, SDXL base
1024x576, seed-locked); NEG = v6 face unchanged (white-robe pair + cyan-dress
block; glass keeps its cyan refraction accent as scene element).
Outputs via kf OUT binding to results/mv_work/kf/, log style_gen.log.
Pattern credit: _r774bmc_style_gen_v6.py."""
import importlib.util
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
KFDIR = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work\kf"
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
                   "deformed hand, extra fingers, melted fingers, "
                   "cyan dress, teal gown, blue robes")

STYLES_V7 = [
    # goddess white-robe second seed: pick-of-two against c (7/8/7)
    ("st3_goddess_e",
     "female deity manifesting from golden light and drifting dust on an "
     "ancient stone bridge at night, flowing WHITE robes forming out of mist, "
     "pure white gown luminous against the darkness, distinct human "
     "silhouette with one gently raised hand, warm torch glow from below "
     "the bridge, backlit volumetric rays, 50mm medium shot, warm amber "
     "monochrome with the white gown as the brightest element, 2001 music "
     "video still, 35mm film grain", 20011031),
    # glass lane retry: cyan confined to a THIN SLIVER at one extreme edge
    # (glass_c 7/8/5 failure = cyan window overrun; this narrows to a corner
    # sliver strictly under 5% of frame area, warm torch light dominates)
    ("st4_glass_d",
     "double exposure through textured ancient glass, two overlapping eras "
     "in one frame, a modern reader silhouette and an ancient scribe "
     "silhouette merging into a single figure, clay tablet texture showing "
     "through the glass, warm torch light filling the frame, only a THIN "
     "SLIVER of glass-cyan refraction confined to the extreme lower-left "
     "corner edge, cyan strictly tiny and confined under 5 percent of "
     "frame area, 50mm medium close shot, warm amber monochrome, 2001 "
     "music video still, 35mm film grain", 20011032),
]


def composite_z4(log):
    """library z4 composite: base3 + overlay3 scaled 45%, placed opposite the
    reader (same deterministic brightness split as z3), screen blend alpha
    0.45 -- ghost transparency one notch DOWN from z3's 0.6."""
    from PIL import Image, ImageChops
    base_p = os.path.join(KFDIR, "st1_library_base3.png")
    over_p = os.path.join(KFDIR, "st1_scribe_overlay3.png")
    base = Image.open(base_p).convert("RGB")
    over = Image.open(over_p).convert("RGB")
    W, H = base.size
    import numpy as np
    arr = np.asarray(base.convert("L"), dtype=float)
    band = arr[int(H * 0.3):int(H * 0.9), :]
    left_mean = band[:, : W // 2].mean()
    right_mean = band[:, W // 2:].mean()
    side = "right" if left_mean >= right_mean else "left"
    scale = 0.45
    ow, oh = int(W * scale), int(H * scale)
    over_small = over.resize((ow, oh), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    if side == "right":
        pos = (int(W * 0.52), int(H * 0.30))
    else:
        pos = (int(W * 0.03), int(H * 0.30))
    canvas.paste(over_small, pos)
    screen = ImageChops.screen(base, canvas)
    comp = Image.blend(base, screen, 0.45)
    out_p = os.path.join(KFDIR, "st1_library_z4_composite.png")
    comp.save(out_p)
    log("COMPOSITE z4 side=%s left_mean=%.1f right_mean=%.1f -> %s (%d B)"
        % (side, left_mean, right_mean, out_p, os.path.getsize(out_p)))
    return {"side": side, "left_mean": round(left_mean, 1),
            "right_mean": round(right_mean, 1),
            "scale": scale, "alpha": 0.45,
            "out": "st1_library_z4_composite.png",
            "bytes": os.path.getsize(out_p)}


def main():
    logf = open(LOGF, "a", encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    todo = [t for t in STYLES_V7
            if not os.path.exists(os.path.join(KFDIR, t[0] + ".png"))]
    log("=== style gen v7 start (A-direction rolling cont, todo=%s) ==="
        % [t[0] for t in todo])
    ok = True
    for name, prompt, seed in todo:
        try:
            ok = kf.run_one(name, prompt, seed, log) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    comp_info = None
    if ok and os.path.exists(os.path.join(KFDIR, "st1_library_base3.png")) \
            and os.path.exists(os.path.join(KFDIR, "st1_scribe_overlay3.png")):
        try:
            comp_info = composite_z4(log)
        except Exception as exc:
            log("EXC composite_z4: %r" % exc)
            ok = False
    elif ok:
        log("SKIP composite_z4: r774 base3/overlay3 faces missing")
    manifest = {"round": "r775 bm-c", "lane": "A-direction rolling continuation",
                "generated": [t[0] for t in todo],
                "ok": ok, "composite": comp_info,
                "neg_extended": "v6 face unchanged",
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    mp = os.path.join(KFDIR, "style_v7_manifest.json")
    with open(mp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
    log("=== style gen v7 done ok=%s manifest=%s ===" % (ok, mp))
    print("V7_DONE ok=%s n=%d composite=%s" % (ok, len(todo), comp_info))


if __name__ == "__main__":
    main()
