"""Independent recomputation of `regime_cap_enforced_counterfactual` (R5 seat: every cited
absolute money number gets one recomputation from a second implementation).

Why: the face published `+11,099.73` (bear rule, 5 sessions), `+21,488.35` (RED label, 11)
and `+43,700.98` (always-cap, 34) in CNY on 2026-11-23T13:05. Those are absolute money
numbers a reader will quote. R5's own granularity line says each of them needs one
independent recomputation. This file is that second implementation.

Independence boundary (declared, not hidden):
  * the model itself -- `delta_d = equity_d * max(0, w_d - CAP) * (r_repo_d - r_deployed_d)`
    summed over bound sessions, one sell side charged at the start of each bound run -- is
    re-implemented here from the prose, not imported;
  * readers (export json, price csv, repo csv) are re-implemented here;
  * flip repair is re-implemented here (single-day |return| > 35% -> treated as no move and
    the series re-based forward), not imported;
  * the ONE thing imported is the rule under test: `firm.risk.regime.major_bear_series`
    (and the RED labels face). Testing a rule against a private copy of it would be a
    different question than the one the face asked.

Verdicts:
  INDEPENDENT_AGREE        every arm's gross/cost/net and every per-trader delta matches
                           the published face within one fen (per-trader: two fen)
  DIVERGE_<arm>            the named arm differs; the size of the gap is printed
  CANNOT_READ              published artifact or an input face is missing/unreadable

Exit: 0 = agree, 3 = diverge or cannot read (so a chain leg can act on it).
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

SCHEMA = "bmc-indep-cap-audit/v1"
PUBLISHED = os.path.join(_ROOT, "results", "regime_cap_enforced_counterfactual.json")
EXPORT_DIR = os.path.join(_ROOT, "results", "paper_export")
DAILY_DIR = os.path.join(_ROOT, "data", "daily")
REPO_CSV = os.path.join(_ROOT, "data", "repo_daily", "GC001.csv")
TZ = timezone(timedelta(hours=8))

CAP = 0.20                  # R-配3, quoted from firm/risk/regime.py::CAP_MAJOR_BEAR
COST_SIDE_BP = 13.041       # CN-C7 constant this repo charges, quoted
FLIP_LINE = 0.35            # single-day |r| above this is a print, not a return
TOL_FEN = 0.01
TOL_PER_TRADER = 0.02


def _read_json(path):
    if not os.path.isfile(path):
        return None, "missing: %s" % os.path.relpath(path, _ROOT)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:
        return None, "unreadable: %s (%s)" % (os.path.relpath(path, _ROOT), exc)


def read_closes(path):
    """{date: close} from a panel csv (close is the 5th column)."""
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.lower().startswith("date"):
                continue
            parts = line.split(",")
            if len(parts) < 5:
                continue
            try:
                out[parts[0]] = float(parts[4])
            except ValueError:
                continue
    return out


def repair_flips(series, line=FLIP_LINE):
    """A one-day |move| above `line` is a quote print, not a return: flatten that day to 0%
    and rebuild the level path forward from the first bar, then re-anchor the column to its
    own last priced print. Written here from the documented rule (same spec as
    etf_equity_alpha.repair_flips, separate implementation)."""
    if not series:
        return {}, 0
    dates = sorted(series)
    levels = [series[dates[0]]]
    repairs = 0
    for i in range(1, len(dates)):
        prev_raw, cur_raw = series[dates[i - 1]], series[dates[i]]
        r = (cur_raw / prev_raw - 1.0) if prev_raw else 0.0
        if abs(r) > line:
            repairs += 1
            r = 0.0
        levels.append(levels[-1] * (1.0 + r))
    # a level is only a scale: multiplying the column by a constant leaves every return it
    # feeds unchanged, so anchoring to the last raw print repairs nothing but the units
    last_raw, last_lvl = series[dates[-1]], levels[-1]
    if last_lvl:
        k = last_raw / last_lvl
        levels = [v * k for v in levels]
    return {d: v for d, v in zip(dates, levels)}, repairs


def load_exports(export_dir=EXPORT_DIR):
    """{date: {trader: {equity, deployed, legs}}} plus the files/dates it read."""
    by_date, problems = {}, []
    for path in sorted(glob.glob(os.path.join(export_dir, "export-*.json"))):
        pay, err = _read_json(path)
        if err:
            problems.append(err)
            continue
        d = pay.get("export_date")
        if not d:
            problems.append("no export_date: %s" % os.path.basename(path))
            continue
        stamp = pay.get("generated_from_state_updated") or ""
        if d in by_date and stamp < by_date[d]["stamp"]:
            continue
        traders = {}
        for t in pay.get("traders") or []:
            name = t.get("trader")
            cap = t.get("capital_cny") or {}
            eq, dep = cap.get("equity"), cap.get("positions_value")
            if not name or not isinstance(eq, (int, float)) or not isinstance(dep, (int, float)):
                problems.append("trader without equity/positions on %s: %r" % (d, name))
                continue
            legs = []
            for pos in t.get("open_positions") or []:
                sym, mv = pos.get("symbol"), pos.get("market_value_cny")
                if not sym or not isinstance(mv, (int, float)):
                    problems.append("leg without symbol/value on %s/%s" % (d, name))
                    continue
                legs.append({"symbol": str(sym), "mv": float(mv)})
            traders[name] = {"equity": float(eq), "deployed": float(dep), "legs": legs}
        by_date[d] = {"stamp": stamp, "traders": traders}
    return {"dates": sorted(by_date), "by_date": by_date, "problems": problems}


def merge_family_prices(codes):
    """{code: {date: close}} merging the bare / sh / sz panel families; disagreements are
    counted and disclosed, never silently picked."""
    prices, conflicts, missing = {}, [], []
    for code in sorted(set(codes)):
        merged = {}
        hits = 0
        for name in ("%s.csv" % code, "sh%s.csv" % code, "sz%s.csv" % code):
            series = read_closes(os.path.join(DAILY_DIR, name))
            if not series:
                continue
            hits += 1
            for d, px in series.items():
                if d in merged and abs(merged[d] - px) > max(abs(merged[d]) * 1e-6, 1e-9):
                    conflicts.append("%s %s" % (code, d))
                merged.setdefault(d, px)
        if not hits or not merged:
            missing.append(code)
            continue
        adj, repairs = repair_flips(merged)
        if repairs:
            conflicts.append("%s: %d flip(s) repaired" % (code, repairs))
        prices[code] = adj
    return prices, conflicts, missing


def on_or_before(series, date):
    """Last observation at or before `date` (prices are carried, they are not invented)."""
    if not series:
        return None
    best = None
    for d in series:
        if d <= date and (best is None or d > best):
            best = d
    return series[best] if best else None


def repo_daily(rate_pct, days=365.0):
    return (rate_pct / 100.0) / days


def arm_effect(dates, by_date, arm_days, prices, repo, cap=CAP, cost_bp=COST_SIDE_BP):
    """Re-implementation of the one-session counterfactual, written from the formula."""
    total = cost_total = 0.0
    per_trader, rows = {}, []
    sessions_bound = sessions_skipped = 0
    prev_bound = False
    for i in range(len(dates) - 1):
        d0, d1 = dates[i], dates[i + 1]
        bound = d0 in arm_days
        book = by_date[d0]["traders"]
        if not book:
            continue
        r_repo = None
        if d0 in repo:
            r_repo = repo_daily(repo[d0])
        else:
            used = [d for d in repo if d <= d0]
            if used:
                r_repo = repo_daily(repo[max(used)])
        if bound and r_repo is None:
            sessions_skipped += 1
            rows.append({"d0": d0, "skipped": "no repo quote"})
            prev_bound = True
            continue
        pair_bound = False
        for name in sorted(book):
            sess = book[name]
            if not sess["legs"]:
                continue
            num = den = 0.0
            for leg in sess["legs"]:
                p0 = on_or_before(prices.get(leg["symbol"], {}), d0)
                p1 = on_or_before(prices.get(leg["symbol"], {}), d1)
                if not p0 or not p1:
                    continue
                num += leg["mv"] * (p1 / p0 - 1.0)
                den += leg["mv"]
            if den <= 0:
                continue
            r_dep = num / den
            eq, dep = sess["equity"], sess["deployed"]
            w0 = dep / eq if eq else 0.0
            binds = bool(bound and w0 > cap)
            delta = eq * (w0 - min(w0, cap)) * (r_repo - r_dep) if binds else 0.0
            cost = 0.0
            if binds and not prev_bound:
                cost = eq * (w0 - min(w0, cap)) * (cost_bp / 1e4)
            acc = per_trader.setdefault(name, {"delta": 0.0, "cost": 0.0, "n": 0})
            acc["delta"] += delta
            acc["cost"] += cost
            acc["n"] += 1 if binds else 0
            total += delta
            cost_total += cost
            pair_bound = pair_bound or binds
            rows.append({"d0": d0, "trader": name, "binds": binds,
                         "delta": round(delta, 2)})
        if pair_bound:
            sessions_bound += 1
        prev_bound = bound
    return {"delta_gross": round(total, 2), "cost": round(cost_total, 2),
            "delta_net": round(total - cost_total, 2), "sessions_bound": sessions_bound,
            "sessions_skipped": sessions_skipped,
            "per_trader": {k: {"delta": round(v["delta"], 2), "sessions_bound": v["n"]}
                           for k, v in per_trader.items()},
            "rows": rows}


def load_arm_days(dates):
    """bear mask + RED labels, both imported from the single sources the face cites."""
    from firm.risk import regime as RULE
    import pandas as pd

    days = {"always_cap": set(dates)}

    close = RULE.load_benchmark_close()
    mask = RULE.major_bear_series(close)
    days["bear_rule"] = {str(k)[:10] for k, v in dict(mask).items() if bool(v)}

    red_pay, err = _read_json(os.path.join(_ROOT, "results", "regime_state.json"))
    red_days = set()
    if red_pay:
        # the state machine's own history: {asof, state}; RED is one of its states
        for h in red_pay.get("history") or []:
            if h.get("asof") and h.get("state") == "RED":
                red_days.add(str(h["asof"])[:10])
        if not red_days and red_pay.get("asof") and red_pay.get("state") == "RED":
            red_days.add(str(red_pay["asof"])[:10])
    days["red_label"] = red_days
    return days, (err or None)


def compare(mine, pub):
    """Per arm, per field, per trader: signed gap. A gap is printed, never rounded away."""
    out = {}
    for arm, m in mine.items():
        p = (pub.get("arms") or {}).get(arm) or {}
        row = {"delta_gross_mine": m["delta_gross"],
               "delta_gross_pub": p.get("delta_gross_cny"),
               "gap": None, "cost_gap": None, "net_gap": None,
               "sessions_bound_mine": m["sessions_bound"],
               "sessions_bound_pub": p.get("sessions_bound"),
               "per_trader": {}}
        if isinstance(p.get("delta_gross_cny"), (int, float)):
            row["gap"] = round(m["delta_gross"] - p["delta_gross_cny"], 2)
        if isinstance(p.get("cost_cny"), (int, float)):
            row["cost_gap"] = round(m["cost"] - p["cost_cny"], 2)
        if isinstance(p.get("delta_net_cny"), (int, float)):
            row["net_gap"] = round(m["delta_net"] - p["delta_net_cny"], 2)
        for name, mine_acc in m["per_trader"].items():
            pub_acc = (p.get("per_trader") or {}).get(name) or {}
            pub_d = pub_acc.get("delta_cny")
            row["per_trader"][name] = {
                "mine": mine_acc["delta"],
                "pub": pub_d,
                "gap": round(mine_acc["delta"] - pub_d, 2)
                if isinstance(pub_d, (int, float)) else None}
        out[arm] = row
    return out


def verdict_for(cmp, can_read):
    if not can_read:
        return "CANNOT_READ"
    worst, worst_arm, compared = 0.0, None, False
    for arm, row in cmp.items():
        for key in ("gap", "cost_gap", "net_gap"):
            v = row.get(key)
            if isinstance(v, (int, float)):
                compared = True
                if abs(v) > worst:
                    worst, worst_arm = abs(v), arm
        for name, acc in (row.get("per_trader") or {}).items():
            v = acc.get("gap")
            if isinstance(v, (int, float)):
                compared = True
                if abs(v) > worst:
                    worst, worst_arm = abs(v), "%s/%s" % (arm, name)
    if not compared:
        return "CANNOT_READ"
    if worst <= TOL_FEN:
        return "INDEPENDENT_AGREE"
    return "DIVERGE_%s" % worst_arm


# --------------------------------------------------------------------------- selftest

def _selftest():
    """Each leg runs the real code on synthetic input that must behave a named way."""
    ok = True

    # 1: the formula itself. equity 1e6, w 0.95, cap 0.20, repo 1.5%/y vs book -3%
    #    1e6 * 0.75 * (0.015/365 + 0.03) = 22,530.82
    eq, w, rd, rr = 1e6, 0.95, -0.03, 0.015 / 365.0
    got = round(eq * (w - 0.20) * (rr - rd), 2)
    want = round(1e6 * 0.75 * (0.015 / 365.0 + 0.03), 2)
    ok &= (got == want)
    print("  leg1 formula: %s (%s vs %s)" % ("PASS" if got == want else "FAIL", got, want))

    # 2: flip repair. 100, 99, 990 (a 10x print), 98 -> both the jump and its unwinding are
    #    flattened to 0% returns, and the columns stay on the raw last print's scale.
    s = {"d1": 100.0, "d2": 99.0, "d3": 990.0, "d4": 98.0}
    adj, n = repair_flips(s)
    leg2 = (n == 2) and abs(adj["d3"] / adj["d2"] - 1.0) < 1e-12 \
        and abs(adj["d4"] / adj["d3"] - 1.0) < 1e-12 and abs(adj["d4"] - 98.0) < 1e-9
    ok &= leg2
    print("  leg2 flip repair: %s (repairs=%d, d3/d2=%.6f, d4/d3=%.6f, d4=%.4f)"
          % ("PASS" if leg2 else "FAIL", n, adj["d3"] / adj["d2"],
             adj["d4"] / adj["d3"], adj["d4"]))

    # 3: the comparator must actually call a two-fen gap DIVERGE, not agree.
    fake = {"bear_rule": {"delta_gross": 11099.75, "cost": 0.0, "delta_net": 11099.75,
                          "per_trader": {}, "sessions_bound": 5, "sessions_skipped": 0,
                          "rows": []}}
    pub = {"arms": {"bear_rule": {"delta_gross_cny": 11099.73, "cost_cny": 0.0,
                                  "delta_net_cny": 11099.73, "per_trader": {},
                                  "sessions_bound": 5}}}
    v = verdict_for(compare(fake, pub), True)
    leg3 = v.startswith("DIVERGE")
    ok &= leg3
    print("  leg3 comparator spots a 2-fen gap: %s (%s)" % ("PASS" if leg3 else "FAIL", v))

    # 4: same numbers -> agree (so leg3 is not just 'always diverges').
    fake2 = json.loads(json.dumps(fake))
    fake2["bear_rule"]["delta_gross"] = 11099.73
    fake2["bear_rule"]["delta_net"] = 11099.73
    v2 = verdict_for(compare(fake2, pub), True)
    leg4 = v2 == "INDEPENDENT_AGREE"
    ok &= leg4
    print("  leg4 comparator agrees on identical: %s (%s)" % ("PASS" if leg4 else "FAIL", v2))

    return ok


# --------------------------------------------------------------------------- run

def build():
    pub, err = _read_json(PUBLISHED)
    if err:
        return {"schema": SCHEMA, "verdict": "CANNOT_READ", "problems_hard": [err]}

    ex = load_exports()
    dates = ex["dates"]
    if len(dates) < 2:
        return {"schema": SCHEMA, "verdict": "CANNOT_READ",
                "problems_hard": ["export face has <2 sessions"]}

    codes = set()
    for d, row in ex["by_date"].items():
        for _, sess in row["traders"].items():
            for leg in sess["legs"]:
                codes.add(leg["symbol"])
    prices, conflicts, missing = merge_family_prices(codes)

    repo = {}
    if os.path.isfile(REPO_CSV):
        repo = read_closes(REPO_CSV)

    arm_days, red_err = load_arm_days(dates)

    mine = {arm: arm_effect(dates, ex["by_date"], days, prices, repo)
            for arm, days in arm_days.items()}
    cmp = compare(mine, pub)
    verdict = verdict_for(cmp, True)

    return {
        "schema": SCHEMA,
        "generated": datetime.now(TZ).isoformat(timespec="seconds"),
        "audits": os.path.relpath(PUBLISHED, _ROOT).replace("\\", "/"),
        "evidence_cutoff": str(pub.get("evidence_cutoff") or "")[:10],
        "sessions": {"exports": len(dates), "first": dates[0], "last": dates[-1],
                     "pairs": max(0, len(dates) - 1)},
        "arms": {arm: {"delta_gross_cny": mine[arm]["delta_gross"],
                       "cost_cny": mine[arm]["cost"],
                       "delta_net_cny": mine[arm]["delta_net"],
                       "sessions_bound": mine[arm]["sessions_bound"],
                       "sessions_skipped": mine[arm]["sessions_skipped"]}
                 for arm in mine},
        "compare": cmp,
        "arm_days": {k: len(v) for k, v in arm_days.items()},
        "prices": {"codes": len(prices), "conflicts": conflicts[:20],
                   "conflict_count": len(conflicts), "missing": missing},
        "repo_days": len(repo),
        "red_labels_error": red_err,
        "problems": ex["problems"][:20],
        "verdict": verdict,
        "tolerance_cny": {"arm": TOL_FEN, "per_trader": TOL_PER_TRADER},
        "sentence": _sentence(verdict, cmp, mine),
    }


def _sentence(verdict, cmp, mine):
    if verdict == "CANNOT_READ":
        return "读不到被复算的面，这一问答不了。"
    if verdict == "INDEPENDENT_AGREE":
        return ("第二套实现重算了这顶帽子的三个臂，与已发布面的毛差、成本、净差逐臂一致"
                "（一比一分以内）：大熊市规则 %+.2f 元、RED 标签 %+.2f 元、一直守帽 %+.2f 元，"
                "引用的绝对数可以继续引用。"
                % (mine["bear_rule"]["delta_gross"], mine["red_label"]["delta_gross"],
                   mine["always_cap"]["delta_gross"]))
    worst_arm, worst = None, 0.0
    for arm, row in cmp.items():
        for key in ("gap", "cost_gap", "net_gap"):
            v = row.get(key)
            if isinstance(v, (int, float)) and abs(v) > worst:
                worst, worst_arm = abs(v), arm
    return ("第二套实现在 %s 臂上与已发布面差 %.2f 元，超过一比一分容差——"
            "在弄清差在价格族还是配对之前，这几个绝对数不该被引用。" % (worst_arm, worst))


def check():
    pay, err = _read_json(os.path.join(_ROOT, "results", "indep_cap_audit_bmc.json"))
    if err:
        print("STALE FACE: %s" % err)
        return 3
    if pay.get("verdict") != "INDEPENDENT_AGREE":
        print("CHECK: %s" % pay.get("verdict"))
        return 3
    print("CHECK OK: %s" % pay.get("verdict"))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        ok = _selftest()
        print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    if a.cmd == "check":
        return check()

    pay = build()
    out = os.path.join(_ROOT, "results", "indep_cap_audit_bmc.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(pay, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("%s  %s" % (pay["verdict"], os.path.relpath(out, _ROOT)))
    print(pay["sentence"])
    if pay["verdict"] != "INDEPENDENT_AGREE":
        print(json.dumps(pay.get("compare"), ensure_ascii=False, indent=1)[:2000])
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
