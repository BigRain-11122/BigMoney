# -*- coding: utf-8 -*-
"""R258 bm-a: T-73 ticket progress_r258 write-back.
Byte-face mirror (five-face law, probed _r258bma_ticket_probe.py):
no BOM / LF-only / indent=1 / ensure_ascii=False / NO trailing newline.
Target diff = field-increment level only."""
import io
import json

P = "fleet/tasks/T-2026-09-26-73-P1.json"
art = json.load(io.open(P, encoding="utf-8"))

art["progress_r258"] = (
    "R258 s2 slice-D = FACTOR-HISTORY three laws one-round census (fourth s2 "
    "slice closed): scripts/t73_s2_factor_history.py prereg-frozen header + "
    "selftest 10 legs + corrected batch 78.5s -> results/t73_s2/"
    "factor_history.json + digest DIGEST-20260926-t73-s2-sliceD-factor-"
    "history.md. SIZE law = float-cap IC census (cap=close_ffill*volume/"
    "turnover_derived osh back-solve) ALIVE BOTH SIDES: SIZE/h10 OOS ic "
    "-0.0566 (35x 1.6bp thr) IS -0.0470, gates v2 single-fail (IS ir "
    "0.246<0.30), size/h20 variant ALL-GATES pass (descriptive family fact, "
    "judged face stays h10 frozen); era table 2017-2020 INVERSION +0.0075 "
    "(core-asset era, law regime-dead 4y) vs 2015-2016 -0.1125 peak, 2025+ "
    "alive. R258 unit amendment in header+runs log+defect_disclosure: cache "
    "volume ALREADY normalized (amount/volume~close x1.0007 2025+ / x1.0014 "
    "2019-2021 anchors, probe _r258bma_688_probe.py; doc 688-100x lore = "
    "raw-bars face only) -> run1 /100 double-correction caught by cap_sanity "
    "leg (688 median cap 71M CNY implausible), 3 size faces discarded + "
    "recomputed, N=13 IC computations consumed honest (10 in final artifact). "
    "LOWVOL law = VOL60/h10 ALIVE BOTH SIDES OOS -0.0479 IS -0.0495 (30x/31x), "
    "gates v2 fail (ir 0.216), ALL-SIX-ERAS negative no inversion (only s2 "
    "law never to flip: pre2005 -0.034 .. 2021-2024 -0.088 strongest .. 2025+ "
    "-0.048). DIVIDEND = 510880vs510300 style-history era face (no yield "
    "cross-section in-repo, honest proxy; price face understates dividend "
    "style = bias against law): full-window excess ~-0.05%/yr, 2021-2024 "
    "+12.39%/yr (dividend era), 2017-2020 -11.63% (core-asset era), 2025+ "
    "-8.63% REVERSAL in case, cy2024 price-face -3.82% (distributions ~4-5% "
    "excluded, total-return likely positive, bias note). corr(size,vol60 "
    "daily IC)=-0.158 non-collinear. Anti-repeat pre-build verified: no raw "
    "size/vol law-census face in P-1c/d/e; low_vol_long(60,5)=6-member "
    "strategy face cross-cited; 510880/512890 rotation judged negative R252 "
    "(different face). Design inputs: CORE-SATELLITE ballast negative-"
    "selection feature family complete (low-vol six-era + low-turnover "
    "slice-C + size OOS); bare-factor exposure banned (size 2017-2020 + "
    "dividend dual-segment reversals in case); factor-alive != rotation-"
    "tradable (div_lowvol MA200-gate double-MISS precedent). NEXT SLICE "
    "(exact resume): s2 finale = STYLE-ROTATION history (2017 core-asset / "
    "2021 growth / 2023 microcap / 2024 dividend via data/daily 700+ ETF "
    "corpus in-repo windows) -> s2 chain closes; then CORE-SATELLITE prereg "
    "decision (satellite supply absent per T-57 0/25 -- feature-family "
    "direct-freeze option per digest sect4); T-82 deep-shard branch still "
    "not on origin (armed each S0.5); 09-28 Monday new-bar chain; 10-01 "
    "month trio + v3 date gate")

io.open(P, "w", encoding="utf-8", newline="\n").write(
    json.dumps(art, ensure_ascii=False, indent=1))
print("written; keys:", len(art))
