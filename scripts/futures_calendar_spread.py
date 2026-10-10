"""Futures calendar-spread monitoring face (E8, r828 bm-b, claim lock 3b5b3686b).

Consumes the 9-variety main-continuous panel (data/futures_daily, update_futures
lane R48/R51) plus live per-contract sina daily klines to serialize near/far
calendar-spread series per variety. Pure descriptive face: zero prereg, zero
backtest, zero judgment thresholds (explore-queue precedent r821/r823/r827 --
E7 scanner / E3 probe family). Judged faces need a separate ticket through
PREREG_TEMPLATE.

Source shape (probe results/_r828bmb_e8_shape_probe.py, 5/5 families alive):
stock2.finance.sina.com.cn InnerFuturesNewService.getDailyKLine?symbol=<CONTRACT>
keys: d=date o=open h=high l=low c=close v=volume p=positions(OI) s=settle.
NOTE latent upstream key-slot bug: update_futures.py raw-fallback reads OI from
key "o" (which is OPEN); akshare-primary path unaffected (local panel OI sane,
e.g. RB 1.67M). Registered to tech queue -- bm-a lane, not fixed here.

Pair selection (descriptive, no thresholds-as-judgments):
- alive = last bar within ALIVE_MAX_AGE_DAYS and last OI > 0
- near  = earliest-expiry alive contract with OI >= OI_FLOOR_RATIO * max OI
- far   = next-expiry alive contract meeting the same floor
  (roll migration self-heals: an expiring front month drops below the floor
  and the next month becomes near -- RB2610 OI 6.9k vs dominant ~1.67M).

Panel cross-ref per variety: main-continuous close/OI at local cutoff,
dominant_guess = alive contract whose close is nearest the panel close,
basis = near_close - panel_close at panel cutoff date (if present in near
series; else honest null).

Outputs: results/futures_calendar_spread/{face.json, spreads.csv}.
Exit codes: 0 = face built (>=1 variety pair, partial varieties honest);
2 = mechanism fault / zero pairs built. selftest subcommand: hermetic.
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_DIR = os.path.join(ROOT, "data", "futures_daily")
OUT_DIR = os.path.join(ROOT, "results", "futures_calendar_spread")
FACE_JSON = os.path.join(OUT_DIR, "face.json")
SPREADS_CSV = os.path.join(OUT_DIR, "spreads.csv")

VARIETIES = ["IF", "IC", "IM", "IH", "T", "TF", "RB", "AU", "SC"]
INDEX_FUT = {"IF", "IC", "IM", "IH"}
TREASURY_FUT = {"T", "TF"}
COMMODITY_FUT = {"RB", "AU", "SC"}

RAW_URL = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/"
           "var%20_F={sym}/InnerFuturesNewService.getDailyKLine?symbol={sym}")
SLEEP_S = 2.5
REQ_TIMEOUT_S = 45
ALIVE_MAX_AGE_DAYS = 20
OI_FLOOR_RATIO = 0.15
COMMODITY_MONTHS_AHEAD = 8
TREASURY_QUARTERS = 4

SPREAD_COLS = ["variety", "near", "far", "date", "near_close", "far_close",
               "spread", "ratio"]


# ------------------------------------------------------------------ contracts


def _month_iter(y: int, m: int, n: int):
    for _ in range(n):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


def candidate_contracts(now: dt.datetime, variety: str) -> list:
    """Deterministic candidate contract codes for a variety at `now` (pure).

    CFFEX index rule: current month, next month, then the next two
    quarter-end months. Treasury: next TREASURY_QUARTERS quarter months
    (Mar/Jun/Sep/Dec). Commodity: rolling COMMODITY_MONTHS_AHEAD months.
    """
    y, m = now.year, now.month
    if variety in INDEX_FUT:
        out = []
        cur = (y, m)
        nxt = (y + 1, 1) if m == 12 else (y, m + 1)
        out.append(cur)
        out.append(nxt)
        # next two quarter-end months after `nxt`
        qy, qm = nxt
        picked = 0
        while picked < 2:
            qm += 1
            if qm > 12:
                qm = 1
                qy += 1
            if qm in (3, 6, 9, 12):
                out.append((qy, qm))
                picked += 1
        return [f"{variety}{yy % 100:02d}{mm:02d}" for yy, mm in out]
    if variety in TREASURY_FUT:
        out = []
        qy, qm = y, m
        while len(out) < TREASURY_QUARTERS:
            if qm in (3, 6, 9, 12):
                out.append((qy, qm))
            qm += 1
            if qm > 12:
                qm = 1
                qy += 1
        return [f"{variety}{yy % 100:02d}{mm:02d}" for yy, mm in out]
    # commodity: rolling months ahead from current month inclusive
    out = [(yy, mm) for yy, mm in _month_iter(y, m, COMMODITY_MONTHS_AHEAD)]
    return [f"{variety}{yy % 100:02d}{mm:02d}" for yy, mm in out]


def contract_sort_key(code: str) -> int:
    return int(code[-4:])


# -------------------------------------------------------------------- source


def _no_proxy_opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def parse_payload(txt: str) -> list:
    """Extract the json array from the jsonp wrapper; [] when empty/dead."""
    m = re.search(r"\(\s*(\[.*\])\s*\)", txt, re.S)
    if not m:
        return []
    arr = json.loads(m.group(1))
    if not isinstance(arr, list):
        return []
    return arr


def parse_rows(arr: list) -> list:
    """Endpoint item -> normalized row. Keys: d o h l c v p s (p=OI!)."""
    rows = []
    for it in arr:
        try:
            d = str(it.get("d", ""))
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
                continue
            row = {"date": d}
            for col, k in (("open", "o"), ("high", "h"), ("low", "l"),
                           ("close", "c"), ("volume", "v"),
                           ("oi", "p"), ("settle", "s")):
                v = it.get(k)
                try:
                    row[col] = None if v in (None, "", "0.000", "0") else float(v)
                except (TypeError, ValueError):
                    row[col] = None
            rows.append(row)
        except Exception:
            continue
    return rows


def fetch_contract(opener, sym: str) -> list:
    """Full per-contract daily kline rows (may be empty = not listed)."""
    with opener.open(RAW_URL.format(sym=sym), timeout=REQ_TIMEOUT_S) as resp:
        txt = resp.read().decode("utf-8", errors="replace")
    return parse_rows(parse_payload(txt))


# ------------------------------------------------------- pair select (pure)


def is_alive(rows: list, now: dt.datetime, max_age_days: int = ALIVE_MAX_AGE_DAYS) -> bool:
    if not rows:
        return False
    last = rows[-1]
    if (last.get("oi") or 0) <= 0:
        return False
    try:
        age = (now - dt.datetime.strptime(last["date"], "%Y-%m-%d")).days
    except Exception:
        return False
    return 0 <= age <= max_age_days


def pick_pair(candidates: dict, now: dt.datetime):
    """candidates: {sym: rows}. Returns (near, far, near_rows, far_rows,
    alive_syms, far_thin) -- near/far by expiry among alive contracts; near
    must meet the OI floor (skips expiring dead fronts); far meets the floor
    when possible, else falls back to the next alive expiry with any OI>0
    (far_thin=True -- treasury quarterly structure: next-quarter OI ~5% of
    front is a real, tradable calendar leg, not a dead month). Honest
    (None, ...) when no near qualifies or no far exists."""
    alive = {s: r for s, r in candidates.items() if is_alive(r, now)}
    if not alive:
        return None, None, None, None, [], False
    max_oi = max(r[-1].get("oi") or 0 for r in alive.values())
    floor = max_oi * OI_FLOOR_RATIO
    ranked = sorted(alive, key=contract_sort_key)
    qualified = [s for s in ranked if (alive[s][-1].get("oi") or 0) >= floor]
    if not qualified:
        return None, None, None, None, sorted(alive), False
    near = qualified[0]
    far = None
    far_thin = False
    if len(qualified) >= 2:
        far = qualified[1]
    else:
        rest = [s for s in ranked if contract_sort_key(s) > contract_sort_key(near)]
        if rest:
            far = rest[0]
            far_thin = True
    if far is None:
        return None, None, None, None, sorted(alive), False
    return near, far, alive[near], alive[far], sorted(alive), far_thin


# ------------------------------------------------------------ spread series


def spread_rows(near_rows: list, far_rows: list) -> list:
    """Inner join on date, sorted by date. spread = far - close, ratio = far/near."""
    nb = {r["date"]: r for r in near_rows}
    out = []
    for r in sorted(far_rows, key=lambda x: x["date"]):
        n = nb.get(r["date"])
        if n is None:
            continue
        nc, fc = n.get("close"), r.get("close")
        if nc is None or fc is None or nc == 0:
            continue
        out.append({"date": r["date"], "near_close": nc, "far_close": fc,
                    "spread": fc - nc, "ratio": fc / nc})
    return out


def series_stats(rows: list) -> dict:
    if not rows:
        return {"n": 0}
    sp = [r["spread"] for r in rows]
    n = len(sp)
    mean = sum(sp) / n
    var = sum((x - mean) ** 2 for x in sp) / max(n - 1, 1)
    std = var ** 0.5
    latest = sp[-1]
    return {"n": n, "first": rows[0]["date"], "last": rows[-1]["date"],
            "latest_spread": latest, "latest_ratio": rows[-1]["ratio"],
            "mean": mean, "std": std, "min": min(sp), "max": max(sp),
            "z_latest": ((latest - mean) / std) if std and std > 0 else None}


# ------------------------------------------------------------ panel crossref


def panel_tail(variety: str, data_dir=None) -> dict:
    """Main-continuous panel tail: cutoff date/close/oi (local, pure read)."""
    data_dir = data_dir or PANEL_DIR
    p = os.path.join(data_dir, variety + ".csv")
    if not os.path.exists(p):
        return {"cutoff": None, "close": None, "oi": None, "rows": None}
    import csv as _csv
    with io.open(p, "r", encoding="utf-8") as f:
        rows = list(_csv.DictReader(f))
    if not rows:
        return {"cutoff": None, "close": None, "oi": None, "rows": 0}
    last = rows[-1]
    return {"cutoff": last.get("date"), "close": _f(last.get("close")),
            "oi": _f(last.get("oi")), "rows": len(rows)}


def _f(v):
    try:
        return None if v in (None, "") else float(v)
    except (TypeError, ValueError):
        return None


def dominant_guess(alive_rows: dict, panel_close) -> str | None:
    """Alive contract whose close is nearest the main-continuous close."""
    if panel_close is None or not alive_rows:
        return None
    best, bestd = None, None
    for sym, rows in alive_rows.items():
        if not rows:
            continue
        c = rows[-1].get("close")
        if c is None:
            continue
        d = abs(c - panel_close)
        if bestd is None or d < bestd:
            best, bestd = sym, d
    return best


# ------------------------------------------------------------------- csv out


def spreads_csv_text(all_rows: list) -> str:
    import csv
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(SPREAD_COLS)
    for r in all_rows:
        w.writerow([r["variety"], r["near"], r["far"], r["date"],
                    f'{r["near_close"]:.10g}', f'{r["far_close"]:.10g}',
                    f'{r["spread"]:.10g}', f'{r["ratio"]:.10g}'])
    return buf.getvalue()


def atomic_write(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


# ---------------------------------------------------------------------- run


def run(now: dt.datetime = None) -> int:
    now = now or dt.datetime.now()
    opener = _no_proxy_opener()
    face = {"ts": now.isoformat(timespec="seconds"),
            "claim": "E8 r828 bm-b lock 3b5b3686b",
            "law": "explore-queue descriptive face (r821/r823/r827 precedent); "
                   "zero prereg zero backtest zero judgment thresholds",
            "source": "sina InnerFuturesNewService.getDailyKLine per-contract "
                      "(probe r828 5/5 families alive; p=OI s=settle)",
            "alive_max_age_days": ALIVE_MAX_AGE_DAYS,
            "oi_floor_ratio": OI_FLOOR_RATIO,
            "varieties": {}, "panel": {}, "failures": {}, "summary": {}}
    csv_rows = []
    pairs_built = 0
    req_total = 0
    for vi, v in enumerate(VARIETIES):
        tail = panel_tail(v)
        face["panel"][v] = tail
        cands = candidate_contracts(now, v)
        got = {}
        for ci, sym in enumerate(cands):
            req_total += 1
            try:
                got[sym] = fetch_contract(opener, sym)
            except Exception as e:
                got[sym] = []
                face["failures"][f"{v}:{sym}"] = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(SLEEP_S)
        near, far, nrow, frow, alive_syms, far_thin = pick_pair(got, now)
        rec = {"candidates": cands, "alive": {s: {"last_date": got[s][-1]["date"],
                                                  "last_oi": got[s][-1].get("oi"),
                                                  "last_close": got[s][-1].get("close"),
                                                  "rows": len(got[s])}
                                              for s in alive_syms}}
        if near is not None:
            sr = spread_rows(nrow, frow)
            st = series_stats(sr)
            rec.update({"near": near, "far": far, "far_thin": far_thin,
                        "near_oi": nrow[-1].get("oi"), "far_oi": frow[-1].get("oi"),
                        "series": st})
            pc = tail.get("close")
            rec["dominant_guess"] = dominant_guess({s: got[s] for s in alive_syms}, pc)
            nb_by_date = {r["date"]: r.get("close") for r in nrow}
            pcut = tail.get("cutoff")
            rec["basis_near_minus_panel"] = (
                (nb_by_date.get(pcut) - pc) if (pcut in nb_by_date and pc is not None)
                else None)
            pairs_built += 1
            for r in sr:
                csv_rows.append({"variety": v, "near": near, "far": far, **r})
        else:
            rec["near"] = None
            rec["far"] = None
            rec["note"] = ("no near contract meeting OI floor in candidate "
                           "window -- honest empty face" if alive_syms else
                           "no alive contract in candidate window")
        face["varieties"][v] = rec
    face["summary"] = {"pairs_built": pairs_built, "requests": req_total,
                      "spread_rows": len(csv_rows),
                      "panel_cutoff": max((t.get("cutoff") or "") for t in
                                          face["panel"].values()) or None}
    os.makedirs(OUT_DIR, exist_ok=True)
    atomic_write(FACE_JSON, json.dumps(face, ensure_ascii=True, indent=1))
    atomic_write(SPREADS_CSV, spreads_csv_text(csv_rows))
    print(f"face -> {FACE_JSON}")
    print(f"spreads -> {SPREADS_CSV} ({len(csv_rows)} rows)")
    for v in VARIETIES:
        rec = face["varieties"][v]
        if rec.get("near"):
            st = rec["series"]
            thin = " [far_thin]" if rec.get("far_thin") else ""
            print(f"  {v}: {rec['near']}/{rec['far']}{thin} n={st['n']} "
                  f"latest_spread={st['latest_spread']:.4g} "
                  f"ratio={st['latest_ratio']:.6g} z={st['z_latest'] if st['z_latest'] is None else round(st['z_latest'], 3)}")
        else:
            print(f"  {v}: no pair ({rec.get('note', '')})")
    if pairs_built == 0:
        print("MECHANISM FAULT: zero pairs built")
        return 2
    return 0


# ----------------------------------------------------------------- selftest


def _selftest() -> int:
    now = dt.datetime(2026, 10, 10, 10, 0)
    # S1 candidate generation: CFFEX index rule (cur, next, +2 quarter months)
    c = candidate_contracts(now, "IF")
    assert c == ["IF2610", "IF2611", "IF2612", "IF2703"], c
    # December edge: cur=12 -> next=next-year 01
    c2 = candidate_contracts(dt.datetime(2026, 12, 3), "IF")
    assert c2 == ["IF2612", "IF2701", "IF2703", "IF2706"], c2
    # S2 treasury quarter months
    t = candidate_contracts(now, "T")
    assert t == ["T2612", "T2703", "T2706", "T2709"], t
    # S3 commodity rolling months
    rb = candidate_contracts(now, "RB")
    assert rb == ["RB2610", "RB2611", "RB2612", "RB2701", "RB2702",
                  "RB2703", "RB2704", "RB2705"], rb
    # S4 payload parse: jsonp wrapper, empty array, key mapping p->oi s->settle
    arr = parse_payload('var _RB2610=([{"d":"2026-10-09","o":"3010.0",'
                        '"h":"3010.0","l":"2986.0","c":"3005.0","v":"3450",'
                        '"p":"6870","s":"2998.0"}])')
    rows = parse_rows(arr)
    assert len(rows) == 1 and rows[0]["oi"] == 6870.0 and rows[0]["settle"] == 2998.0 \
        and rows[0]["open"] == 3010.0 and rows[0]["volume"] == 3450.0
    assert parse_rows(parse_payload("var _X=([])")) == []
    assert parse_payload("garbage no array") == []
    # settle "0.000" -> None (CFFEX zero face)
    z = parse_rows([{"d": "2026-10-09", "o": "1", "h": "2", "l": "0.5", "c": "1.5",
                     "v": "10", "p": "5", "s": "0.000"}])
    assert z[0]["settle"] is None and z[0]["oi"] == 5.0
    # S5 is_alive: freshness + OI>0
    fresh = parse_rows([{"d": "2026-10-08", "o": "1", "h": "1", "l": "1", "c": "1",
                         "v": "1", "p": "100", "s": "1"}])
    assert is_alive(fresh, now) and not is_alive(fresh, dt.datetime(2026, 12, 1))
    stale = parse_rows([{"d": "2026-08-01", "o": "1", "h": "1", "l": "1", "c": "1",
                          "v": "1", "p": "100", "s": "1"}])
    assert not is_alive(stale, now)  # > 20 days old
    dead_oi = parse_rows([{"d": "2026-10-08", "o": "1", "h": "1", "l": "1", "c": "1",
                            "v": "1", "p": "0", "s": "1"}])
    assert not is_alive(dead_oi, now)
    # S6 pick_pair: expiring front month below OI floor -> skipped
    def mk(d, oi, c="3000.0"):
        return parse_rows([{"d": d, "o": c, "h": c, "l": c, "c": c,
                            "v": "1", "p": str(oi), "s": c}])
    got = {"RB2610": mk("2026-10-08", 69), "RB2601": mk("2026-10-08", 1670000),
           "RB2605": mk("2026-10-08", 900000)}
    near, far, nrow, frow, alive, thin = pick_pair(got, now)
    assert near == "RB2601" and far == "RB2605" and not thin \
        and alive == ["RB2601", "RB2605", "RB2610"]
    # S7 pick_pair: single qualified near, no later alive far -> honest None
    got2 = {"RB2610": mk("2026-10-08", 69), "RB2701": mk("2026-10-08", 1670000)}
    near2, far2, _, _, _, thin2 = pick_pair(got2, now)
    assert near2 is None and far2 is None and not thin2
    # S7b far_thin fallback: only near meets floor, next alive expiry = thin far
    got3 = {"T2612": mk("2026-10-08", 377917), "T2703": mk("2026-10-08", 18601),
            "T2706": mk("2026-10-08", 1116)}
    near3, far3, _, _, _, thin3 = pick_pair(got3, now)
    assert near3 == "T2612" and far3 == "T2703" and thin3
    # S8 spread join + stats math
    n_rows = parse_rows([{"d": "2026-10-07", "o": "10", "h": "10", "l": "10", "c": "10",
                          "v": "1", "p": "9", "s": "10"},
                         {"d": "2026-10-08", "o": "11", "h": "11", "l": "11", "c": "11",
                          "v": "1", "p": "9", "s": "11"},
                         {"d": "2026-10-09", "o": "12", "h": "12", "l": "12", "c": "12",
                          "v": "1", "p": "9", "s": "12"}])
    f_rows = parse_rows([{"d": "2026-10-06", "o": "20", "h": "20", "l": "20", "c": "20",
                          "v": "1", "p": "9", "s": "20"},
                         {"d": "2026-10-08", "o": "22", "h": "22", "l": "22", "c": "22",
                          "v": "1", "p": "9", "s": "22"},
                         {"d": "2026-10-09", "o": "24", "h": "24", "l": "24", "c": "24",
                          "v": "1", "p": "9", "s": "24"}])
    sr = spread_rows(n_rows, f_rows)
    assert [r["date"] for r in sr] == ["2026-10-08", "2026-10-09"]
    assert sr[0]["spread"] == 11.0 and sr[0]["ratio"] == 2.0
    st = series_stats(sr)
    assert st["n"] == 2 and st["mean"] == 11.5 and st["latest_spread"] == 12.0 \
        and abs(st["std"] - 0.5 * 2 ** 0.5) < 1e-9
    assert abs(st["z_latest"] - 1 / 2 ** 0.5) < 1e-9  # (12-11.5)/std
    # S9 empty series honest
    assert series_stats([]) == {"n": 0}
    # S10 dominant_guess + basis math
    alive_rows = {"RB2601": n_rows, "RB2612": f_rows}
    assert dominant_guess(alive_rows, 12.0) == "RB2601"
    assert dominant_guess(alive_rows, None) is None
    nb = {r["date"]: r.get("close") for r in n_rows}
    assert nb.get("2026-10-08") - 11.5 == -0.5
    # S11 csv text roundtrip
    csv_text = spreads_csv_text([{"variety": "RB", "near": "RB2601",
                                  "far": "RB2605", "date": "2026-10-08",
                                  "near_close": 3500.0, "far_close": 3511.0,
                                  "spread": 11.0, "ratio": 1.0031428571}])
    assert csv_text.splitlines()[0] == ",".join(SPREAD_COLS)
    assert "RB,RB2601,RB2605,2026-10-08,3500,3511,11,1.003142857" in csv_text
    # S12 panel tail on a temp dir
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "RB.csv")
        atomic_write(p, "date,open,high,low,close,volume,oi,settle\n"
                        "2026-10-08,3093,3094,3000,3080,770052,1686678,3080\n")
        tail = panel_tail("RB", data_dir=td)
        assert tail["cutoff"] == "2026-10-08" and tail["close"] == 3080.0 \
            and tail["oi"] == 1686678.0 and tail["rows"] == 1
        assert panel_tail("XX", data_dir=td)["cutoff"] is None
    # S14 contract sort across year boundary
    assert contract_sort_key("RB2612") < contract_sort_key("RB2701")
    print("selftest: 14/14 PASS")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return _selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())
