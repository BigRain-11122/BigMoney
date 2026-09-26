# -*- coding: utf-8 -*-
"""R259 bm-a: append progress_r259 to the T-73 ticket (byte-mirrored:
utf-8 no BOM, LF, no trailing newline, ensure_ascii=False, indent=1)."""
import io
import json

P = "fleet/tasks/T-2026-09-26-73-P1.json"
raw = io.open(P, "rb").read()
assert not raw.startswith(b"\xef\xbb\xbf") and not raw.endswith(b"\n")
d = json.loads(raw.decode("utf-8"))
assert "progress_r258" in d and "progress_r259" not in d

d["progress_r259"] = (
    "R259 bm-a: s2 slice-E style-rotation FULL ARC CLOSED (last remaining "
    "s2 empirical topic) -> s2 COMPLETE (slices A/B/C/D/E all landed with "
    "in-repo number faces). Batch T73-STYLE-ROT-S1: prereg freeze commit "
    "cb2e0e84 (runner header + SEED_REGISTRY t73_style_rot_s1 base 20261030 "
    "one-step R250 law, band-scan clean); 9-leg long-history ETF panel "
    "(510300 base + 510050/510500/512100/159915/588000/510880/512890/563300, "
    "union 5248 days, cutoff 2026-09-22). LAW: STYLE-MOM-252-63 year->"
    "quarter style momentum ALIVE both sides but THIN (IS +0.100 vs null "
    "p95 0.096, OOS +0.151 vs 0.140, 1.04x/1.08x margins, n=114/17 months "
    "k~5-6); STYLE-MOM-63-21 quarter->month NOT alive (frozen one-sided), "
    "OOS -0.192 beyond null -0.146 = quarter-scale REVERSAL face "
    "(post-hoc hypothesis, future prereg candidate, NOT a verdict). "
    "Rotation structure = dual-horizon: annual trend + quarterly "
    "mean-reversion. DESCRIPTIVE (clean_value bridge face): narrative "
    "cross-check CONFIRMED 2017 core-asset (sse50 +24.8% vs csi1000 -13.3% "
    "spread +38pp), 2024 dividend (div_lowvol +22.5% absolute best, "
    "2021-2024 FOUR-YEAR dynasty); PARTIAL 2021 growth (chinext rel +15pp "
    "but absolute winner div_lowvol +24.2%/csi1000 +22.9%); 2023 micro "
    "rel-win modest (csi2000 +9.3% vs hs300 -11.8% but corpus starts "
    "2023-09 partial window, csi1000 only rel 1.045). 2025+ era = "
    "growth/small regime (star50 rel 1.476/chinext 1.435), dividend "
    "dynasty ended 2024. Yearly leader repeats 5/14 (regime-clustered "
    "dynasties, not uniform persistence). FUND-EVENT GUARD (r239 family, "
    "envelope rule): 4 artifacts caught +248.6%/+176.3%/-51.1%/-12.7% "
    "(510500 x2, 512100, 512890; all |base-day|<1%), 20%-family real "
    "extreme days kept (159915 2024-09-30 +20% = 924 rally premium face). "
    "DEFECTS self-caught E1 x2 zero-escape: (1) run1 descriptive quoted "
    "RAW closes -> 3 artifact CAGR cells (+454%/+124%/-41%) -> clean_value "
    "bridge amendment, run1 archived defective, law faces immune "
    "(strict-window); (2) ledger self-echo trap (re-run chained onto own "
    "prev row 187687->187789 intermediate discarded in-round) -> prev = "
    "head-scan minus own-prev-batch-trials guard added. Ledger: 187585 + "
    "102 (2 judged faces + 100 permutation null draws) = 187687 "
    "single-count. trials_N 2 faces + 50 seeds. Digest research/digests/"
    "DIGEST-20260926-t73-s2-sliceE-rotation.md. Post-review registered "
    "same round (O-2115). Next: s3 remaining CN-native model consumption "
    "(CN-CORE-SATELLITE evidence base complete: ballast=lowvol all-era + "
    "dividend defense, satellite=rotation dual-scale rhythm, regime=v3 "
    "guard); 09-28 new-bar chain; 10-01 trio."
)
io.open(P, "wb").write(json.dumps(d, ensure_ascii=False, indent=1)
                       .encode("utf-8"))
print("progress_r259 written; post-write byte faces:")
raw2 = io.open(P, "rb").read()
print("BOM:", raw2.startswith(b"\xef\xbb\xbf"), "CRLF:", b"\r\n" in raw2,
      "trailing_newline:", raw2.endswith(b"\n"))
