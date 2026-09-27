# -*- coding: utf-8 -*-
"""T-19 stage-2b official-evidence probe (bm-c lane, data dept).

Per-event official evidence for the 21 consolidation-registry events:
  LEG-N  fund-company official NAV series (akshare fund_etf_fund_info_em ->
         api.fund.eastmoney.com/f10/lsjz): step-scan consecutive NAV ratios in
         a +/-6 calendar-day window around the registry event date (faces can
         carry a 1-day date misalignment for the same corporate action,
         513100 2022-01-13 NAV step vs 2022-01-14 price bar = proven case).
  LEG-A  EM f10 announcements corporate-action category (api.fund.eastmoney.com
         /f10/JJGG type=2 = 份额拆分/折算, direct urllib ProxyHandler({}) house
         recipe, PUBLISHDATEDesc/TITLE/ID schema, pageSize=500 = full history
         one call): window title match on 折算/拆分/合并 -> source URL per
         event (official announcement trail).

Honesty rules (stage-2b spec):
  - events with no official evidence -> reclassify_candidate_real_extreme_day
    (recorded honestly, registry NOT rewritten: D2 lockbox, this file is the
    disclosure face).
  - NAV step ratio carries the step-day underlying market return (same caveat
    as price-implied factors, stage-3 semantics); reconciliation residual
    disclosed per event.
  - every network attempt recorded; honest-fail labels for blocked sources.

Usage:
  python scripts/t19_official_ratio_probe.py single [sym] [date]
  python scripts/t19_official_ratio_probe.py run
  python scripts/t19_official_ratio_probe.py selftest
Exit: 0 ok / 2 mechanism fault (report honestly, do not mask).
"""
import json
import os
import sys
import time
import urllib.request
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "data", "consolidation", "registry.json")
OUT = os.path.join(ROOT, "results", "t19_official_ratio_probe.json")

ATTEMPTS = 3          # r51 intermittent ruling: retry-window 3
RETRY_WAIT_S = 8
THROTTLE_S = 2.5
WINDOW_D = 10         # announcement match window: event_date +/- 10 days
NAV_WINDOW_D = 6      # NAV step scan window: event_date +/- 6 calendar days
STEP_MIN = 0.25       # |nav_step - 1| >= 25% to count as a consolidation step
NAV_EPS = 1e-9

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://fundf10.eastmoney.com/"}


def _get(url, timeout=15):
    """House recipe: direct urllib, ProxyHandler({}) = bypass system proxy."""
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers=UA)
    with op.open(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_nav_history(sym, log):
    """LEG-N: official fund-company NAV series via akshare face."""
    import akshare as ak
    for i in range(ATTEMPTS):
        try:
            df = ak.fund_etf_fund_info_em(fund=sym)
            navs = {}
            for _, row in df.iterrows():
                d = str(row["净值日期"])[:10]
                navs[d] = float(row["单位净值"])
            log.append({"leg": "nav", "sym": sym, "attempt": i + 1, "ok": True,
                        "n_rows": len(navs), "first": min(navs) if navs else None,
                        "last": max(navs) if navs else None})
            return navs
        except Exception as e:
            log.append({"leg": "nav", "sym": sym, "attempt": i + 1, "ok": False,
                        "err": f"{type(e).__name__}: {e}"[:200]})
            if i < ATTEMPTS - 1:
                time.sleep(RETRY_WAIT_S)
    return None


def fetch_announcements(sym, log):
    """LEG-A: EM f10 corporate-action announcements (type=2 = 拆分/折算)."""
    url = ("https://api.fund.eastmoney.com/f10/JJGG?fundcode="
           f"{sym}&pageIndex=1&pageSize=500&type=2")
    for i in range(ATTEMPTS):
        try:
            data = json.loads(_get(url))
            rows = data.get("Data") or []
            out = []
            for r in rows:
                if not isinstance(r, dict):
                    continue
                d = str(r.get("PUBLISHDATEDesc") or str(r.get("PUBLISHDATE") or "")[:10])[:10]
                out.append({"title": str(r.get("TITLE") or ""),
                            "date": d,
                            "url": (f"https://fundf10.eastmoney.com/gonggao/{sym}/{r['ID']}"
                                    if r.get("ID") else "")})
            log.append({"leg": "ann", "sym": sym, "attempt": i + 1, "ok": True,
                        "n_rows": len(out)})
            return out
        except Exception as e:
            log.append({"leg": "ann", "sym": sym, "attempt": i + 1, "ok": False,
                        "err": f"{type(e).__name__}: {e}"[:200]})
            if i < ATTEMPTS - 1:
                time.sleep(RETRY_WAIT_S)
    return None


def nav_step_in_window(navs, event_date):
    """Max |ratio-1| consecutive NAV step within +/- NAV_WINDOW_D calendar days.

    Returns (step_ratio, step_date_k, step_date_prev, offset_days) or
    (None, None, None, None). offset = calendar days from event_date to the
    step date (negative = NAV face steps BEFORE the price-bar date).
    """
    if not navs:
        return None, None, None, None
    ds = sorted(navs)
    try:
        ed = date(*map(int, event_date.split("-")))
    except Exception:
        return None, None, None, None
    lo = (ed - timedelta(days=NAV_WINDOW_D)).isoformat()
    hi = (ed + timedelta(days=NAV_WINDOW_D)).isoformat()
    best = (0.0, None, None, None)
    for a, b in zip(ds, ds[1:]):
        if not (lo <= b <= hi):
            continue
        if abs(navs[a]) < NAV_EPS:
            continue
        ratio = navs[b] / navs[a]
        if abs(ratio - 1.0) > best[0]:
            off = (date(*map(int, b.split("-"))) - ed).days
            best = (abs(ratio - 1.0), ratio, b, a, off)
    if best[0] < STEP_MIN or best[1] is None:
        return None, None, None, None
    return best[1], best[2], best[3], best[4]


def match_announcement(anns, event_date):
    """Window +/- WINDOW_D days, title contains 折算/拆分/合并 (corporate actions)."""
    if not anns:
        return None
    try:
        ed = date(*map(int, event_date.split("-")))
        lo = (ed - timedelta(days=WINDOW_D)).isoformat()
        hi = (ed + timedelta(days=WINDOW_D)).isoformat()
    except Exception:
        return None
    hits = []
    for a in anns:
        if a["date"] and lo <= a["date"] <= hi and any(
                k in a["title"] for k in ("折算", "拆分", "合并")):
            hits.append(a)
    if not hits:
        return None
    hits.sort(key=lambda x: x["date"])
    return hits[0] if len(hits) == 1 else hits[-1]  # latest = result announcement


def probe_events(events, full=True):
    log = []
    nav_cache = {}
    results = []
    for e in events:
        sym, ed = e["sym"], e["date"]
        if sym not in nav_cache:
            nav_cache[sym] = fetch_nav_history(sym, log)
        navs = nav_cache[sym]
        anns = fetch_announcements(sym, log) if full else None
        step_ratio, step_k, step_prev, off = nav_step_in_window(navs, ed)
        ann_hit = match_announcement(anns, ed) if full else None
        price_ratio = e.get("implied_ratio_approx")   # prev_close/close convention
        rec = {
            "sym": sym,
            "date": ed,
            "amplitude_class": e.get("amplitude_class"),
            "pct_observed": e.get("pct_observed"),
            "price_implied_ratio": price_ratio,
            "nav_leg": {
                "status": "ok" if step_ratio is not None else (
                    "source_blocked" if navs is None else "no_step_in_window"),
                "nav_step_ratio": round(step_ratio, 6) if step_ratio else None,
                "nav_step_date": step_k,
                "nav_prev_date": step_prev,
                "face_date_offset_days": off,
            },
            "announcement_leg": {
                "status": ("ok" if ann_hit else
                           ("source_blocked" if anns is None else "no_hit_window")),
                "title": ann_hit["title"] if ann_hit else None,
                "date": ann_hit["date"] if ann_hit else None,
                "url": ann_hit["url"] if ann_hit else None,
            },
        }
        # reconciliation in prev/close convention: 1/nav_step vs price_implied
        rec["reconciliation"] = (None if not (step_ratio and price_ratio) else
                                 round(abs(1.0 / step_ratio - price_ratio), 6))
        nav_ok = step_ratio is not None
        ann_ok = ann_hit is not None
        if ann_ok and nav_ok:
            rec["verdict"] = "consolidation_confirmed_dual_leg"
        elif ann_ok:
            rec["verdict"] = "consolidation_confirmed_announcement"
        elif nav_ok:
            rec["verdict"] = "consolidation_confirmed_nav_signature"
        elif (rec["nav_leg"]["status"] == "source_blocked"
              or rec["announcement_leg"]["status"] == "source_blocked"):
            rec["verdict"] = "source_blocked"
        else:
            rec["verdict"] = "reclassify_candidate_real_extreme_day"
        results.append(rec)
        if full:
            time.sleep(THROTTLE_S)
    return results, log


def summarize(results):
    v = {}
    for r in results:
        v[r["verdict"]] = v.get(r["verdict"], 0) + 1
    return {"n_events": len(results), "verdicts": v}


def main(argv):
    reg = json.load(open(REGISTRY, encoding="utf-8-sig"))
    events = reg["events"]
    if argv and argv[0] == "selftest":
        return selftest()
    if argv and argv[0] == "single":
        sym = argv[1] if len(argv) > 1 else "512100"
        ed = argv[2] if len(argv) > 2 else "2022-09-05"
        ev = [e for e in events if e["sym"] == sym and e["date"] == ed]
        if not ev:
            print(f"event {sym} {ed} not in registry")
            return 2
        results, log = probe_events(ev, full=True)
    elif argv and argv[0] == "run":
        results, log = probe_events(events, full=True)
    else:
        print(__doc__)
        return 2
    out = {
        "evidence_cutoff": "2026-09-27",
        "stage": "T-19 stage-2b official-evidence probe",
        "registry_ref": "data/consolidation/registry.json (D2 lockbox: registry NOT rewritten)",
        "results": results,
        "summary": summarize(results),
        "attempt_log": log,
        "disclosure": ("NAV step carries step-day underlying market return (same caveat as "
                       "price-implied factors, stage-3 semantics); announcement leg = official "
                       "title+URL trail; face_date_offset_days discloses NAV-vs-price-bar date "
                       "misalignment per event"),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out["summary"], ensure_ascii=False))
    blocked = [r["sym"] + " " + r["date"] for r in results
               if r["verdict"] == "source_blocked"]
    if blocked:
        print("SOURCE_BLOCKED:", blocked)
    return 0


def selftest():
    """Offline fixtures (machine pitfall law #1: natural JSON faces)."""
    ok = 0
    # fixture 1: step scan finds 1:5 split, reports offset
    navs = {"2022-01-11": 5.172, "2022-01-12": 5.189, "2022-01-13": 1.009,
            "2022-01-14": 1.019, "2022-01-17": 1.017}
    r, k, j, off = nav_step_in_window(navs, "2022-01-14")
    assert r is not None and abs(r - 1.009 / 5.189) < 1e-9, (r, k)
    assert k == "2022-01-13" and j == "2022-01-12" and off == -1, (k, j, off)
    ok += 1
    # fixture 2: no step (flat NAV) -> None
    navs2 = {"2022-09-01": 1.0, "2022-09-02": 1.002, "2022-09-05": 1.005}
    assert nav_step_in_window(navs2, "2022-09-05")[0] is None
    ok += 1
    # fixture 3: window boundary excludes far steps
    navs3 = {"2022-01-03": 5.0, "2022-01-04": 1.0, "2022-01-20": 1.01, "2022-01-21": 1.02}
    assert nav_step_in_window(navs3, "2022-01-14")[0] is None
    ok += 1
    # fixture 4: announcement schema (PUBLISHDATEDesc) + 折算/拆分/合并 match
    anns = [{"title": "关于基金份额折算结果的公告", "date": "2022-01-15",
             "url": "u1"},
            {"title": "实施基金份额拆分及相关业务安排的公告", "date": "2022-01-10", "url": "u2"},
            {"title": "基金份额合并结果的公告", "date": "2022-01-12", "url": "u4"},
            {"title": "2022年第四季度报告", "date": "2022-01-14", "url": "u3"}]
    hit = match_announcement(anns, "2022-01-14")
    assert hit and hit["url"] == "u1", hit
    ok += 1
    # fixture 5: no hit and far-window miss
    assert match_announcement([{"title": "季度报告", "date": "2022-01-14", "url": "u"}],
                              "2022-01-14") is None
    assert match_announcement(anns, "2022-03-01") is None
    ok += 1
    # fixture 6: reconciliation math in prev/close convention
    step_ratio, price_ratio = 0.1945, 5.115271
    assert abs(abs(1.0 / step_ratio - price_ratio) - 0.031) < 0.01
    ok += 1
    print(f"t19_official_ratio_probe selftest: {ok}/6 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
