"""T-18 deep-axis machinery -- infra leg (gates + build), frozen prereg
research/DEEP_AXIS_REVALIDATION.md s2/s6 (r97 freeze, sha256 5cdea03e...).

gates: GA twin/bare overlap parity 48/48 (|dclose| tol 0, spotcheck 3/3
      upgraded to full-population), GB per-member completeness (warmup=252,
      valid rows >=252, close NaN <0.5%, dates strictly monotonic, zero rows
      after evidence_cutoff), GC bars anchor Money02/data/bars ==10444 files,
      GD break-registry re-derive bit-match (t14 build_guard chain),
      GE manifest deterministic freeze (panel_start gate-computed from the
      >=5-valid-member rule -- 手写禁 per prereg), GF adjusted-view hard-gate
      STATE PROBE (record-only here; blocks nulls/reval/pbo runs per
      O-1310 s3; gates/build infra unblocked).
build: growing-membership panel cache -> Money02/data/cache/t18_deep_panel/
      (gitignored, regenerable). Twin sources truncated at evidence_cutoff;
      bare-code files are never touched (anchor-reproduction law).
nulls/reval/pbo: GF + XSTOCK data-dir mutex checked first; blocked = exit 2.
status/selftest.

Exit codes: 0 = pass / no-op, 1 = gate fail / refused, 2 = stage blocked
(GF hard gate, XSTOCK mutex, or machinery pending implementation rounds).
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY = os.path.join(ROOT, "data", "daily")
MANIFEST_PATH = os.path.join(ROOT, "results", "shortline", "t18_deep_manifest.json")
CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "t18_deep_panel")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
REGISTRY_PATH = os.path.join(ROOT, "data", "consolidation", "registry.json")
T19_TICKET_PATH = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-24-19-P1.json")
ORDERS_DIR = os.path.join(ROOT, "fleet", "orders")

# Frozen prereg constants (research/DEEP_AXIS_REVALIDATION.md s2 -- do not tune).
WARMUP_BARS = 252          # covers high252 / mom_12_1 max lookback of all 6 traders
MIN_Z_NAMES = 5            # cross-section validity floor (MIN_Z_NAMES=5 precedent)
EVIDENCE_CUTOFF = "2026-09-22"   # twin-data measured end == registry anchor cutoff
BARS_ANCHOR = 10444        # Money02/data/bars total file count (T-01 chain)
NAN_RATE_MAX = 0.005       # per-member close NaN rate ceiling
VALID_ROWS_MIN = 252      # effective rows after warmup floor
PREREG_SHA = "5cdea03e48933d219aea7d666d8cc808b84c70d4b66fe062cee7dd35bbab309d"


def _twin_prefix(code: str) -> str:
    return "sz" if code.startswith(("0", "1", "3")) else "sh"


def _twin_path(code: str) -> str:
    return os.path.join(DAILY, _twin_prefix(code) + code + ".csv")


def _read_daily(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df.rename(columns={c: c.strip() for c in df.columns})


def _universe() -> list[str]:
    """core48 caliber: bare 6-digit CSVs with >=60 rows (live.paper listing floor)."""
    out = []
    for f in sorted(os.listdir(DAILY)):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        n = sum(1 for _ in open(os.path.join(DAILY, f), encoding="utf-8")) - 1
        if n >= 60:
            out.append(f[:-4])
    return out


def _gate_ga(codes: list[str]) -> tuple[bool, dict]:
    rows, worst = [], 0.0
    for code in codes:
        bare = _read_daily(os.path.join(DAILY, code + ".csv")).set_index("date")["close"]
        twin = _read_daily(_twin_path(code)).set_index("date")["close"]
        common = bare.index.intersection(twin.index)
        if len(common) == 0:
            rows.append({"code": code, "common_rows": 0, "max_abs_close_diff": None, "pass": False})
            continue
        diff = float((bare.loc[common] - twin.loc[common]).abs().max())
        worst = max(worst, diff)
        rows.append({"code": code, "common_rows": int(len(common)),
                     "max_abs_close_diff": diff, "pass": diff == 0.0})
    ok = bool(rows) and all(r["pass"] for r in rows)
    return ok, {"pass": ok, "n_checked": len(rows), "tolerance": 0.0,
                "max_abs_close_diff_worst": worst, "per_member": rows}


def _gate_gb(codes: list[str]) -> tuple[bool, dict]:
    members, ok = {}, True
    for code in codes:
        twin = _read_daily(_twin_path(code))
        dates = twin["date"].astype(str).tolist()
        rows = len(twin)
        mono = all(dates[i] < dates[i + 1] for i in range(len(dates) - 1))
        nan_rate = float(twin["close"].isna().mean())
        after_cut = sum(1 for d in dates if d > EVIDENCE_CUTOFF)
        valid_from = dates[WARMUP_BARS] if rows > WARMUP_BARS else None
        valid_rows = rows - WARMUP_BARS if rows > WARMUP_BARS else 0
        member_ok = (mono and nan_rate < NAN_RATE_MAX and after_cut == 0
                     and valid_rows >= VALID_ROWS_MIN)
        ok = ok and member_ok
        members[code] = {
            "twin_start": dates[0], "twin_end": dates[-1], "rows": rows,
            "valid_from": valid_from, "valid_rows": valid_rows,
            "nan_rate": nan_rate, "dates_mono": mono,
            "rows_after_cutoff": after_cut, "pass": member_ok,
        }
    return ok, {"pass": ok, "members": members}


def _gate_gc() -> tuple[bool, dict]:
    if not os.path.isdir(BARS_DIR):
        return False, {"pass": False, "bars_files": None, "error": "bars dir absent"}
    files = [f for f in os.listdir(BARS_DIR) if os.path.isfile(os.path.join(BARS_DIR, f))]
    n_pq = sum(1 for f in files if f.endswith(".parquet"))
    info = {"pass": len(files) == BARS_ANCHOR, "bars_files": len(files),
            "parquet_files": n_pq, "anchor": BARS_ANCHOR}
    return info["pass"], info


def _gd_compare(registry_path: str, derived_canon: list) -> dict:
    """Pure comparison leg of GD (registry file vs re-derived canon)."""
    reg = json.load(open(registry_path, encoding="utf-8-sig"))
    events = reg.get("events", [])
    # registry face stores the detector 4dp value (pct_detector_4dp); the
    # t14-derived face uses "pct" -- both canon to pct@4dp (t19 build law)
    reg_canon = sorted((e["sym"], e["date"],
                        round(float(e.get("pct", e.get("pct_detector_4dp"))), 4))
                       for e in events)
    n_pre = sum(1 for _, d, _ in reg_canon if d[:4] < "2020")
    return {
        "registry_events": len(events),
        "derived_events": len(derived_canon),
        "bit_match": reg_canon == list(derived_canon),
        "n_pre_2020": n_pre,
        "first_event": min((d for _, d, _ in reg_canon), default=None),
        "last_event": max((d for _, d, _ in reg_canon), default=None),
    }


def _gate_gd() -> tuple[bool, dict]:
    _repo = ROOT
    if _repo not in sys.path:
        sys.path.insert(0, _repo)
    import live.paper as LP
    from scripts.t14_rules_fidelity import build_guard
    from scripts.t19_consolidation_registry import _canon

    prices = LP.load_core()
    _, diag = build_guard(prices)
    tot = diag["totals"]
    derived = _canon(diag["break_days"])
    cmp_ = _gd_compare(REGISTRY_PATH, derived)
    ok = (cmp_["bit_match"] and tot["break_days"] == 21
          and tot["break_days_distinct_syms"] == 19 and cmp_["n_pre_2020"] == 0)
    info = {"pass": ok, "detector": "t14 build_guard re-derive -> _canon bit-match",
            "totals": {"break_days": tot["break_days"],
                       "break_days_distinct_syms": tot["break_days_distinct_syms"]},
            **cmp_}
    return ok, info


def _panel_start(members: dict) -> str | None:
    """First trading day with >= MIN_Z_NAMES warmup-valid members (gate-computed)."""
    starts = sorted(m["valid_from"] for m in members.values() if m["valid_from"])
    for d in starts:
        n = sum(1 for m in members.values() if m["valid_from"] and m["valid_from"] <= d)
        if n >= MIN_Z_NAMES:
            return d
    return None


def _gf_state() -> dict:
    """O-1310 s3 literal: T-19 adjusted view delivered (files on disk + ticket
    note delivery marker) OR GM waiver in an O-file -- else nulls/reval/pbo exit 2."""
    basis: dict = {}
    adj_files = sorted(glob.glob(os.path.join(ROOT, "data", "consolidation", "adjust*")))
    basis["adjusted_files_on_disk"] = [os.path.basename(f) for f in adj_files]
    note = ""
    try:
        note = json.load(open(T19_TICKET_PATH, encoding="utf-8-sig")).get("note", "")
    except Exception as e:  # honest: unreadable ticket recorded, not fatal for probe
        basis["t19_note_error"] = str(e)[:120]
    low = note.lower()
    basis["t19_note_stage3_delivered_marker"] = (
        "stage-3 delivered" in low or "stage-3 adjusted panel delivered" in low)
    waiver_lines = []
    for f in sorted(glob.glob(os.path.join(ORDERS_DIR, "O-*.md"))):
        try:
            txt = open(f, encoding="utf-8-sig").read()
        except Exception:
            continue
        for ln in txt.splitlines():
            l = ln.lower()
            if ("豁免" in ln or "waiver" in l) and any(
                    k in l for k in ("t-18", "t18", "deep axis", "deep-axis",
                                     "deep_axis", "deep reval", "deep_reval")):
                waiver_lines.append(os.path.basename(f) + ": " + ln.strip()[:160])
    basis["gm_waiver_lines"] = waiver_lines
    delivered = bool(adj_files) and basis["t19_note_stage3_delivered_marker"]
    waiver = bool(waiver_lines)
    return {
        "satisfied": delivered or waiver,
        "delivered": delivered,
        "gm_waiver": waiver,
        "basis": basis,
        "contract": "nulls/reval/pbo stages exit 2 until satisfied (O-1310 s3); "
                    "gates/build infra unblocked",
    }


def _xstock_mutex() -> tuple[bool, str]:
    """s0 compute-budget law: heavy stages must not ignite while the XSTOCK
    build/post chain holds the shared data dirs (Money02 cache contention)."""
    try:
        import psutil
    except ImportError:
        return True, "psutil unavailable (fail-safe block)"
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            cl = " ".join(p.info.get("cmdline") or [])
        except Exception:
            continue
        if "xstock_synth.py" in cl and " run" in cl:
            return True, f"xstock_synth run in flight (PID {p.info['pid']})"
    return False, ""


def _compute_gates() -> tuple[bool, dict]:
    codes = _universe()
    ga_ok, ga = _gate_ga(codes)
    gb_ok, gb = _gate_gb(codes)
    gc_ok, gc = _gate_gc()
    gd_ok, gd = _gate_gd()
    panel_start = _panel_start(gb["members"])
    gf = _gf_state()
    payload = {
        "batch": "t18_deep_reval",
        "stage": "gates",
        "prereg": f"research/DEEP_AXIS_REVALIDATION.md (frozen sha256 {PREREG_SHA})",
        "universe_n": len(codes),
        "warmup_bars": WARMUP_BARS,
        "min_z_names": MIN_Z_NAMES,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "panel_start": panel_start,
        "members": gb["members"],
        "gates": {"GA": ga, "GB": {"pass": gb_ok}, "GC": gc, "GD": gd, "GF": gf},
        "verdict": "PASS" if (ga_ok and gb_ok and gc_ok and gd_ok
                              and panel_start and len(codes) == 48) else "FAIL",
    }
    ok = payload["verdict"] == "PASS"
    # GE determinism: recompute the whole payload and demand byte-equality.
    ga2_ok, ga2 = _gate_ga(codes)
    gb2_ok, gb2 = _gate_gb(codes)
    gc2_ok, gc2 = _gate_gc()
    ps2 = _panel_start(gb2["members"])
    payload2 = dict(payload)
    payload2["gates"] = {"GA": ga2, "GB": {"pass": gb2_ok}, "GC": gc2,
                         "GD": gd, "GF": _gf_state()}
    payload2["members"] = gb2["members"]
    payload2["panel_start"] = ps2
    same = json.dumps(payload, sort_keys=True) == json.dumps(payload2, sort_keys=True)
    payload["ge_determinism_double_run"] = same
    if not same:
        payload["verdict"] = "FAIL"
        ok = False
    return ok, payload


def cmd_gates() -> int:
    ok, payload = _compute_gates()
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: payload[k] for k in
                      ("universe_n", "panel_start", "evidence_cutoff", "verdict",
                       "ge_determinism_double_run")}, ensure_ascii=False))
    for g in ("GA", "GB", "GC", "GD", "GF"):
        info = payload["gates"][g]
        print(f"[gate {g}] pass={info.get('pass', info.get('satisfied'))}")
    print("manifest written:", MANIFEST_PATH)
    return 0 if ok else 1


def _manifest_sha() -> str:
    return hashlib.sha256(open(MANIFEST_PATH, "rb").read()).hexdigest()


def cmd_build() -> int:
    if not os.path.exists(MANIFEST_PATH):
        print("[build] manifest absent -- running gates first")
        rc = cmd_gates()
        if rc != 0:
            return rc
    man = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    if man.get("verdict") != "PASS":
        print("[build] manifest verdict != PASS; rebuild refused")
        return 1
    msha = _manifest_sha()
    meta_path = os.path.join(CACHE_DIR, "meta.json")
    ohlcv_dir = os.path.join(CACHE_DIR, "ohlcv")
    if os.path.exists(meta_path):
        try:
            meta = json.load(open(meta_path, encoding="utf-8-sig"))
            done = (meta.get("manifest_sha256") == msha
                    and all(os.path.exists(os.path.join(ohlcv_dir, c + ".parquet"))
                            for c in man["members"]))
            if done:
                print(f"[build] no-op: cache fresh for manifest {msha[:12]} "
                      f"({len(man['members'])} members)")
                return 0
        except Exception as e:
            print("[build] stale meta read:", str(e)[:120])
    os.makedirs(ohlcv_dir, exist_ok=True)
    n_rows = 0
    for code, m in sorted(man["members"].items()):
        df = _read_daily(_twin_path(code))
        df = df.set_index("date").sort_index()
        df = df.loc[df.index <= EVIDENCE_CUTOFF]  # cutoff 后新 bar 锁定不回流
        df[["open", "high", "low", "close", "volume"]].to_parquet(
            os.path.join(ohlcv_dir, code + ".parquet"))
        n_rows += len(df)
    meta = {
        "manifest_sha256": msha,
        "warmup_bars": WARMUP_BARS,
        "min_z_names": MIN_Z_NAMES,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "members": len(man["members"]),
        "rows_total": n_rows,
        "panel_start": man["panel_start"],
        "source": "twin files (bare-code files untouched; anchor-reproduction law)",
    }
    with open(meta_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    print(f"[build] panel cache written: {ohlcv_dir} ({len(man['members'])} members, "
          f"{n_rows} rows, panel_start {man['panel_start']})")
    return 0


def _blocked_stage(name: str) -> int:
    gf = _gf_state()
    if not gf["satisfied"]:
        print(f"[{name}] BLOCKED by GF adjusted-view hard gate (O-1310 s3): "
              "T-19 stage-3 not delivered and no GM waiver on file")
        print(f"[{name}] gf basis: files={gf['basis']['adjusted_files_on_disk']} "
              f"note_marker={gf['basis']['t19_note_stage3_delivered_marker']} "
              f"waiver_lines={gf['basis']['gm_waiver_lines']}")
        return 2
    busy, why = _xstock_mutex()
    if busy:
        print(f"[{name}] BLOCKED by XSTOCK data-dir mutex (s0): {why}")
        return 2
    print(f"[{name}] GF satisfied and mutex clear, but stage machinery is pending "
          "implementation rounds (r101 delivered gates/build only); refusing to fake a run")
    return 2


def cmd_status() -> int:
    if os.path.exists(MANIFEST_PATH):
        man = json.load(open(MANIFEST_PATH, encoding="utf-8"))
        print(json.dumps({k: man.get(k) for k in
                          ("verdict", "universe_n", "panel_start", "evidence_cutoff",
                           "ge_determinism_double_run")}, ensure_ascii=False))
    else:
        print("manifest absent (run: python scripts/t18_deep_axis.py gates)")
    gf = _gf_state()
    print("GF:", json.dumps({"satisfied": gf["satisfied"], "delivered": gf["delivered"],
                             "gm_waiver": gf["gm_waiver"]}, ensure_ascii=False))
    meta_path = os.path.join(CACHE_DIR, "meta.json")
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path, encoding="utf-8-sig"))
        fresh = meta.get("manifest_sha256") == (_manifest_sha()
                                                if os.path.exists(MANIFEST_PATH) else None)
        print("cache:", json.dumps({**meta, "fresh_for_manifest": fresh},
                                   ensure_ascii=False))
    else:
        print("cache: absent")
    return 0


def _selftest() -> int:
    import tempfile
    tmp = tempfile.mkdtemp(prefix="t18gates_")
    fake = os.path.join(tmp, "daily")
    os.makedirs(fake)
    # 7 synthetic members, staggered twin starts, constant close=1.0
    starts = ["2010-01-0" + str(i + 1) for i in range(7)]
    for i, s in enumerate(starts):
        code = f"51000{i}"
        idx = pd.bdate_range(s, "2020-01-01")
        pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "open": 1.0, "high": 1.0,
                      "low": 1.0, "close": 1.0, "volume": 1.0,
                      }).to_csv(os.path.join(fake, code + ".csv"), index=False)
        pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "open": 1.0, "high": 1.0,
                      "low": 1.0, "close": 1.0, "volume": 1.0,
                      }).to_csv(os.path.join(fake, "sh" + code + ".csv"), index=False)
    import t18_deep_axis as mod
    mod.DAILY = fake

    def chk(name, cond):
        assert cond, f"selftest FAIL: {name}"
        print(f"  [ok] {name}")

    codes = [f"51000{i}" for i in range(7)]
    ga_ok, ga = mod._gate_ga(codes)
    chk("GA parity all-zero on synthetic", ga_ok and ga["n_checked"] == 7
        and ga["max_abs_close_diff_worst"] == 0.0)
    # GA violation case: corrupt one twin close
    bad = pd.read_csv(os.path.join(fake, "sh510000.csv"))
    bad.loc[3, "close"] = 9.9
    bad.to_csv(os.path.join(fake, "sh510000.csv"), index=False)
    ga2_ok, ga2 = mod._gate_ga(codes)
    chk("GA catches corrupted twin", not ga2_ok
        and ga2["per_member"][0]["pass"] is False)
    pd.read_csv(os.path.join(fake, "sh510000.csv")).assign(
        close=1.0).to_csv(os.path.join(fake, "sh510000.csv"), index=False)

    gb_ok, gb = mod._gate_gb(codes)
    chk("GB pass on synthetic long twins", gb_ok
        and all(m["valid_rows"] >= mod.VALID_ROWS_MIN for m in gb["members"].values()))
    m0 = gb["members"]["510000"]
    chk("GB valid_from = twin_start + 252 bars",
        m0["valid_from"] == pd.bdate_range(starts[0], periods=253)[-1].strftime("%Y-%m-%d"))
    # GB violation: rows-after-cutoff on one twin
    bad = pd.read_csv(os.path.join(fake, "sh510001.csv"))
    bad.loc[len(bad)] = ["2026-09-23", 1.0, 1.0, 1.0, 1.0, 1.0]
    bad.to_csv(os.path.join(fake, "sh510001.csv"), index=False)
    gb2_ok, gb2 = mod._gate_gb(codes)
    chk("GB catches rows after evidence_cutoff", not gb2_ok
        and gb2["members"]["510001"]["rows_after_cutoff"] == 1)
    # restore the corrupted twin so later recomputes stay deterministic
    idx = pd.bdate_range(starts[1], "2020-01-01")
    pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "open": 1.0, "high": 1.0,
                  "low": 1.0, "close": 1.0, "volume": 1.0,
                  }).to_csv(os.path.join(fake, "sh510001.csv"), index=False)

    ps = mod._panel_start(gb["members"])
    # staggered starts -> the 5th member's valid_from is the first day the
    # >=5-member cross-section exists (members 0..4 by start order)
    chk("panel_start = first day with >=5 valid members",
        ps == gb["members"]["510004"]["valid_from"])
    # thin-universe case: only 3 valid -> None
    thin = {k: gb["members"][k] for k in list(gb["members"])[:3]}
    chk("panel_start None when <5 members ever valid", mod._panel_start(thin) is None)

    reg = os.path.join(tmp, "registry.json")
    json.dump({"events": [{"sym": "159901", "date": "2021-04-12", "pct": -0.5103},
                          {"sym": "512100", "date": "2022-05-20", "pct": 1.7627}]},
              open(reg, "w"))
    cmp_ = mod._gd_compare(reg, sorted([("159901", "2021-04-12", -0.5103),
                                        ("512100", "2022-05-20", 1.7627)]))
    chk("GD compare bit-match true", cmp_["bit_match"] and cmp_["n_pre_2020"] == 0)
    cmp2 = mod._gd_compare(reg, [("159901", "2021-04-12", -0.5103)])
    chk("GD compare catches drift", not cmp2["bit_match"])

    # GF probe on synthetic ticket/orders
    mod.T19_TICKET_PATH = os.path.join(tmp, "t19.json")
    json.dump({"note": "stage-1 delivered; Remaining: ... stage-3 adjusted panel"},
              open(mod.T19_TICKET_PATH, "w"))
    mod.ORDERS_DIR = os.path.join(tmp, "orders")
    os.makedirs(mod.ORDERS_DIR)
    gf = mod._gf_state()
    chk("GF unsatisfied when neither files nor marker", gf["satisfied"] is False)
    open(os.path.join(mod.ORDERS_DIR, "O-x.md"), "w", encoding="utf-8").write(
        "GM waiver: T-18 deep reval adjusted-view 豁免 effective now")
    gf2 = mod._gf_state()
    chk("GF satisfied via GM waiver line", gf2["satisfied"] and gf2["gm_waiver"])
    json.dump({"note": "... stage-3 adjusted panel delivered by bm-c ..."},
              open(mod.T19_TICKET_PATH, "w"))
    open(os.path.join(mod.ORDERS_DIR, "O-x.md"), "w", encoding="utf-8").write("no waiver")
    gf3 = mod._gf_state()
    chk("GF delivered requires files too (files empty -> false)",
        gf3["satisfied"] is False and gf3["delivered"] is False)

    # determinism on synthetic members payload
    p1 = json.dumps({"m": gb["members"], "ps": ps}, sort_keys=True)
    p2 = json.dumps({"m": mod._gate_gb(codes)[1]["members"],
                     "ps": mod._panel_start(mod._gate_gb(codes)[1]["members"])},
                    sort_keys=True)
    chk("GE payload deterministic across recomputes", p1 == p2)

    print("selftest: all PASS")
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "status"
    if cmd == "gates":
        return cmd_gates()
    if cmd == "build":
        return cmd_build()
    if cmd in ("nulls", "reval", "pbo"):
        return _blocked_stage(cmd)
    if cmd == "status":
        return cmd_status()
    if cmd == "selftest":
        return _selftest()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
