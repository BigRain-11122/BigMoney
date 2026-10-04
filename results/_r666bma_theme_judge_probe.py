"""r666 bm-a S3 slice: THEME-JUDGE-P1 pre-freeze probe (deterministic, zero-network).

Facts face for the theme wave-ride judgment prereg (next candidate exam batch
per TRIAL_LABOR_LAW standing-supply + O-1819 queue-never-empty). Measures:
v0.3 algorithmic episode set x data/daily panel coverage x nulls/cost
machinery support x ride-censoring structure. Output facts JSON feeds the
prereg drafting window (r647 roster-probe / r659 CFO-gap-probe lineage).

Zero network, zero engine touch, marks+0, ledger+0. Rerun byte-identical.
"""
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
SCRIPTS = os.path.join(BASE, "scripts")
V03 = os.path.join(BASE, "results", "theme_ring", "theme_events_v03_algorithmic.json")
FACE_PROBE = os.path.join(BASE, "results", "theme_ring", "theme_ignition_face_probe.json")
DAILY = os.path.join(BASE, "data", "daily")
OUT = os.path.join(BASE, "results", "_r666bma_theme_judge_probe_facts.json")

COST_X1_EXPECT = 0.0013041
SEED_BAND_EXPECT = 20_580_000


def sha16_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def code_to_file(code: str) -> str:
    """Episode code -> data/daily filename. v0.3 codes are MIXED format:
    bare 6-digit (rest-of-panel) and sh/sz-prefixed (famous16 proxies) --
    normalize: strip prefix if present, then map 1->sz, 5->sh."""
    c = code[2:] if code[:2] in ("sh", "sz") else code
    if c.startswith("1"):
        return f"sz{c}.csv"
    if c.startswith("5"):
        return f"sh{c}.csv"
    return f"UNKNOWN-{code}.csv"


def episode_census(eps) -> dict:
    n = len(eps)
    famous = [e for e in eps if e.get("famous16_proxy")]
    codes = {}
    for e in eps:
        codes[e["code"]] = codes.get(e["code"], 0) + 1
    mult = sorted(codes.values())
    ign_dates = sorted(e["ignition_date"] for e in eps if e.get("ignition_date"))
    has_exit = sum(1 for e in eps if e.get("days_to_minus20") is not None)
    rets = [e.get("ret_ign_to_peak") for e in eps if e.get("ret_ign_to_peak") is not None]
    rets = sorted(float(r) for r in rets)
    dur = [e.get("dur_to_peak_td") for e in eps if e.get("dur_to_peak_td") is not None]
    return {
        "n_episodes": n,
        "n_famous16": len(famous),
        "n_rest": n - len(famous),
        "n_unique_codes": len(codes),
        "episodes_per_code_median": float(mult[len(mult) // 2]) if mult else None,
        "episodes_per_code_max": int(mult[-1]) if mult else None,
        "ignition_date_min": ign_dates[0] if ign_dates else None,
        "ignition_date_max": ign_dates[-1] if ign_dates else None,
        "n_with_minus20_exit": has_exit,
        "n_censored_no_exit": n - has_exit,
        "ret_ign_to_peak_p50": float(rets[len(rets) // 2]) if rets else None,
        "ret_ign_to_peak_p90": float(rets[int(len(rets) * 0.9)]) if rets else None,
        "dur_to_peak_td_median": float(np.median(dur)) if dur else None,
    }


def panel_support(eps) -> dict:
    files = set(os.listdir(DAILY))
    need = {}
    for e in eps:
        c = e["code"]
        if c not in need:
            need[c] = code_to_file(c)
    present = {c: fn in files for c, fn in need.items()}
    missing = sorted(c for c, ok in present.items() if not ok)
    unknown_prefix = sorted(c for c, fn in need.items() if fn.startswith("UNKNOWN-"))
    # tail-date sample on up to 5 present famous codes (bars freshness face)
    tails = {}
    sample = [c for c, ok in present.items() if ok][:5]
    for c in sample:
        df = pd.read_csv(os.path.join(DAILY, need[c]), usecols=[0])
        tails[c] = str(df.iloc[-1, 0])
    return {
        "n_daily_files": len(files),
        "n_episode_codes": len(need),
        "n_codes_missing_panel": len(missing),
        "missing_sample": missing[:10],
        "n_unknown_prefix": len(unknown_prefix),
        "tail_date_sample": tails,
    }


def main() -> int:
    sys.path.insert(0, BASE)        # repo root: knowledge/ single-source imports
    sys.path.insert(0, SCRIPTS)
    import science_gates  # noqa: F401  SEED_REGISTRY single source
    import theme_persist_p1 as tpp

    from rev_osc_stock_p1 import COST_X1

    with open(V03, "rb") as f:
        v03_raw = f.read()
    v03 = json.loads(v03_raw.decode("utf-8"))
    eps = v03["episodes"]

    facts = {
        "probe": "r666 bm-a THEME-JUDGE-P1 pre-freeze probe",
        "v03_sha16": sha16_file(V03),
        "v03_kind": v03["kind"],
        "v03_evidence_cutoff": v03["evidence_cutoff"],
        "v03_constants": v03["constants"],
        "v03_summary_by_bucket": v03["summary_by_bucket"],
        "episode_census": episode_census(eps),
        "panel_support": panel_support(eps),
        "machinery": {
            "cost_x1": float(COST_X1),
            "cost_x1_expect": COST_X1_EXPECT,
            "cost_x1_match": abs(float(COST_X1) - COST_X1_EXPECT) < 1e-9,
            "seed_registry_theme_persist_p1_nulls": science_gates.SEED_REGISTRY.get("theme_persist_p1_nulls"),
            "seed_band_expect": SEED_BAND_EXPECT,
            "seed_band_match": science_gates.SEED_REGISTRY.get("theme_persist_p1_nulls") == SEED_BAND_EXPECT,
            "persist_K_NULLS": tpp.K_NULLS,
            "persist_MINUS20_LINE": tpp.MINUS20_LINE,
            "persist_simulate_callable": callable(getattr(tpp, "simulate", None)),
            "persist_rng_substream": f"rng([{tpp.SEED_NULLS}, k])",
        },
        "r665_face_probe": {
            "exists": os.path.exists(FACE_PROBE),
            "sha16": sha16_file(FACE_PROBE) if os.path.exists(FACE_PROBE) else None,
        },
        "audit": {
            "network": False,
            "engine_touched": False,
            "marks_ledger_delta": 0,
            "deterministic": True,
        },
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({k: facts[k] for k in
                      ("v03_sha16", "episode_census", "panel_support", "machinery")},
                     ensure_ascii=False, indent=1, sort_keys=True))
    print(f"FACTS -> {OUT}")
    return 0


def selftest() -> int:
    legs = []
    # leg 1: code_to_file mapping (bare + prefixed normalization + unknown)
    legs.append(code_to_file("159901") == "sz159901.csv"
                and code_to_file("510300") == "sh510300.csv"
                and code_to_file("sz159915") == "sz159915.csv"
                and code_to_file("sh510500") == "sh510500.csv"
                and code_to_file("830001").startswith("UNKNOWN-"))
    # leg 2: episode census on synthetic set (bucket split + multiplicity + censoring)
    syn = [
        {"code": "159901", "famous16_proxy": True, "ignition_date": "2024-01-02",
         "days_to_minus20": 69, "ret_ign_to_peak": 0.46, "dur_to_peak_td": 100},
        {"code": "159901", "famous16_proxy": True, "ignition_date": "2025-01-02",
         "days_to_minus20": None, "ret_ign_to_peak": 0.20, "dur_to_peak_td": 50},
        {"code": "510500", "famous16_proxy": False, "ignition_date": "2023-01-02",
         "days_to_minus20": 10, "ret_ign_to_peak": 0.30, "dur_to_peak_td": 30},
    ]
    cen = episode_census(syn)
    legs.append(cen["n_episodes"] == 3 and cen["n_famous16"] == 2 and cen["n_rest"] == 1
                and cen["n_unique_codes"] == 2 and cen["episodes_per_code_max"] == 2
                and cen["n_with_minus20_exit"] == 2 and cen["n_censored_no_exit"] == 1
                and cen["ignition_date_min"] == "2023-01-02"
                and cen["ignition_date_max"] == "2025-01-02")
    # leg 3: sha16 stability on temp file
    tmp = os.path.join(HERE, "_r666bma_selftest_tmp.bin")
    with open(tmp, "wb") as f:
        f.write(b"probe-stability")
    legs.append(sha16_file(tmp) == hashlib.sha256(b"probe-stability").hexdigest()[:16])
    os.remove(tmp)
    # leg 4: sorted median/p90 face on even-length rets list
    r = episode_census([{"code": "1", "ret_ign_to_peak": 0.1},
                         {"code": "2", "ret_ign_to_peak": 0.2},
                         {"code": "3", "ret_ign_to_peak": 0.3},
                         {"code": "4", "ret_ign_to_peak": 0.4}])
    legs.append(r["ret_ign_to_peak_p50"] == 0.3 and r["ret_ign_to_peak_p90"] == 0.4)
    ok = all(legs)
    for i, lv in enumerate(legs, 1):
        print(f"selftest leg {i}: {'PASS' if lv else 'FAIL'}")
    print(f"selftest: {sum(legs)}/{len(legs)} {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    rc = selftest() if (len(sys.argv) > 1 and sys.argv[1] == "selftest") else main()
    sys.exit(rc)
