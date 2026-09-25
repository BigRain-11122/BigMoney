"""T-67 s0: OPTIONS_WAVE2 P0 panel enumeration probe (prereg §2 data-completeness gate feed).

Frozen refs: research/OPTIONS_WAVE2_PREREG.md §2 (month set {202609}∪{202610,202612,202703},
evidence_cutoff 2026-09-24, span<90 -> descriptive-only degrade rule) + s3 audit
(results/option_s3_audit.json six green) + 2026-09-25 face-behavior probe (round R192 log:
greeks face returns 行权价/交易代码/简称 for EXPIRED contracts too; 300ETF retains 202609;
daily face cols [日期,开盘,最高,最低,收盘,成交量]).

P0 gate criteria (prereg §2 ①-⑤ + span adaptive ruling):
  G1 contract set present: every enumerated code has >=1 daily row kept at cutoff
  G2 first-row dates (listing proxy) disclosed per contract
  G3 calendar alignment: option panel dates vs underlying daily (SSE), 0 gap both directions
  G4 premium hygiene: close > 0 for all kept rows
  G5 strike face: greeks 行权价 primary + long-code parse + 简称尾数 cross, 100% resolvable
  put-leg empty enumeration (s3 verified call side only) -> honest PP/CSP FAIL feed
  span verdict: <90 trading days -> descriptive_only_degrade (prereg frozen rule)

Laws: direct-connection recipe (ProxyHandler({}) T4 family), honest FAIL records,
repr-first field typing (r158), column anchors live-probed 2026-09-25 (r125: no blind
positions), checkpoint row-key resume (t22), future-row truncation at frozen
evidence_cutoff (r186 observation-date guard).

Outputs:
  results/options_s0_panel_probe.json   -- audit + gates + span verdict
  results/options_s0_panel_codes.json   -- codes census (resume face)
  results/options_s0_panel_cells.jsonl -- per-contract checkpoint (append-only resume)
  data/options/daily/<code>.csv         -- per-contract daily panel (rows <= cutoff)
  data/options/contracts.json          -- runner contract registry face

Usage: python scripts/options_s0_panel_probe.py run|selftest
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import sys
import time

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)
import urllib.request  # noqa: E402

urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))

FROZEN_MONTHS = ["202609", "202610", "202612", "202703"]  # prereg §2: expired {202609} ∪ listed 3
FROZEN_LISTED = ["202610", "202612", "202703"]
EVIDENCE_CUTOFF = "2026-09-24"  # prereg §2 frozen (last complete bar day)
SPAN_DEGRADE_MIN = 90  # prereg §2 frozen adaptive-degrade threshold (trading days)
DIRECTIONS = {"call": "看涨期权", "put": "看跌期权"}
UNDERLYINGS = {
    "510050": {"display": "50ETF"},
    "510300": {"display": "300ETF"},
}
LONG_CODE_RE = re.compile(r"^(\d{6})([CP])(\d{4})M(\d{5})$")

OUT_JSON = os.path.join("results", "options_s0_panel_probe.json")
CODES_JSON = os.path.join("results", "options_s0_panel_codes.json")
CELLS_JSONL = os.path.join("results", "options_s0_panel_cells.jsonl")
PANEL_DIR = os.path.join("data", "options", "daily")
REGISTRY_JSON = os.path.join("data", "options", "contracts.json")

CODES_SLEEP = 2.0
CONTRACT_SLEEP = 0.5
FUSE_N = 3  # consecutive contract-level failures -> honest exit 2 (conn-fuse)


# ---------------------------------------------------------------- pure functions

def normalize_daily_df(df):
    """Raw sina option daily frame -> (rows, meta). Column anchor: live-probed
    2026-09-25 (s3 + face probe agree): [日期,开盘,最高,最低,收盘,成交量], col0=date."""
    if df is None or len(df) == 0:
        return None, {"status": "EMPTY", "rows": 0}
    cols = [str(c) for c in df.columns]
    if len(cols) != 6:
        return None, {"status": "SHAPE_DRIFT", "cols_repr": repr(cols)[:200],
                      "rows": int(len(df))}
    d0 = df.iloc[0, 0]
    if not isinstance(d0, dt.date):
        return None, {"status": "SHAPE_DRIFT", "reason": "col0_not_date",
                      "col0_repr": repr(d0)[:80]}
    rows = []
    bad = 0
    for t in df.itertuples(index=False, name=None):
        d, o, h, l, c, v = t
        if not isinstance(d, dt.date):
            bad += 1
            continue
        try:
            ro, rh, rl, rc, rv = float(o), float(h), float(l), float(c), float(v)
        except (TypeError, ValueError):
            bad += 1
            continue
        rows.append({"date": d.isoformat(), "open": ro, "high": rh,
                     "low": rl, "close": rc, "volume": rv})
    if bad:
        return None, {"status": "SHAPE_DRIFT", "reason": f"unparsable_rows={bad}"}
    return rows, {"status": "OK", "rows": len(rows), "cols": cols}


def parse_strike_faces(kv):
    """greeks KV dict -> strike with cross-source agreement (primary=行权价)."""
    out = {"long_code": str(kv.get("交易代码", "")),
           "name": str(kv.get("期权合约简称", "")), "sources": {}}
    v = kv.get("行权价")
    if v is not None and str(v) != "":
        try:
            out["sources"]["greeks_kv"] = float(v)
        except (TypeError, ValueError):
            out["sources"]["greeks_kv"] = f"unparsable:{v!r}"
    m = LONG_CODE_RE.match(out["long_code"])
    if m:
        out["sources"]["long_code"] = int(m.group(4)) / 1000.0
    mt = re.search(r"(\d{4,5})\s*$", out["name"])
    if mt:
        out["sources"]["name_tail"] = int(mt.group(1)) / 1000.0
    vals = [x for x in out["sources"].values() if isinstance(x, float)]
    agree = mismatch = 0
    for x in vals[1:]:
        if abs(x - vals[0]) < 1e-6:
            agree += 1
        else:
            mismatch += 1
    out["strike"] = vals[0] if vals else None
    out["n_sources"] = len(vals)
    out["cross_agree"] = agree
    out["cross_mismatch"] = mismatch
    return out


def ladder_check(values):
    vals = sorted(v for v in values if v is not None and not (v != v))
    nan = sum(1 for v in values if v is None or (isinstance(v, float) and v != v))
    dups = len(vals) - len(set(vals))
    steps = sorted({round(b - a, 6) for a, b in zip(vals, vals[1:])}) if len(vals) > 1 else []
    return {"n": len(vals), "nan": nan, "dup": dups,
            "min": vals[0] if vals else None, "max": vals[-1] if vals else None,
            "steps": steps}


def span_calc(panel_dates, under_dates):
    """panel_dates: iterable of ISO str; under_dates: sorted list of ISO str."""
    if not panel_dates or not under_dates:
        return {"span_days": 0, "window": None,
                "missing_in_option": None, "foreign_in_underlying": None}
    pd_set = set(panel_dates)
    ud_set = set(under_dates)
    lo, hi = min(pd_set), max(pd_set)
    win = [d for d in under_dates if lo <= d <= hi]
    missing = [d for d in win if d not in pd_set]
    foreign = sorted(d for d in pd_set if d not in ud_set)
    return {"span_days": len(win), "window": [lo, hi],
            "missing_in_option": missing, "foreign_in_underlying": foreign}


def truncate_at_cutoff(rows, cutoff):
    kept = [r for r in rows if r["date"] <= cutoff]
    return kept, {"rows_raw": len(rows), "rows_kept": len(kept),
                  "dropped_after_cutoff": len(rows) - len(kept),
                  "raw_last": rows[-1]["date"] if rows else None}


def close_hygiene(rows):
    bad = 0
    for r in rows:
        c = r["close"]
        if c != c or c <= 0:  # NaN or non-positive premium
            bad += 1
    return bad


# ---------------------------------------------------------------- network probe

def probe(fn, **kw):
    t0 = time.time()
    try:
        r = fn(**kw)
        if isinstance(r, (list, tuple)):
            return {"status": "OK_SEQ", "items": [str(x) for x in r][:8],
                    "repr": repr(r)[:160], "sec": round(time.time() - t0, 1)}, r
        if r is None or len(r) == 0:
            return {"status": "EMPTY", "sec": round(time.time() - t0, 1)}, r
        return ({"status": "OK", "rows": int(len(r)),
                 "cols": [str(c) for c in r.columns][:16],
                 "sec": round(time.time() - t0, 1)}, r)
    except Exception as e:
        return {"status": "FAIL", "err": f"{type(e).__name__}: {str(e)[:180]}",
                "sec": round(time.time() - t0, 1)}, None


def kv_from_frame(df):
    if df is None or df.shape[1] != 2:
        return {}
    return {str(a): str(b) for a, b in zip(df.iloc[:, 0], df.iloc[:, 1])}


def load_checkpoint():
    done = {}
    torn = 0
    if os.path.exists(CELLS_JSONL):
        with open(CELLS_JSONL, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    torn += 1
                    continue
                if o.get("status") == "ok":
                    done[o["code"]] = o
    return done, torn


def write_csv(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write("date,open,high,low,close,volume\n")
        for r in rows:
            f.write(f"{r['date']},{r['open']},{r['high']},{r['low']},{r['close']},{r['volume']}\n")
    os.replace(tmp, path)


def read_underlying_dates(code):
    path = os.path.join("data", "daily", f"{code}.csv")
    dates = []
    with open(path, encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            d = line.split(",", 1)[0]
            if d:
                dates.append(d)
    return header, dates


def run():
    import akshare as ak  # noqa: import after env scrub

    t_start = time.time()
    os.makedirs(PANEL_DIR, exist_ok=True)
    res = {"run_date": dt.date.today().isoformat(),
           "gate": "T-67 s0 P0 panel enumeration probe (OPTIONS_WAVE2 prereg §2)",
           "prereg_ref": "research/OPTIONS_WAVE2_PREREG.md §2 (frozen)",
           "frozen": {"months": FROZEN_MONTHS, "evidence_cutoff": EVIDENCE_CUTOFF,
                      "span_degrade_min": SPAN_DEGRADE_MIN},
           "evidence_cutoff": EVIDENCE_CUTOFF,
           "science_gates": {"cutoff_meta": EVIDENCE_CUTOFF},
           "codes_census": {}, "months_list_face": {}, "expiry": {},
           "contracts": {}, "ladder": {}, "gates": {}, "span": {}, "verdict": {}}
    ckpt_done, torn = load_checkpoint()
    if torn:
        res["checkpoint_torn_lines_ignored"] = torn

    # -- months list face (drift disclosure vs prereg-frozen listed set) ------------
    for u, cfg in UNDERLYINGS.items():
        meta, r = probe(ak.option_sse_list_sina, symbol=cfg["display"], exchange="null")
        res["months_list_face"][u] = {"meta": meta,
                                      "listed_now": [str(x) for x in r]
                                      if meta["status"] == "OK_SEQ" else None,
                                      "listed_frozen": FROZEN_LISTED}
        time.sleep(CODES_SLEEP)

    # -- codes census (16 pulls, resume via codes file) ------------------------------
    census = None
    if os.path.exists(CODES_JSON):
        with open(CODES_JSON, encoding="utf-8") as f:
            census = json.load(f)
        res["codes_census_resume"] = True
    if census is None:
        census = {"generated_at": dt.datetime.now().isoformat(timespec="seconds"),
                  "evidence_cutoff": EVIDENCE_CUTOFF, "faces": {}}
        for u in UNDERLYINGS:
            census["faces"][u] = {}
            for mo in FROZEN_MONTHS:
                census["faces"][u][mo] = {}
                for dkey, dsym in DIRECTIONS.items():
                    meta, r = probe(ak.option_sse_codes_sina, symbol=dsym,
                                    trade_date=mo, underlying=u)
                    codes = ([str(x) for x in r["期权代码"].astype(str).tolist()]
                             if meta["status"] == "OK" and r is not None
                             and "期权代码" in r.columns else [])
                    census["faces"][u][mo][dkey] = {
                        "meta": meta, "codes": codes}
                    time.sleep(CODES_SLEEP)
        with open(CODES_JSON, "w", encoding="utf-8") as f:
            json.dump(census, f, ensure_ascii=False, indent=1)

    # code -> (underlying, month, direction) map; dup disclosure
    code_map = {}
    dups = []
    for u, mos in census["faces"].items():
        for mo, dirs in mos.items():
            for dkey, face in dirs.items():
                for c in face["codes"]:
                    if c in code_map:
                        dups.append(c)
                    else:
                        code_map[c] = (u, mo, dkey)
    res["codes_dup_disclosure"] = sorted(set(dups))

    # -- expire face (per underlying x frozen month) ---------------------------------
    for u, cfg in UNDERLYINGS.items():
        res["expiry"][u] = {}
        for mo in FROZEN_MONTHS:
            meta, r = probe(ak.option_sse_expire_day_sina, trade_date=mo,
                            symbol=cfg["display"])
            res["expiry"][u][mo] = {"meta": meta,
                                    "items": [str(x) for x in r]
                                    if meta["status"] == "OK_SEQ" and r else None}
            time.sleep(CODES_SLEEP)

    # -- per-contract loop (greeks + daily, checkpoint resume) -----------------------
    pending = sorted(c for c in code_map if c not in ckpt_done)
    print(f"[s0] contracts total={len(code_map)} done={len(ckpt_done)} "
          f"pending={len(pending)}", flush=True)
    fuse = 0
    ckpt_f = open(CELLS_JSONL, "a", encoding="utf-8")
    for i, code in enumerate(pending):
        u, mo, dkey = code_map[code]
        line = {"code": code, "underlying": u, "month": mo, "direction": dkey}
        try:
            gmeta, gdf = probe(ak.option_sse_greeks_sina, symbol=code)
            line["greeks_meta"] = gmeta
            kv = kv_from_frame(gdf) if gmeta["status"] == "OK" else {}
            sf = parse_strike_faces(kv)
            line.update({"strike": sf["strike"], "n_strike_sources": sf["n_sources"],
                         "strike_cross_agree": sf["cross_agree"],
                         "strike_cross_mismatch": sf["cross_mismatch"],
                         "long_code": sf["long_code"], "contract_name": sf["name"]})
            dmeta, ddf = probe(ak.option_sse_daily_sina, symbol=code)
            line["daily_meta"] = dmeta
            if dmeta["status"] == "OK":
                rows, nmeta = normalize_daily_df(ddf)
                if rows is not None:
                    kept, tmeta = truncate_at_cutoff(rows, EVIDENCE_CUTOFF)
                    line.update(tmeta)
                    line["close_nonpos_nan"] = close_hygiene(kept)
                    if kept:
                        line["first_date"] = kept[0]["date"]
                        line["last_date_kept"] = kept[-1]["date"]
                        line["head_repr"] = [repr(x)[:240] for x in kept[:2]]
                        line["tail_repr"] = repr(kept[-1])[:240]
                        write_csv(os.path.join(PANEL_DIR, f"{code}.csv"), kept)
                        line["status"] = "ok"
                    else:
                        line["status"] = "excluded_honest"
                        line["reason"] = "no rows at/below evidence cutoff (listed after cutoff?)"
                else:
                    line["status"] = "fail"
                    line["reason"] = f"daily {nmeta['status']}"
            else:
                line["status"] = "fail"
                line["reason"] = f"daily {dmeta['status']}"
        except Exception as e:
            line["status"] = "fail"
            line["reason"] = f"exc:{type(e).__name__}:{str(e)[:120]}"
        if line["status"] == "ok":
            fuse = 0
        else:
            fuse += 1
        ckpt_f.write(json.dumps(line, ensure_ascii=False) + "\n")
        ckpt_f.flush()
        print(f"[s0] {i+1}/{len(pending)} {code} {line['status']} "
              f"rows={line.get('rows_kept')} strike={line.get('strike')}", flush=True)
        if fuse >= FUSE_N:
            ckpt_f.close()
            print(f"[s0] conn-fuse: {FUSE_N} consecutive contract failures, honest stop",
                  flush=True)
            sys.exit(2)
        time.sleep(CONTRACT_SLEEP)
    ckpt_f.close()

    # -- aggregate gates from full checkpoint ----------------------------------------
    done, _ = load_checkpoint()
    res["contracts"] = done
    excluded = {c: o for c, o in done.items() if o.get("status") != "ok"}
    kept_ct = {c: o for c, o in done.items() if o.get("status") == "ok"}

    # ladder per u/mo/dir
    for u in UNDERLYINGS:
        res["ladder"][u] = {}
        for mo in FROZEN_MONTHS:
            res["ladder"][u][mo] = {}
            for dkey in DIRECTIONS:
                strikes = [o.get("strike") for c, o in kept_ct.items()
                           if o["underlying"] == u and o["month"] == mo
                           and o["direction"] == dkey]
                res["ladder"][u][mo][dkey] = ladder_check(strikes)

    # put-leg empty feed + codes-face presence
    put_empty, call_empty = [], []
    for u in UNDERLYINGS:
        for mo in FROZEN_MONTHS:
            for dkey in DIRECTIONS:
                face = census["faces"][u][mo][dkey]
                n_codes = len(face["codes"])
                n_ok = sum(1 for c, o in kept_ct.items()
                           if o["underlying"] == u and o["month"] == mo
                           and o["direction"] == dkey)
                if dkey == "put" and n_codes == 0:
                    put_empty.append(f"{u}_{mo}")
                if dkey == "call" and n_codes == 0:
                    call_empty.append(f"{u}_{mo}")

    # calendar alignment + span per underlying
    under_dates = {}
    for u in UNDERLYINGS:
        _, dates = read_underlying_dates(u)
        under_dates[u] = dates
        pdates = {o["first_date"] for o in kept_ct.values()
                  if o["underlying"] == u}
        for c, o in kept_ct.items():
            if o["underlying"] == u:
                pdates.add(o["last_date_kept"])
        # full union from csv files (authoritative per-contract rows)
        pdates = set()
        for c, o in kept_ct.items():
            if o["underlying"] != u:
                continue
            pth = os.path.join(PANEL_DIR, f"{c}.csv")
            if os.path.exists(pth):
                with open(pth, encoding="utf-8") as f:
                    f.readline()
                    for ln in f:
                        d = ln.split(",", 1)[0]
                        if d:
                            pdates.add(d)
        res["span"][u] = span_calc(pdates, under_dates[u])
        sv = res["span"][u]
        sv["verdict"] = ("descriptive_only_degrade" if sv["span_days"] < SPAN_DEGRADE_MIN
                         else "registration_eligible")
        sv["weekly_entries_estimate"] = sv["span_days"] // 5  # informational only

    g1_fail = {c: o.get("reason", "") for c, o in excluded.items()}
    strike_fail = {c: {"strike": o.get("strike"), "n_sources": o.get("n_strike_sources"),
                       "cross_mismatch": o.get("strike_cross_mismatch")}
                   for c, o in kept_ct.items()
                   if o.get("strike") is None or o.get("strike_cross_mismatch", 0) > 0
                   or (o.get("n_strike_sources") or 0) < 2}
    close_bad = sum(o.get("close_nonpos_nan", 0) for o in kept_ct.values())
    align_ok = True
    for u in UNDERLYINGS:
        sv = res["span"][u]
        if sv["missing_in_option"] or sv["foreign_in_underlying"]:
            align_ok = False
    ladder_bad = []
    for u in UNDERLYINGS:
        for mo in FROZEN_MONTHS:
            for dkey in DIRECTIONS:
                ld = res["ladder"][u][mo][dkey]
                if ld["n"] and (ld["nan"] or ld["dup"]):
                    ladder_bad.append(f"{u}_{mo}_{dkey}:{ld}")

    res["gates"] = {
        "G1_contract_set_present": {"pass": len(g1_fail) == 0, "fails": g1_fail},
        "G2_first_row_disclosed": {"pass": all(o.get("first_date") for o in kept_ct.values()),
                                   "n_contracts": len(kept_ct)},
        "G3_calendar_alignment_zero_gap": {"pass": align_ok},
        "G4_close_positive": {"pass": close_bad == 0, "nonpos_nan_rows": close_bad},
        "G5_strike_face_100pct": {"pass": len(strike_fail) == 0, "fails": strike_fail},
        "ladder_continuity": {"pass": len(ladder_bad) == 0, "fails": ladder_bad},
    }
    res["gates"]["put_leg_empty_feed"] = put_empty
    res["gates"]["call_leg_empty_feed"] = call_empty
    gate_pass = all(v["pass"] for k, v in res["gates"].items()
                    if isinstance(v, dict) and "pass" in v)
    batch_span = min(res["span"][u]["span_days"] for u in UNDERLYINGS)
    res["verdict"] = {
        "gate_pass": gate_pass,
        "batch_span_days": batch_span,
        "span_verdict": ("descriptive_only_degrade" if batch_span < SPAN_DEGRADE_MIN
                         else "registration_eligible"),
        "kept_contracts": len(kept_ct),
        "excluded_honest": sorted(excluded),
        "put_empty_feed": put_empty,
    }

    # registry face for the s1 runner (kept contracts only)
    registry = {"evidence_cutoff": EVIDENCE_CUTOFF,
                "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
                "probe_ref": OUT_JSON, "underlyings": UNDERLYINGS,
                "expiry": res["expiry"], "contracts": []}
    for c, o in sorted(kept_ct.items()):
        registry["contracts"].append({
            "code": c, "underlying": o["underlying"], "month": o["month"],
            "direction": o["direction"], "strike": o["strike"],
            "n_strike_sources": o.get("n_strike_sources"),
            "strike_cross_mismatch": o.get("strike_cross_mismatch"),
            "long_code": o.get("long_code"), "contract_name": o.get("contract_name"),
            "expiry_items": res["expiry"][o["underlying"]][o["month"]]["items"],
            "first_date": o["first_date"], "last_date": o["last_date_kept"],
            "rows": o["rows_kept"], "daily_csv": f"data/options/daily/{c}.csv"})
    with open(REGISTRY_JSON, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=1)

    res["runtime_sec"] = round(time.time() - t_start, 1)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": res["verdict"], "gates_pass": {k: v.get("pass")
                  for k, v in res["gates"].items() if isinstance(v, dict)},
                  "span": {u: res["span"][u] for u in UNDERLYINGS}},
                     ensure_ascii=False, indent=1)[:2400])
    return 0


def selftest():
    import pandas as pd
    fails = 0

    def check(name, cond):
        nonlocal fails
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails += 1

    # normalize: production-shape frame (mirrors live face anchor)
    df = pd.DataFrame({c: v for c, v in zip(
        ["日期", "开盘", "最高", "最低", "收盘", "成交量"],
        [[dt.date(2026, 9, 23), dt.date(2026, 9, 24), dt.date(2026, 9, 25)],
         [0.1, 0.2, 0.3], [0.11, 0.21, 0.31], [0.09, 0.19, 0.29],
         [0.1, 0.2, 0.3], [100, 200, 300]])})
    rows, meta = normalize_daily_df(df)
    check("normalize production-shape", meta["status"] == "OK" and len(rows) == 3
          and rows[0]["date"] == "2026-09-23")
    kept, t = truncate_at_cutoff(rows, EVIDENCE_CUTOFF)
    check("cutoff truncation drops future row", len(kept) == 2 and t["dropped_after_cutoff"] == 1
          and t["raw_last"] == "2026-09-25")
    check("close hygiene clean", close_hygiene(kept) == 0)
    bad = list(kept) + [{"date": "2026-09-22", "open": 1, "high": 1, "low": 1,
                         "close": 0.0, "volume": 1}]
    check("close hygiene catches nonpositive", close_hygiene(bad) == 1)

    # normalize negatives: 5-col drift + empty
    rows2, meta2 = normalize_daily_df(pd.DataFrame({"a": [1, 2], "b": [3, 4]}))
    check("normalize shape-drift negative", rows2 is None and meta2["status"] == "SHAPE_DRIFT")
    rows3, meta3 = normalize_daily_df(pd.DataFrame({c: [] for c in
                                  ["日期", "开盘", "最高", "最低", "收盘", "成交量"]}))
    check("normalize empty negative", rows3 is None and meta3["status"] == "EMPTY")

    # strike faces: production KV form (greeks 2-col dict)
    kv = {"行权价": "2.7500", "交易代码": "510050C2610M02750",
          "期权合约简称": "50ETF购10月2750"}
    sf = parse_strike_faces(kv)
    check("strike 3-source agree", sf["strike"] == 2.75 and sf["n_sources"] == 3
          and sf["cross_agree"] == 2 and sf["cross_mismatch"] == 0)
    sf2 = parse_strike_faces({"交易代码": "510050P2610M03000",
                              "期权合约简称": "50ETF沽10月3000"})
    check("strike fallback long_code+name", sf2["strike"] == 3.0 and sf2["n_sources"] == 2)
    sf3 = parse_strike_faces({"行权价": "2.7500", "交易代码": "510050C2610M02800",
                              "期权合约简称": "50ETF购10月2750"})
    check("strike cross-mismatch caught", sf3["strike"] == 2.75
          and sf3["cross_mismatch"] >= 1)
    sf4 = parse_strike_faces({})
    check("strike empty kv honest", sf4["strike"] is None and sf4["n_sources"] == 0)

    # ladder
    ld = ladder_check([2.65, 2.70, 2.75, 2.80])
    check("ladder ok", ld["n"] == 4 and ld["dup"] == 0 and ld["steps"] == [0.05])
    ld2 = ladder_check([2.7, 2.7, None])
    check("ladder dup+nan caught", ld2["dup"] == 1 and ld2["nan"] == 1)

    # span
    ud = [f"2026-09-{d:02d}" for d in range(1, 11)]
    sp = span_calc({"2026-09-02", "2026-09-03", "2026-09-09", "2026-09-30"}, ud)
    check("span window+missing+foreign", sp["span_days"] == 9
          and "2026-09-01" not in sp["missing_in_option"]
          and len(sp["missing_in_option"]) == 6 and sp["foreign_in_underlying"] == ["2026-09-30"])
    sp2 = span_calc(set(), ud)
    check("span empty honest", sp2["span_days"] == 0 and sp2["window"] is None)

    print(f"selftest: {'ALL PASS' if fails == 0 else f'{fails} FAIL'}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "run":
        sys.exit(run())
    print(f"unknown subcommand: {cmd}")
    sys.exit(2)
