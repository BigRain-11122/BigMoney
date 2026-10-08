# -*- coding: utf-8 -*-
"""r774 bm-c: MV-0001 A-direction pre-start batch (ORD 10-08 19:25 item-4:
library/glass/goddess white-dress vs smoke-cyan dual / carve quick-cut
alternatives -- local SDXL rolling output, O-1715 self-decision authority,
CEO picks later, products reusable either way).
Design per REVIEW-PACKAGE-v1 option-A + blind-eval verdicts:
- st3_goddess_c/d: WHITE-ROBE dual-seed pair (dress color = CEO decision
  point; existing b version keeps the smoke-cyan read as the other half of
  the dual menu);
- st4_glass_c: cyan plate narrowed (glass_a 7/7/7 flaw = plate slightly
  large);
- st1_library_base3: clean base (v2 lamp already fixed; v2 failure column
  drifted to hieroglyphs -> plain mud-brick walls, no carved reliefs);
- st1_scribe_overlay3: ISOLATED scribe silhouette on pure black (screen-
  blend-safe: black contributes nothing) -> z composite = base3 + overlay
  scaled ~45% placed opposite the reader (deterministic brightness split),
  alpha 0.6 -- mechanical fix of x/y failures (portrait too large / same-
  position collision);
- st2_carve_i/j: quick-cut alternatives (i = pure hand+stylus silhouette
  rim-lit, text weak BY DESIGN per C-hint; j = top-down abstract
  impressions, cuneiform illegibility honest at macro).
Mechanics reuses Tools/_r768bmc_kf_gen.py verbatim (single-source: wf/NEG/
run_one, SDXL base 1024x576, seed-locked). NEG extended per regen3 + cyan-
dress block (white-robe pair only affected; glass keeps its cyan accent).
Outputs via kf OUT binding to results/mv_work/kf/, log style_gen.log.
Composite + manifest at end. Pattern credit: _r769bmc_style_regen3.py."""
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

STYLES_V6 = [
    ("st3_goddess_c",
     "female deity manifesting from golden light and drifting dust on an "
     "ancient stone bridge at night, flowing WHITE robes forming out of mist, "
     "pure white gown luminous against the darkness, distinct human "
     "silhouette with one gently raised hand, warm torch glow from below "
     "the bridge, backlit volumetric rays, 50mm medium shot, warm amber "
     "monochrome with the white gown as the brightest element, 2001 music "
     "video still, 35mm film grain", 20011024),
    ("st3_goddess_d",
     "female deity manifesting from golden light and drifting dust on an "
     "ancient stone bridge at night, flowing WHITE robes forming out of mist, "
     "pure white gown luminous against the darkness, distinct human "
     "silhouette with one gently raised hand, warm torch glow from below "
     "the bridge, backlit volumetric rays, 50mm medium shot, warm amber "
     "monochrome with the white gown as the brightest element, 2001 music "
     "video still, 35mm film grain", 20011025),
    ("st4_glass_c",
     "double exposure through textured ancient glass, two overlapping eras "
     "in one frame, a modern reader silhouette and an ancient scribe "
     "silhouette merging into a single figure, clay tablet texture showing "
     "through the glass, warm torch light dominating the frame, only a "
     "NARROW BAND of glass-cyan refraction along one thin edge as the sole "
     "cold accent, cyan area small and confined, 50mm medium close shot, "
     "warm amber monochrome, 2001 music video still, 35mm film grain",
     20011026),
    ("st1_library_base3",
     "cinematic photograph from a live-action film set, ancient mesopotamian "
     "archive room at night, a young man seated at a wooden reading desk "
     "holding a clay tablet, lit by a single warm clay oil lamp with an open "
     "flame, plain smooth mud-brick walls with no carved reliefs, simple "
     "wooden columns, tall wooden shelves stacked with clay tablets in the "
     "background, warm amber sepia monochrome grade, 35mm medium wide shot, "
     "deep shadows, photographed on 35mm film, natural film grain, 2001 "
     "music video still, dust motes in lamplight", 20011027),
    ("st1_scribe_overlay3",
     "isolated full-body silhouette of a robed ancient mesopotamian scribe "
     "standing and holding a cut reed stylus, pure solid black background, "
     "figure outlined by warm rim light only, no background scenery, no "
     "room, centered single figure, warm amber monochrome, 2001 music video "
     "still, 35mm film grain", 20011028),
    ("st2_carve_i",
     "cinematic photograph from a live-action film set, extreme close-up "
     "pure silhouette of a hand holding a cut reed stylus pressed onto a "
     "wet clay tablet, figure and tablet as dark shapes outlined by warm "
     "torch rim light from the left, glowing torch flame bokeh in the far "
     "background, marks on the tablet kept in shadow and unreadable by "
     "design, warm amber sepia monochrome grade, photographed on 35mm film, "
     "natural film grain, 2001 music video still", 20011029),
    ("st2_carve_j",
     "cinematic photograph from a live-action film set, overhead top-down "
     "shot of a large wet clay tablet on a wooden desk, two hands pressing "
     "a cut reed stylus onto the surface leaving fresh abstract wedge "
     "impressions, impressions intentionally soft and impressionistic, "
     "torch light raking from the frame edge, long dramatic shadows, warm "
     "amber sepia monochrome grade, photographed on 35mm film, natural film "
     "grain, 2001 music video still, dust motes", 20011030),
]


def composite_z(log):
    """library z composite: base3 + overlay3 scaled 45%, placed opposite the
    reader (deterministic brightness split), screen blend alpha 0.6."""
    from PIL import Image, ImageChops
    base_p = os.path.join(KFDIR, "st1_library_base3.png")
    over_p = os.path.join(KFDIR, "st1_scribe_overlay3.png")
    base = Image.open(base_p).convert("RGB")
    over = Image.open(over_p).convert("RGB")
    W, H = base.size
    # reader/lamp side = brighter half of the bottom 2/3 of base3
    import numpy as np
    arr = np.asarray(base.convert("L"), dtype=float)
    band = arr[int(H * 0.3):int(H * 0.9), :]
    left_mean = band[:, : W // 2].mean()
    right_mean = band[:, W // 2:].mean()
    side = "right" if left_mean >= right_mean else "left"
    # scale overlay so the figure is clearly secondary (~45% frame width)
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
    comp = Image.blend(base, screen, 0.6)
    out_p = os.path.join(KFDIR, "st1_library_z_composite.png")
    comp.save(out_p)
    log("COMPOSITE z side=%s left_mean=%.1f right_mean=%.1f -> %s (%d B)"
        % (side, left_mean, right_mean, out_p, os.path.getsize(out_p)))
    return {"side": side, "left_mean": round(left_mean, 1),
            "right_mean": round(right_mean, 1),
            "scale": scale, "alpha": 0.6,
            "out": "st1_library_z_composite.png",
            "bytes": os.path.getsize(out_p)}


def main():
    logf = open(LOGF, "a", encoding="utf-8")

    def log(msg):
        logf.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
        logf.flush()

    todo = [t for t in STYLES_V6
            if not os.path.exists(os.path.join(KFDIR, t[0] + ".png"))]
    log("=== style gen v6 start (A-direction pre-start ORD-19:25, todo=%s) ==="
        % [t[0] for t in todo])
    ok = True
    for name, prompt, seed in todo:
        try:
            ok = kf.run_one(name, prompt, seed, log) and ok
        except Exception as exc:
            log("EXC %s: %r" % (name, exc))
            ok = False
    comp_info = None
    if ok:
        try:
            comp_info = composite_z(log)
        except Exception as exc:
            log("EXC composite_z: %r" % exc)
            ok = False
    manifest = {"round": "r774 bm-c", "lane": "A-direction pre-start (ORD 19:25)",
                "generated": [t[0] for t in todo],
                "ok": ok, "composite": comp_info,
                "neg_extended": "regen3 + cyan-dress block",
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    mp = os.path.join(KFDIR, "style_v6_manifest.json")
    with open(mp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
    log("=== style gen v6 done ok=%s manifest=%s ===" % (ok, mp))
    print("V6_DONE ok=%s n=%d composite=%s" % (ok, len(todo), comp_info))


if __name__ == "__main__":
    main()
