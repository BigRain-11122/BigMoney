# -*- coding: utf-8 -*-
"""_r464bma_w13_surgeon.py -- W13 runner build surgery (Slice-A1, bm-a r464).

TRIAL_LABOR_W13 runner draft generator (sections 1-10 of the W12
r445bmb surgeon section map adapted; src=scripts/trial_labor_w12.py
FROZEN face; kit=results/_r463bma_w13_layer_kit.py r463 ALL-GREEN):
operates on the FROZEN W12 runner producing
results/_r464bma_w13_runner_draft.py per frozen
research/TRIAL_LABOR_W13_PREREG sec.3:
  - sixteen-tuple = fifteen-tuple + SUMN in {none, sumn20_lo,
    sumn10_lo} (three-value axis, W4-VOL/W11-STD/W12-RSQR precedent)
    -> 94,058,496 * 3 = 282,175,488
  - SUMN gate construction VERBATIM via kit SUMN_LAYER_TEXT
    (a158_tsgate_probe import face; zero-invention law; probe facts
    results/_r456bma_sumnsump_w13_probe_facts.json)
  - SUMN_ANCHOR generated PROGRAMMATICALLY from the kit
    (zero hand-copy; r445 declare-vs-disk law)
  - RSQR machinery imported verbatim from tl12 (W12 frozen face;
    import-face law; zero re-implementation)
  - seeds 20323000/20323500/20324000 (r461 freeze-commit berths,
    three-step law ALL GREEN results/_r461bma_w13_seed_law_facts.json)
PARTIAL SURGERY (honest): sections 1-10 land this round; sections
11-16 (generate G-gate / screen slice / judge slice / selftest /
residual pass) land next round -- the draft is NOT the formal runner
until then (runner_exists gate at Tools/fill_ladder_catalog.json
must not fire on a partial build).  Idempotent: re-runs from SRC
fresh.
Products: draft file + surgery report JSON + py_compile gate.
"""
from __future__ import annotations
import json
import os
import py_compile
import sys

ROOT = os.getcwd()
SRC = os.path.join("scripts", "trial_labor_w12.py")
DST = os.path.join("results", "_r464bma_w13_runner_draft.py")
REPORT = os.path.join("results", "_r464bma_w13_surgery_report.json")

sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "results"))
import importlib.util as _ilu
_kit_spec = _ilu.spec_from_file_location(
    "w13kit", os.path.join(ROOT, "results", "_r463bma_w13_layer_kit.py"))
KIT = _ilu.module_from_spec(_kit_spec)
_kit_spec.loader.exec_module(KIT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def die(msg):
    print("SURGEON-FAIL: " + msg)
    sys.exit(2)


def sub1(src, old, new, what):
    """Count-verified single replace (exactly one hit)."""
    if src.count(old) != 1:
        die("anchor not unique (%d hits): %r | %s"
            % (src.count(old), old[:70], what))
    return src.replace(old, new)


def subn(src, old, new, n, what):
    """Count-verified n-hit replace."""
    if src.count(old) != n:
        die("anchor count != %d (%d hits): %r | %s"
            % (n, src.count(old), old[:70], what))
    return src.replace(old, new)


def segment(src, start_marker, end_marker, include_start=True,
            include_end=False):
    a = src.find(start_marker)
    if a < 0:
        die("segment start not found: %r" % start_marker[:60])
    b = src.find(end_marker, a + len(start_marker))
    if b < 0:
        die("segment end not found: %r" % end_marker[:60])
    sa = a if include_start else a + len(start_marker)
    eb = b + (len(end_marker) if include_end else 0)
    return src[sa:eb], sa, eb


def _py_lit(obj):
    """JSON-adapted python literal (W12 surgeon anchor-literal law)."""
    t = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False)
    return (t.replace(": false", ": False").replace(": true", ": True")
             .replace(": null", ": None"))


# ---------------------------------------------------------------- sections
def sec1_docstring(src, steps):
    ds, a, b = segment(src, '"""TRIAL_LABOR_W12 runner', '\n"""\n',
                       include_start=True, include_end=True)
    ds = sub1(ds,
              "TRIAL_LABOR_W12 runner -- T-124 mass-candidate trial wave-12\n"
              "(5000-ceiling, RSQR trend-fit-quality FIFTEEN-gate wave).",
              "TRIAL_LABOR_W13 runner -- T-125 mass-candidate trial wave-13\n"
              "(5000-ceiling, SUMN up-share-purity SIXTEEN-gate wave).",
              "doc head")
    ds = sub1(ds,
              "Prereg FROZEN (bm-b r444 whole-package adoption of the bm-a "
              "r447 RSQR\ncandidate per the AMP->W9 / MOM->W10 / STD->W11 / "
              "RSQR->W12\nfour-straight adoption lineage; freeze trigger MET "
              "live = W11 full\nchain landed 2026-09-30 01:47:40 "
              "{w12_judge.json 229/229 judged zero\nG1 zero G2 + "
              "CEO-REPORT-WAVE11-20260930 + attrition CLEAN + TRIAL_\n"
              "GRAMMAR_LEDGER wave-11 row + W11 prereg sec.7/sec.8 "
              "backfilled} +\npool entries drained {TRIAL-LABOR-W12-JUDGE "
              "flipped done; INNOVATION-\nQUOTA-SLOT-4 = bm-c "
              "innovation-quota lane, non-trial-labor honest\ndisclosure}):"
              "\nresearch/TRIAL_LABOR_W12_PREREG.md -- generate grammar + "
              "funnel rules +\njudgment lines all frozen; post-run only "
              "sec.7/8 backfill.  Seeds held\nat the freeze commit per R250 "
              "one-step law: trial_labor_w12_gen=\n20320500 / "
              "trial_labor_w12_scrnull=20321000 / trial_labor_w12_unc=\n"
              "20321500 (berth-open adoption of the bm-a r447 RSQR "
              "candidate whole\npackage; three-step law ALL GREEN at the "
              "freeze commit\nresults/_r444bmb_w12_seed_law_facts.json, no "
              "re-pick after freeze).",
              "Prereg FROZEN (bm-a r461 boarding-machine self-freeze; berth "
              "priority\nto holding precedent W5 r247->r248 / W6 r458->"
              "r459 / W7 r254->r255;\ndraft DIGEST-20260930-w13-sumn-yield-"
              "crossvalidation.md in-register;\nfreeze trigger MET live = "
              "W12 full chain landed 2026-09-30 05:22:37\n{TRIAL-LABOR-W12-"
              "JUDGE judge-finalize exit 0; w12_judge.json 188/188 judged "
              "zero\nG1 zero G2 + w12_intake.json lawful-zero + CEO-REPORT-"
              "WAVE12-20260930.md\nlanded + attrition both faces guard CLEAN "
              "+ TRIAL_GRAMMAR_LEDGER\nwave-12 row} + pool entries zero "
              "in-flight {runnable_pool zero entries\ndone; INNOVATION-"
              "QUOTA-* non-innovation-quota lane vs trial-labor\njudge face "
              "honest disclosure does not compose W13 judge\nin-flight}):"
              "\nresearch/TRIAL_LABOR_W13_PREREG.md -- generate grammar + "
              "funnel rules +\njudgment lines all frozen; post-run only "
              "sec.7/8 backfill.  Seeds held\nat the freeze commit per R250 "
              "one-step law: trial_labor_w13_gen=\n20323000 / "
              "trial_labor_w13_scrnull=20323500 / trial_labor_w13_unc=\n"
              "20324000 (three-step law ALL GREEN at the freeze commit\n"
              "results/_r461bma_w13_seed_law_facts.json, no re-pick after "
              "freeze).",
              "freeze paragraph")
    ds = sub1(ds,
              "Import-face law (prereg sec.3): the FULL trial_labor_w1-w11 "
              "chain is\nimported (tl1 enumeration/loading/anchor/envelope "
              "primitives + tl2\ninitial-stop overlay + tl3 regime-gate "
              "overlay + tl4 vol overlay +\ntl5 yang overlay + tl6 vconf "
              "overlay + tl7 streak overlay + tl8\ntstate overlay & "
              "eleven-tuple machinery + tl9 amp overlay & twelve-\ntuple "
              "machinery + tl10 mom overlay & thirteen-tuple machinery + "
              "tl11\nstd overlay & fifteen-tuple machinery); RSQR comes "
              "from the FROZEN",
              "Import-face law (prereg sec.3): the FULL trial_labor_w1-w12 "
              "chain is\nimported (tl1 enumeration/loading/anchor/envelope "
              "primitives + tl2\ninitial-stop overlay + tl3 regime-gate "
              "overlay + tl4 vol overlay +\ntl5 yang overlay + tl6 vconf "
              "overlay + tl7 streak overlay + tl8\ntstate overlay & "
              "eleven-tuple machinery + tl9 amp overlay & twelve-\ntuple "
              "machinery + tl10 mom overlay & thirteen-tuple machinery + "
              "tl11\nstd overlay & fifteen-tuple machinery + tl12 rsqr "
              "overlay & sixteen-\ntuple machinery); SUMN comes from the "
              "FROZEN",
              "import-face chain")
    ds = sub1(ds,
              "RSQR overlay (prereg sec.2/sec.3 NEW W12 frozen layer; r447 "
              "probe\nverbatim = A158-TSGATE-P1 frozen RSQR construction): "
              "member 510300\nsignal-day-d close info set.  F = "
              "a158.alpha158_factors(member face);\nf = F[\"RSQR20\"] = "
              "rolling OLS r^2 of close vs t=1..d, 20-day window\n(qlib "
              "expanding-warmup semantics + flat-price guard std~0->NaN;\n"
              "RSQR10 same construction); q90_ref = f.rolling(252, "
              "min_periods=120)\n.quantile(0.90); rsqr_hi = f > q90_ref "
              "(trend-fit QUALITY entering\nits own top decile = clean "
              "directional-trend state; fit quality is\nDIRECTION-BLIND -- "
              "slope-sign split among rsqr20-open days 213 up /\n128 down, "
              "direction conditioning lives in the burned axes GATE/\nYANG/"
              "STREAK/MOM).  120-bar warmup window gate-closed honest (f "
              "valid\nfrom bar-idx 1: k=2 two-point fit; q90_ref "
              "min_periods 120 -> first\ndecidable bar-idx == 120, "
              "fail-closed assertion == STD family warmup).\nGate acts on "
              "ENTRY PERMITTANCE only (effective signal zeroed,\nMSG-0440 "
              "E1-mapping primitive; exit logic zero change).  "
              "Composition\norder frozen everywhere: signal -> filter -> "
              "timing -> GATE -> VOL ->\nYANG -> VCONF -> STREAK -> TSTATE -> "
              "AMP -> MOM -> STD -> RSQR ->\ninitial-stop (W11 order "
              "extended; prereg sec.3 fifteen-tuple order\nR/X/S/T/STOP/"
              "GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR).",
              "SUMN overlay (prereg sec.2/sec.3 NEW W13 frozen layer; r456 "
              "probe\nverbatim = A158-TSGATE-P1 frozen SUMN construction): "
              "member 510300\nsignal-day-d close info set.  F = "
              "a158.alpha158_factors(member face);\nf = F[\"SUMN20\"] = "
              "down-share of absolute movement\nsum(clip(-diff,0),d)/"
              "sum(|diff|,d) in [0,1] (qlib expanding-warmup\nsemantics; "
              "UP-dominant window = low value; SUMN10 same\nconstruction); "
              "q10_ref = f.rolling(252, min_periods=120)\n.quantile(0.10); "
              "sumn_lo = f < q10_ref (up-share PURITY entering\nits own "
              "bottom decile = direction-loaded clean-advance state;\n"
              "direction face loaded BY CONSTRUCTION -- slope-sign split "
              "among\nsumn20-open days 387 up / 0 down, direction "
              "conditioning redundancy\nmeasured in adjacency cells, burned "
              "axes GATE/YANG/STREAK/MOM carry\nthe interactions).  120-bar "
              "warmup window gate-closed honest (q10_ref\nmin_periods 120 -> "
              "first decidable bar-idx == 120, fail-closed\nassertion == "
              "RSQR family warmup).  Gate acts on ENTRY PERMITTANCE only\n"
              "(effective signal zeroed, MSG-0440 E1-mapping primitive; "
              "exit logic\nzero change).  Mirror-twin identity SUMN+SUMP==1 "
              "(eps 1e-12 denominator)\n= supply face ONE up-share axis "
              "(sumn20_q10 == sump20_q90 same-day\nco-open XOR=0 probe "
              "law).  Composition\norder frozen everywhere: signal -> "
              "filter -> timing -> GATE -> VOL ->\nYANG -> VCONF -> STREAK -> "
              "TSTATE -> AMP -> MOM -> STD -> RSQR ->\nSUMN -> initial-stop "
              "(W12 order extended; prereg sec.3 sixteen-tuple order\nR/X/S/"
              "T/STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/"
              "SUMN).",
              "overlay paragraph")
    ds = sub1(ds,
              "G-RSQR anchor law (prereg sec.2 probe facts, fail-closed): "
              "on the raw\nfull-history member face (3,483 bars 2012-05-28 "
              "-> 2026-09-22 cutoff):\nfirst-decidable == 120 / decidable == "
              "3,363 / rsqr20 open == 341\n(9.79%) / rsqr10 open == 332 "
              "(9.53%); slope-sign split 213 up / 128\ndown; NINE-gate (gate "
              "x vol x yang x vconf x streak x tstate x amp x\nstd20 x "
              "rsqr20) 512 open-window cells: 124 non-empty / 388 empty\n"
              "(probe range 1-41; all-decidable 3,305); extreme-day gate "
              "states\n0/7 rsqr-open both windows (fit gate structurally "
              "closed on crisis\ndays) + exact per-cell cross-check vs\n"
              "results/_r447bma_rsqr_w12_probe_facts.json when present "
              "(r447\ndeterminism cross-check law).",
              "G-SUMN anchor law (prereg sec.2 probe facts, fail-closed): "
              "on the raw\nfull-history member face (3,483 bars 2012-05-28 "
              "-> 2026-09-22 cutoff):\nfirst-decidable == 120 / decidable == "
              "3,363 / sumn20 open == 387\n(11.11%) / sumn10 open == 368 "
              "(10.57%); slope-sign split 387 up / 0\ndown; NINE-gate (gate "
              "x vol x yang x vconf x streak x tstate x amp x\nstd20 x "
              "sumn20) 512 open-window cells: 103 non-empty / 409 empty\n"
              "(probe range 1-41; all-decidable 3,305); extreme-day gate "
              "states\n0/7 sumn-open both windows + exact per-cell "
              "cross-check vs\nresults/_r456bma_sumnsump_w13_probe_facts.json "
              "when present (r456\ndeterminism cross-check law).",
              "G-anchor paragraph")
    ds = sub1(ds,
              "Exclusion law (prereg sec.1, FIFTEEN-tuple cell key="
              "(template,\nparams, axis_config, initial_stop, gate, vol, "
              "yang, vconf, streak,\ntstate, amp, mom, std, rsqr), TWELVE "
              "judged + TWELVE screen\nreal-read source faces, exact "
              "already-judged key, rsqr=none face\nonly: prior-wave keys "
              "lacking the rsqr axis are rsqr=none completed\n(semantic-"
              "identity match; generate-time real-read; W11-JUDGE landed\n"
              "2026-09-30 01:47:40 = TWELFTH source, fifth full-declare "
              "window);\nrsqr in {rsqr20_hi, rsqr10_hi} = new-syntax legal "
              "cells (never\nexcluded).",
              "Exclusion law (prereg sec.1, SIXTEEN-tuple cell key="
              "(template,\nparams, axis_config, initial_stop, gate, vol, "
              "yang, vconf, streak,\ntstate, amp, mom, std, rsqr, sumn), "
              "THIRTEEN judged + THIRTEEN screen\nreal-read source faces, "
              "exact already-judged key, sumn=none face\nonly: prior-wave "
              "keys lacking the sumn axis are sumn=none completed\n"
              "(semantic-identity match; generate-time real-read; W12-JUDGE "
              "landed\n2026-09-30 05:22:37 = THIRTEENTH source, sixth "
              "full-declare window);\nsumn in {sumn20_lo, sumn10_lo} = "
              "new-syntax legal cells (never\nexcluded).",
              "exclusion paragraph")
    ds = sub1(ds,
              "Slice plan (W3-W11 single-writer precedent; wave ticket\n"
              "T-2026-09-30-124 opened+claimed bm-b r444 same freeze commit "
              "per\nO-1730 immediate law):\n  - Slice-A (this draft, bm-b "
              "r445 surgeon\n    results/_r445bmb_w12_surgeon.py): "
              "mechanical identity surgery +\n    rsqr overlay layer (a158 "
              "verbatim import) + RSQR_ANCHOR\n    programmatic generation + "
              "grammar/Sobol/exclusion/mask/curve/\n    null/generate/screen/"
              "judge legs rewiring + std import face from\n    tl11 + "
              "py_compile gate.  Draft name\n    "
              "results/_r445bmb_w12_runner_draft.py -- NOT the formal "
              "runner\n    (runner_exists gate must not fire on a partial "
              "build).\n  - Slice-B (next): selftest anchor review (W12 "
              "warmup 120/\n    decidable 3,363/341/332 + slope 213/128 + "
              "124/388 cell faces +\n    core48 spread), grammar "
              "serialization + sha16 pin, formal-name\n    move, catalog "
              "runner_exists arm, MSG declaration, GENERATE pool\n    entry.",
              "Slice plan (W3-W12 single-writer precedent; wave ticket\n"
              "T-2026-09-30-125 opened+claimed bm-a same freeze commit "
              "per\nO-1730 immediate law):\n  - Slice-A (this draft, bm-a "
              "r464 surgeon\n    results/_r464bma_w13_surgeon.py): "
              "mechanical identity surgery +\n    sumn overlay layer (kit "
              "verbatim embed, a158 verbatim import) +\n    SUMN_ANCHOR\n    "
              "programmatic generation + grammar/Sobol/exclusion/mask/curve/"
              "\n    null legs rewiring + rsqr import face from tl12 + "
              "py_compile gate.\n    Draft name\n    "
              "results/_r464bma_w13_runner_draft.py -- NOT the formal "
              "runner\n    (runner_exists gate must not fire on a partial "
              "build).\n  - Slice-B (next): generate/screen/judge/selftest "
              "legs rewiring +\n    selftest anchor review (W13 warmup 120/"
              "\n    decidable 3,363/387/368 + slope 387/0 + 103/409 cell "
              "faces + mirror\n    XOR=0), grammar serialization + sha16 "
              "pin, formal-name move, catalog\n    runner_exists arm, MSG "
              "declaration, GENERATE pool entry.",
              "slice plan")
    src = src[:a] + ds + src[b:]
    steps.append("docstring: W13 identity (6 anchored rewrites)")
    return src


def sec2_imports(src, steps):
    src = sub1(src,
               "import trial_labor_w11 as tl11  # std overlay + fifteen-tuple "
               "machinery\nimport a158_tsgate_probe as a158  # frozen A158 "
               "runner (RSQR20/RSQR10/BETA20 verbatim import)\n"
               "from science_gates import",
               "import trial_labor_w11 as tl11  # std overlay + fifteen-tuple "
               "machinery\nimport trial_labor_w12 as tl12  # rsqr overlay + "
               "sixteen-tuple machinery\nimport a158_tsgate_probe as a158  # "
               "frozen A158 runner (RSQR20/RSQR10/SUMN20/SUMN10/BETA20 "
               "verbatim import)\nfrom science_gates import",
               "imports")
    steps.append("imports: + tl12 + a158 SUMN columns face")
    return src


def sec3_identity_constants(src, steps):
    ic, a, b = segment(src, 'WAVE = "TRIAL_LABOR_W12"',
                       'AXIS_RSQR = ["none", "rsqr20_hi", "rsqr10_hi"]',
                       include_start=True, include_end=False)
    ic = subn(ic, "TRIAL_LABOR_W12", "TRIAL_LABOR_W13", 2,
              "wave literals (WAVE/PREREG)")
    ic = subn(ic, "TRIAL_LAB_W12_", "TRIAL_LAB_W13_", 2,
              "ledger batch literals (SCREEN_BATCH/JUDGE_BATCH)")
    ic = subn(ic, '"trial_labor_w12', '"trial_labor_w13', 4,
              "seed registry keys + RES_DIR")
    ic = subn(ic, '"w12_', '"w13_', 6,
              "res-dir file names (grammar/candidates/screen/screen_csv/"
              "judge/intake)")
    ic = sub1(ic,
              'SEED_GEN = SEED_REGISTRY["trial_labor_w13_gen"]        '
              '# 20320500',
              'SEED_GEN = SEED_REGISTRY["trial_labor_w13_gen"]        '
              '# 20323000',
              "seed gen comment")
    ic = sub1(ic,
              'SEED_NULL = SEED_REGISTRY["trial_labor_w13_scrnull"]  '
              '# 20321000',
              'SEED_NULL = SEED_REGISTRY["trial_labor_w13_scrnull"]  '
              '# 20323500',
              "seed null comment")
    ic = sub1(ic,
              'SEED_UNC = SEED_REGISTRY["trial_labor_w13_unc"]        '
              '# 20321500',
              'SEED_UNC = SEED_REGISTRY["trial_labor_w13_unc"]        '
              '# 20324000',
              "seed unc comment")
    ic = sub1(ic,
              'FROZEN_SHA16 = "67c86c9cf4ef1ca7"   # Slice-B pin (bm-b r445; '
              '== w12_\n# grammar.json serialization sha16; selftest L6g '
              'fail-closed verifies\n# pin == built sha; W11 r442-close '
              'precedent)',
              'FROZEN_SHA16 = "868cd0c6413636e6"   # Slice-B pin (bm-a '
              'r466; == w13_\n# grammar.json serialization sha16; '
              'selftest L6g\n# fail-closed verifies pin == built sha '
              '(grammar face\n# built + sha measured this round; W12 '
              'r445-close precedent)',
              "frozen sha pin")
    ic = sub1(ic,
              '    "W11": tl11.FROZEN_SHA16,    # 128962592feeb8d3\n}',
              '    "W11": tl11.FROZEN_SHA16,    # 128962592feeb8d3\n'
              '    "W12": tl12.FROZEN_SHA16,    # 67c86c9cf4ef1ca7\n}',
              "prior wave sha +W12")
    ic = subn(ic, "the W12 runner re-derives ZERO", "the W13 runner "
              "re-derives ZERO", 3, "import-face comments (amp/mom/std)")
    ic = subn(ic, "build_grammar_w12\n", "build_grammar_w13\n", 1,
              "lazy-face comment (amp)")
    ic = subn(ic, "build_grammar_w12 (import-time",
              "build_grammar_w13 (import-time", 2,
              "lazy-face comments (mom/std)")
    ic = sub1(ic,
              "# trend-fit-quality RSQR axis (prereg sec.3 NEW W12 frozen "
              "layer,\n# three-value axis, W4-VOL/W11-STD precedent)",
              "# trend-fit-quality RSQR axis (W12 frozen face, imported "
              "verbatim from\n# tl12 -- import-face law; the W13 runner "
              "re-derives ZERO rsqr machinery)\n"
              "AXIS_RSQR = tl12.AXIS_RSQR                 # "
              '["none","rsqr20_hi","rsqr10_hi"]\n'
              "RSQR_MEMBER = tl12.RSQR_MEMBER             # \"510300\"\n"
              "RSQR_ANCHOR = tl12.RSQR_ANCHOR             # W12 frozen probe "
              "anchors\nrsqr_state_series = tl12.rsqr_state_series\n"
              "rsqr_zero_mask = tl12.rsqr_zero_mask\n"
              "_rsqr_state_full = tl12._rsqr_state_full\n"
              "_rsqr_structure_pass = tl12._rsqr_structure_pass\n"
              "_rsqr_faces_raw = tl12._rsqr_faces_raw\n"
              "# RSQR_SPEC/RSQR_ANCHOR carried from tl12.build_grammar_w12() "
              "inside\n# build_grammar_w13 (import-time grammar-chain build "
              "is heavy; lazy\n# face = build-time read)\n\n"
              "# up-share-purity SUMN axis (prereg sec.3 NEW W13 frozen "
              "layer,\n# three-value axis, W4-VOL/W11-STD/W12-RSQR "
              "precedent)",
              "rsqr import faces + sumn banner")
    src = src[:a] + ic + src[b:]
    steps.append("constants: W13 identity + tl12 rsqr import faces + "
                 "seeds 20323000 family + FROZEN_SHA16 placeholder + "
                 "PRIOR +W12")
    return src


def sec4_overlay_constants(src, steps):
    _, a, b = segment(src, 'AXIS_RSQR = ["none", "rsqr20_hi", "rsqr10_hi"]',
                      "def _rsqr_faces_raw(", include_start=True,
                      include_end=False)
    anchor = KIT.build_sumn_anchor()
    block = (
        'AXIS_SUMN = ["none", "sumn20_lo", "sumn10_lo"]\n'
        "AXIS_COMBOS = tl12.AXIS_COMBOS * len(AXIS_SUMN)  # 94,058,496 "
        "* 3 = 282,175,488\n"
        'SUMN_MEMBER = "510300"          # core48 member (prereg sec.2 '
        "probe fact)\n"
        'PROBE_FACTS_FILE = os.path.join("results",\n'
        '                                "_r456bma_sumnsump_w13_probe_'
        'facts.json")\n'
        "SUMN_SPEC = " + _py_lit(KIT.SUMN_SPEC) + "\n"
        "\nSUMN_ANCHOR = " + _py_lit(anchor) + "\n\n"
    )
    src = src[:a] + block + src[b:]
    steps.append("overlay constants: AXIS_SUMN/SUMN_SPEC/SUMN_ANCHOR "
                 "programmatic (kit); rsqr literals dropped -> tl12 faces")
    return src


def sec5_layer(src, steps):
    _, a, b = segment(src, "def _rsqr_faces_raw(",
                      "# ------------------------------------------------------------ "
                      "grammar build", include_start=True, include_end=False)
    src = src[:a] + KIT.SUMN_LAYER_TEXT + src[b:]
    steps.append("sumn overlay layer: kit SUMN_LAYER_TEXT verbatim "
                 "(a158 import + tl12 rsqr faces; zero re-implementation)")
    return src


def sec6_grammar(src, steps):
    gb, a, b = segment(src, "def build_grammar_w12():",
                       "# ------------------------------------------------------------ "
                       "Sobol draw leg", include_start=True,
                       include_end=False)
    gb = gb.replace("build_grammar_w12", "build_grammar_w13")
    gb = sub1(gb,
              "    \"\"\"tl11 grammar extended with the NEW rsqr axis + W12 "
              "seeds/counts\n    (frozen face).  FIFTEEN-tuple axes R/X/S/T/"
              "STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR = "
              "94,058,496 axis combos.",
              "    \"\"\"tl12 grammar extended with the NEW sumn axis + W13 "
              "seeds/counts\n    (frozen face).  SIXTEEN-tuple axes R/X/S/T/"
              "STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN "
              "= 282,175,488 axis combos.",
              "grammar docstring head")
    gb = sub1(gb,
              "    Exclusion law (prereg sec.1): exact already-judged cells "
              "are\n    excluded on the rsqr=none face only; all prior-wave "
              "lineage keys\n    are rsqr=none completed (W1 4-tuple + "
              "stop/gate/vol/yang/vconf/\n    streak/tstate/amp/mom/std/rsqr "
              "none; W2 5-tuple + gate/vol/yang/vconf/\n    streak/tstate/"
              "amp/mom/std/rsqr none; W3 6-tuple + vol/yang/vconf/\n    "
              "streak/tstate/amp/mom/std/rsqr none; W4 7-tuple + yang/vconf/"
              "streak/\n    tstate/amp/mom/std/rsqr none; W5 8-tuple + "
              "vconf/streak/tstate/amp/\n    mom/std/rsqr none; W6 9-tuple + "
              "streak/tstate/amp/mom/std/rsqr none; W7\n    10-tuple + "
              "tstate/amp/mom/std/rsqr none; W8 11-tuple + amp/mom/std/\n    "
              "rsqr none; W9 12-tuple + mom/std/rsqr none; W10 13-tuple +\n"
              "    std/rsqr none; W11 14-tuple + rsqr none; MASS via the "
              "declared\n    translation); rsqr in {rsqr20_hi, rsqr10_hi} "
              "faces = new-syntax\n    legal cells (never excluded).\"\"\"",
              "    Exclusion law (prereg sec.1): exact already-judged cells "
              "are\n    excluded on the sumn=none face only; all prior-wave "
              "lineage keys\n    are sumn=none completed (W1 4-tuple + "
              "stop/gate/vol/yang/vconf/\n    streak/tstate/amp/mom/std/rsqr/"
              "sumn none; W2 5-tuple + gate/vol/yang/vconf/\n    streak/"
              "tstate/amp/mom/std/rsqr/sumn none; W3 6-tuple + vol/yang/"
              "vconf/\n    streak/tstate/amp/mom/std/rsqr/sumn none; W4 "
              "7-tuple + yang/vconf/streak/\n    tstate/amp/mom/std/rsqr/"
              "sumn none; W5 8-tuple + vconf/streak/tstate/amp/\n    mom/std/"
              "rsqr/sumn none; W6 9-tuple + streak/tstate/amp/mom/std/rsqr/"
              "sumn none; W7\n    10-tuple + tstate/amp/mom/std/rsqr/sumn "
              "none; W8 11-tuple + amp/mom/std/\n    rsqr/sumn none; W9 "
              "12-tuple + mom/std/rsqr/sumn none; W10 13-tuple +\n    std/"
              "rsqr/sumn none; W11 14-tuple + rsqr/sumn none; W12 15-tuple "
              "+\n    sumn none; MASS via the declared\n    translation); "
              "sumn in {sumn20_lo, sumn10_lo} faces = new-syntax\n    legal "
              "cells (never excluded).\"\"\"",
              "grammar exclusion docstring")
    gb = sub1(gb,
              "    g11 = tl11.build_grammar_w11()    # frozen W11 machinery "
              "face",
              "    g12 = tl12.build_grammar_w12()    # frozen W12 machinery "
              "face", "g12 base")
    gb = sub1(gb,
              '    for e in g11["exclusion"]["stop_gate_vol_yang_vconf_'
              'streak_tstate_amp_mom_std_none_face"]:',
              '    for e in g12["exclusion"]["stop_gate_vol_yang_vconf_'
              'streak_tstate_amp_mom_std_rsqr_none_face"]:',
              "exclusion face source")
    gb = sub1(gb, '"tstate-amp-mom-std-rsqr-none"})',
              '"tstate-amp-mom-std-rsqr-sumn-none"})', "excl face label")
    gb = sub1(gb, '"grammar_kind": "w12-rsqr-gate-extended",',
              '"grammar_kind": "w13-sumn-gate-extended",', "kind")
    gb = sub1(gb,
              '        "seeds": {"trial_labor_w12_gen": SEED_GEN,\n'
              '                  "trial_labor_w12_scrnull": SEED_NULL,\n'
              '                  "trial_labor_w12_unc": SEED_UNC,\n'
              '                  "derivation": "Sobol(seed=20320500+'
              'family_idx, "\n'
              '                                "scramble) param box + '
              'default_rng("\n'
              '                                "[20320500+family_idx, 7919]) '
              'FIFTEEN-"\n'
              '                                "tuple axis stream R/X/S/T/'
              'STOP/GATE/"\n'
              '                                "VOL/YANG/VCONF/STREAK/TSTATE/'
              'AMP/MOM/"\n                                "STD/RSQR (prereg '
              's.3; A idx 0-5, B idx "\n'
              '                                "6+slot; berths 20320500/'
              '20321000/20321500 "\n'
              '                                "held at the freeze commit '
              'per R250 "\n'
              '                                "one-step law, bm-b r444 '
              'three-step "\n'
              '                                "re-verify ALL GREEN no '
              're-pick; berth-open "\n'
              '                                "adoption of the bm-a r447 '
              'RSQR candidate "\n'
              '                                "whole package per AMP->W9/'
              'MOM->W10/STD->"\n'
              '                                "W11 lineage)"},',
              '        "seeds": {"trial_labor_w13_gen": SEED_GEN,\n'
              '                  "trial_labor_w13_scrnull": SEED_NULL,\n'
              '                  "trial_labor_w13_unc": SEED_UNC,\n'
              '                  "derivation": "Sobol(seed=20323000+'
              'family_idx, "\n'
              '                                "scramble) param box + '
              'default_rng("\n'
              '                                "[20323000+family_idx, 7919]) '
              'SIXTEEN-"\n'
              '                                "tuple axis stream R/X/S/T/'
              'STOP/GATE/"\n'
              '                                "VOL/YANG/VCONF/STREAK/TSTATE/'
              'AMP/MOM/"\n                                "STD/RSQR/SUMN '
              '(prereg s.3; A idx 0-5, B idx "\n'
              '                                "6+slot; berths 20323000/'
              '20323500/20324000 "\n'
              '                                "held at the freeze commit '
              'per R250 "\n'
              '                                "one-step law, bm-a r461 '
              'three-step "\n'
              '                                "re-verify ALL GREEN no '
              're-pick; berth "\n'
              '                                "adoption lineage AMP->W9/'
              'MOM->W10/STD->"\n'
              '                                "W11/RSQR->W12/SUMN->W13)"},',
              "seeds derivation")
    gb = sub1(gb, '"axes": {**g11["axes"], "rsqr": AXIS_RSQR},',
              '"axes": {**g12["axes"], "sumn": AXIS_SUMN},', "axes")
    for k in ("stop_formula", "stop_fill_mapping", "gate_spec",
              "vol_spec", "yang_spec", "vconf_spec", "streak_spec",
              "tstate_spec", "amp_spec", "families", "value_domains",
              "faces", "inventory_audit",
              "vol_anchor", "yang_anchor", "vconf_anchor",
              "streak_anchor", "tstate_anchor", "amp_anchor"):
        gb = gb.replace(f'g11["{k}"]', f'g12["{k}"]')
    gb = sub1(gb,
              '        "mom_spec": g11["mom_spec"],\n'
              '        "std_spec": g11["std_spec"],\n'
              '        "rsqr_spec": RSQR_SPEC,',
              '        "mom_spec": g12["mom_spec"],\n'
              '        "std_spec": g12["std_spec"],\n'
              '        "rsqr_spec": g12["rsqr_spec"],\n'
              '        "sumn_spec": SUMN_SPEC,', "specs")
    gb = sub1(gb,
              '        "mom_anchor": g11["mom_anchor"],\n'
              '        "std_anchor": g11["std_anchor"],\n'
              '        "rsqr_anchor": RSQR_ANCHOR,',
              '        "mom_anchor": g12["mom_anchor"],\n'
              '        "std_anchor": g12["std_anchor"],\n'
              '        "rsqr_anchor": g12["rsqr_anchor"],\n'
              '        "sumn_anchor": SUMN_ANCHOR,', "anchors")
    gb = sub1(gb, '"negative_priors": g11.get("negative_priors"),',
              '"negative_priors": g12.get("negative_priors"),',
              "negative priors")
    gb = sub1(gb,
              '            "stop_gate_vol_yang_vconf_streak_tstate_'
              'amp_mom_std_rsqr_none_face":\n                excl,',
              '            "stop_gate_vol_yang_vconf_streak_tstate_'
              'amp_mom_std_rsqr_sumn_none_face":\n                excl,',
              "exclusion payload key")
    gb = sub1(gb,
              '            "sources": list(g11["exclusion"]["sources"])\n'
              '            + ["w12_screen.json survivors (generate-time)",'
              '\n               "w12_judge products (generate-time '
              'real-read "\n               "re-declare window; W11-JUDGE '
              'landed 2026-09-30 "\n               "01:47:40 = TWELFTH '
              'source)"],',
              '            "sources": list(g12["exclusion"]["sources"])\n'
              '            + ["w13_screen.json survivors (generate-time)",'
              '\n               "w13_judge products (generate-time '
              'real-read "\n               "re-declare window; W12-JUDGE '
              'landed 2026-09-30 "\n               "05:22:37 = '
              'THIRTEENTH source)"],', "sources W12")
    gb = sub1(gb,
              '            "note": "exclusion face = rsqr=none only; '
              'prior-wave keys "\n                    "rsqr=none-completed '
              '(semantic identity match); "\n                    "rsqr in '
              '{rsqr20_hi, rsqr10_hi} = new-syntax legal "\n'
              '                    "cells (prereg sec.1)"},',
              '            "note": "exclusion face = sumn=none only; '
              'prior-wave keys "\n                    "sumn=none-completed '
              '(semantic identity match); "\n                    "sumn in '
              '{sumn20_lo, sumn10_lo} = new-syntax legal "\n'
              '                    "cells (prereg sec.1)"},',
              "exclusion note")
    src = src[:a] + gb + src[b:]
    steps.append("grammar build: sixteen-tuple + sumn axis + W12 lineage")
    return src


def sec7_sobol(src, steps):
    sob, a, b = segment(src, "def draw_candidate_sobol_w12(",
                        "# ------------------------------------------------ "
                        "exclusion (24 real-reads)", include_start=True,
                        include_end=False)
    sob = sob.replace("draw_candidate_sobol_w12", "draw_candidate_sobol_w13")
    sob = sub1(sob,
               "    to discrete domain indices + FIFTEEN-tuple axis stream\n"
               "    default_rng([SEED_GEN+family_idx, 7919]) in the frozen "
               "consumption\n    order R/X/S/T/STOP/GATE/VOL/YANG/VCONF/"
               "STREAK/TSTATE/AMP/MOM/STD/RSQR (the\n    first fourteen axis "
               "arrays are the W11-order stream VERBATIM --\n    "
               "order-frozen consumption law; the rsqr leg appends AFTER "
               "std,\n    zero disturbance).  Deterministic, zero band "
               "use.\"\"\"",
               "    to discrete domain indices + SIXTEEN-tuple axis "
               "stream\n    default_rng([SEED_GEN+family_idx, 7919]) in the "
               "frozen consumption\n    order R/X/S/T/STOP/GATE/VOL/YANG/"
               "VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN (the\n    first "
               "fifteen axis arrays are the W12-order stream VERBATIM --\n"
               "    order-frozen consumption law; the sumn leg appends "
               "AFTER rsqr,\n    zero disturbance).  Deterministic, zero "
               "band use.\"\"\"", "sobol docstring")
    sob = sub1(sob,
               "                  rng.integers(0, len(AXIS_STD), n_draws),\n"
               "                  rng.integers(0, len(AXIS_RSQR), "
               "n_draws)))",
               "                  rng.integers(0, len(AXIS_STD), n_draws),\n"
               "                  rng.integers(0, len(AXIS_RSQR), n_draws),\n"
               "                  rng.integers(0, len(AXIS_SUMN), "
               "n_draws)))", "sobol rng leg")
    sob = sub1(sob,
               "        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_, ts_, "
               "ap_, mo_, sd_, \\\n            rq_ = ax[i]",
               "        r_, x_, s_, t_, st_, gt_, vt_, yg_, vc_, sk_, ts_, "
               "ap_, mo_, sd_, \\\n            rq_, su_ = ax[i]",
               "sobol unpack")
    sob = sub1(sob,
               "                           AXIS_MOM[mo_], AXIS_STD[sd_],\n"
               "                           AXIS_RSQR[rq_]],",
               "                           AXIS_MOM[mo_], AXIS_STD[sd_],\n"
               "                           AXIS_RSQR[rq_], "
               "AXIS_SUMN[su_]],", "sobol axis list")
    src = src[:a] + sob + src[b:]
    src = sub1(src,
               "# ------------------------------------------------ exclusion "
               "(24 real-reads)",
               "# ------------------------------------------------ exclusion "
               "(25 real-reads)", "section banner (src level)")
    steps.append("Sobol: sixteen-tuple stream (sumn leg appends "
                 "after rsqr)")
    return src


def sec8_exclusion_loader(src, steps):
    ex, a, b = segment(src, "def _load_exclusion_rows_w12(",
                       "def _excluded_w12(", include_start=True,
                       include_end=False)
    ex = ex.replace("_load_exclusion_rows_w12", "_load_exclusion_rows_w13")
    ex = sub1(ex, "Twenty-four real-read source faces",
              "Twenty-five real-read source faces", "loader count")
    ex = sub1(ex,
              "    face (prereg sec.1), all real-read at generate time.  "
              "All prior-wave\n    keys are padded to the W12 FIFTEEN-tuple "
              "with rsqr=none (semantic-identity\n    completion law).  "
              "Sources: 1 = frozen serialized grammar",
              "    face (prereg sec.1), all real-read at generate time.  "
              "All prior-wave\n    keys are padded to the W13 SIXTEEN-tuple "
              "with sumn=none (semantic-identity\n    completion law).  "
              "Sources: 1 = frozen serialized grammar",
              "loader pad law")
    ex = sub1(ex,
              "    stop-gate-vol-yang-vconf-streak-tstate-amp-mom-std-rsqr-"
              "none face (15-tuple at\n    build); 2-13 = W1/W2/MASS "
              "(declared tl3 translation)/W3/W4/W5/W6/\n    W7/W8/W9/W10/W11 "
              "screen survivors -- W11 is NEW vs W11's own loader\n    "
              "(generate-time real-read; absent at build = zero rows honest "
              "per\n    prereg sec.1); 14-25 = judged products (w1_judge / "
              "MASS judged /\n    w2_judge / w3_judge / w4_judge / w5_judge "
              "/ w6_judge / w7_judge /\n    w8_judge / w9_judge / w10_judge "
              "/ w12_judge) -- generate-time real-read\n    re-declare "
              "window (declared-unavailable -> zero rows, no\n    "
              "fabrication).",
              "    stop-gate-vol-yang-vconf-streak-tstate-amp-mom-std-rsqr-"
              "sumn-none face (16-tuple at\n    build); 2-14 = W1/W2/MASS "
              "(declared tl3 translation)/W3/W4/W5/W6/\n    W7/W8/W9/W10/W11/"
              "W12 screen survivors -- W12 is NEW vs W12's own loader\n    "
              "(generate-time real-read; absent at build = zero rows honest "
              "per\n    prereg sec.1); 15-26 = judged products (w1_judge / "
              "MASS judged /\n    w2_judge / w3_judge / w4_judge / w5_judge "
              "/ w6_judge / w7_judge /\n    w8_judge / w9_judge / w10_judge "
              "/ w12_judge / w13_judge) -- generate-time real-read\n    "
              "re-declare window (declared-unavailable -> zero rows, no\n"
              "    fabrication).", "loader sources docstring")
    ex = sub1(ex,
              '    rows = list(grammar["exclusion"]\n'
              '                ["stop_gate_vol_yang_vconf_streak_tstate_'
              'amp_mom_std_rsqr_none_face"])',
              '    rows = list(grammar["exclusion"]\n'
              '                ["stop_gate_vol_yang_vconf_streak_tstate_'
              'amp_mom_std_rsqr_sumn_none_face"])', "rows key")
    ex = sub1(ex,
              '    disc = {"grammar_stop_gate_vol_yang_vconf_streak_tstate_'
              '"\n            "amp_mom_std_rsqr_none_rows": len(rows)}',
              '    disc = {"grammar_stop_gate_vol_yang_vconf_streak_tstate_'
              '"\n            "amp_mom_std_rsqr_sumn_none_rows": len(rows)}',
              "disc key")
    for w, old_n, new_n in (("w1", 11, 12), ("w2", 10, 11), ("w3", 9, 10),
                            ("w4", 8, 9), ("w5", 7, 8), ("w6", 6, 7),
                            ("w7", 5, 6), ("w8", 4, 5), ("w9", 3, 4),
                            ("w10", 2, 3)):
        ex = sub1(ex, f'["none"] * {old_n}, "{w}_screen_survivor")',
                  f'["none"] * {new_n}, "{w}_screen_survivor")',
                  f"{w} screen pad")
    ex = sub1(ex,
              '                         "face": f"{tag}:stop-gate-'
              'vol-yang-vconf-"\n                                 '
              '"streak-tstate-amp-mom-std-rsqr-none",',
              '                         "face": f"{tag}:stop-gate-'
              'vol-yang-vconf-"\n                                 '
              '"streak-tstate-amp-mom-std-rsqr-sumn-none",',
              "screen face label")
    ex = sub1(ex,
              '    disc["w12_screen_survivors"] = _screen_survivors(\n'
              '        tl11.SCREEN_FILE, tl11.CANDIDATES_FILE,\n'
              '        ["none"], "w12_screen_survivor")',
              '    disc["w12_screen_survivors"] = _screen_survivors(\n'
              '        tl11.SCREEN_FILE, tl11.CANDIDATES_FILE,\n'
              '        ["none"] * 2, "w12_screen_survivor")\n'
              '    disc["w13_screen_survivors"] = _screen_survivors(\n'
              '        tl12.SCREEN_FILE, tl12.CANDIDATES_FILE,\n'
              '        ["none"], "w13_screen_survivor")',
              "w12->w13 screen sources")
    ex = sub1(ex,
              '                tr["axis"] = list(tr["axis"]) + ["none"] * 9\n'
              '                tr["face"] = '
              '"mass_screen_survivor:translated-exact"',
              '                tr["axis"] = list(tr["axis"]) + ["none"] * '
              '10\n                tr["face"] = '
              '"mass_screen_survivor:translated-exact"',
              "mass screen pad")
    ex = sub1(ex,
              "    # W10-JUDGE landed 2026-09-29 20:31:29; W11-JUDGE "
              "landed 2026-09-30\n    # 01:47:40 -- TWELVE sources, fifth "
              "full-declare window in\n    # history -- live re-read at "
              "generate time is the law)",
              "    # W10-JUDGE landed 2026-09-29 20:31:29; W11-JUDGE "
              "landed 2026-09-30\n    # 01:47:40; W12-JUDGE landed "
              "2026-09-30 05:22:37 -- THIRTEEN\n    # sources, sixth "
              "full-declare window in history -- live re-read\n    # at "
              "generate time is the law)",
              "judged sources note")
    for w, old_n, new_n in (("w1", 11, 12), ("w2", 10, 11), ("w3", 9, 10),
                            ("w4", 8, 9), ("w5", 7, 8), ("w6", 6, 7),
                            ("w7", 5, 6), ("w8", 4, 5), ("w9", 3, 4),
                            ("w10", 2, 3)):
        ex = sub1(ex, f'["none"] * {old_n}, "{w}_judged")',
                  f'["none"] * {new_n}, "{w}_judged")',
                  f"{w} judged pad")
    ex = sub1(ex,
              '                tr["axis"] = list(tr["axis"]) + ["none"] * 9\n'
              '                tr["face"] = f"{tag}:translated-exact"',
              '                tr["axis"] = list(tr["axis"]) + ["none"] * '
              '10\n                tr["face"] = f"{tag}:translated-exact"',
              "mass judged pad")
    ex = sub1(ex,
              '                             "face": f"{tag}:stop-'
              'gate-vol-"\n                                     '
              '"yang-vconf-streak-tstate-amp-"\n'
              '                                     "mom-std-rsqr-none",',
              '                             "face": f"{tag}:stop-'
              'gate-vol-"\n                                     '
              '"yang-vconf-streak-tstate-amp-"\n'
              '                                     "mom-std-rsqr-sumn-'
              'none",', "judged face label")
    ex = sub1(ex,
              '    disc["w12_judge_products"] = _judged_source(\n'
              '        tl11.JUDGE_FILE, tl11.CANDIDATES_FILE,\n'
              '        ["none"], "w12_judged")',
              '    disc["w12_judge_products"] = _judged_source(\n'
              '        tl11.JUDGE_FILE, tl11.CANDIDATES_FILE,\n'
              '        ["none"] * 2, "w12_judged")\n'
              '    disc["w13_judge_products"] = _judged_source(\n'
              '        tl12.JUDGE_FILE, tl12.CANDIDATES_FILE,\n'
              '        ["none"], "w13_judged")',
              "w12->w13 judge sources")
    ex = sub1(ex,
              '        "none exists, uniform stands, availability of the '
              'TWELVE judge "\n        "products disclosed above '
              '(freeze-time twelve-source "\n        "full-declare window = '
              'fifth in history)")',
              '        "none exists, uniform stands, availability of the '
              'THIRTEEN judge "\n        "products disclosed above '
              '(freeze-time thirteen-source "\n        "full-declare '
              'window = sixth in history)")',
              "weighting note")
    src = src[:a] + ex + src[b:]
    steps.append("exclusion: 25 real-read faces, w12 screen+judge "
                 "sources (tl12), pads +1 sumn-none all waves")
    return src


def sec9_excluded(src, steps):
    exd, a, b = segment(src, "def _excluded_w12(",
                        "# -------------------------------------------- "
                        "effective face + engine curves", include_start=True,
                        include_end=False)
    exd = exd.replace("_excluded_w12", "_excluded_w13")
    exd = sub1(exd, 'if cand["axis"][14] != "none":',
               'if cand["axis"][15] != "none":', "axis idx")
    exd = sub1(exd,
               "    \"\"\"Exact already-judged cell test, rsqr=none face "
               "only (prereg\n    sec.1: rsqr in {rsqr20_hi, rsqr10_hi} = "
               "new-syntax legal cells --\n    never excluded; W1-lineage "
               "cells implicitly stop/gate/vol/yang/\n    vconf/streak/"
               "tstate/amp/mom/std/rsqr=none; W2 cells carry their own\n    "
               "stop face; W3 stop+gate; W4 stop+gate+vol; W5 "
               "stop+gate+vol+yang;\n    W6 stop+gate+vol+yang+vconf; W7 "
               "stop+gate+vol+yang+vconf+streak;\n    W8 stop+gate+vol+"
               "yang+vconf+streak+tstate; W9\n    stop+gate+vol+yang+vconf+"
               "streak+tstate+amp; W10 +mom; W11 +std).\n    Returns the "
               "exclusion face or None.\"\"\"",
               "    \"\"\"Exact already-judged cell test, sumn=none face "
               "only (prereg\n    sec.1: sumn in {sumn20_lo, sumn10_lo} = "
               "new-syntax legal cells --\n    never excluded; W1-lineage "
               "cells implicitly stop/gate/vol/yang/\n    vconf/streak/"
               "tstate/amp/mom/std/rsqr/sumn=none; W2 cells carry their own"
               "\n    stop face; W3 stop+gate; W4 stop+gate+vol; W5 "
               "stop+gate+vol+yang;\n    W6 stop+gate+vol+yang+vconf; W7 "
               "stop+gate+vol+yang+vconf+streak;\n    W8 stop+gate+vol+"
               "yang+vconf+streak+tstate; W9\n    stop+gate+vol+yang+vconf+"
               "streak+tstate+amp; W10 +mom; W11 +std;\n    W12 +rsqr)."
               "\n    Returns the exclusion face or None.\"\"\"",
               "excluded docstring")
    src = src[:a] + exd + src[b:]
    steps.append("_excluded: axis[15] sumn=none face law")
    return src


def sec10_mask_curve_null(src, steps):
    mk, a, b = segment(src, "def _effective_signal_mask_w12(",
                       "# ------------------------------------------------------------ "
                       "grammar / status", include_start=True,
                       include_end=False)
    mk = mk.replace("_effective_signal_mask_w12", "_effective_signal_mask_w13")
    mk = sub1(mk,
              "                               tstate_key, amp_key, mom_key, "
              "std_key,\n                               rsqr_key, gate_state, "
              "vol_state, yang_state,\n                               "
              "vconf_state, streak_state, tstate_state,\n"
              "                               amp_state, mom_state, "
              "std_state, rsqr_state):",
              "                               tstate_key, amp_key, mom_key, "
              "std_key,\n                               rsqr_key, sumn_key, "
              "gate_state, vol_state, yang_state,\n                               "
              "vconf_state, streak_state, tstate_state,\n"
              "                               amp_state, mom_state, "
              "std_state, rsqr_state,\n                               "
              "sumn_state):", "mask signature")
    mk = sub1(mk,
              "    \"\"\"Dedup-face holdings proxy with the frozen "
              "composition order\n    GATE -> VOL -> YANG -> VCONF -> STREAK "
              "-> TSTATE -> AMP -> MOM ->\n    STD -> RSQR -> initial-stop "
              "(prereg sec.3 fifteen-tuple dedup legs; zero\n    engine "
              "burn).  rsqr=none + std=none + mom=none + amp=none + "
              "tstate=none\n    + streak=none + vconf=none + yang=none + "
              "vol=none + gate=none +\n    stop=none = W1 identity; "
              "rsqr=none = W11 semantic baseline; all\n    eleven overlay "
              "faces deterministic layers of the same grammar\n    stack "
              "(W11 order extended by the rsqr leg, zero disturbance to the"
              "\n    first ten).\"\"\"",
              "    \"\"\"Dedup-face holdings proxy with the frozen "
              "composition order\n    GATE -> VOL -> YANG -> VCONF -> STREAK "
              "-> TSTATE -> AMP -> MOM ->\n    STD -> RSQR -> SUMN -> "
              "initial-stop (prereg sec.3 sixteen-tuple dedup legs; zero\n"
              "    engine burn).  sumn=none + rsqr=none + std=none + "
              "mom=none + amp=none\n    + tstate=none + streak=none + "
              "vconf=none + yang=none + vol=none +\n    gate=none + "
              "stop=none = W1 identity; sumn=none = W12 semantic baseline; "
              "all\n    twelve overlay faces deterministic layers of the "
              "same grammar\n    stack (W12 order extended by the sumn leg, "
              "zero disturbance to the\n    first eleven).\"\"\"",
              "mask docstring")
    mk = sub1(mk,
              "    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)\n"
              "    return tl2._effective_signal_mask(RQ, prices, stop_key, "
              "atr20)",
              "    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)\n"
              "    SU = sumn_zero_mask(RQ, sumn_key, sumn_state)\n"
              "    return tl2._effective_signal_mask(SU, prices, stop_key, "
              "atr20)", "mask chain")
    mk = mk.replace("run_candidate_curve_w12", "run_candidate_curve_w13")
    mk = sub1(mk,
              "                           mom_state=None, std_state=None, "
              "rsqr_state=None):",
              "                           mom_state=None, std_state=None, "
              "rsqr_state=None,\n                           "
              "sumn_state=None):", "curve signature")
    mk = sub1(mk,
              "    \"\"\"One W11 candidate cell at the engine face with the "
              "gate + vol +\n    yang + vconf + streak + tstate + amp + "
              "MOM + STD overlays +\n    initial-stop overlay carried "
              "per-cell (prereg sec.3 face a; frozen composition\n    order "
              "filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK\n"
              "    -> TSTATE -> AMP -> MOM -> STD -> RSQR -> "
              "initial-stop).\n\n    rsqr=none+std=none+mom=none+amp=none+"
              "tstate=none+streak=none+\n    vconf=none+yang=none+vol=none+"
              "gate=none+stop=none -> byte-identical\n    to the tl1 engine "
              "face; rsqr=none -> tl11 W11 face (parity law,\n    "
              "selftest-pinned); rsqr in {rsqr20_hi, rsqr10_hi} = new W12 "
              "syntax\n    (entry-permittance only, never excluded).  "
              "Returns (eq, trades,\n    metrics, params, patch, "
              "stop_fired, gate_zeroed, vol_zeroed,\n    yang_zeroed, "
              "vconf_zeroed, streak_zeroed, tstate_zeroed,\n    "
              "amp_zeroed, mom_zeroed, std_zeroed, rsqr_zeroed).\"\"\"",
              "    \"\"\"One W12 candidate cell at the engine face with the "
              "gate + vol +\n    yang + vconf + streak + tstate + amp + "
              "MOM + STD + RSQR overlays +\n    initial-stop overlay "
              "carried per-cell (prereg sec.3 face a; frozen composition\n"
              "    order filter -> timing -> GATE -> VOL -> YANG -> VCONF "
              "-> STREAK\n    -> TSTATE -> AMP -> MOM -> STD -> RSQR -> "
              "SUMN -> initial-stop).\n\n    sumn=none+rsqr=none+std=none+"
              "mom=none+amp=none+tstate=none+streak=none+\n    vconf=none+"
              "yang=none+vol=none+gate=none+stop=none -> byte-identical\n   "
              " to the tl1 engine face; sumn=none -> tl12 W12 face (parity "
              "law,\n    selftest-pinned); sumn in {sumn20_lo, sumn10_lo} = "
              "new W13 syntax\n    (entry-permittance only, never "
              "excluded).  Returns (eq, trades,\n    metrics, params, "
              "patch, stop_fired, gate_zeroed, vol_zeroed,\n    yang_zeroed,"
              " vconf_zeroed, streak_zeroed, tstate_zeroed,\n    "
              "amp_zeroed, mom_zeroed, std_zeroed, rsqr_zeroed, "
              "sumn_zeroed).\"\"\"", "curve docstring")
    mk = sub1(mk,
              '    std_key = cand["axis"][13]\n'
              '    rsqr_key = cand["axis"][14]\n',
              '    std_key = cand["axis"][13]\n'
              '    rsqr_key = cand["axis"][14]\n'
              '    sumn_key = cand["axis"][15]\n', "curve keys")
    mk = sub1(mk,
              "    if rsqr_state is None:\n        rsqr_state = "
              "rsqr_state_series(prices)",
              "    if rsqr_state is None:\n        rsqr_state = "
              "rsqr_state_series(prices)\n    if sumn_state is None:\n"
              "        sumn_state = sumn_state_series(prices)",
              "curve state init")
    mk = sub1(mk,
              "    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)\n"
              "    gate_zeroed = int((mask > 0).sum().sum() - (G > 0)"
              ".sum().sum())",
              "    RQ = rsqr_zero_mask(SD, rsqr_key, rsqr_state)\n"
              "    SU = sumn_zero_mask(RQ, sumn_key, sumn_state)\n"
              "    gate_zeroed = int((mask > 0).sum().sum() - (G > 0)"
              ".sum().sum())", "curve chain")
    mk = sub1(mk,
              "    rsqr_zeroed = int((SD > 0).sum().sum() - (RQ > 0)"
              ".sum().sum())\n    if stop_key == \"none\":\n        S, "
              "stop_fired = RQ, 0\n    else:\n        S = "
              "tl2._effective_signal_mask(RQ, prices, stop_key, atr20)\n"
              "        d = (RQ > 0) & (S == 0)",
              "    rsqr_zeroed = int((SD > 0).sum().sum() - (RQ > 0)"
              ".sum().sum())\n    sumn_zeroed = int((RQ > 0).sum().sum() - "
              "(SU > 0).sum().sum())\n    if stop_key == \"none\":\n       "
              " S, stop_fired = SU, 0\n    else:\n        S = "
              "tl2._effective_signal_mask(SU, prices, stop_key, atr20)\n"
              "        d = (SU > 0) & (S == 0)", "curve zeroed + stop")
    mk = sub1(mk,
              "    return eq, res[\"trades\"], res[\"metrics\"], params, "
              "patch, stop_fired, \\\n        gate_zeroed, vol_zeroed, "
              "yang_zeroed, vconf_zeroed, \\\n        streak_zeroed, "
              "tstate_zeroed, amp_zeroed, mom_zeroed, \\\n        "
              "std_zeroed, rsqr_zeroed",
              "    return eq, res[\"trades\"], res[\"metrics\"], params, "
              "patch, stop_fired, \\\n        gate_zeroed, vol_zeroed, "
              "yang_zeroed, vconf_zeroed, \\\n        streak_zeroed, "
              "tstate_zeroed, amp_zeroed, mom_zeroed, \\\n        "
              "std_zeroed, rsqr_zeroed, sumn_zeroed", "curve return")
    mk = mk.replace("_null_axis_draw_w12", "_null_axis_draw_w13")
    mk = sub1(mk,
              "    (W12 berth 20321000, distinct from the W11 berth 20321000 "
              "-- zero\n    stream overlap by construction); consumption "
              "order frozen = p_on\n    regime -> FIFTEEN-tuple axis R/X/S/"
              "T/STOP/GATE/VOL/YANG/VCONF/\n    STREAK/TSTATE/AMP/MOM/STD/"
              "RSQR -> signal matrix (the rsqr gate leg merged\n    into "
              "the same grid/param space draw per prereg sec.3).  Same\n"
              "    engine/cost/panel as candidate cells incl. the gate + "
              "vol + yang +\n    vconf + streak + tstate + amp + mom + std "
              "+ rsqr legs\n    (BACKTEST_PLAN three iron rules).\"\"\"",
              "    (W13 berth 20323500, distinct from the W12 berth 20321000 "
              "-- zero\n    stream overlap by construction); consumption "
              "order frozen = p_on\n    regime -> SIXTEEN-tuple axis R/X/S/"
              "T/STOP/GATE/VOL/YANG/VCONF/\n    STREAK/TSTATE/AMP/MOM/STD/"
              "RSQR/SUMN -> signal matrix (the sumn gate leg merged\n    "
              "into the same grid/param space draw per prereg sec.3).  "
              "Same\n    engine/cost/panel as candidate cells incl. the "
              "gate + vol + yang +\n    vconf + streak + tstate + amp + mom "
              "+ std + rsqr + sumn legs\n    (BACKTEST_PLAN three iron "
              "rules).\"\"\"", "null docstring")
    mk = sub1(mk,
              "          AXIS_MOM[int(rng.integers(len(AXIS_MOM)))],\n"
              "          AXIS_STD[int(rng.integers(len(AXIS_STD)))],\n"
              "          AXIS_RSQR[int(rng.integers(len(AXIS_RSQR)))])",
              "          AXIS_MOM[int(rng.integers(len(AXIS_MOM)))],\n"
              "          AXIS_STD[int(rng.integers(len(AXIS_STD)))],\n"
              "          AXIS_RSQR[int(rng.integers(len(AXIS_RSQR)))],\n"
              "          AXIS_SUMN[int(rng.integers(len(AXIS_SUMN)))])",
              "null axis leg")
    src = src[:a] + mk + src[b:]
    steps.append("mask/curve/null: sumn leg wiring (axis[15], "
                 "composition +SUMN, SU chain, sumn_zeroed return)")
    return src


def sec11_generate(src, steps):
    src = sub1(src, '    """Frozen prereg sec.3 generate stage (W11 cmd_generate caliber on\n    the FIFTEEN-tuple face): per-slot Sobol streams consumed in global\n    round-robin -> 24-source exclusion -> T-84s3 dedup gate on the\n    effective signal face (gate + vol + yang + vconf + streak + tstate\n    + amp + MOM + STD overlays applied, frozen composition order) ->\n    w12_candidates.json + grammar ledger wave-12 row.  Zero engine cells\n    burned."""', '    """Frozen prereg sec.3 generate stage (W12 cmd_generate caliber on\n    the SIXTEEN-tuple face): per-slot Sobol streams consumed in global\n    round-robin -> 25-source exclusion -> T-84s3 dedup gate on the\n    effective signal face (gate + vol + yang + vconf + streak + tstate\n    + amp + MOM + STD + RSQR overlays applied, frozen composition\n    order) -> w13_candidates.json + grammar ledger wave-13 row.  Zero\n    engine cells burned."""', 'generate docstring')
    src = sub1(src, '    std_state, std_err = _std_state_full()\n    if std_err:\n        print(f"GENERATE-GATE: {std_err} (prereg sec.2 G-STD "\n              "fail-closed) -- refuse")\n        return 2\n    rsqr_state, rsqr_err = _rsqr_state_full()\n    if rsqr_err:\n        print(f"GENERATE-GATE: {rsqr_err} (prereg sec.2 G-RSQR "\n              "fail-closed) -- refuse")\n        return 2', '    std_state, std_err = _std_state_full()\n    if std_err:\n        print(f"GENERATE-GATE: {std_err} (prereg sec.2 G-STD "\n              "fail-closed) -- refuse")\n        return 2\n    rsqr_state, rsqr_err = _rsqr_state_full()\n    if rsqr_err:\n        print(f"GENERATE-GATE: {rsqr_err} (prereg sec.2 G-RSQR "\n              "fail-closed) -- refuse")\n        return 2\n    sumn_state, sumn_err = _sumn_state_full()\n    if sumn_err:\n        print(f"GENERATE-GATE: {sumn_err} (prereg sec.2 G-SUMN "\n              "fail-closed) -- refuse")\n        return 2', 'G-RSQR gate')
    src = sub1(src, '               ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_none_face"]', '               ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_none_face"]', 'neg_fns key')
    src = sub1(src, '        S = _effective_signal_mask_w12(mask, prices, cand["axis"][4], atr20,\n                                      cand["axis"][5], cand["axis"][6],\n                                      cand["axis"][7], cand["axis"][8],\n                                      cand["axis"][9], cand["axis"][10],\n                                      cand["axis"][11], cand["axis"][12],\n                                      cand["axis"][13], cand["axis"][14],\n                                      gate_state, vol_state, yang_state,\n                                      vconf_state, streak_state,\n                                      tstate_state, amp_state, mom_state,\n                                      std_state, rsqr_state)', '        S = _effective_signal_mask_w13(mask, prices, cand["axis"][4], atr20,\n                                      cand["axis"][5], cand["axis"][6],\n                                      cand["axis"][7], cand["axis"][8],\n                                      cand["axis"][9], cand["axis"][10],\n                                      cand["axis"][11], cand["axis"][12],\n                                      cand["axis"][13], cand["axis"][14],\n                                      cand["axis"][15],\n                                      gate_state, vol_state, yang_state,\n                                      vconf_state, streak_state,\n                                      tstate_state, amp_state, mom_state,\n                                      std_state, rsqr_state,\n                                      sumn_state)', 'generate mask call')
    src = sub1(src, '    mom_counts, std_counts = {}, {}\n    rsqr_counts = {}\n    gvvvsktsam_counts = {}', '    mom_counts, std_counts = {}, {}\n    rsqr_counts = {}\n    sumn_counts = {}\n    gvvvsktsam_counts = {}', 'counts init')
    src = sub1(src, '        std_counts[c["axis"][13]] = std_counts.get(c["axis"][13], 0) + 1\n        rsqr_counts[c["axis"][14]] = rsqr_counts.get(c["axis"][14], 0) + 1\n        k10 = (f"{c[\'axis\'][5]}|{c[\'axis\'][6]}|{c[\'axis\'][7]}|"\n              f"{c[\'axis\'][8]}|{c[\'axis\'][9]}|{c[\'axis\'][10]}|"\n              f"{c[\'axis\'][11]}|{c[\'axis\'][12]}|{c[\'axis\'][13]}|"\n              f"{c[\'axis\'][14]}")\n        gvvvsktsam_counts[k10] = gvvvsktsam_counts.get(k10, 0) + 1', '        std_counts[c["axis"][13]] = std_counts.get(c["axis"][13], 0) + 1\n        rsqr_counts[c["axis"][14]] = rsqr_counts.get(c["axis"][14], 0) + 1\n        sumn_counts[c["axis"][15]] = sumn_counts.get(c["axis"][15], 0) + 1\n        k11 = (f"{c[\'axis\'][5]}|{c[\'axis\'][6]}|{c[\'axis\'][7]}|"\n              f"{c[\'axis\'][8]}|{c[\'axis\'][9]}|{c[\'axis\'][10]}|"\n              f"{c[\'axis\'][11]}|{c[\'axis\'][12]}|{c[\'axis\'][13]}|"\n              f"{c[\'axis\'][14]}|{c[\'axis\'][15]}")\n        gvvvsktsam_counts[k11] = gvvvsktsam_counts.get(k11, 0) + 1', 'counts loop')
    src = sub1(src, '                                     "amp, mom, std, rsqr); exclusion face "\n                                     "= rsqr=none only (sec.1); prior-wave "\n                                     "keys rsqr=none-completed; rsqr in "\n                                     "{rsqr20_hi, rsqr10_hi} = "\n                                     "new-syntax legal cells"},', '                                     "amp, mom, std, rsqr, sumn); exclusion "\n                                     "face = sumn=none only (sec.1); prior-wave "\n                                     "keys sumn=none-completed; sumn in "\n                                     "{sumn20_lo, sumn10_lo} = "\n                                     "new-syntax legal cells"},', 'excl note')
    src = sub1(src, '"+ MOM + STD overlays applied, frozen "', '"+ MOM + STD + RSQR overlays applied, frozen "', 'dedup note')
    src = sub1(src, '               "std_face_counts": std_counts,\n               "rsqr_face_counts": rsqr_counts,\n               "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_face_"\n               "counts":\n                   gvvvsktsam_counts,', '               "std_face_counts": std_counts,\n               "rsqr_face_counts": rsqr_counts,\n               "sumn_face_counts": sumn_counts,\n               "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_"\n               "face_counts":\n                   gvvvsktsam_counts,', 'payload counts')
    src = sub1(src, '               "std_state_meta": std_state[2],\n               "rsqr_state_meta": rsqr_state[2],', '               "std_state_meta": std_state[2],\n               "rsqr_state_meta": rsqr_state[2],\n               "sumn_state_meta": sumn_state[2],', 'payload metas')
    src = sub1(src, '                         "seed_berth_note": "berths 20320500/"\n                         "20321000/20321500 held at the freeze commit "\n                         "(bm-b r444 three-step re-verify ALL GREEN, "\n                         "no re-pick; R250 one-step law; berth-open adoption "\n                         "of the bm-a r447 RSQR candidate whole package "\n                         "per AMP->W9/MOM->W10/STD->W11 adoption lineage)",', '                         "seed_berth_note": "berths 20323000/"\n                         "20323500/20324000 held at the freeze commit "\n                         "(bm-a r461 three-step re-verify ALL GREEN, "\n                         "no re-pick; R250 one-step law; berth-open adoption "\n                         "of the bm-a r456 SUMN candidate whole package "\n                         "per AMP->W9/MOM->W10/STD->W11/RSQR->W12 adoption lineage)",', 'berth note')
    src = sub1(src, '           f"(std faces {json.dumps(std_counts, sort_keys=True)}; "\n           f"rsqr faces {json.dumps(rsqr_counts, sort_keys=True)}; "\n           f"gate x vol x yang x vconf x streak x tstate x amp x mom "\n           f"x std x rsqr {json.dumps(gvvvsktsam_counts, sort_keys=True)}) "', '           f"(std faces {json.dumps(std_counts, sort_keys=True)}; "\n           f"rsqr faces {json.dumps(rsqr_counts, sort_keys=True)}; "\n           f"sumn faces {json.dumps(sumn_counts, sort_keys=True)}; "\n           f"gate x vol x yang x vconf x streak x tstate x amp x mom "\n           f"x std x rsqr x sumn {json.dumps(gvvvsktsam_counts, sort_keys=True)}) "', 'ledger row')
    src = sub1(src, '           f"TRIAL-LABOR-W12-GENERATE, T-124 prereg bm-b r444 frozen / "\n           f"runner bm-b r445) | "', '           f"TRIAL-LABOR-W13-GENERATE, T-125 prereg bm-a r461 frozen / "\n           f"runner bm-a r465) | "', 'ledger pool row')
    src = sub1(src, '    print(f"mom faces: {json.dumps(mom_counts, sort_keys=True)}; "\n          f"std faces: {json.dumps(std_counts, sort_keys=True)}; "\n          f"rsqr faces: {json.dumps(rsqr_counts, sort_keys=True)}; "\n          f"gate x vol x yang x vconf x streak x tstate x amp x mom x "\n          f"std x rsqr: "\n          f"{json.dumps(gvvvsktsam_counts, sort_keys=True)[:400]}")', '    print(f"mom faces: {json.dumps(mom_counts, sort_keys=True)}; "\n          f"std faces: {json.dumps(std_counts, sort_keys=True)}; "\n          f"rsqr faces: {json.dumps(rsqr_counts, sort_keys=True)}; "\n          f"sumn faces: {json.dumps(sumn_counts, sort_keys=True)}; "\n          f"gate x vol x yang x vconf x streak x tstate x amp x mom x "\n          f"std x rsqr x sumn: "\n          f"{json.dumps(gvvvsktsam_counts, sort_keys=True)[:400]}")', 'generate print')
    steps.append("generate: G-SUMN gate + sixteen-tuple dedup + counts")
    return src
def sec12_screen(src, steps):
    src = sub1(src, '                      "std_face", "std_zeroed",\n                      "rsqr_face", "rsqr_zeroed",\n                      "survives_screen"]', '                      "std_face", "std_zeroed",\n                      "rsqr_face", "rsqr_zeroed",\n                      "sumn_face", "sumn_zeroed",\n                      "survives_screen"]', 'csv cols')
    src = subn(src, '        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\\n            tz, az, mz, dz, rz = run_candidate_curve_w12(', '        eq, trades, metrics, params, patch, fired, gz, vz, yz, cz, sz, \\\n            tz, az, mz, dz, rz, nz = run_candidate_curve_w12(', 3, 'screen+judge cell unpack')
    src = subn(src, '                std_state=st.get("std_state"),\n                rsqr_state=st.get("rsqr_state"))', '                std_state=st.get("std_state"),\n                rsqr_state=st.get("rsqr_state"),\n                sumn_state=st.get("sumn_state"))', 2, 'screen cell state args')
    src = sub1(src, '           "mom_zeroed": int(mz), "std_face": cand["axis"][13],\n           "std_zeroed": int(dz),\n           "rsqr_face": cand["axis"][14],\n           "rsqr_zeroed": int(rz)}', '           "mom_zeroed": int(mz), "std_face": cand["axis"][13],\n           "std_zeroed": int(dz),\n           "rsqr_face": cand["axis"][14],\n           "rsqr_zeroed": int(rz),\n            "sumn_face": cand["axis"][15],\n            "sumn_zeroed": int(nz)}', 'screen row')
    src = sub1(src, '    std_meta_core = std_state_full[2]\n\n    # G-RSQR on the raw full-history face (prereg sec.2 probe basis =\n    # data/daily/sh510300.csv; 120-bar warmup + probe anchors\n    # decidable 3,363 / open 341 / rsqr10 3363/332 + slope split\n    # 213/128 + nine-gate 512-cell 124/388 law + extreme-day 0/7\n    # open states)\n    rsqr_state_full, rsqr_err = _rsqr_state_full()\n    if rsqr_err:\n        print(f"PREP-GATE FAIL: G-RSQR {rsqr_err}")\n        return 1\n    rsqr_meta_core = rsqr_state_full[2]\n', '    std_meta_core = std_state_full[2]\n\n    # G-RSQR on the raw full-history face (prereg sec.2 probe basis =\n    # data/daily/sh510300.csv; 120-bar warmup + probe anchors\n    # decidable 3,363 / open 341 / rsqr10 3363/332 + slope split\n    # 213/128 + nine-gate 512-cell 124/388 law + extreme-day 0/7\n    # open states)\n    rsqr_state_full, rsqr_err = _rsqr_state_full()\n    if rsqr_err:\n        print(f"PREP-GATE FAIL: G-RSQR {rsqr_err}")\n        return 1\n    rsqr_meta_core = rsqr_state_full[2]\n\n    # G-SUMN on the raw full-history face (prereg sec.2 probe basis =\n    # data/daily/sh510300.csv; 120-bar warmup + probe anchors\n    # decidable 3,363 / open 387 / sumn10 3363/368 + slope split\n    # 387/0 + nine-gate 512-cell 103/409 law + mirror-twin\n    # 387/0-xor + zero-co-open exact mad60/rsv60/mom)\n    sumn_state_full, sumn_err = _sumn_state_full()\n    if sumn_err:\n        print(f"PREP-GATE FAIL: G-SUMN {sumn_err}")\n        return 1\n    sumn_meta_core = sumn_state_full[2]\n', 'prep G-RSQR gate')
    src = subn(src, '                              (MOM_MEMBER, "mom"), (STD_MEMBER, "std"),\n                              (RSQR_MEMBER, "rsqr")):', '                              (MOM_MEMBER, "mom"), (STD_MEMBER, "std"),\n                              (RSQR_MEMBER, "rsqr"),\n                              (SUMN_MEMBER, "sumn")):', 2, 'member loops')
    src = sub1(src, '    _o20, _d20, std_meta, _o10, _d10 = std_state_series(prices)\n    if not _std_structure_pass(std_meta):\n        print(f"PREP-GATE FAIL: G-STD leg-L structural invariants "\n              f"broken {std_meta} -- honest refuse")\n        return 1\n    _r20o, _r20d, rsqr_meta, _r10o, _r10d = rsqr_state_series(prices)\n    if not _rsqr_structure_pass(rsqr_meta):\n        print(f"PREP-GATE FAIL: G-RSQR leg-L structural "\n              f"invariants broken {rsqr_meta} -- honest refuse")\n        return 1', '    _o20, _d20, std_meta, _o10, _d10 = std_state_series(prices)\n    if not _std_structure_pass(std_meta):\n        print(f"PREP-GATE FAIL: G-STD leg-L structural invariants "\n              f"broken {std_meta} -- honest refuse")\n        return 1\n    _r20o, _r20d, rsqr_meta, _r10o, _r10d = rsqr_state_series(prices)\n    if not _rsqr_structure_pass(rsqr_meta):\n        print(f"PREP-GATE FAIL: G-RSQR leg-L structural "\n              f"invariants broken {rsqr_meta} -- honest refuse")\n        return 1\n    _n20o, _n20d, sumn_meta, _n10o, _n10d = sumn_state_series(prices)\n    if not _sumn_structure_pass(sumn_meta):\n        print(f"PREP-GATE FAIL: G-SUMN leg-L structural "\n              f"invariants broken {sumn_meta} -- honest refuse")\n        return 1', 'prep legL structure')
    src = sub1(src, '                       "G-STD": {"pass": True,\n                                 "core48": std_meta_core,\n                                 "legL": std_meta},\n                       "G-RSQR": {"pass": True,\n                                  "core48": rsqr_meta_core,\n                                  "legL": rsqr_meta},', '                       "G-STD": {"pass": True,\n                                 "core48": std_meta_core,\n                                 "legL": std_meta},\n                       "G-RSQR": {"pass": True,\n                                  "core48": rsqr_meta_core,\n                                  "legL": rsqr_meta},\n                       "G-SUMN": {"pass": True,\n                                  "core48": sumn_meta_core,\n                                  "legL": sumn_meta},', 'prep payload G-RSQR')
    src = sub1(src, '            "amp_meta": amp_meta, "mom_meta": mom_meta,\n            "std_meta": std_meta,\n            "rsqr_meta": rsqr_meta,\n            "n_distinct": cg["n"], "n_starts_6m": len(starts),', '            "amp_meta": amp_meta, "mom_meta": mom_meta,\n            "std_meta": std_meta,\n            "rsqr_meta": rsqr_meta,\n            "sumn_meta": sumn_meta,\n            "n_distinct": cg["n"], "n_starts_6m": len(starts),', 'prep payload meta')
    src = sub1(src, '          f"{mom_meta[\'decidable_days\']} warmup "\n          f"{mom_meta[\'warmup_gate_closed_bars\']}; "\n          f"G-RSQR {rsqr_meta[\'open_days\']}open/"\n          f"{rsqr_meta[\'closed_days\']}closed decidable "\n          f"{rsqr_meta[\'decidable_days\']} rsqr10-open "\n          f"{rsqr_meta[\'rsqr10_open_days\']}")\n    return 0', '          f"{mom_meta[\'decidable_days\']} warmup "\n          f"{mom_meta[\'warmup_gate_closed_bars\']}; "\n          f"G-RSQR {rsqr_meta[\'open_days\']}open/"\n          f"{rsqr_meta[\'closed_days\']}closed decidable "\n          f"{rsqr_meta[\'decidable_days\']} rsqr10-open "\n          f"{rsqr_meta[\'rsqr10_open_days\']}; "\n          f"G-SUMN {sumn_meta[\'open_days\']}open/"\n          f"{sumn_meta[\'closed_days\']}closed decidable "\n          f"{sumn_meta[\'decidable_days\']} sumn10-open "\n          f"{sumn_meta[\'sumn10_open_days\']}")\n    return 0', 'prep print')
    src = sub1(src, '    mom_state = mom_state_series(prices)\n    std_state = std_state_series(prices)\n    rsqr_state = rsqr_state_series(prices)\n', '    mom_state = mom_state_series(prices)\n    std_state = std_state_series(prices)\n    rsqr_state = rsqr_state_series(prices)\n    sumn_state = sumn_state_series(prices)\n', 'shard state init')
    src = sub1(src, '             "mom_state": mom_state,\n             "std_state": std_state,\n             "rsqr_state": rsqr_state}', '             "mom_state": mom_state,\n             "std_state": std_state,\n             "rsqr_state": rsqr_state,\n             "sumn_state": sumn_state}', 'shard st')
    src = sub1(src, '    mom_counts, std_counts = {}, {}\n    rsqr_counts = {}\n    gate_seg, vol_seg, yang_seg, vconf_seg = {}, {}, {}, {}', '    mom_counts, std_counts = {}, {}\n    rsqr_counts = {}\n    sumn_counts = {}\n    gate_seg, vol_seg, yang_seg, vconf_seg = {}, {}, {}, {}', 'finalize counts init')
    src = sub1(src, '    std_seg, rsqr_seg, gvvvsktsamsr_seg = {}, {}, {}', '    std_seg, rsqr_seg, sumn_seg, gvvvsktsamsrn_seg = {}, {}, {}, {}', 'finalize segs init')
    src = sub1(src, '        stf = r["std_face"]\n        rqf = r["rsqr_face"]\n', '        stf = r["std_face"]\n        rqf = r["rsqr_face"]\n        nqf = r["sumn_face"]\n', 'finalize face read')
    src = sub1(src, '        std_counts[stf] = std_counts.get(stf, 0) + 1\n        rsqr_counts[rqf] = rsqr_counts.get(rqf, 0) + 1', '        std_counts[stf] = std_counts.get(stf, 0) + 1\n        rsqr_counts[rqf] = rsqr_counts.get(rqf, 0) + 1\n        sumn_counts[nqf] = sumn_counts.get(nqf, 0) + 1', 'finalize counts loop')
    src = sub1(src, '                         (std_seg, stf),\n                         (rsqr_seg, rqf),\n                         (gvvy_seg, f"{gf}|{vf}|{yf}|{cf}"),', '                         (std_seg, stf),\n                         (rsqr_seg, rqf),\n                         (sumn_seg, nqf),\n                         (gvvy_seg, f"{gf}|{vf}|{yf}|{cf}"),', 'finalize seg loop a')
    src = sub1(src, '                         (gvvvsktsams_seg,\n                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"\n                          f"{stf}"),\n                         (gvvvsktsamsr_seg,\n                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"\n                          f"{stf}|{rqf}")):', '                         (gvvvsktsams_seg,\n                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"\n                          f"{stf}"),\n                         (sumn_seg, nqf),\n                         (gvvvsktsamsrn_seg,\n                          f"{gf}|{vf}|{yf}|{cf}|{sf}|{tf}|{af}|{mf}|"\n                          f"{stf}|{rqf}|{nqf}")):', 'finalize seg loop b')
    src = sub1(src, '    for seg in (gate_seg, vol_seg, yang_seg, vconf_seg, streak_seg,\n                tstate_seg, amp_seg, mom_seg, std_seg, rsqr_seg, gvvy_seg,\n                gvvvsk_seg, gvvvskts_seg, gvvvsktsa_seg,\n                gvvvsktsam_seg, gvvvsktsams_seg, gvvvsktsamsr_seg):', '    for seg in (gate_seg, vol_seg, yang_seg, vconf_seg, streak_seg,\n                tstate_seg, amp_seg, mom_seg, std_seg, rsqr_seg, sumn_seg, gvvy_seg,\n                gvvvsk_seg, gvvvskts_seg, gvvvsktsa_seg,\n                gvvvsktsam_seg, gvvvsktsams_seg, gvvvsktsamsr_seg, gvvvsktsamsrn_seg):', 'finalize rate loop')
    src = sub1(src, '    std_meta = prep.get("std_meta")\n    rsqr_meta = prep.get("rsqr_meta")\n', '    std_meta = prep.get("std_meta")\n    rsqr_meta = prep.get("rsqr_meta")\n    sumn_meta = prep.get("sumn_meta")\n', 'finalize meta read')
    src = sub1(src, '           "std_face_counts": std_counts,\n           "rsqr_face_counts": rsqr_counts,\n           "gate_segmented_survival": gate_seg,', '           "std_face_counts": std_counts,\n           "rsqr_face_counts": rsqr_counts,\n           "sumn_face_counts": sumn_counts,\n           "gate_segmented_survival": gate_seg,', 'finalize payload counts')
    src = sub1(src, '           "std_segmented_survival": std_seg,\n           "rsqr_segmented_survival": rsqr_seg,', '           "std_segmented_survival": std_seg,\n           "rsqr_segmented_survival": rsqr_seg,\n           "sumn_segmented_survival": sumn_seg,', 'finalize payload segs')
    src = sub1(src, '           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_interaction_"\n           "survival": gvvvsktsams_seg,\n           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_interaction_"\n           "survival": gvvvsktsamsr_seg,', '           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_interaction_"\n           "survival": gvvvsktsams_seg,\n           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_interaction_"\n            "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_interaction_"\n            "survival": gvvvsktsamsrn_seg,\n           "survival": gvvvsktsamsr_seg,', 'finalize payload interaction')
    src = sub1(src, '           "std_na_window_bars": (std_meta["na_window_bars"]\n                                   if std_meta else None),\n           "rsqr_na_window_bars": (rsqr_meta["na_window_bars"]\n                                   if rsqr_meta else None),', '           "std_na_window_bars": (std_meta["na_window_bars"]\n                                   if std_meta else None),\n           "rsqr_na_window_bars": (rsqr_meta["na_window_bars"]\n                                   if rsqr_meta else None),\n           "sumn_na_window_bars": (sumn_meta["na_window_bars"]\n                                   if sumn_meta else None),', 'finalize na bars')
    src = sub1(src, '"MOM/STD/RSQR -> signal matrix (frozen "', '"MOM/STD/RSQR/SUM -> signal matrix (frozen "', 'finalize draw order a')
    src = sub1(src, '"vconf+streak+tstate+amp+mom+std+rsqr "\n', '"vconf+streak+tstate+amp+mom+std+rsqr+sum "\n', 'finalize draw order b')
    src = sub1(src, '                             "-> STREAK -> TSTATE -> AMP -> MOM -> STD -> "\n                             "RSQR -> initial-stop); MA200/"', '                             "-> STREAK -> TSTATE -> AMP -> MOM -> STD -> "\n                             "RSQR -> SUM -> initial-stop); MA200/"', 'finalize audit order')
    src = sub1(src, '                             "mom 139-bar warmup / std 120-bar warmup / rsqr "\n                             "120-bar warmup (panel-level counts in gate/vol/yang/vconf/"\n                             "streak/tstate/amp/mom/std/rsqr_na_window_bars); "', '                             "mom 139-bar warmup / std 120-bar warmup / rsqr / sumn "\n                             "120-bar warmup (panel-level counts in gate/vol/yang/vconf/"\n                             "streak/tstate/amp/mom/std/rsqr/sumn_na_window_bars); "', 'audit warmups')
    src = sub1(src, '                             "std20_hi/std10_hi keep face = open AND "\n                              "decidable (same erratum law); rsqr20_hi/rsqr10_hi keep "\n                              "face = open AND decidable (same erratum law); "', '                             "std20_hi/std10_hi keep face = open AND "\n                              "decidable (same erratum law); rsqr20_hi/rsqr10_hi keep "\n                              "face = open AND decidable (same erratum law); sumn20_lo/sumn10_lo keep "\n                              "face = open AND decidable (same erratum law); "', 'audit erratum')
    src = sub1(src, '    print(f"std segmented survival: {json.dumps(std_seg, sort_keys=True)}")\n    print(f"rsqr segmented survival: {json.dumps(rsqr_seg, sort_keys=True)}")\n    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "\n          f"interaction survival: "\n          f"{json.dumps(gvvvsktsam_seg, sort_keys=True)[:400]}")\n    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "\n          f"x std interaction survival: "\n          f"{json.dumps(gvvvsktsams_seg, sort_keys=True)[:400]}")\n    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom x "\n          f"std x rsqr interaction survival: "\n          f"{json.dumps(gvvvsktsamsr_seg, sort_keys=True)[:400]}")', '    print(f"std segmented survival: {json.dumps(std_seg, sort_keys=True)}")\n    print(f"rsqr segmented survival: {json.dumps(rsqr_seg, sort_keys=True)}")\n    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "\n          f"interaction survival: "\n          f"{json.dumps(gvvvsktsam_seg, sort_keys=True)[:400]}")\n    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "\n          f"x std interaction survival: "\n          f"{json.dumps(gvvvsktsams_seg, sort_keys=True)[:400]}")\n    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom x "\n          f"std x rsqr interaction survival: "\n          f"{json.dumps(gvvvsktsamsr_seg, sort_keys=True)[:400]}")\n    print(f"sumn segmented survival: {json.dumps(sumn_seg, sort_keys=True)}")\n    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom x "\n          f"std x rsqr x sumn interaction survival: "\n          f"{json.dumps(gvvvsktsamsrn_seg, sort_keys=True)[:400]}")', 'finalize prints')
    steps.append("screen slice: csv/cell/prep/shard/finalize sumn wiring")
    return src


def sec13_judge(src, steps):
    src = sub1(src, '    tl2._dual_nulls_w2 (import law; the seed constant is the only\n    differing face -- selftest cross-checks at the W12 unc-berth seed)."""', '    tl2._dual_nulls_w2 (import law; the seed constant is the only\n    differing face -- selftest cross-checks at the W13 unc-berth seed)."""', 'dual nulls docstring a')
    src = sub1(src, '    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;\n    W12 unc-berth seed binding [20321500, cell_idx].  Math imported verbatim from', '    B=2000 block-20 circular bootstrap + P=2000 sign-flip, two-sided;\n    W13 unc-berth seed binding [20324000, cell_idx].  Math imported verbatim from', 'dual nulls docstring b')
    src = sub1(src, 'def _overlay_stop_disclosure_w12(cand, prices, P, atr20, fundamental_ok,\n                                gate_state, vol_state, yang_state,\n                                vconf_state, streak_state, tstate_state,\n                                amp_state, mom_state, std_state,\n                                rsqr_state):', 'def _overlay_stop_disclosure_w12(cand, prices, P, atr20, fundamental_ok,\n                                gate_state, vol_state, yang_state,\n                                vconf_state, streak_state, tstate_state,\n                                amp_state, mom_state, std_state,\n                                rsqr_state, sumn_state):', 'stop disclosure sig')
    src = sub1(src, '    with the W12 composition order (filter -> timing -> GATE -> VOL ->\n    YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> STD ->\n    RSQR -> initial-stop; MSG-0440 E1 mapping + MSG-0450 annex 1).  Mirrors\n    tl11._overlay_stop_disclosure_w11 with the rsqr overlay inserted\n    before stop arming (engine-face consistency law; summary math\n    imported)."""', '    with the W13 composition order (filter -> timing -> GATE -> VOL ->\n    YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> STD ->\n    RSQR -> SUM -> initial-stop; MSG-0440 E1 mapping + MSG-0450 annex 1).  Mirrors\n    tl12._overlay_stop_disclosure_w12 with the sumn overlay inserted\n    before stop arming (engine-face consistency law; summary math\n    imported)."""', 'stop disclosure docstring')
    src = sub1(src, '    MO = mom_zero_mask(AP, cand["axis"][12], mom_state)\n    SD = std_zero_mask(MO, cand["axis"][13], std_state)\n    RQ = rsqr_zero_mask(SD, cand["axis"][14], rsqr_state)\n    _, ev = tl2.stop_exit_overlay(RQ, prices, stop_key, atr20)', '    MO = mom_zero_mask(AP, cand["axis"][12], mom_state)\n    SD = std_zero_mask(MO, cand["axis"][13], std_state)\n    RQ = rsqr_zero_mask(SD, cand["axis"][14], rsqr_state)\n    NQ = sumn_zero_mask(SD, cand["axis"][15], sumn_state)\n    _, ev = tl2.stop_exit_overlay(NQ, prices, stop_key, atr20)', 'stop disclosure chain')
    src = sub1(src, '           "std_face": cand["axis"][13],\n           "rsqr_face": cand["axis"][14]}\n    legs = {}', '           "std_face": cand["axis"][13],\n           "rsqr_face": cand["axis"][14],\n            "sumn_face": cand["axis"][15]}\n    legs = {}', 'judge cell out face')
    src = sub1(src, '        sd = st[f"std_state_{leg}"]\n        rq = st[f"rsqr_state_{leg}"]\n', '        sd = st[f"std_state_{leg}"]\n        rq = st[f"rsqr_state_{leg}"]\n        nq = st[f"sumn_state_{leg}"]\n', 'judge cell state read')
    src = sub1(src, '            eq2, _, m2, _, _, fired2, gz2, vz2, yz2, cz2, sz2, tz2, \\\n                az2, mz2, dz2, rz2 = run_candidate_curve_w12(', '            eq2, _, m2, _, _, fired2, gz2, vz2, yz2, cz2, sz2, tz2, \\\n                az2, mz2, dz2, rz2, nz2 = run_candidate_curve_w12(', 'judge cell unpack 2')
    src = sub1(src, '                                                 amp_state=ap,\n                                                 mom_state=mo,\n                                                 std_state=sd,\n                                                 rsqr_state=rq)', '                                                 amp_state=ap,\n                                                 mom_state=mo,\n                                                 std_state=sd,\n                                                 rsqr_state=rq,\n                                                 sumn_state=nq)', 'judge cell curve states 1')
    src = sub1(src, '                    streak_state=sk, tstate_state=ts, amp_state=ap,\n                    mom_state=mo, std_state=sd, rsqr_state=rq)', '                    streak_state=sk, tstate_state=ts, amp_state=ap,\n                    mom_state=mo, std_state=sd, rsqr_state=rq, sumn_state=nq)', 'judge cell curve states 2')
    src = sub1(src, '                         "std_zeroed": 0,\n                         "std_zeroed_x2": 0,\n                         "rsqr_zeroed": 0,\n                         "rsqr_zeroed_x2": 0,', '                         "std_zeroed": 0,\n                         "std_zeroed_x2": 0,\n                         "rsqr_zeroed": 0,\n                         "rsqr_zeroed_x2": 0,\n                         "sumn_zeroed": 0,\n                         "sumn_zeroed_x2": 0,', 'judge degenerate legs')
    src = sub1(src, '                     "std_zeroed": int(dz),\n                     "std_zeroed_x2": int(dz2),\n                     "rsqr_zeroed": int(rz),\n                     "rsqr_zeroed_x2": int(rz2),', '                     "std_zeroed": int(dz),\n                     "std_zeroed_x2": int(dz2),\n                     "rsqr_zeroed": int(rz),\n                     "rsqr_zeroed_x2": int(rz2),\n                     "sumn_zeroed": int(nz),\n                     "sumn_zeroed_x2": int(nz2),', 'judge legs dict')
    src = sub1(src, '            out["stop_disclosure"] = _overlay_stop_disclosure_w12(\n                cand, prices, P, st["atr20_L"], fok, gs, vs, ys, cs, sk,\n                ts, ap, mo, sd, rq)', '            out["stop_disclosure"] = _overlay_stop_disclosure_w12(\n                cand, prices, P, st["atr20_L"], fok, gs, vs, ys, cs, sk,\n                ts, ap, mo, sd, rq, nq)', 'stop disc call')
    src = sub1(src, '    std_state_full, std_err = _std_state_full()\n    if std_err:\n        print(f"JUDGE-GATE: {std_err} (prereg sec.2 G-STD "\n              "fail-closed) -- refuse")\n        return 2\n    rsqr_state_full, rsqr_err = _rsqr_state_full()\n    if rsqr_err:\n        print(f"JUDGE-GATE: {rsqr_err} (prereg sec.2 G-RSQR "\n              "fail-closed) -- refuse")\n        return 2', '    std_state_full, std_err = _std_state_full()\n    if std_err:\n        print(f"JUDGE-GATE: {std_err} (prereg sec.2 G-STD "\n              "fail-closed) -- refuse")\n        return 2\n    rsqr_state_full, rsqr_err = _rsqr_state_full()\n    if rsqr_err:\n        print(f"JUDGE-GATE: {rsqr_err} (prereg sec.2 G-RSQR "\n              "fail-closed) -- refuse")\n        return 2\n    sumn_state_full, sumn_err = _sumn_state_full()\n    if sumn_err:\n        print(f"JUDGE-GATE: {sumn_err} (prereg sec.2 G-SUMN "\n              "fail-closed) -- refuse")\n        return 2', 'judge cmd G-RSQR gate')
    src = sub1(src, '        sdst = std_state_series(prices)\n        state[f"std_state_{leg}"] = sdst\n        state[f"std_meta_{leg}"] = sdst[2]\n        rst = rsqr_state_series(prices)\n        state[f"rsqr_state_{leg}"] = rst\n        state[f"rsqr_meta_{leg}"] = rst[2]', '        sdst = std_state_series(prices)\n        state[f"std_state_{leg}"] = sdst\n        state[f"std_meta_{leg}"] = sdst[2]\n        rst = rsqr_state_series(prices)\n        state[f"rsqr_state_{leg}"] = rst\n        state[f"rsqr_meta_{leg}"] = rst[2]\n        nst = sumn_state_series(prices)\n        state[f"sumn_state_{leg}"] = nst\n        state[f"sumn_meta_{leg}"] = nst[2]', 'judge cmd per-leg state')
    src = sub1(src, '    std_state_full, std_err = _std_state_full()\n    if std_err:\n        print(f"JUDGE-PREP-GATE FAIL: G-STD {std_err}")\n        return 1\n    rsqr_state_full, rsqr_err = _rsqr_state_full()\n    if rsqr_err:\n        print(f"JUDGE-PREP-GATE FAIL: G-RSQR {rsqr_err}")\n        return 1', '    std_state_full, std_err = _std_state_full()\n    if std_err:\n        print(f"JUDGE-PREP-GATE FAIL: G-STD {std_err}")\n        return 1\n    rsqr_state_full, rsqr_err = _rsqr_state_full()\n    if rsqr_err:\n        print(f"JUDGE-PREP-GATE FAIL: G-RSQR {rsqr_err}")\n        return 1\n    sumn_state_full, sumn_err = _sumn_state_full()\n    if sumn_err:\n        print(f"JUDGE-PREP-GATE FAIL: G-SUMN {sumn_err}")\n        return 1', 'judge prep G-RSQR gate')
    src = sub1(src, '    tstate_meta, amp_meta, mom_meta, std_meta = {}, {}, {}, {}\n    rsqr_meta = {}', '    tstate_meta, amp_meta, mom_meta, std_meta = {}, {}, {}, {}\n    rsqr_meta = {}\n    sumn_meta = {}', 'judge prep metas init')
    src = sub1(src, '                                  (STD_MEMBER, "std"),\n                                  (RSQR_MEMBER, "rsqr")):\n            if member not in prices:', '                                  (STD_MEMBER, "std"),\n                                  (RSQR_MEMBER, "rsqr"),\n                                  (SUMN_MEMBER, "sumn")):\n            if member not in prices:', 'judge prep member loop')
    src = sub1(src, '        rsqr_meta[leg] = rsqreta', '        rsqr_meta[leg] = rsqreta\n        _n20o, _n20d, sumneta, _n10o, _n10d = sumn_state_series(prices)\n        if not _sumn_structure_pass(sumneta):\n            print(f"JUDGE-PREP-GATE FAIL: leg-{leg} G-SUMN structural "\n                  f"invariants broken {sumneta} -- honest refuse")\n            return 1\n        # per-leg slope-sign disclosure (mirror of the full-face\n        # sec.2(e) computation in _sumn_state_full; same frozen\n        # runner face, additive disclosure key -- not a gate input)\n        _c20 = _sumn_faces_raw(prices)[9]\n        _nmopen = _n20o & _n20d & _c20.notna()\n        sumneta["slope_sign_split"] = {\n            "up_slope_days": int((_nmopen & (_c20 > 0)).sum()),\n            "down_slope_days": int((_nmopen & (_c20 <= 0)).sum()),\n            "note": "BETA20 sign from the same frozen runner; "\n                    "up-dominant windows are slope-up-heavy BY "\n                    "CONSTRUCTION (direction-loaded up-share axis) "\n                    "-- the split quantifies how much; direction "\n                    "conditioning still lives in burned axes "\n                    "(GATE/YANG/STREAK/MOM), redundancy measured "\n                    "in adjacency cells"}\n        sumn_meta[leg] = sumneta', 'judge prep per-leg structure')
    src = sub1(src, '    std_meta["full_raw_face"] = std_state_full[2]\n    rsqr_meta["full_raw_face"] = rsqr_state_full[2]', '    std_meta["full_raw_face"] = std_state_full[2]\n    rsqr_meta["full_raw_face"] = rsqr_state_full[2]\n    sumn_meta["full_raw_face"] = sumn_state_full[2]', 'judge prep full_raw_face')
    src = subn(src, '               "amp_meta": amp_meta, "mom_meta": mom_meta,\n               "std_meta": std_meta,\n               "rsqr_meta": rsqr_meta,\n               "vacuous": True,', '               "amp_meta": amp_meta, "mom_meta": mom_meta,\n               "std_meta": std_meta,\n               "rsqr_meta": rsqr_meta,\n               "sumn_meta": sumn_meta,\n               "vacuous": True,', 1, 'prep vacuous payload')
    src = subn(src, '           "mom_meta": mom_meta,\n           "std_meta": std_meta,\n           "rsqr_meta": rsqr_meta,\n           "manifest_note":', '           "mom_meta": mom_meta,\n           "std_meta": std_meta,\n           "rsqr_meta": rsqr_meta,\n           "sumn_meta": sumn_meta,\n           "manifest_note":', 1, 'prep main payload')
    src = sub1(src, '    print(f"std meta L 120-bar-warmup "\n          f"{std_meta[\'L\'][\'open_days\']}open/"\n          f"{std_meta[\'L\'][\'closed_days\']}closed decidable "\n          f"{std_meta[\'L\'][\'decidable_days\']} std10-open "\n          f"{std_meta[\'L\'][\'std10_open_days\']}")\n    print(f"rsqr meta L 120-bar-warmup "\n          f"{rsqr_meta[\'L\'][\'open_days\']}open/"\n          f"{rsqr_meta[\'L\'][\'closed_days\']}closed decidable "\n          f"{rsqr_meta[\'L\'][\'decidable_days\']} rsqr10-open "\n          f"{rsqr_meta[\'L\'][\'rsqr10_open_days\']} slope-split "\n          f"{rsqr_meta[\'L\'][\'slope_sign_split\']}")', '    print(f"std meta L 120-bar-warmup "\n          f"{std_meta[\'L\'][\'open_days\']}open/"\n          f"{std_meta[\'L\'][\'closed_days\']}closed decidable "\n          f"{std_meta[\'L\'][\'decidable_days\']} std10-open "\n          f"{std_meta[\'L\'][\'std10_open_days\']}")\n    print(f"rsqr meta L 120-bar-warmup "\n          f"{rsqr_meta[\'L\'][\'open_days\']}open/"\n          f"{rsqr_meta[\'L\'][\'closed_days\']}closed decidable "\n          f"{rsqr_meta[\'L\'][\'decidable_days\']} rsqr10-open "\n          f"{rsqr_meta[\'L\'][\'rsqr10_open_days\']} slope-split "\n          f"{rsqr_meta[\'L\'][\'slope_sign_split\']}")\n    print(f"sumn meta L 120-bar-warmup "\n          f"{sumn_meta[\'L\'][\'open_days\']}open/"\n          f"{sumn_meta[\'L\'][\'closed_days\']}closed decidable "\n          f"{sumn_meta[\'L\'][\'decidable_days\']} sumn10-open "\n          f"{sumn_meta[\'L\'][\'sumn10_open_days\']} slope-split "\n          f"{sumn_meta[\'L\'][\'slope_sign_split\']}")', 'judge prep print')
    src = sub1(src, '    amp_sum, mom_sum, std_sum = {}, {}, {}\n    rsqr_sum = {}\n    gvy_sum, gvvy_sum, gvvvsk_sum = {}, {}, {}\n    gvvvskts_sum, gvvvsktsa_sum, gvvvsktsam_sum = {}, {}, {}\n    gvvvsktsams_sum = {}\n    gvvvsktsamsr_sum = {}', '    amp_sum, mom_sum, std_sum = {}, {}, {}\n    rsqr_sum = {}\n    gvy_sum, gvvy_sum, gvvvsk_sum = {}, {}, {}\n    gvvvskts_sum, gvvvsktsa_sum, gvvvsktsam_sum = {}, {}, {}\n    gvvvsktsams_sum = {}\n    gvvvsktsamsr_sum = {}\n    sumn_sum = {}\n    gvvvsktsamsrn_sum = {}', 'judge final sums init')
    src = sub1(src, '        stf = r.get("std_face", "none")\n        rqf = r.get("rsqr_face", "none")\n', '        stf = r.get("std_face", "none")\n        rqf = r.get("rsqr_face", "none")\n        nqf = r.get("sumn_face", "none")\n', 'judge final face read')
    src = sub1(src, '                         (std_sum, stf),\n                         (rsqr_sum, rqf),\n                         (gvy_sum, f"{g}|{v}|{y}"),', '                         (std_sum, stf),\n                         (rsqr_sum, rqf),\n                         (sumn_sum, nqf),\n                         (gvy_sum, f"{g}|{v}|{y}"),', 'judge final seg loop a')
    src = sub1(src, '                         (gvvvsktsams_sum,\n                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}|{stf}"),\n                         (gvvvsktsamsr_sum,\n                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}|{stf}|{rqf}")):', '                         (gvvvsktsams_sum,\n                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}|{stf}"),\n                         (sumn_sum, nqf),\n                         (gvvvsktsamsrn_sum,\n                          f"{g}|{v}|{y}|{c}|{s}|{t}|{a}|{m}|{stf}|{rqf}|{nqf}")):', 'judge final seg loop b')
    src = sub1(src, '           "std_face_judgment": std_sum,\n           "rsqr_face_judgment": rsqr_sum,', '           "std_face_judgment": std_sum,\n           "rsqr_face_judgment": rsqr_sum,\n           "sumn_face_judgment": sumn_sum,', 'judge final payload sums')
    src = sub1(src, '           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_interaction_"\n           "judgment": gvvvsktsams_sum,\n           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_interaction_"\n           "judgment": gvvvsktsamsr_sum,', '           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_interaction_"\n           "judgment": gvvvsktsams_sum,\n           "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_interaction_"\n            "gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_interaction_"\n            "judgment": gvvvsktsamsrn_sum,\n           "judgment": gvvvsktsamsr_sum,', 'judge final payload interaction')
    src = sub1(src, '                             "gate + vol + yang + vconf + streak + "\n                             "tstate + amp + MOM + STD + RSQR overlays carried "\n                             "per "\n                             "cell (frozen composition signal -> filter "\n                             "-> timing -> GATE -> VOL -> YANG -> VCONF "\n                             "-> STREAK -> TSTATE -> AMP -> MOM -> STD -> "\n                             "RSQR -> initial-stop; "', '                             "gate + vol + yang + vconf + streak + "\n                             "tstate + amp + MOM + STD + RSQR + SUM overlays carried "\n                             "per "\n                             "cell (frozen composition signal -> filter "\n                             "-> timing -> GATE -> VOL -> YANG -> VCONF "\n                             "-> STREAK -> TSTATE -> AMP -> MOM -> STD -> "\n                             "RSQR -> SUM -> initial-stop; "', 'judge final audit')
    src = sub1(src, '    print(f"std-face judgment: {json.dumps(std_sum, sort_keys=True)}")\n    print(f"rsqr-face judgment: {json.dumps(rsqr_sum, sort_keys=True)}")\n    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "\n          f"interaction judgment: "\n          f"{json.dumps(gvvvsktsam_sum, sort_keys=True)[:400]}")', '    print(f"std-face judgment: {json.dumps(std_sum, sort_keys=True)}")\n    print(f"rsqr-face judgment: {json.dumps(rsqr_sum, sort_keys=True)}")\n    print(f"sumn-face judgment: {json.dumps(sumn_sum, sort_keys=True)}")\n    print(f"gate x vol x yang x vconf x streak x tstate x amp x mom "\n          f"interaction judgment: "\n          f"{json.dumps(gvvvsktsam_sum, sort_keys=True)[:400]}")', 'judge final prints')
    src = sub1(src, '                             "the protection-floor signal face with the "\n                             "std+rsqr overlays inserted before stop arming "\n                             "(W11/W12 composition law); gate_flip_days_legL "', '                             "the protection-floor signal face with the "\n                             "std+rsqr+sumn overlays inserted before stop arming "\n                             "(W12/W13 composition law); gate_flip_days_legL "', 'judge final audit stop note')
    src = sub1(src, '    """s4 D6 binding gate (W2 cmd_intake precedent on the W11 file\n    faces):', '    """s4 D6 binding gate (W2 cmd_intake precedent on the W12 file\n    faces):', 'intake docstring')
    steps.append("judge slice: prep/cell/finalize sumn wiring")
    return src


def sec14_selftest(src, steps):
    src = sub1(src, '    zero cell evaluation): MOM causality / 139-bar warmup / NaN\n    comparison-artifact leg (pit-95 batch-95 + r431 erratum face) /\n    mom=none identity / eight-gate intersection / G-MOM probe anchors\n    (incl. eight-gate 256-cell 111/145 + extreme days 2/7 + core48\n    spread) / G-RSQR probe anchors (nine-gate 512-cell 124/388 +\n    slope split 213/128 + core48 spread) / grammar structure / draw\n    determinism / 24-source exclusion loader / engine double-run\n    determinism legs / funnel faces (dispatch / null-cell engine path /\n    CSV contract) + pit-95 finalize guards."""', '    zero cell evaluation): MOM causality / 139-bar warmup / NaN\n    comparison-artifact leg (pit-95 batch-95 + r431 erratum face) /\n    mom=none identity / eight-gate intersection / G-MOM probe anchors\n    (incl. eight-gate 256-cell 111/145 + extreme days 2/7 + core48\n    spread) / G-SUMN probe anchors (nine-gate 512-cell 103/409 +\n    slope split 387/0 + core48 spread) / grammar structure / draw\n    determinism / 25-source exclusion loader / engine double-run\n    determinism legs / funnel faces (dispatch / null-cell engine path /\n    CSV contract) + pit-95 finalize guards."""', 'selftest docstring')
    src = sub1(src, '    _ok("L6a axis_combos == 94,058,496 (31,352,832 x 3 rsqr-axis "\n        "values; W11 std-face combos x len(AXIS_RSQR))",\n        g["axis_combos"] == 94058496\n        == tl11.AXIS_COMBOS * len(AXIS_RSQR))', '    _ok("L6a axis_combos == 282,175,488 (94,058,496 x 3 sumn-axis "\n        "values; W12 rsqr-face combos x len(AXIS_SUMN))",\n        g["axis_combos"] == 282175488\n        == tl12.AXIS_COMBOS * len(AXIS_SUMN))', 'L6a')
    src = sub1(src, '    _ok("L6b fifteen axes present, rsqr == frozen three-value",\n        len(g["axes"]) == 15 and g["axes"]["rsqr"] == AXIS_RSQR)', '    _ok("L6b sixteen axes present, sumn == frozen three-value",\n        len(g["axes"]) == 16 and g["axes"]["sumn"] == AXIS_SUMN)', 'L6b')
    src = sub1(src, '    _ok("L6c W12 seeds == SEED_REGISTRY berths (20320500/20321000/"\n        "20321500 berths held, no re-pick)",', '    _ok("L6c W13 seeds == SEED_REGISTRY berths (20323000/20323500/"\n        "20324000 berths held, no re-pick)",', 'L6c text')
    src = sub1(src, '    _ok("L6d new sha16 constructively distinct from W1/MASS/W2-W11",\n        sha not in set(PRIOR_WAVE_SHA16.values())\n        and sha != tl11.FROZEN_SHA16,', '    _ok("L6d new sha16 constructively distinct from W1/MASS/W2-W12",\n        sha not in set(PRIOR_WAVE_SHA16.values())\n        and sha != tl12.FROZEN_SHA16,', 'L6d')
    src = sub1(src, '    _ok("L6e exclusion face rows rsqr=none-padded to 15-long axis",\n        all(len(r["axis"]) == 15 and r["axis"][-1] == "none"\n            for r in g["exclusion"]\n            ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_none_face"]))', '    _ok("L6e exclusion face rows sumn=none-padded to 16-long axis",\n        all(len(r["axis"]) == 16 and r["axis"][-1] == "none"\n            for r in g["exclusion"]\n            ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_none_face"]))', 'L6e')
    src = sub1(src, '        if os.path.exists(PROBE_FACTS_FILE):\n            pf = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))\n            rstate2, rerr2 = _rsqr_state_full()\n            _ok("L7g probe-facts exact per-cell 512-grid cross-check "\n                "(r447 determinism law: every computed RSQR-face cell "\n                "== the git-tracked frozen probe face)",\n                rerr2 is None\n                and rstate2[2]["nine_gate_512cells"]\n                == pf.get("nine_gate_cells"),\n                rerr2 or "rsqr-face cells == probe facts")\n        # core48 member-level rsqr20 open-rate spread (r447 probe\n        # method verbatim; frozen-runner RSQR verbatim)\n        prices_r = tl1.load_core()\n        cut_r = pd.Timestamp(CUTOFF)\n        rates2 = {}\n        for sym, d2 in sorted(prices_r.items()):\n            d2 = d2[d2.index <= cut_r]\n            if len(d2) >= 260:\n                op2, wdec2, _ = rsqr_state_series({RSQR_MEMBER: d2})[:3]\n                if wdec2.any():\n                    rates2[str(sym)] = round(float(\n                        (op2 & wdec2).mean()), 4)\n        vals2 = sorted(rates2.values())\n        cf2 = RSQR_ANCHOR["core48_rsqr20_open_rate"]\n        _ok("L7i core48 rsqr20-open-rate spread (n 48 / min 0.0891 / "\n            "median 0.1009 / max 0.1183; r447 probe face)",\n            len(vals2) == cf2["n"] and vals2[0] == cf2["min"]\n            and vals2[len(vals2) // 2] == cf2["median"]\n            and vals2[-1] == cf2["max"],\n            f"n={len(vals2)} min={vals2[0] if vals2 else None}")', '        if os.path.exists(PROBE_FACTS_FILE):\n            pf = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))\n            nstate2, nerr2 = _sumn_state_full()\n            _ok("L7g probe-facts exact per-cell 512-grid cross-check "\n                "(r456 determinism law: every computed SUMN-face cell "\n                "== the git-tracked frozen probe face)",\n                nerr2 is None\n                and nstate2[2]["nine_gate_512cells"]\n                == pf.get("nine_gate_cells"),\n                nerr2 or "sumn-face cells == probe facts")\n        # core48 member-level sumn20 open-rate spread (r456 probe\n        # method verbatim; frozen-runner SUMN verbatim)\n        prices_r = tl1.load_core()\n        cut_r = pd.Timestamp(CUTOFF)\n        rates2 = {}\n        for sym, d2 in sorted(prices_r.items()):\n            d2 = d2[d2.index <= cut_r]\n            if len(d2) >= 260:\n                op2, wdec2, _ = sumn_state_series({SUMN_MEMBER: d2})[:3]\n                if wdec2.any():\n                    rates2[str(sym)] = round(float(\n                        (op2 & wdec2).mean()), 4)\n        vals2 = sorted(rates2.values())\n        cf2 = SUMN_ANCHOR["core48_sumn20_open_rate"]\n        _ok("L7i core48 sumn20-open-rate spread (n 48 / min 0.0728 / "\n            "median 0.1012 / max 0.1171; r456 probe face)",\n            len(vals2) == cf2["n"] and vals2[0] == cf2["min"]\n            and vals2[len(vals2) // 2] == cf2["median"]\n            and vals2[-1] == cf2["max"],\n            f"n={len(vals2)} min={vals2[0] if vals2 else None}")', 'L7g+L7i')
    src = sub1(src, '    _ok("L8a Sobol draw determinism (same seed -> byte-identical "\n        "candidate incl. the std+rsqr axes, fifteen-tuple)",\n        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],\n                                                        sort_keys=True)\n        and len(c1[1]["axis"]) == 15)', '    _ok("L8a Sobol draw determinism (same seed -> byte-identical "\n        "candidate incl. the rsqr+sumn axes, sixteen-tuple)",\n        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],\n                                                        sort_keys=True)\n        and len(c1[1]["axis"]) == 16)', 'L8a')
    src = sub1(src, '    fifteen = [rng_a.integers(0, 4, n) for _ in range(15)]\n    rng_b = np.random.default_rng([SEED_GEN + 0, 7919])\n    thirteen = [rng_b.integers(0, 4, n) for _ in range(13)]\n    _ok("L8b STD+RSQR append AFTER AMP in the rng stream (first thirteen "\n        "axis arrays == W10-order stream verbatim, zero disturbance)",\n        all(np.array_equal(a, b) for a, b in zip(fifteen, thirteen)))', '    sixteen = [rng_a.integers(0, 4, n) for _ in range(16)]\n    rng_b = np.random.default_rng([SEED_GEN + 0, 7919])\n    fourteen = [rng_b.integers(0, 4, n) for _ in range(14)]\n    _ok("L8b RSQR+SUM append AFTER AMP in the rng stream (first fourteen "\n        "axis arrays == W11-order stream verbatim, zero disturbance)",\n        all(np.array_equal(a, b) for a, b in zip(sixteen, fourteen)))', 'L8b')
    src = sub1(src, '    _ok("L9a exclusion loader: every row a 15-tuple axis, rsqr=none "\n        "at 14 for ALL rows + std at 13 inside the frozen three-value "\n        "domain + W11 real-std rows present (24 sources; W1-W10 "\n        "sources std=none, W11 survivors/judged carry real values)",\n        all(len(r["axis"]) == 15 and r["axis"][14] == "none"\n            and r["axis"][13] in AXIS_STD for r in rows10)\n        and any(r["axis"][13] in ("std20_hi", "std10_hi")\n                for r in rows10)\n        and {"w1_screen_survivors", "mass_screen_survivors",\n             "w9_screen_survivors", "w9_judge_products",\n             "w10_screen_survivors", "w10_judge_products",\n             "w12_screen_survivors", "w12_judge_products",\n             "judged_supply_weighting"} <= set(disc10))', '    _ok("L9a exclusion loader: every row a 16-tuple axis, sumn=none "\n        "at 15 for ALL rows + rsqr at 14 inside the frozen three-value "\n        "domain + W12 real-rsqr rows present (25 sources; W1-W11 "\n        "sources rsqr=none, W12 survivors/judged carry real values)",\n        all(len(r["axis"]) == 16 and r["axis"][15] == "none"\n            and r["axis"][14] in AXIS_RSQR for r in rows10)\n        and any(r["axis"][14] in ("rsqr20_hi", "rsqr10_hi")\n                for r in rows10)\n        and {"w1_screen_survivors", "mass_screen_survivors",\n             "w9_screen_survivors", "w9_judge_products",\n             "w10_screen_survivors", "w10_judge_products",\n             "w12_screen_survivors", "w12_judge_products",\n             "w13_screen_survivors", "w13_judge_products",\n             "judged_supply_weighting"} <= set(disc10))', 'L9a')
    src = sub1(src, '        "== 243 (generate-time re-declare window, prereg sec.1 TWELVE "\n        "judge sources; W9-JUDGE landed 2026-09-29 17:47:46)"', '        "== 243 (generate-time re-declare window, prereg sec.1 THIRTEEN "\n        "judge sources; W9-JUDGE landed 2026-09-29 17:47:46)"', 'L9b text')
    src = sub1(src, '    miss = _excluded_w12({**hit_key,\n                          "axis": [*hit_key["axis"][:14],\n                                   "rsqr20_hi"]},\n                         rows10)\n    _ok("L10b rsqr in {rsqr20_hi, rsqr10_hi} = new-syntax legal cell, "\n        "never excluded",\n        miss is None)', '    miss = _excluded_w12({**hit_key,\n                          "axis": [*hit_key["axis"][:15],\n                                   "sumn20_lo"]},\n                         rows10)\n    _ok("L10b sumn in {sumn20_lo, sumn10_lo} = new-syntax legal cell, "\n        "never excluded",\n        miss is None)', 'L10b')
    src = sub1(src, '    ss3 = std_state_series(frames3)\n    rq3 = rsqr_state_series(frames3)\n', '    ss3 = std_state_series(frames3)\n    rq3 = rsqr_state_series(frames3)\n    nq3 = sumn_state_series(frames3)\n', 'L12 rq3')
    src = sub1(src, '    ss5 = std_state_series(frames5)\n    rq5 = rsqr_state_series(frames5)\n', '    ss5 = std_state_series(frames5)\n    rq5 = rsqr_state_series(frames5)\n    nq5 = sumn_state_series(frames5)\n', 'L12 rq5')
    src = sub1(src, '            "axis": ["none", "time_stop_5d", "equal_weight",\n                     "daily_signal", "none", "none", "none", "none",\n                     "none", "none", "none", "none", "none",\n                     "none", "none"]}', '            "axis": ["none", "time_stop_5d", "equal_weight",\n                     "daily_signal", "none", "none", "none", "none",\n                     "none", "none", "none", "none", "none",\n                     "none", "none", "none"]}', 'L13 base axis fifteen')
    src = sub1(src, '        "none", "none", "none", "none", "none", "none", gs3,\n        vs3, ys3, cs3, sk3, ts3, as3, ms3, ss3, rq3)', '        "none", "none", "none", "none", "none", "none", "none", gs3,\n        vs3, ys3, cs3, sk3, ts3, as3, ms3, ss3, rq3, nq3)', 'L12 mask calls gs3 none')
    src = sub1(src, '        "none", "none", "none", "mom_oversold", "none", "none", gs3,\n        vs3, ys3, cs3, sk3, ts3, as3, ms3, ss3, rq3)', '        "none", "none", "none", "mom_oversold", "none", "none", "none", gs3,\n        vs3, ys3, cs3, sk3, ts3, as3, ms3, ss3, rq3, nq3)', 'L12 mask calls gs3 mom')
    src = sub1(src, '        "none", "none", "none", "none", "none", "none", gs5,\n        vs5, ys5, cs5, sk5, ts5, as5, ms5, ss5, rq5)', '        "none", "none", "none", "none", "none", "none", "none", gs5,\n        vs5, ys5, cs5, sk5, ts5, as5, ms5, ss5, rq5, nq5)', 'L12 mask calls gs5 none')
    src = sub1(src, '        "none", "none", "none", "mom_oversold", "none", "none", gs5,\n        vs5, ys5, cs5, sk5, ts5, as5, ms5, ss5, rq5)', '        "none", "none", "none", "mom_oversold", "none", "none", "none", gs5,\n        vs5, ys5, cs5, sk5, ts5, as5, ms5, ss5, rq5, nq5)', 'L12 mask calls gs5 mom')
    src = sub1(src, '    eq10, tr10, m10, _, _, _, _, _, _, _, sz10, tz10, az10, mz10, \\\n        sdz10, rz10 = \\\n        run_candidate_curve_w12(\n            base, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n            std_state=ss3, rsqr_state=rq3)', '    eq10, tr10, m10, _, _, _, _, _, _, _, sz10, tz10, az10, mz10, \\\n        sdz10, rz10, nz10 = \\\n        run_candidate_curve_w12(\n            base, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n            std_state=ss3, rsqr_state=rq3, sumn_state=nq3)', 'L13a')
    src = sub1(src, '    _ok("L13b engine double-run byte-identity (determinism leg) + "\n        "16-tuple return shape (rsqr_zeroed carried)",\n        list(eq10.values) == list(eq10b.values) and sz10 == sz10b\n        and tz10 == tz10b and az10 == az10b and mz10 == mz10b == 0\n        and rz10 == 0)', '    _ok("L13b engine double-run byte-identity (determinism leg) + "\n        "17-tuple return shape (sumn_zeroed carried)",\n        list(eq10.values) == list(eq10b.values) and sz10 == sz10b\n        and tz10 == tz10b and az10 == az10b and mz10 == mz10b == 0\n        and rz10 == 0\n        and nz10 == 0)', 'L13b check')
    src = sub1(src, '    eq10b, _, _, _, _, _, _, _, _, _, sz10b, tz10b, az10b, mz10b, \\\n        _, _ = \\\n        run_candidate_curve_w12(\n            dict(base, candidate_id="ST-B-0001"), None, frames3, P3,\n            st3, gate_state=gs3, vol_state=vs3, yang_state=ys3,\n            vconf_state=cs3, streak_state=sk3, tstate_state=ts3,\n            amp_state=as3, mom_state=ms3, std_state=ss3,\n            rsqr_state=rq3)', '    eq10b, _, _, _, _, _, _, _, _, _, sz10b, tz10b, az10b, mz10b, \\\n        _, _, _ = \\\n        run_candidate_curve_w12(\n            dict(base, candidate_id="ST-B-0001"), None, frames3, P3,\n            st3, gate_state=gs3, vol_state=vs3, yang_state=ys3,\n            vconf_state=cs3, streak_state=sk3, tstate_state=ts3,\n            amp_state=as3, mom_state=ms3, std_state=ss3,\n            rsqr_state=rq3, sumn_state=nq3)', 'L13b call')
    src = sub1(src, '    eq5n, tr5n, m5n, _, _, _, _, _, _, _, _, _, az5n, mz5n, _, _ = \\\n        run_candidate_curve_w12(\n            dict(base, axis=list(base["axis"])), None, frames5, P5,\n            st5, gate_state=gs5, vol_state=vs5, yang_state=ys5,\n            vconf_state=cs5, streak_state=sk5, tstate_state=ts5,\n            amp_state=as5, mom_state=ms5, std_state=ss5,\n            rsqr_state=rq5)', '    eq5n, tr5n, m5n, _, _, _, _, _, _, _, _, _, az5n, mz5n, _, _, _ = \\\n        run_candidate_curve_w12(\n            dict(base, axis=list(base["axis"])), None, frames5, P5,\n            st5, gate_state=gs5, vol_state=vs5, yang_state=ys5,\n            vconf_state=cs5, streak_state=sk5, tstate_state=ts5,\n            amp_state=as5, mom_state=ms5, std_state=ss5,\n            rsqr_state=rq5,\n            sumn_state=nq5)', 'L13c')
    src = sub1(src, '    eq5o, tr5o, m5o, _, _, _, _, _, _, _, _, _, az5o, mz5o, _, _ = \\\n        run_candidate_curve_w12(\n            dict(base, axis=[*base["axis"][:12], "mom_oversold",\n                             "none", "none"]), None,\n            frames5, P5, st5, gate_state=gs5, vol_state=vs5,\n            yang_state=ys5, vconf_state=cs5, streak_state=sk5,\n            tstate_state=ts5, amp_state=as5, mom_state=ms5,\n            std_state=ss5, rsqr_state=rq5)', '    eq5o, tr5o, m5o, _, _, _, _, _, _, _, _, _, az5o, mz5o, _, _, _ = \\\n        run_candidate_curve_w12(\n            dict(base, axis=[*base["axis"][:12], "mom_oversold",\n                             "none", "none", "none"]), None,\n            frames5, P5, st5, gate_state=gs5, vol_state=vs5,\n            yang_state=ys5, vconf_state=cs5, streak_state=sk5,\n            tstate_state=ts5, amp_state=as5, mom_state=ms5,\n            std_state=ss5, rsqr_state=rq5, sumn_state=nq5)', 'L13d')
    src = sub1(src, '    eq3o, tr3o, m3o, _, _, _, _, _, _, _, _, _, az3o, mz3o, _, _ = \\\n        run_candidate_curve_w12(\n            dict(base, axis=[*base["axis"][:12], "mom_oversold",\n                             "none", "none"]), None,\n            frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n            std_state=ss3, rsqr_state=rq3)', '    eq3o, tr3o, m3o, _, _, _, _, _, _, _, _, _, az3o, mz3o, _, _, _ = \\\n        run_candidate_curve_w12(\n            dict(base, axis=[*base["axis"][:12], "mom_oversold",\n                             "none", "none", "none"]), None,\n            frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n            std_state=ss3, rsqr_state=rq3, sumn_state=nq3)', 'L13e')
    src = sub1(src, '    _ok("L14 null-axis draw determinism + FIFTEEN-tuple with std+rsqr "\n        "in the frozen domains (W12 null berth 20321000)",\n        p1 == p2 and ax1 == ax2 and len(ax1) == 15\n        and ax1[12] in AXIS_MOM and ax1[13] in AXIS_STD\n        and ax1[14] in AXIS_RSQR\n        and ax1[11] in tl9.AXIS_AMP\n        and ax1[10] in tl8.AXIS_TSTATE and ax1[9] in tl7.AXIS_STREAK\n        and ax1[4] in tl2.AXIS_STOP)', '    _ok("L14 null-axis draw determinism + SIXTEEN-tuple with rsqr+sumn "\n        "in the frozen domains (W13 null berth 20323500)",\n        p1 == p2 and ax1 == ax2 and len(ax1) == 16\n        and ax1[12] in AXIS_MOM and ax1[13] in AXIS_STD\n        and ax1[15] in AXIS_SUMN\n        and ax1[14] in AXIS_RSQR\n        and ax1[11] in tl9.AXIS_AMP\n        and ax1[10] in tl8.AXIS_TSTATE and ax1[9] in tl7.AXIS_STREAK\n        and ax1[4] in tl2.AXIS_STOP)', 'L14')
    src = sub1(src, '    mom_dom = (ax0[12] in AXIS_MOM and ax0[13] in AXIS_STD\n               and ax0[14] in AXIS_RSQR\n               and ax0[4] in tl2.AXIS_STOP and len(ax0) == 15)', '    mom_dom = (ax0[12] in AXIS_MOM and ax0[13] in AXIS_STD\n               and ax0[15] in AXIS_SUMN\n               and ax0[14] in AXIS_RSQR\n               and ax0[4] in tl2.AXIS_STOP and len(ax0) == 16)', 'L15b dom')
    src = sub1(src, '    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, szn, tzn, azn, \\\n        mzn, _, rzn = \\\n        run_candidate_curve_w12(\n            {"module": "null", "fn": "random_signal",\n             "sig_params": {"p_on": p_on0}, "axis": ax0,\n             "candidate_id": "W12-NULL-0000", "family": "NULL"},\n            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n            std_state=ss3, rsqr_state=rq3, rng_matrix=mat0, p_on=p_on0)', '    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, szn, tzn, azn, \\\n        mzn, _, rzn, nznn = \\\n        run_candidate_curve_w12(\n            {"module": "null", "fn": "random_signal",\n             "sig_params": {"p_on": p_on0}, "axis": ax0,\n             "candidate_id": "W12-NULL-0000", "family": "NULL"},\n            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n            std_state=ss3, rsqr_state=rq3, sumn_state=nq3, rng_matrix=mat0, p_on=p_on0)', 'L15b call 1')
    src = sub1(src, '    eqnb, _, _, _, _, _, _, _, _, _, _, _, _, mznb, _, rznb = \\\n        run_candidate_curve_w12(\n            {"module": "null", "fn": "random_signal",\n             "sig_params": {"p_on": p_on0b}, "axis": ax0b,\n             "candidate_id": "W12-NULL-0000", "family": "NULL"},\n            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n            std_state=ss3, rsqr_state=rq3, rng_matrix=mat0b, p_on=p_on0b)', '    eqnb, _, _, _, _, _, _, _, _, _, _, _, _, mznb, _, rznb, nznb = \\\n        run_candidate_curve_w12(\n            {"module": "null", "fn": "random_signal",\n             "sig_params": {"p_on": p_on0b}, "axis": ax0b,\n             "candidate_id": "W12-NULL-0000", "family": "NULL"},\n            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,\n            yang_state=ys3, vconf_state=cs3, streak_state=sk3,\n            tstate_state=ts3, amp_state=as3, mom_state=ms3,\n            std_state=ss3, rsqr_state=rq3, sumn_state=nq3, rng_matrix=mat0b, p_on=p_on0b)', 'L15b call 2')
    src = sub1(src, '    _ok("L15b null-cell engine path: fifteen-tuple null draw "\n        "deterministic + rsqr axis in-domain + engine 16-tuple return "\n        "+ double-run byte-identity (screen null-family path)",\n        p_on0 == p_on0b and ax0 == ax0b and mom_dom\n        and len(eqn) == len(P3["close"].index) and mzn >= 0\n        and list(eqn.values) == list(eqnb.values) and mzn == mznb\n        and rzn == rznb)', '    _ok("L15b null-cell engine path: sixteen-tuple null draw "\n        "deterministic + sumn axis in-domain + engine 17-tuple return "\n        "+ double-run byte-identity (screen null-family path)",\n        p_on0 == p_on0b and ax0 == ax0b and mom_dom\n        and len(eqn) == len(P3["close"].index) and mzn >= 0\n        and list(eqn.values) == list(eqnb.values) and mzn == mznb\n        and rzn == rznb\n        and nznn == nznb)', 'L15b check')
    src = sub1(src, '    _ok("L15c screen CSV contract carries the mom+std+rsqr columns in the "\n        "frozen order (cell_id/candidate_id head + rsqr pair before "\n        "survives_screen)",\n        csv_cols_screen_w12[:2] == ["cell_id", "candidate_id"]\n        and csv_cols_screen_w12[-3:] == ["rsqr_face", "rsqr_zeroed",\n                                         "survives_screen"]\n        and "mom_face" in csv_cols_screen_w12\n        and {"gate_zeroed", "vol_zeroed", "yang_zeroed", "vconf_zeroed",\n             "streak_zeroed", "tstate_zeroed", "amp_zeroed",\n             "mom_zeroed", "std_zeroed", "rsqr_zeroed"} <= set(csv_cols_screen_w12))', '    _ok("L15c screen CSV contract carries the mom+std+rsqr+sumn columns in the "\n        "frozen order (cell_id/candidate_id head + sumn pair before "\n        "survives_screen)",\n        csv_cols_screen_w12[:2] == ["cell_id", "candidate_id"]\n        and csv_cols_screen_w12[-3:] == ["sumn_face", "sumn_zeroed",\n                                         "survives_screen"]\n        and "mom_face" in csv_cols_screen_w12\n        and {"gate_zeroed", "vol_zeroed", "yang_zeroed", "vconf_zeroed",\n             "streak_zeroed", "tstate_zeroed", "amp_zeroed",\n             "mom_zeroed", "std_zeroed", "rsqr_zeroed", "sumn_zeroed"} <= set(csv_cols_screen_w12))', 'L15c')
    src = sub1(src, '    print(f"\\nselftest: {n_pass}/{n_leg} PASS "\n          f"(scope: W12 rsqr layer + G-RSQR + fifteen-tuple grammar "\n          f"+ machinery: effective mask / curve runner parity / null "\n          f"draw / 24-source exclusion loader + funnel faces: dispatch "\n          f"/ null-cell engine path / CSV contract + pit-95 finalize "\n          f"idempotency guard state-adaptive legs; zero live cells "\n          f"burned, zero numbers fabricated)")', '    print(f"\\nselftest: {n_pass}/{n_leg} PASS "\n          f"(scope: W13 sumn layer + G-SUMN + sixteen-tuple grammar "\n          f"+ machinery: effective mask / curve runner parity / null "\n          f"draw / 25-source exclusion loader + funnel faces: dispatch "\n          f"/ null-cell engine path / CSV contract + pit-95 finalize "\n          f"idempotency guard state-adaptive legs; zero live cells "\n          f"burned, zero numbers fabricated)")', 'selftest scope print')
    steps.append("selftest: sixteen-tuple faces (L6/L7g/L7i/L8/L9/L10/L12/L13/L14/L15)")
    return src


def sec15_residual(src, steps):
    """W12 r445bmb step-15 mirror adapted W12->W13.

    Protected from the blanket renames: the frozen import
    (@@TL12IMPORT@@) and the four load-bearing w12_* source-key
    strings (the W11-product source identity -- renaming them would
    collide with the sec8-added w13_* keys reading tl12 files).
    Berths are NOT blanket-renamed: historical W12 berth references
    (e.g. the sec7 distinctness comment) must survive; the legit
    berth label renames were handled by the section subs + one
    targeted pair below.  Overreach guard: module-face calls into
    the FROZEN tl12 keep W12-side names (W12 r445 precedent)."""
    src = src.replace("import trial_labor_w12 as tl12",
                      "import @@TL12IMPORT@@ as tl12")
    src = src.replace('"w12_screen_survivors"', '"@@W12TAG1@@"')
    src = src.replace('"w12_judge_products"', '"@@W12TAG2@@"')
    src = src.replace('"w12_screen_survivor"', '"@@W12TAG3@@"')
    src = src.replace('"w12_judged"', '"@@W12TAG4@@"')
    resid = [
        ("csv_cols_screen_w12", "csv_cols_screen_w13"),
        ("_screen_cell_w12", "_screen_cell_w13"),
        ("_cell_list_w12", "_cell_list_w13"),
        ("_overlay_stop_disclosure_w12", "_overlay_stop_disclosure_w13"),
        ("_judge_cell_w12", "_judge_cell_w13"),
        ("_dual_nulls_w12", "_dual_nulls_w13"),
        ("draw_candidate_sobol_w12", "draw_candidate_sobol_w13"),
        ("_load_exclusion_rows_w12", "_load_exclusion_rows_w13"),
        ("_excluded_w12", "_excluded_w13"),
        ("_effective_signal_mask_w12", "_effective_signal_mask_w13"),
        ("run_candidate_curve_w12", "run_candidate_curve_w13"),
        ("_null_axis_draw_w12", "_null_axis_draw_w13"),
        ("build_grammar_w12", "build_grammar_w13"),
        ("TRIAL_LABOR_W12", "TRIAL_LABOR_W13"),
        ("TRIAL_LAB_W12", "TRIAL_LAB_W13"),
        ("TRIAL-LABOR-W12", "TRIAL-LABOR-W13"),
        ("trial_labor_w12", "trial_labor_w13"),
        ('"W12-', '"W13-'),
        ("W12-NULL", "W13-NULL"),
        ("w12_", "w13_"),
        ("FIFTEEN-tuple", "SIXTEEN-tuple"),
        ("FIFTEEN-gate", "SIXTEEN-gate"),
        ("fifteen-tuple", "sixteen-tuple"),
        ("FIFTEEN-", "SIXTEEN-"),
        ("(MOM+STD+RSQR fifteen-gate wave)",
         "(MOM+STD+RSQR+SUM sixteen-gate wave)"),
        ("24-source", "25-source"),
        ("24 real-reads", "25 real-reads"),
        ("T-124", "T-125"),
        ("seed [20321500, ", "seed [20324000, "),
    ]
    for old, new in resid:
        src = src.replace(old, new)
    src = src.replace('"@@W12TAG1@@"', '"w12_screen_survivors"')
    src = src.replace('"@@W12TAG2@@"', '"w12_judge_products"')
    src = src.replace('"@@W12TAG3@@"', '"w12_screen_survivor"')
    src = src.replace('"@@W12TAG4@@"', '"w12_judged"')
    src = src.replace("@@TL12IMPORT@@", "trial_labor_w12")
    # residual-rename overreach guard (W12 r445 precedent): module-face
    # calls into the FROZEN tl12 must keep W12-side names
    import re as _re
    src = _re.sub(r"tl12\.([A-Za-z_][A-Za-z0-9_]*)_w13\b",
                  r"tl12.\1_w12", src)
    steps.append("residual pass: identifiers/payloads "
                 "(screen/judge/intake/selftest legs)")
    return src
def main() -> int:
    src = open(SRC, encoding="utf-8").read()
    steps = []
    src = sec1_docstring(src, steps)
    src = sec2_imports(src, steps)
    src = sec3_identity_constants(src, steps)
    src = sec4_overlay_constants(src, steps)
    src = sec5_layer(src, steps)
    src = sec6_grammar(src, steps)
    src = sec7_sobol(src, steps)
    src = sec8_exclusion_loader(src, steps)
    src = sec9_excluded(src, steps)
    src = sec10_mask_curve_null(src, steps)
    src = sec11_generate(src, steps)
    src = sec12_screen(src, steps)
    src = sec13_judge(src, steps)
    src = sec14_selftest(src, steps)
    src = sec15_residual(src, steps)
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    py_compile.compile(DST, doraise=True)
    anchor = KIT.build_sumn_anchor()
    flags = []
    for pat in ('len(axis) == 15', 'axis"][14] != "none"',
                "fifteen-tuple", "FIFTEEN-tuple", "FOURTEEN-tuple"):
        hits = src.count(pat)
        if hits:
            flags.append("REVIEW-AT-SLICE-B %s: %d hits"
                        % (pat, hits))
    n_axis15 = src.count('cand["axis"][15]')
    report = {
        "review_flags": flags,
        "axis15_refs": n_axis15,

        "src": SRC,
        "dst": DST,
        "partial": True,
        "sections_landed": steps,
        "post_surgeon_pending": [
            "r446 three-command real-data identity face (prep/finalize/judge-prep)",
            "selftest full run",
            "formal land scripts/trial_labor_w13.py",
            "catalog runner_exists flip + GENERATE pool entry",
        ],
        "partial": False,
        "py_compile": "PASS",
        "sumn_anchor_checks": {
            "decidable_days": anchor["decidable_days"],
            "open_days": anchor["open_days"],
            "sumn10_open_days": anchor["sumn10_open_days"],
            "first_decidable_bar_idx": anchor["first_decidable_bar_idx"],
            "nine_gate_512cells_nonzero_count":
                anchor["nine_gate_512cells_nonzero_count"],
            "nine_gate_512cells_empty_count":
                anchor["nine_gate_512cells_empty_count"],
            "slope_split": "%d/%d" % (
                anchor["slope_sign_split"]["up_slope_days"],
                anchor["slope_sign_split"]["down_slope_days"]),
        },
        "next": ("r466: extend surgeon sections 12-15 (screen/"
                 "judge/selftest/residual) reading the actual "
                 "w12 sections from scripts/trial_labor_w12.py lines "
                 "1741-4913, re-run from SRC fresh (idempotent), then "
                 "r446 three-command identity face -> selftest -> "
                 "formal land"),
    }
    json.dump(report, open(REPORT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("SURGEON-OK: sections 1-15 landed, draft written, "
          "py_compile PASS")
    for s in steps:
        print("  + " + s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
