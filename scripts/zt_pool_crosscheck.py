"""ZT-pool four-panel cross validator (T-20261010 tech-queue T10;
O-20261001-2103 R2 data face consumer; O-20261009-1246 self-drive P2).

Read-only L1 deterministic consistency face over the four zt_pool panels
(zt/zbgc/dtgc/strong): zero network, zero engine, zero mutation, ledger N
untouched. Single-source law: endpoint registry, panel paths, day ledger,
FIRST_DATE and the trading calendar all come from the collector module
(update_zt_pool) by import -- this validator re-declares NOTHING.

Check families (HARD findings = exit 3, honest report, never a repair):
  A. panel structural: invariant columns present; (日期,代码) unique;
     日期 strictly ascending (append-only discipline); no empty/NaN 代码
     shells (R58 landed-side verification).
  B. ledger<->panel alignment: every panel date is ledgered (unledgered
     rows = HARD); ledger days absent from the panel are legitimate
     zero-row days (账记不落行) -- not findings.
  C. cross-panel close-state disjointness per date: zt∩dtgc and
     zt∩zbgc must be empty (a close cannot be limit-up AND limit-down,
     nor limit-up AND failed-board). strong∩dtgc = SOFT warn (strong is
     a strength-score face, not a close-state face).
  D. band sanity (SOFT warns, spec-evolution signal, never exit-driving):
     zt 涨跌幅 >= +4.9; dtgc 涨跌幅 <= -4.9; zt 连板数 >= 1 integral.
  E. ledger cross-endpoint alignment: the four endpoints are collected in
     one pass -- divergent day sets = partial-pass residue (HARD).
  F. calendar completeness: every bar-landed trading day inside
     [FIRST_DATE, max ledger day] must appear in each endpoint's ledger
     (HARD). Days beyond the max ledger day are pending collection, not
     findings (bm-a lane catches up; R31 no lane guard here: read-only
     validation is legal on any machine, pool_dualrun precedent).

Exit codes: 0 = clean (no HARD findings); 3 = HARD findings present
(zero mutation, honest report); 2 = mechanism fault (panel/ledger
unreadable). Never masked, never re-mapped. Selftest = offline synthetic
fixtures in a temp sandbox, zero network.
"""
import json
import os
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from update_zt_pool import (  # noqa: E402 -- single-source import
    ENDPOINTS, PANEL_DIR, LEDGER, FIRST_DATE, _load_trading_dates,
)

EVIDENCE = os.path.join(ROOT, "results", "zt_pool_crosscheck.json")
SOFT_BAND = 4.9          # ST 5% boards sit just beyond; tolerance for
                         # round-board artifacts, spec-evolution signal


def _atomic_json_write(obj, path):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def _panel_path(key):
    return os.path.join(PANEL_DIR, f"{key}.parquet")


def _codes_for_day(df, day):
    if "日期" not in df.columns or "代码" not in df.columns:
        return set()
    sl = df[df["日期"] == day]
    return set(sl["代码"].astype(str))


def run_checks(panels, ledger, calendar):
    """Pure function over (panels: {key: DataFrame}, ledger: {key: [days]},
    calendar: [trading days]) -> (findings, soft_warns). No I/O."""
    findings, soft = [], []
    days_all = sorted({d for v in ledger.values() for d in v})

    # ---- A. panel structural (per endpoint)
    for key, df in panels.items():
        inv = ENDPOINTS[key][1]
        for col in inv:
            if col not in df.columns:
                findings.append({"check": "A/invariant_col", "endpoint": key,
                                 "detail": f"missing invariant column {col}"})
        if "代码" in df.columns and len(df):
            shells = df["代码"].isna() | (df["代码"].astype(str)
                                          .str.strip() == "")
            if int(shells.sum()):
                findings.append({"check": "A/row_shell", "endpoint": key,
                                "detail": f"{int(shells.sum())} empty/NaN "
                                          "代码 rows landed (R58)"})
        if all(c in df.columns for c in ("日期", "代码")) and len(df):
            dup = df.duplicated(subset=["日期", "代码"]).sum()
            if int(dup):
                findings.append({"check": "A/dedupe_key", "endpoint": key,
                                 "detail": f"{int(dup)} duplicate "
                                          "(日期,代码) rows"})
            dates = list(df["日期"])
            if dates != sorted(dates):
                findings.append({"check": "A/date_order", "endpoint": key,
                                 "detail": "日期 not ascending "
                                           "(append-only discipline)"})

    # ---- B. ledger<->panel alignment (panel dates must be ledgered)
    for key, df in panels.items():
        if "日期" not in df.columns:
            continue
        pdates = set(df["日期"].unique()) if len(df) else set()
        unledgered = sorted(pdates - set(ledger.get(key, [])))
        if unledgered:
            findings.append({"check": "B/unledgered_rows", "endpoint": key,
                             "detail": f"panel dates missing from day "
                                       f"ledger: {unledgered[:5]}"})

    # ---- E. ledger cross-endpoint alignment
    sets = {k: set(ledger.get(k, [])) for k in ENDPOINTS}
    for k, s in sets.items():
        for other, s2 in sets.items():
            if other <= k:
                continue
            only = sorted(s - s2)
            if only:
                findings.append({"check": "E/ledger_divergence",
                                 "endpoint": k, "detail":
                                 f"days ledgered here but absent on "
                                 f"{other}: {only[:5]}"})

    # ---- C. cross-panel close-state disjointness + D. band sanity
    for day in days_all:
        for a, b in (("zt", "dtgc"), ("zt", "zbgc")):
            inter = _codes_for_day(panels[a], day) & _codes_for_day(panels[b], day)
            if inter:
                findings.append({"check": f"C/{a}_x_{b}", "endpoint": a,
                                 "date": day, "detail":
                                 f"same-day overlap codes: "
                                 f"{sorted(inter)[:5]}"})
        inter = _codes_for_day(panels["strong"], day) & \
            _codes_for_day(panels["dtgc"], day)
        if inter:
            soft.append({"check": "C/strong_x_dtgc", "date": day, "detail":
                         f"same-day overlap codes: {sorted(inter)[:5]}"})
        for key in ("zt", "dtgc"):
            df = panels[key]
            if "涨跌幅" not in df.columns or "日期" not in df.columns:
                continue
            sl = df[df["日期"] == day]
            vals = pd.to_numeric(sl["涨跌幅"], errors="coerce")
            bad = sl[~vals.isna()]
            if key == "zt":
                viol = bad[vals[bad.index] < SOFT_BAND]
                if len(viol):
                    soft.append({"check": "D/zt_band", "date": day,
                                 "detail": f"{len(viol)} zt rows 涨跌幅 < "
                                           f"+{SOFT_BAND}"})
                if "连板数" in sl.columns:
                    lb = pd.to_numeric(sl["连板数"], errors="coerce")
                    badlb = sl[~lb.isna() & (lb < 1)]
                    if len(badlb):
                        soft.append({"check": "D/zt_ladder", "date": day,
                                     "detail": f"{len(badlb)} zt rows "
                                               "连板数 < 1"})
            else:
                viol = bad[vals[bad.index] > -SOFT_BAND]
                if len(viol):
                    soft.append({"check": "D/dtgc_band", "date": day,
                                 "detail": f"{len(viol)} dtgc rows 涨跌幅 > "
                                           f"-{SOFT_BAND}"})

    # ---- F. calendar completeness inside [FIRST_DATE, max ledger day]
    if days_all:
        hi = days_all[-1]
        window = [d for d in calendar if FIRST_DATE <= d <= hi]
        for k, s in sets.items():
            holes = [d for d in window if d not in s]
            if holes:
                findings.append({"check": "F/calendar_hole", "endpoint": k,
                                 "detail": f"bar-landed trading days missing "
                                           f"from ledger: {holes[:5]}"})
    return findings, soft


def _load_panels():
    panels = {}
    for key in ENDPOINTS:
        path = _panel_path(key)
        if not os.path.exists(path):
            return None, f"panel missing: {key} ({path})"
        try:
            panels[key] = pd.read_parquet(path)
        except Exception as ex:
            return None, f"panel unreadable: {key} ({type(ex).__name__})"
    return panels, None


def _load_ledger():
    if not os.path.exists(LEDGER):
        return None, "day ledger missing"
    try:
        with open(LEDGER, encoding="utf-8") as f:
            d = json.load(f)
        return {k: sorted(v) for k, v in d.items()
                if k in ENDPOINTS and isinstance(v, list)}, None
    except Exception as ex:
        return None, f"day ledger unreadable ({type(ex).__name__})"


def main():
    t0 = time.time()
    panels, err = _load_panels()
    if err:
        print(f"MECHANISM FAULT: {err}", flush=True)
        return 2
    ledger, err = _load_ledger()
    if err:
        print(f"MECHANISM FAULT: {err}", flush=True)
        return 2
    calendar = _load_trading_dates() or []
    findings, soft = run_checks(panels, ledger, calendar)
    days_checked = sorted({d for v in ledger.values() for d in v})
    payload = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "first_date": FIRST_DATE,
        "days_checked": days_checked,
        "per_endpoint_rows": {k: int(len(v)) for k, v in panels.items()},
        "calendar_window_days": len([d for d in calendar
                                     if d >= FIRST_DATE]),
        "findings_n": len(findings),
        "soft_warns_n": len(soft),
        "findings": findings[:50],
        "soft_warns": soft[:50],
        "verdict": "CLEAN" if not findings else
                   f"FINDINGS x{len(findings)} (zero mutation, honest)",
        "elapsed_sec": round(time.time() - t0, 2),
    }
    _atomic_json_write(payload, EVIDENCE)
    print(f"zt_pool crosscheck: {payload['verdict']} "
          f"(days={len(days_checked)} rows={payload['per_endpoint_rows']} "
          f"findings={len(findings)} soft={len(soft)}) -> "
          f"{os.path.relpath(EVIDENCE, ROOT)}", flush=True)
    for f in findings[:10]:
        print(f"  FINDING {f['check']} [{f.get('endpoint','-')}] "
              f"{f.get('date','-')}: {f['detail']}", flush=True)
    for w in soft[:10]:
        print(f"  soft-warn {w['check']} [{w.get('date','-')}]: "
              f"{w['detail']}", flush=True)
    return 3 if findings else 0


def selftest():
    """Offline synthetic fixtures in a temp sandbox: green path + one
    violation per HARD family + soft-warn path. Zero network, zero
    writes outside the sandbox + a temp evidence path."""
    import tempfile
    ts = pd.Timestamp

    def _mk(rows, cols=("代码", "名称", "涨跌幅")):
        d = {c: [] for c in cols}
        for r in rows:
            for c, v in zip(cols, r):
                d[c].append(v)
        return pd.DataFrame(d)

    cal = ["2026-10-08", "2026-10-09", "2026-10-12"]
    base_led = {k: ["2026-10-08", "2026-10-09"] for k in ENDPOINTS}

    def _green_panels():
        zt = _mk([("000001", "a", 10.03, 3), ("000002", "b", 9.98, 1)],
                 ("代码", "名称", "涨跌幅", "连板数"))
        zt.insert(0, "日期", ["2026-10-08", "2026-10-09"])
        zbgc = _mk([("300001", "c", 4.5)])
        zbgc.insert(0, "日期", ["2026-10-08"])
        dtgc = _mk([("600001", "d", -10.0)])
        dtgc.insert(0, "日期", ["2026-10-09"])
        strong = _mk([("000002", "b", 9.98), ("600001", "d", -10.0)])
        strong.insert(0, "日期", ["2026-10-08", "2026-10-09"])
        return {"zt": zt, "zbgc": zbgc, "dtgc": dtgc, "strong": strong}

    # green: zero findings, the strong_x_dtgc overlap is soft-only
    panels = _green_panels()
    f, s = run_checks(panels, base_led, cal)
    assert f == [], f
    assert any(w["check"] == "C/strong_x_dtgc" for w in s), s
    print("[PASS] green path -> zero HARD findings + strong/dtgc soft warn",
          flush=True)

    # A: duplicate dedupe key
    panels = _green_panels()
    zt = panels["zt"]
    panels["zt"] = pd.concat([zt, zt.iloc[[-1]]], ignore_index=True)
    f, _ = run_checks(panels, base_led, cal)
    assert any(x["check"] == "A/dedupe_key" for x in f), f
    print("[PASS] A/dedupe_key duplicate row -> flagged", flush=True)

    # A: date order violation
    panels = _green_panels()
    panels["zt"] = panels["zt"].iloc[::-1].reset_index(drop=True)
    f, _ = run_checks(panels, base_led, cal)
    assert any(x["check"] == "A/date_order" for x in f), f
    print("[PASS] A/date_order reversed panel -> flagged", flush=True)

    # A: row shell (empty code)
    panels = _green_panels()
    shell = _mk([("", "x", 5.0)])
    shell.insert(0, "日期", ["2026-10-08"])
    panels["zbgc"] = pd.concat([panels["zbgc"], shell], ignore_index=True)
    f, _ = run_checks(panels, base_led, cal)
    assert any(x["check"] == "A/row_shell" for x in f), f
    print("[PASS] A/row_shell empty code -> flagged", flush=True)

    # B: unledgered panel date
    panels = _green_panels()
    extra = _mk([("999999", "z", 10.0)])
    extra.insert(0, "日期", ["2026-10-12"])
    panels["zt"] = pd.concat([panels["zt"], extra], ignore_index=True)
    f, _ = run_checks(panels, base_led, cal)
    assert any(x["check"] == "B/unledgered_rows" for x in f), f
    print("[PASS] B/unledgered_rows panel day absent from ledger",
          flush=True)

    # C: zt x dtgc same-day overlap (HARD)
    panels = _green_panels()
    dup = _mk([("000001", "a", -10.0)])
    dup.insert(0, "日期", ["2026-10-08"])
    panels["dtgc"] = pd.concat([panels["dtgc"], dup], ignore_index=True)
    f, _ = run_checks(panels, base_led, cal)
    assert any(x["check"] == "C/zt_x_dtgc" for x in f), f
    print("[PASS] C/zt_x_dtgc close-state overlap -> flagged", flush=True)

    # C: zt x zbgc same-day overlap (HARD)
    panels = _green_panels()
    dup = _mk([("000002", "b", 2.0)])
    dup.insert(0, "日期", ["2026-10-09"])
    panels["zbgc"] = pd.concat([panels["zbgc"], dup], ignore_index=True)
    f, _ = run_checks(panels, base_led, cal)
    assert any(x["check"] == "C/zt_x_zbgc" for x in f), f
    print("[PASS] C/zt_x_zbgc close-state overlap -> flagged", flush=True)

    # D: zt band soft-warn (涨跌幅 below band)
    panels = _green_panels()
    lowband = _mk([("500001", "e", 3.0, 1)],
                  ("代码", "名称", "涨跌幅", "连板数"))
    lowband.insert(0, "日期", ["2026-10-08"])
    panels["zt"] = pd.concat([panels["zt"], lowband], ignore_index=True)
    f, s = run_checks(panels, base_led, cal)
    assert not any(x["check"].startswith("D/") for x in f), f
    assert any(w["check"] == "D/zt_band" for w in s), s
    print("[PASS] D/zt_band below-band row -> soft warn, never HARD",
          flush=True)

    # D: dtgc band soft-warn
    panels = _green_panels()
    hi = _mk([("600002", "g", -3.0)])
    hi.insert(0, "日期", ["2026-10-09"])
    panels["dtgc"] = pd.concat([panels["dtgc"], hi], ignore_index=True)
    _, s = run_checks(panels, base_led, cal)
    assert any(w["check"] == "D/dtgc_band" for w in s), s
    print("[PASS] D/dtgc_band shallow-band row -> soft warn", flush=True)

    # D: zt ladder soft-warn (连板数 < 1)
    panels = _green_panels()
    lb0 = _mk([("500002", "h", 10.0, 0)],
              ("代码", "名称", "涨跌幅", "连板数"))
    lb0.insert(0, "日期", ["2026-10-08"])
    panels["zt"] = pd.concat([panels["zt"], lb0], ignore_index=True)
    _, s = run_checks(panels, base_led, cal)
    assert any(w["check"] == "D/zt_ladder" for w in s), s
    print("[PASS] D/zt_ladder zero-ladder row -> soft warn", flush=True)

    # E: ledger divergence (partial-pass residue; pairwise face -- the
    # deficient endpoint appears in the OTHER endpoints' findings)
    led = {k: list(v) for k, v in base_led.items()}
    led["zbgc"] = ["2026-10-08"]
    f, _ = run_checks(_green_panels(), led, cal)
    assert any(x["check"] == "E/ledger_divergence" and
               "zbgc" in x["detail"] for x in f), f
    print("[PASS] E/ledger_divergence one endpoint missing a day",
          flush=True)

    # F: calendar hole (bar-landed mid-window day absent from EVERY
    # ledger = true collection hole; empty panels isolate F from B)
    led = {k: ["2026-10-08", "2026-10-12"] for k in ENDPOINTS}
    empty = {k: _mk([], ("代码", "名称", "涨跌幅")) for k in ENDPOINTS}
    f, _ = run_checks(empty, led, cal)
    assert any(x["check"] == "F/calendar_hole" and
               "2026-10-09" in x["detail"] for x in f), f
    print("[PASS] F/calendar_hole mid-window gap -> flagged", flush=True)

    # F: days beyond max ledger day are pending, never findings
    f, _ = run_checks(_green_panels(), base_led, cal)
    assert not any(x["check"] == "F/calendar_hole" for x in f), f
    print("[PASS] F beyond-window day (2026-10-12) -> pending, clean",
          flush=True)

    # evidence write roundtrip (temp path, atomic replace, no .tmp left)
    with tempfile.TemporaryDirectory() as td:
        global EVIDENCE
        real = EVIDENCE
        EVIDENCE = os.path.join(td, "ev.json")
        try:
            _atomic_json_write({"v": 1}, EVIDENCE)
            assert json.load(open(EVIDENCE, encoding="utf-8")) == {"v": 1}
            assert not os.path.exists(EVIDENCE + ".tmp")
            print("[PASS] evidence atomic write roundtrip + tmp cleanup",
                  flush=True)
        finally:
            EVIDENCE = real

    # single-source: registry shape (import-time, mirrors collector law)
    assert set(ENDPOINTS) == {"zt", "zbgc", "dtgc", "strong"}
    assert isinstance(FIRST_DATE, str) and FIRST_DATE == "2026-10-08"
    print("[PASS] single-source registry/paths imported, nothing "
          "re-declared", flush=True)

    print("selftest: all crosscheck cases PASS", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main())
