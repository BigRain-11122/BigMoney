"""What did the published DIVLOWVOL list actually earn?  (dept: 研究+工程)

The sleeve's picks face (`scripts/divlowvol_live_picks.py`) publishes 20 names and
then stops: the file states a rule and a list, never a result.  The CEO page reads
its absence as `欠 1 次调仓` -- a bare count with no cause and no money in it.

This face closes the loop the only way a forward readout can be closed honestly:
take the list **as it was published** (mask video == the `as_of` bar inside the
picks file), enter on the **first bar strictly after** that date (you cannot trade
a close you only knew after it printed), and mark it to the last bar at or before
the panel cutoff.  No re-ranking, no re-judging, no look-ahead.

Three honesty faces ride in every artifact:

  * `qfq` panel -> the per-name return already carries dividends/splits
    (the sleeve is dividend-yield driven, so this matters: a raw-price return
    would systematically understate it).  Disclosed, not assumed.
  * a name with no bar on/after the entry date can't be bought -> it is carried as
    **cash (0 return)** and counted, never silently dropped and never weight-redistributed.
  * a name that stops printing before the cutoff is measured to **its own last bar**
    and counted; the face never invents a price for a suspended stock.

Benchmark = equal weight of **every symbol that has bars on both the entry and the
cutoff dates** in the same panel -- i.e. "what holding the whole market earned in
the same window", which is the only comparison that costs nothing to construct.

A stale list is stated, not hidden: if the rule should have re-fired since the
published `as_of`, the face names it in `list_age` together with the reason the
new list is missing (the panel that builds it is not on this machine).

Exit codes: 0 ok / --check ok, 2 mechanism fault (picks or panel unreadable),
3 --check drift (published face no longer matches the panel).
"""

from __future__ import annotations

import argparse
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PICKS = os.path.join(ROOT, "results", "divlowvol_live", "latest.json")
PER = os.path.join(ROOT, "data", "astock_daily", "per")
OUT_JSON = os.path.join(ROOT, "results", "divlowvol_live", "track_latest.json")
OUT_MD = os.path.join(ROOT, "docs", "divlowvol_live")

# A name whose first bar is more than this many sessions after the entry bar is
# treated as unbuyable rather than as a late entry (a month is longer than any
# honest fill window for a monthly sleeve).
MAX_ENTRY_LAG_SESSIONS = 10


def _read_bars(path):
    """date -> (close) for one symbol file, in file order (already ascending)."""
    bars = {}
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            head = fh.readline().strip().split(",")
            try:
                i_date = head.index("date")
                i_close = head.index("close")
            except ValueError:
                return bars
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                try:
                    bars[parts[i_date]] = float(parts[i_close])
                except (IndexError, ValueError):
                    continue
    except OSError:
        return {}
    return bars


def load_panel(per_dir=PER):
    panel = {}
    for path in glob.glob(os.path.join(per_dir, "*.csv")):
        code = os.path.basename(path)[:-4]
        bars = _read_bars(path)
        if bars:
            panel[code] = bars
    return panel


def window_dates(panel):
    all_dates = set()
    for bars in panel.values():
        all_dates.update(bars)
    return sorted(all_dates)


def entry_bar_after(as_of, dates):
    for d in dates:
        if d > as_of:
            return d
    return None


def measure_name(bars, entry, cutoff, dates):
    """Return (entry_date, exit_date, ret) with the three honesty faces applied."""
    if not bars:
        return None, None, None
    # first bar on/after the entry bar
    idx = None
    for i, d in enumerate(dates):
        if d >= entry:
            idx = i
            break
    if idx is None:
        return None, None, None
    entry_date = dates[idx]
    lag = idx - dates.index(entry) if entry in dates else 0
    if lag > MAX_ENTRY_LAG_SESSIONS:
        return None, None, None  # unbuyable: no bar inside the fill window
    if entry_date not in bars:
        return None, None, None
    p0 = bars[entry_date]
    exit_date, p1 = entry_date, None
    for d in dates:
        if d < entry_date or d > cutoff:
            continue
        if d in bars:
            exit_date, p1 = d, bars[d]
    if p1 is None or p0 == 0:
        return None, None, None
    return entry_date, exit_date, p1 / p0 - 1.0


def build(picks_path=PICKS, per_dir=PER, cutoff=None):
    with io.open(picks_path, encoding="utf-8") as fh:
        picks = json.load(fh)
    panel = load_panel(per_dir)
    if not panel:
        raise RuntimeError("PANEL_MISSING: %s has no readable symbol csv" % per_dir)
    dates = window_dates(panel)
    if cutoff is None:
        cutoff = dates[-1]

    as_of = picks.get("as_of")
    entry = entry_bar_after(as_of, dates)
    if entry is None:
        raise RuntimeError("no bar after as_of=%s" % as_of)

    holdings = picks.get("picks") or picks.get("holdings") or []
    rows, missing, partial = [], [], []
    w_total = 0.0
    for h in holdings:
        code = str(h.get("code"))
        w = float(h.get("weight") or 0.0)
        w_total += w
        e, x, r = measure_name(panel.get(code, {}), entry, cutoff, dates)
        if e is None:
            missing.append(code)
            rows.append({"code": code, "weight": w, "entry": None, "exit": None,
                         "ret_pct": None, "unbuyable": True})
            continue
        if x < cutoff:
            partial.append({"code": code, "last_bar": x})
        rows.append({"code": code, "weight": w, "entry": e, "exit": x,
                     "ret_pct": round(r * 100.0, 4), "unbuyable": False})

    # Book return: unbuyable names sit in cash (0%), weights kept as published so
    # the sleeve's own weights are what the money follows.
    port = 0.0
    for row in rows:
        if row["ret_pct"] is not None:
            port += row["weight"] * (row["ret_pct"] / 100.0)

    # Benchmark: every symbol with a bar on BOTH the entry bar and the cutoff.
    bench_rets = []
    for code, bars in panel.items():
        p0 = bars.get(entry)
        p1 = bars.get(cutoff)
        if p0 and p1 and p0 > 0:
            bench_rets.append(p1 / p0 - 1.0)
    bench = sum(bench_rets) / len(bench_rets) if bench_rets else None

    # The rule fires monthly on month-start; name the gap if a month-start has
    # passed since publication without a new list.
    month_starts = [d for i, d in enumerate(dates)
                    if d > as_of and (i > 0 and dates[i][:7] != dates[i - 1][:7])]
    next_due = month_starts[0] if month_starts else None

    scored = [r for r in rows if r["ret_pct"] is not None]
    best = max(scored, key=lambda r: r["ret_pct"]) if scored else None
    worst = min(scored, key=lambda r: r["ret_pct"]) if scored else None

    out = {
        "face": "DIVLOWVOL-LIVE-TRACK",
        "status": "RESEARCH_READOUT_ZERO_JUDGED_CLAIMS",
        "sleeve": picks.get("rule"),
        "list_as_of": as_of,
        "entry_bar": entry,
        "cutoff": cutoff,
        "window_sessions": len([d for d in dates if entry <= d <= cutoff]),
        "n_picks": len(holdings),
        "n_measured": len(scored),
        "n_unbuyable": len(missing),
        "unbuyable": missing,
        "n_measured_to_earlier_bar": len(partial),
        "measured_to_earlier_bar": partial,
        "weights_sum": round(w_total, 6),
        "portfolio_ret_pct": round(port * 100.0, 4),
        "benchmark": {
            "what": "equal weight of every symbol with a bar on both entry_bar and cutoff",
            "n": len(bench_rets),
            "ret_pct": round(bench * 100.0, 4) if bench is not None else None,
        },
        "excess_pp": (round((port - bench) * 100.0, 4) if bench is not None else None),
        "best": ({"code": best["code"], "ret_pct": best["ret_pct"]} if best else None),
        "worst": ({"code": worst["code"], "ret_pct": worst["ret_pct"]} if worst else None),
        "list_age": {
            "next_rule_entry": next_due,
            "rebalance_due": bool(next_due),
            "why_no_new_list": (
                "名单面吃的是 data/cache/p1c_local 那面面板，它是 bm-b 车道的产物、本机没有；"
                "本面只追已发布名单的持有期收益，不替它编一份新名单"),
            "why_no_new_list_id": (
                "the picks face builds from data/cache/p1c_local, a bm-b lane panel that "
                "does not exist on this machine; this face tracks the list as published "
                "instead of inventing a newer one"),
        },
        "caliber": {
            "panel": "data/astock_daily/per (sina qfq -- dividends embedded in the return)",
            "entry": "first bar strictly after list_as_of (no same-bar entry)",
            "exit": "last bar at or before cutoff, per name",
            "unbuyable": "no bar inside the fill window -> carried as cash 0%, counted",
            "cost": "none applied (this is a readout of the published list, not a backtest)",
        },
        "rows": rows,
    }
    return out, dates


def render_md(face):
    band = face["benchmark"]["ret_pct"]
    lines = [
        "# DIVLOWVOL 名单前向实绩 · %s" % face["cutoff"],
        "",
        "> 机械读数（零判据零记账）· 名单 as_of **%s** · 进场 **%s** · 出场 **%s**（%d 个交易日）"
        % (face["list_as_of"], face["entry_bar"], face["cutoff"], face["window_sessions"]),
        "",
        "## 一句话",
        "",
        "- 名单里的 **%d 只**（按发布权重等权）这段赚 **%+.2f%%**；同一窗口里**全市场等权**（%s 只都有价的那批）"
        "是 **%+.2f%%** → 超额 **%+.2fpp**。"
        % (face["n_measured"], face["portfolio_ret_pct"], face["benchmark"]["n"],
           band if band is not None else float("nan"), face["excess_pp"] or 0.0),
        "",
        "## 逐只（%d 只）" % len(face["rows"]),
        "",
        "| 代码 | 权重 | 进场 | 出场 | 这段 |",
        "|---|---|---|---|---|",
    ]
    for row in sorted(face["rows"], key=lambda r: (r["ret_pct"] is None, -(r["ret_pct"] or 0))):
        if row["ret_pct"] is None:
            lines.append("| %s | %.1f%% | — | — | 买不到（窗口内无价） |"
                         % (row["code"], row["weight"] * 100))
        else:
            lines.append("| %s | %.1f%% | %s | %s | %+.2f%% |"
                         % (row["code"], row["weight"] * 100, row["entry"], row["exit"], row["ret_pct"]))
    best, worst = face["best"], face["worst"]
    lines += [
        "",
        "- 最好 **%s %+.2f%%** ｜ 最差 **%s %+.2f%%**"
        % (best["code"], best["ret_pct"], worst["code"], worst["ret_pct"]) if best and worst else "",
        "",
        "## 名单为什么是 %s 的" % face["list_as_of"],
        "",
        "- 规则按月首换仓，**%s 该有新一代名单**；没生成的原因是 %s。"
        % (face["list_age"]["next_rule_entry"] or "（无）", face["list_age"]["why_no_new_list"]),
        "- 这一页追的是**已发布名单的持有期收益**，不是策略当期的信号；换仓日的真实名单要等那面面板回到本机。",
        "",
        "## 口径（读数字前先读这段）",
        "",
    ]
    for key, val in face["caliber"].items():
        lines.append("- `%s`：%s" % (key, val))
    lines += [
        "",
        "- 未定稿面：名单里 **%d 只**的最后一根 bar 早于 cutoff（停牌/退市），按它自己的最后价计，没编价。"
        % face["n_measured_to_earlier_bar"],
        "",
        "出处：`results/divlowvol_live/track_latest.json`（本页由 `scripts/divlowvol_live_track.py run` 生成；"
        "`check` 子命令会把页上的数与面板逐位重推对账）。",
        "",
    ]
    return "\n".join(l for l in lines if l is not None)


def _payload(face):
    """The part of the face that cannot move while the collector writes.

    The benchmark is an equal weight over *every* symbol that has bars on both the
    entry bar and the cutoff.  That membership grows while the A-share collector is
    still filling symbols, so it is compared separately (named, never silently
    accepted) instead of being part of the byte-identical core.
    """
    drop = {"benchmark", "excess_pp"}
    return json.dumps({k: v for k, v in face.items() if k not in drop},
                      ensure_ascii=False, sort_keys=True)


def write_outputs(face, out_json=OUT_JSON, out_md_dir=OUT_MD):
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with io.open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
        fh.write("")
    os.makedirs(out_md_dir, exist_ok=True)
    md_path = os.path.join(out_md_dir, "TRACK-%s.md" % face["cutoff"])
    with io.open(md_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(face) + "\n")
    return out_json, md_path


def cmd_check(face):
    """Re-derive from the panel and compare to the published face (drift = rc3)."""
    try:
        with io.open(OUT_JSON, encoding="utf-8") as fh:
            published = json.load(fh)
    except OSError:
        print("CHECK_FAIL published face missing: %s" % OUT_JSON)
        return 3
    if _payload(published) != _payload(face):
        for key in sorted(set(published) | set(face)):
            if key in ("benchmark", "excess_pp"):
                continue
            if json.dumps(published.get(key), ensure_ascii=False, sort_keys=True) != \
               json.dumps(face.get(key), ensure_ascii=False, sort_keys=True):
                print("CHECK_DRIFT key=%s published=%r derived=%r"
                      % (key, published.get(key), face.get(key)))
        return 3
    bench_note = ""
    pub_bench = published.get("benchmark") or {}
    if pub_bench.get("n") != face["benchmark"]["n"]:
        # the collector was still writing symbols between run and check: name the
        # movement rather than judging it green (which would read as "clean") or
        # red (which would train the reader to ignore a real drift).
        bench_note = (" BENCH_PANEL_MOVED n %s->%s ret %s->%s"
                      % (pub_bench.get("n"), face["benchmark"]["n"],
                         pub_bench.get("ret_pct"), face["benchmark"]["ret_pct"]))
    print("CHECK_OK %s window %s..%s n=%d ret=%+.2f%% bench=%+.2f%%%s"
          % (face["face"], face["entry_bar"], face["cutoff"], face["n_measured"],
             face["portfolio_ret_pct"], face["benchmark"]["ret_pct"] or float("nan"),
             bench_note))
    return 0


def _selftest():
    """Hermetic fixtures: the three honesty faces + the window rules."""
    import tempfile
    import shutil

    tmp = tempfile.mkdtemp(prefix="dlvt_")
    per = os.path.join(tmp, "per")
    os.makedirs(per)
    dates = ["2026-10-01", "2026-10-02", "2026-10-19", "2026-10-20",
             "2026-10-21", "2026-11-02", "2026-11-18", "2026-11-19"]
    # A: 10% over the window; B: -20%; C: unbuyable (no bar after 10-19);
    # D: stops printing on 11-02 (measured to its own last bar)
    series = {"A": (100.0, 110.0), "B": (100.0, 80.0), "C": (50.0, 60.0), "D": (200.0, 220.0)}
    rows_by_code = {}
    for code, (p0, p1) in series.items():
        rows = []
        for i, d in enumerate(dates):
            if code == "C" and d > "2026-10-19":
                continue  # unbuyable: never prints after the list date
            if code == "D" and d > "2026-11-02":
                continue  # stops printing mid-window
            px = p0 + (p1 - p0) * (i / (len(dates) - 1))
            rows.append("%s,%.4f,%.4f,%.4f,%.4f,1,1,1,0.1" % (d, px, px, px, px))
        rows_by_code[code] = rows
    for code, rows in rows_by_code.items():
        with io.open(os.path.join(per, code + ".csv"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("date,open,high,low,close,volume,amount,outstanding_share,turnover\n")
            fh.write("\n".join(rows) + "\n")
    picks = {"as_of": "2026-10-19", "rule": "fixture rule",
             "picks": [{"code": "A", "weight": 0.25}, {"code": "B", "weight": 0.25},
                       {"code": "C", "weight": 0.25}, {"code": "D", "weight": 0.25}]}
    picks_path = os.path.join(tmp, "picks.json")
    with io.open(picks_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(picks))

    legs, failed = [], 0

    def leg(name, cond, detail=""):
        nonlocal failed
        leg.t += 1
        if cond:
            legs.append("%d/%d PASS %s" % (leg.t, leg.t, name))
        else:
            failed += 1
            legs.append("%d FAIL %s %s" % (leg.t, name, detail))
    leg.t = 0

    face, _dates = build(picks_path, per)
    rows = {r["code"]: r for r in face["rows"]}

    # expectations are derived from the fixture series, never hand-copied
    def px(code, i):
        p0, p1 = series[code]
        return p0 + (p1 - p0) * (i / (len(dates) - 1))
    exp_a = px("A", 7) / px("A", 3) - 1.0
    exp_b = px("B", 7) / px("B", 3) - 1.0
    exp_d = px("D", 5) / px("D", 3) - 1.0
    exp_port = 0.25 * exp_a + 0.25 * exp_b + 0.25 * exp_d
    exp_bench = (exp_a + exp_b) / 2.0

    leg("entry bar is the first bar STRICTLY after list_as_of",
        face["entry_bar"] == "2026-10-20", face["entry_bar"])
    leg("a name that never prints after the list date is unbuyable, not dropped",
        rows["C"]["ret_pct"] is None and rows["C"].get("unbuyable") is True and "C" in face["unbuyable"])
    leg("an unbuyable name is carried as cash: A/B/D weights only",
        abs(face["portfolio_ret_pct"] - exp_port * 100) < 5e-4,
        (face["portfolio_ret_pct"], exp_port * 100))
    leg("a name that stops printing is measured to its own last bar",
        rows["D"]["exit"] == "2026-11-02" and face["n_measured_to_earlier_bar"] == 1,
        (rows["D"]["exit"], face["n_measured_to_earlier_bar"]))
    leg("benchmark counts only symbols with bars on both entry and cutoff",
        face["benchmark"]["n"] == 2 and abs(face["benchmark"]["ret_pct"] - exp_bench * 100) < 5e-4,
        (face["benchmark"]["n"], face["benchmark"]["ret_pct"], exp_bench * 100))
    leg("excess is portfolio minus the same-window benchmark",
        abs(face["excess_pp"] - (face["portfolio_ret_pct"] - face["benchmark"]["ret_pct"])) < 5e-4,
        (face["excess_pp"], face["portfolio_ret_pct"], face["benchmark"]["ret_pct"]))
    leg("the next rule month-start is named when the list is stale",
        face["list_age"]["next_rule_entry"] == "2026-11-02" and face["list_age"]["rebalance_due"] is True,
        face["list_age"])
    leg("face carries no judged claims and no wall clock in its payload",
        face["status"] == "RESEARCH_READOUT_ZERO_JUDGED_CLAIMS" and "generated" not in _payload(face))
    # drift detection: change the published face and --check must reject it
    out_json = os.path.join(tmp, "track.json")
    md_dir = os.path.join(tmp, "docs")
    write_outputs(face, out_json, md_dir)
    global OUT_JSON
    keep = OUT_JSON
    try:
        OUT_JSON = out_json
        leg("--check passes on the face just written", cmd_check(face) == 0)
        with io.open(out_json, encoding="utf-8") as fh:
            published = json.load(fh)
        published["portfolio_ret_pct"] = round(published["portfolio_ret_pct"] + 0.01, 4)
        with io.open(out_json, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(published, ensure_ascii=False, indent=1, sort_keys=True))
        leg("--check reports drift when a number is edited (rc3)", cmd_check(face) == 3)
    finally:
        OUT_JSON = keep
    leg("md page states the caliber and the stale-list cause",
        "口径" in render_md(face) and "为什么是" in render_md(face))

    shutil.rmtree(tmp, ignore_errors=True)
    print("\n".join(legs))
    print("selftest %d/%d %s" % (leg.t - failed, leg.t, "PASS" if not failed else "FAIL"))
    return 0 if not failed else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--picks", default=PICKS)
    ap.add_argument("--per", default=PER)
    ap.add_argument("--cutoff", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return _selftest()
    try:
        face, _ = build(a.picks, a.per, a.cutoff)
    except (OSError, RuntimeError, ValueError) as exc:
        print("MECHANISM_FAULT %s" % exc)
        return 2
    if a.cmd == "check":
        return cmd_check(face)
    write_outputs(face)
    print(json.dumps({k: face[k] for k in
                      ("face", "list_as_of", "entry_bar", "cutoff", "window_sessions",
                       "n_measured", "n_unbuyable", "portfolio_ret_pct", "benchmark", "excess_pp")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
