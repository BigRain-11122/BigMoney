"""Alpha158 comparison export -- O-20260923-1636 outreach queue item (zero-engine digest support).

L1 deterministic layer:
  1. Mechanically parse the VENDORED qlib Alpha158 definition (research/shortline/external/
     qlib_alpha158_loader.py + qlib_alpha158_handler.py) -- operator families, feature names,
     counts -- with invariants (total==158) as the parse gate.
  2. Family-level coverage map vs our four libraries (internal factors + vendored GTJA191 +
     vendored WQ101 + LHB/heat/P-1d survivors). Coverage verdicts are a hand-built auditable
     table (judgment layer, no LLM); gap claims are backed by mechanical keyword scans over
     the vendored external sources.

Outputs results/shortline/alpha158_compare.json. Honest baseline (project law): external-lib
single factors have repeatedly failed the wall (GTJA 0/183 core48, WQ 0/82 strict) -- this is a
COVERAGE MAP, not a survivor forecast. Any future IC batch on gap families needs its own
preregistration + claim (PREREG_TEMPLATE).

Usage: python scripts/alpha158_compare.py run|selftest
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "research/shortline/external/qlib_alpha158_loader.py"
HANDLER = ROOT / "research/shortline/external/qlib_alpha158_handler.py"
GTJA = ROOT / "research/shortline/external/gtja191_alpha191.py"
WQ = ROOT / "research/shortline/external/worldquant101_alpha101.py"
OUT = ROOT / "results/shortline/alpha158_compare.json"

SOURCE_URL = "https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py"
VENDORED_COMMIT = "a7d5a9b500de (file last commit 2024-07-05, fetched 2026-09-24)"

DEFAULT_ROLLING_WINDOWS = [5, 10, 20, 30, 60]
HANDLER_PRICE = {"windows": [0], "feature": ["OPEN", "HIGH", "LOW", "VWAP"]}

# ---------------------------------------------------------------- mechanical parse


def parse_vendored():
    src = LOADER.read_text(encoding="utf-8")
    body = src.split("class Alpha158DL", 1)[1]

    kbar_names = re.findall(r'"(K[A-Z0-9]+)"', body.split('if "price" in config', 1)[0])
    ops = re.findall(r'if use\("([A-Z]+)"\)', body)

    # expression template per operator: first field string of the block
    expr = {}
    for op in ops:
        m = re.search(r'if use\("%s"\):.*?fields \+= (\[.*?\])\n' % op, body, re.S)
        tmpl = "n/a"
        if m:
            try:
                lst = eval(m.group(1))  # literal list of str with %d/%s placeholders
                tmpl = lst[0] if lst else "n/a"
            except Exception:
                tmpl = "n/a"
        expr[op] = tmpl

    hsrc = HANDLER.read_text(encoding="utf-8")
    m = re.search(r'"price":\s*\{[^}]*"feature":\s*\[([^\]]*)\]', hsrc)
    price_feats = re.findall(r'"([A-Z]+)"', m.group(1))
    return kbar_names, ops, expr, price_feats


def build_inventory():
    kbar_names, ops, expr, price_feats = parse_vendored()
    price_names = [f + "0" for f in price_feats]  # windows=[0] per handler config
    rolling = {op: len(DEFAULT_ROLLING_WINDOWS) for op in ops}
    total = len(kbar_names) + len(price_names) + sum(rolling.values())
    gate = {
        "kbar_count": len(kbar_names),
        "price0_count": len(price_names),
        "rolling_ops": len(ops),
        "rolling_feats": sum(rolling.values()),
        "total_features": total,
        "total_is_158": total == 158,
        "names_unique": len(set(kbar_names + price_names + [f"{op}{d}" for op in ops for d in DEFAULT_ROLLING_WINDOWS])) == total,
    }
    assert gate["total_is_158"], f"parse gate FAILED: total={total}"
    assert gate["kbar_count"] == 9 and gate["rolling_ops"] == 29, gate
    return kbar_names, ops, expr, price_names, gate


# ---------------------------------------------------------------- coverage table
# verdict: covered / covered_tested_dead / partial / gap
# refs cite tested evidence (STRATEGY_LIBRARY / research batches). Judgment layer = auditable
# hand-built map; mechanical gap evidence in MECH_CHECKS below.

COVERAGE = {
    "KBAR": dict(v="partial",
        refs="internal intraday_range=KLEN (J6 DNA, strongest single); KUP/KLOW/KSFT covered only as EVENT forms (engulf/needle/hammer G1' candidates); continuous shadow-ratio factor untested",
        cls="C"),
    "PRICE0": dict(v="partial",
        refs="VWAP0=$vwap/$close: GTJA/WQ use vwap extensively (alpha191 wma-vwap family / WQ alpha40-41); internal no direct continuous form; group is ML level-feature oriented",
        cls="C"),
    "ROC": dict(v="covered",
        refs="mom_20/mom_12_1 internal (J6 DNA); tsmom family; GTJA slope trio 021/116/147 tested (weak IS / OOS-strong mom regime)", cls="-"),
    "MA": dict(v="covered",
        refs="432 MA-cross grid (all dead); dual_ma/triple_ma strategies tested (batch 2A negative)", cls="-"),
    "STD": dict(v="covered",
        refs="vol_60 (J6 DNA, stock-pool sign preserved); GTJA std-based factors", cls="-"),
    "BETA": dict(v="covered",
        refs="GTJA REGBETA 021/116/147 re-tested (021 dead-flat, 116/147 pool-only); trend_r2 adjacent", cls="-"),
    "RSQR": dict(v="covered",
        refs="internal trend_r2 (NSP1 new-design 4-grid, ~0.116 = info-overlap with composite, eaten by cost)", cls="-"),
    "RESI": dict(v="partial",
        refs="zoo resid_mom (A-layer) excluded from batches as adjacent to tested trend materials; never IC-tested directly", cls="C"),
    "MAX": dict(v="covered",
        refs="high252_prox (NSP1 G1' pass -> G2 FAIL); 52-week single-sidedness law (George-Hwang strength only on strong side)", cls="-"),
    "MIN": dict(v="covered",
        refs="low252 negative (P4_BATCH1 mirror asymmetry: catching falling knives)", cls="-"),
    "QTLU": dict(v="partial",
        refs="price_position (J6 DNA) = range-position family; quantile form untested", cls="C"),
    "QTLD": dict(v="partial",
        refs="same family, lower side", cls="C"),
    "RANK": dict(v="covered",
        refs="price_position / 52w-rank family (J6 DNA + high252 proximity)", cls="-"),
    "RSV": dict(v="covered_tested_dead",
        refs="KDJ (batch 2A judged negative); oscillator-oversold all-dead law (kdj+cci+williams+rsi four-family)", cls="-"),
    "IMAX": dict(v="gap",
        refs="Aroon time-since-high: ABSENT from GTJA191+WQ101 (mechanical scan), absent internally; zoo has no time-since-extreme family", cls="B"),
    "IMIN": dict(v="gap",
        refs="Aroon time-since-low, same mechanical absence", cls="B"),
    "IMXD": dict(v="gap",
        refs="Aroon max-min index spread (downward-momentum idea), same absence", cls="B"),
    "CORR": dict(v="covered",
        refs="price_volume_trend_20 (P1 observation); 量价背离 family (P4_BATCH1 judged); WQ corr-class", cls="-"),
    "CORD": dict(v="partial",
        refs="return-volume corr variant distinct from level corr; adjacent to tested pv family", cls="C"),
    "CNTP": dict(v="partial",
        refs="streak_up tested deeply negative (-0.976, M0923 cross-domain one-way gate) -- adjacent run-length form; up-day FRACTION untested; low prior", cls="C"),
    "CNTN": dict(v="partial", refs="mirror of CNTP", cls="C"),
    "CNTD": dict(v="partial", refs="derived diff form", cls="C"),
    "SUMP": dict(v="covered_tested_dead",
        refs="RSI-family (SUMP~RSI): rsi_divergence queue-batch negative; kdj negative; oscillator law", cls="-"),
    "SUMN": dict(v="covered_tested_dead", refs="=1-SUMP derived", cls="-"),
    "SUMD": dict(v="covered_tested_dead", refs="=2*SUMP-1 derived", cls="-"),
    "VMA": dict(v="partial",
        refs="换手异动 family (P4_BATCH1 judged); vol_drought uses volume LEVEL (percentile), VMA ratio adjacent", cls="C"),
    "VSTD": dict(v="partial",
        refs="GTJA has std(amount,6) adjacent (volume-level std); volume dispersion as continuous factor untested internally", cls="C"),
    "WVMA": dict(v="gap",
        refs="volume-weighted price-change volatility Std(|ret|*vol)/Mean(...): no volume-x-abs-ret compound in internal set; vendored scan shows GTJA std-lines are close/high std not vol-weighted |ret| -- genuinely new B-class candidate", cls="B"),
    "VSUMP": dict(v="gap",
        refs="up-volume share (volume-RSI): 量堆/放量 tested as EVENT forms only; continuous up-volume share untested", cls="B"),
    "VSUMN": dict(v="gap", refs="=1-VSUMP mirror", cls="B"),
    "VSUMD": dict(v="gap", refs="derived diff form", cls="B"),
}

MECH_CHECKS = {
    "aroon_absent_in_gtja_wq": ("aroon", False),
    "idxmax_absent_in_gtja_wq": ("idxmax", False),
    "vwap_present_in_gtja": ("vwap", True),
}


def mech_scan():
    g = GTJA.read_text(encoding="utf-8", errors="ignore").lower()
    w = WQ.read_text(encoding="utf-8", errors="ignore").lower()
    both = g + w
    out = {}
    for key, (kw, expect) in MECH_CHECKS.items():
        out[key] = {"keyword": kw, "found": kw in both, "expected_found": expect,
                    "pass": (kw in both) == expect}
    # std-x-volume compound scan (line level)
    for name, src in [("gtja", g), ("wq", w)]:
        hits = [ln.strip() for ln in src.split("\n") if "std" in ln and ("volume" in ln or "amount" in ln)]
        out[f"stdxvolume_lines_{name}"] = len(hits)
    return out


def run(write=True):
    kbar_names, ops, expr, price_names, gate = build_inventory()
    fam_rows = []
    fam_rows.append({"family": "KBAR", "features": len(kbar_names), "expr_examples": expr.get("KBAR", kbar_names[0] if kbar_names else ""),
                     "names": kbar_names, **COVERAGE["KBAR"]})
    fam_rows.append({"family": "PRICE0", "features": len(price_names),
                     "expr_examples": "$<field>/$close (windows=[0])", "names": price_names, **COVERAGE["PRICE0"]})
    for op in ops:
        fam_rows.append({"family": op, "features": len(DEFAULT_ROLLING_WINDOWS),
                         "expr_examples": expr.get(op, "n/a"), **COVERAGE.get(op, dict(v="partial", refs="unmapped", cls="?"))})
    verdicts = {}
    for r in fam_rows:
        verdicts.setdefault(r["v"], 0)
        verdicts[r["v"]] += r["features"]
    b_class = [r["family"] for r in fam_rows if r["cls"] == "B"]
    payload = {
        "provenance": {
            "source": SOURCE_URL, "license": "MIT", "vendored_commit": VENDORED_COMMIT,
            "loader_sha256": hashlib.sha256(LOADER.read_bytes()).hexdigest(),
            "handler_sha256": hashlib.sha256(HANDLER.read_bytes()).hexdigest(),
            "handler_price_config": HANDLER_PRICE,
            "handler_excludes_volume_raw": True,
        },
        "composition_gate": gate,
        "rolling_windows": DEFAULT_ROLLING_WINDOWS,
        "families": fam_rows,
        "verdict_tallies_features": verdicts,
        "gap_families_b_class": b_class,
        "mech_scan": mech_scan(),
        "honest_baseline": {
            "law": "external-lib single-factor wall: GTJA 0/183 @core48 (21/181 stock-pool strict), WQ 0/82 strict; strongest single evidence remains proprietary lhb_count_20 |IR|0.84",
            "implication": "coverage map only; gap families are SYNTHESIS-MATERIAL / small-K IC candidates at best, each requiring own preregistration (PREREG_TEMPLATE D6 mechanism section mandatory)",
            "domain_note": "Alpha158 targets CSI500 stock ML; our tradable ETF core48 + B-layer stock pool (long-only tilt failed twice = friction-wall law) -- volume features historically stronger on stocks than ETFs",
        },
        "audit": {"engine_runs": 0, "ledger_trials_added": 0, "evidence_cutoff": "2026-09-23 (data state ref only, zero engine)"},
    }
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({
        "gate": gate, "tallies": verdicts, "b_class_gaps": b_class,
        "mech_pass": all(v["pass"] for k, v in payload["mech_scan"].items() if isinstance(v, dict) and "pass" in v),
    }, ensure_ascii=False, indent=1))
    return payload


def selftest():
    build_inventory()  # gate assertions live here
    assert all(v["pass"] for v in mech_scan().values() if isinstance(v, dict) and "pass" in v)
    print("selftest: parse gate 158/158 OK, mech checks OK")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        selftest()
    else:
        run()
