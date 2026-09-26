# -*- coding: utf-8 -*-
"""R258 bm-a: slice-D artifact defect reset -- discard the 3 size faces
computed with the 688 double-correction cap builder (100x too small 688
caps), rewrite prereg.size_honesty with the R258 unit amendment. Verdict +
era tables rebuilt by the corrected rerun. Vol/dividend faces untouched
(close-only / ETF-only inputs, uncontaminated)."""
import io
import json

P = "results/t73_s2/factor_history.json"
art = json.load(io.open(P, encoding="utf-8"))

dropped = []
for k in list(art["faces"].keys()):
    if k.startswith("size/"):
        dropped.append((k, art["faces"][k]["blocks"]["oos"].get("ic_mean")))
        del art["faces"][k]
print("dropped defective size faces:", dropped)

art["prereg"]["size_honesty"] = (
    "osh_est=volume/turnover_derived, NO board correction -- operative cache "
    "already normalized (amount/volume~close x1.0007 2025+ / x1.0014 "
    "2019-2021, turnover_derived[688] real-turnover magnitude; probe "
    "results/_r258bma_688_probe.py). Run1 /100 double-correction defect: 688 "
    "caps 100x too small, 3 size faces discarded + recomputed. Survivor "
    "panel -> historical small-cap premium overstated, disclosed.")

art.setdefault("defect_disclosure", []).append({
    "ts": "2026-09-26 R258",
    "defect": "run1 cap builder divided 688 volume by 100 (doc lore) while "
              "the operative cache volume column is already real shares -> "
              "688 float caps 100x too small -> size cross-section ranks "
              "contaminated for the 2019+ 688 era",
    "caught_by": "cap_sanity_last_bar disclosure leg (median 688 cap 71M "
                 "CNY implausible) + _r258bma_688_probe.py decisive anchors",
    "action": "3 size faces discarded, recomputed with corrected builder; "
              "vol faces (close-only) and dividend face (ETF-only) "
              "uncontaminated and kept; trials consumed recorded in N",
})
io.open(P, "w", encoding="utf-8", newline="\n").write(
    json.dumps(art, ensure_ascii=False, indent=1) + "\n")
print("reset done; faces remaining:", sorted(art["faces"].keys()))
