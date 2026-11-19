"""ETF board -- "same basket" is a verdict about the last 250 sessions. Ask the year before it.

r1806 built the two-gate screen that decides whether two differently-named tickers are the same
thing (day-level agreement <= 20% of sessions; the gap may not walk more than 1.0 pp over the
year). r1808 and r1809 then priced that answer. Every one of those numbers rests on ONE window:
the 250 sessions that end at today's bar. A reader who swaps on the strength of it is trusting
that the window they happened to be shown is not the year the pair finally drifted apart.

The face's own caveats already say the year gate is chosen rather than measured ("distribution
policy is invisible here: two same-basket tickers that pay different dividends drift in price
and are refused by gate 2"). That sentence is a claim about stability, and it had never been
scored. This face scores it:

  * today's verdicts are taken from the alias census itself (the gates, the constants and the
    pair rule are imported, not re-implemented, so the two faces cannot disagree about what
    "SAME_BASKET" means);
  * the same pairs are then re-measured on up to four earlier, disjoint 250-session windows,
    newest first, and each pair is scored: held in every earlier window it could be measured
    in, refused somewhere (and by which gate), or not measurable at all;
  * a family's money is NOT recomputed for earlier windows. Premiums exist only for one
    session on this board, so a prior-year money number would be invented -- the per-window
    blocks carry membership only, and the check leg refuses a block that grows a money key.

Read the verdict as a null of the face itself: a pair accepted today cannot be called a
substitute if the same two gates refused it last year. What survives every window is a property
of the pair; what survives only this window is a property of the window.

Usage:
    python scripts/etf_alias_stability.py run
    python scripts/etf_alias_stability.py --check
    python scripts/etf_alias_stability.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_alias_census as ac          # noqa: E402  (the gates and the pair rule, one copy)
import etf_book_sibling_entry as sib   # noqa: E402  (the board reader and liquidity floor)
import etf_book_sibling_gap as gap     # noqa: E402  (panels, calendars)
import etf_label_census as lc          # noqa: E402  (components / clique / money, one copy)

OUT_JSON = os.path.join(ROOT, "results", "etf_alias_stability.json")
OUT_MD = os.path.join(ROOT, "results", "etf_alias_stability.md")

YEAR_DAYS = ac.WINDOW_DAYS             # the window the census quotes, not a second opinion
PRIOR_WINDOWS = 4                      # four earlier years: enough to show a flip, short of a decade
STABLE_MIN = 0.80                      # of today's accepted pairs, this share must hold every year
PARTIAL_MIN = 0.50                     # below this the answer belongs to the window
NOTIONAL_CNY = lc.NOTIONAL_CNY

CRITERIA = {
    "year_days": YEAR_DAYS,
    "prior_windows": PRIOR_WINDOWS,
    "share_max": ac.SHARE_MAX,
    "divergent_pp": ac.DIVERGENT_PP,
    "drift_pp_max": ac.DRIFT_PP_MAX,
    "step_sd": ac.STEP_SD,
    "floor_pp": ac.FLOOR_PP,
    "stable_min": STABLE_MIN,
    "partial_min": PARTIAL_MIN,
}


# ---------------------------------------------------------------- windows

def window_label(index):
    return "T" if index == 0 else "T-%dy" % index


def annual_windows(calendar, year=YEAR_DAYS, n=PRIOR_WINDOWS + 1):
    """[(label, window)] newest first, each exactly `year` sessions, none overlapping another.

    A window that would start before the panel does is dropped rather than short-windowed: a
    150-session window is a different question with a different day-count denominator, and
    quietly answering it instead is how a stability test flatters itself.
    """
    out = []
    for i in range(n):
        end = len(calendar) - i * year
        start = end - year
        if start < 0:
            break
        out.append((window_label(i), calendar[start:end]))
    return out


def window_measures(series, window):
    """Codes that traded every session of this window, their log levels, and the day-gate matrix."""
    codes, short = ac.coverage(series, window)
    if not codes:
        return {"codes": [], "short": short, "pos": {}, "logs": None, "shares": None}
    prices = np.array([[series[c][d] for d in window] for c in codes], dtype=float)
    logs = np.log(prices) * 100.0
    shares = ac.share_matrix(np.diff(logs, axis=1))
    return {"codes": codes, "short": short, "pos": {c: i for i, c in enumerate(codes)},
            "logs": logs, "shares": shares}


def pair_state(meas, a, b, drift_max=ac.DRIFT_PP_MAX):
    """One pair inside one window. Missing history is NAMED, never scored as agreement."""
    pos = meas.get("pos") or {}
    if a not in pos or b not in pos:
        return {"state": "NO_HISTORY", "share": None, "drift_pp": None, "steps": None}
    i, j = pos[a], pos[b]
    sh = float(meas["shares"][i, j])
    drift, steps = ac.despiked_drift(meas["logs"][i] - meas["logs"][j])
    verdict = ac.pair_verdict(sh, drift, drift_max=drift_max)
    return {"state": verdict, "share": round(sh, 4), "drift_pp": round(drift, 3),
            "steps": steps}


# ---------------------------------------------------------------- scoring one pair across years

def summarise(today_pairs, history):
    """Score today's accepted pairs against the earlier windows.

    today_pairs : [(a, b)] accepted on the newest window
    history     : [{"label": str, "states": {(a, b): state}}] newest first, T excluded

    Three outcomes per pair, and they are not interchangeable:
      held_every_window -- measured in at least one earlier window and accepted in all of them
      refused_somewhere -- at least one earlier window used a gate to refuse it (gate named)
      not_measurable    -- no earlier window had both tickers trading; it is not a hold
    """
    per_window = []
    for h in history:
        states = h["states"]
        tallies = {"label": h["label"], "measured": 0, "same_basket": 0,
                   "refused_days_apart": 0, "refused_walks_apart": 0, "no_history": 0}
        for key in today_pairs:
            st = states.get(key, "NO_HISTORY")
            if st == "NO_HISTORY":
                tallies["no_history"] += 1
                continue
            tallies["measured"] += 1
            if st == "SAME_BASKET":
                tallies["same_basket"] += 1
            elif st == "DAYS_APART":
                tallies["refused_days_apart"] += 1
            else:
                tallies["refused_walks_apart"] += 1
        tallies["share"] = (round(tallies["same_basket"] / tallies["measured"], 4)
                            if tallies["measured"] else None)
        per_window.append(tallies)

    held, refused, unmeasured = [], [], []
    trials = {}
    for key in today_pairs:
        seen, refused_by = 0, []
        for h in history:
            st = h["states"].get(key, "NO_HISTORY")
            if st == "NO_HISTORY":
                continue
            seen += 1
            if st != "SAME_BASKET":
                refused_by.append((h["label"], st))
        if seen == 0:
            unmeasured.append(key)
            continue
        trials.setdefault(seen, [0, 0])
        trials[seen][0] += 1
        if refused_by:
            refused.append({"pair": list(key), "refused_by": refused_by, "trials": seen})
        else:
            held.append(key)
            trials[seen][1] += 1

    measurable = len(held) + len(refused)
    rate = (len(held) / measurable) if measurable else None
    by_gate = {"DAYS_APART": sum(1 for r in refused
                                 if any(g == "DAYS_APART" for _, g in r["refused_by"])),
               "WALKS_APART": sum(1 for r in refused
                                  if any(g == "WALKS_APART" for _, g in r["refused_by"]))}

    # Two pairs are not the same test: one measurable in a single earlier year only has to clear
    # the gates once, one with four earlier years has to clear them four times. Mixing them into
    # one rate reads "25% of pairs are stable" when the per-window rate is 55% and the pairs with
    # four trials are simply being asked four times.
    by_trials = {str(k): {"pairs": v[0], "held_every_window": v[1],
                          "rate": round(v[1] / v[0], 4) if v[0] else None}
                 for k, v in sorted(trials.items())}
    tot_same = sum(pw["same_basket"] for pw in per_window)
    tot_meas = sum(pw["measured"] for pw in per_window)
    # Published at 4 decimals and then used, so a reader re-deriving the expectation gets the
    # same number; computing it from full precision makes the check leg disagree in the tail.
    pooled = round(tot_same / tot_meas, 4) if tot_meas else None
    # If each earlier window is an independent draw of the same knife-edge gate, a pair with
    # `seen` trials survives with probability pooled**seen. Observed vs that is the whole
    # difference between "these pairs are unstable" and "this gate is a coin flip".
    expect = None if pooled is None else round(
        sum(pooled ** k * v[0] for k, v in trials.items()), 2)

    return {
        "n_pairs": len(today_pairs),
        "n_measurable_before": measurable,
        "n_held_every_window": len(held),
        "n_refused_somewhere": len(refused),
        "n_not_measurable": len(unmeasured),
        "hold_rate": None if rate is None else round(rate, 4),
        "refused_by_gate": by_gate,
        "verdict": stability_verdict(rate),
        "per_window": per_window,
        "by_trials": by_trials,
        "pooled_per_window_rate": pooled,
        "held_if_windows_were_independent": expect,
        # full lists; the face caps what it publishes, but the family arithmetic below must see
        # every refused pair, not the first forty of them
        "refused_all": refused,
        "refused": refused,
        "refused_total": len(refused),
        "not_measurable_all": [list(p) for p in unmeasured],
        "not_measurable": [list(p) for p in unmeasured],
    }


def stability_verdict(rate):
    """No prior measurement is its own answer; it is not a pass (r98 family)."""
    if rate is None:
        return "NO_PRIOR_HISTORY"
    if rate >= STABLE_MIN:
        return "STABLE"
    if rate >= PARTIAL_MIN:
        return "PARTIAL"
    return "WINDOW_LUCK"


# ---------------------------------------------------------------- the face

def build():
    board, session = gap.board_labels()
    live = [c for c, r in board.items() if (r.get("amount") or 0.0) >= sib.LIQ_FLOOR_CNY]
    series = {}
    for code in live:
        path = gap.find_daily(code)
        if path:
            series[code] = gap.load_close(path)

    calendar = sorted({d for s in series.values() for d in s})
    windows = annual_windows(calendar)
    if not windows:
        raise SystemExit("no %d-session window on this panel" % YEAR_DAYS)

    today_label, today_window = windows[0]
    today = window_measures(series, today_window)
    codes = today["codes"]
    labels = {c: board[c].get("label") for c in codes}
    premiums = {c: sib.premium_dec(board[c].get("premium_pct")) for c in codes}
    premiums = {c: (None if p is None else p * 100.0) for c, p in premiums.items()}

    accepted, counts = [], {}
    for i in range(len(codes)):
        for j in range(i + 1, len(codes)):
            sh = float(today["shares"][i, j])
            if sh > ac.SHARE_MAX:
                counts["DAYS_APART"] = counts.get("DAYS_APART", 0) + 1
                continue
            drift, _steps = ac.despiked_drift(today["logs"][i] - today["logs"][j])
            verdict = ac.pair_verdict(sh, drift)
            counts[verdict] = counts.get(verdict, 0) + 1
            if verdict == "SAME_BASKET":
                accepted.append((codes[i], codes[j]))

    history = []
    window_rows = [{"label": today_label, "from": today_window[0], "to": today_window[-1],
                    "days": len(today_window), "n_in_screen": len(codes),
                    "n_excluded_short": len(today["short"])}]
    priors = []
    for label, window in windows[1:]:
        meas = window_measures(series, window)
        states = {}
        for (a, b) in accepted:
            states[(a, b)] = pair_state(meas, a, b)["state"]
        history.append({"label": label, "states": states})
        priors.append(meas)
        window_rows.append({"label": label, "from": window[0], "to": window[-1],
                            "days": len(window), "n_in_screen": len(meas["codes"]),
                            "n_excluded_short": len(meas["short"])})

    stab = summarise(accepted, history)

    # Rule identity. The gates are imported, so on the SAME window and the SAME universe this
    # face must land on the census's own accepted count pair for pair. When the panel took rows
    # after the census was written the universes differ, and then only the difference is spoken.
    census_x = {"census_present": False}
    if os.path.exists(ac.OUT_JSON):
        with open(ac.OUT_JSON, encoding="utf-8") as fh:
            cen = json.load(fh)
        cwin = cen.get("panel") or {}
        c_in = (cen.get("board") or {}).get("n_in_screen")
        c_acc = (cen.get("verdict_counts") or {}).get("SAME_BASKET")
        same_window = (cwin.get("window_to") == today_window[-1]
                       and cwin.get("window_from") == today_window[0])
        same_universe = (c_in == len(codes))
        if same_window and same_universe:
            note = ("同一窗同一宇宙：两份实现必须给出同样的对数，否则是规则漂移而不是口径差")
        elif same_window:
            note = ("同一窗不同宇宙（普查面 %r 票 / 本面 %d 票）：面板在普查面写完之后又落了"
                    "新票，差在宇宙不在规则" % (c_in, len(codes)))
        else:
            note = ("普查面停在上一个盘口 %r，本面在 %s 上重跑：两条数字不同源，不能相减"
                    % ([cwin.get("window_from"), cwin.get("window_to")], today_window[-1]))
        census_x = {"census_present": True, "census_session": cen.get("session"),
                 "census_window": [cwin.get("window_from"), cwin.get("window_to")],
                 "census_n_in_screen": c_in, "census_same_basket": c_acc,
                 "same_window": same_window, "same_universe": same_universe,
                 "rule_identity_ok": ((c_acc == len(accepted))
                                      if (same_window and same_universe) else None),
                 "note": note}

    edges = {frozenset(p) for p in accepted}
    alias, chains = ac.families(edges, labels, premiums)
    cross = [f for f in alias if f["n_names"] > 1]
    over = [f for f in cross if (f.get("money") or {}).get("material")]

    # A family is only as stable as its weakest accepted pair: the reader will swap between
    # two members, not between "the family" and itself.
    refused_pairs = {tuple(sorted(r["pair"])) for r in stab["refused_all"]}
    for f in over:
        pairs = [(f["members"][i], f["members"][j])
                 for i in range(len(f["members"])) for j in range(i + 1, len(f["members"]))]
        pairs = [p for p in pairs if frozenset(p) in edges]
        ok = [p for p in pairs if tuple(sorted(p)) not in refused_pairs]
        f["pair_stability"] = {"n_pairs": len(pairs), "n_held_every_window": len(ok),
                               "all_pairs_hold": len(ok) == len(pairs)}

    material_total = round(sum(f["money"]["cost_cny"] for f in over), 1)
    material_stable = round(sum(f["money"]["cost_cny"] for f in over
                                if f["pair_stability"]["all_pairs_hold"]), 1)

    # Publish a readable slice; the totals above are computed on the full lists.
    stab["refused"] = stab["refused_all"][:40]
    stab["not_measurable"] = stab["not_measurable_all"][:40]
    stab.pop("refused_all", None)
    stab.pop("not_measurable_all", None)

    face = {
        "artifact": "etf_alias_stability",
        "evidence_cutoff": today_window[-1],
        "session": session,
        "panel": {"window_from": today_window[0], "window_to": today_window[-1],
                  "window_days": len(today_window)},
        "source_faces": {
            "gates": "scripts/etf_alias_census.py (share_divergent / despiked_drift / pair_verdict, imported)",
            "board": "results/etf_book_sibling_entry.json (latest snapshot)",
            "panels": "data/daily/*.csv (per-ticker close)",
        },
        "criteria": CRITERIA,
        "windows": window_rows,
        "board": {"n_rows": len(board), "n_live": len(live), "n_with_panel": len(series),
                  "n_in_screen": len(codes), "n_pairs": sum(counts.values()),
                  "verdict_counts_today": counts,
                  "n_accepted_today": len(accepted)},
        "stability": stab,
        "crosscheck": census_x,
        "families": {
            "n_alias": len(alias), "n_cross_name": len(cross), "n_chains": len(chains),
            "n_over_material_line": len(over),
            "total_cost_cny": material_total,
            "cost_where_every_pair_held_cny": material_stable,
            "rows": [{"members": f["members"], "names": f["names"],
                      "money": f["money"], "pair_stability": f["pair_stability"]}
                     for f in over],
        },
        "sentence": sentence(stab, len(over), material_total, material_stable),
        "caveats": [
            "the earlier windows re-ask the SAME two gates of the SAME two tickers; a pair that "
            "holds in all of them is stable in price behaviour, not certified as the same asset",
            "earlier windows carry membership only: premiums exist for one session on this "
            "board, so no earlier money number is published (a prior-year cost would be invented)",
            "the screen is today's: a ticker that only began trading two years ago drops out of "
            "the earlier windows by name and is counted as not measurable, never as a hold",
            "the drift line is still the census's chosen 1.0 pp; this face measures whether the "
            "verdicts move, not whether the line is the right one",
            "windows are disjoint and exactly %d sessions; the panel's own holiday calendar "
            "decides what a session is" % YEAR_DAYS,
        ],
    }
    return face


def sentence(stab, n_over, total_cny, stable_cny):
    pw = stab["per_window"]
    per_win = "、".join("%s %.1f%%" % (r["label"], 100.0 * (r["share"] or 0.0)) for r in pw)
    exp = stab.get("held_if_windows_were_independent")
    tail = ("" if exp is None else
            "把每个历史窗当独立抽样，每窗 %.1f%% 的通过率下这些对应该活下来 %.1f 对，"
            "实测 %d 对——" % (100.0 * (stab["pooled_per_window_rate"] or 0.0), exp,
                              stab["n_held_every_window"]))
    return (
        "这张盘口有 %d 对异名同篮；把同样两道门放到前 %d 个年度窗上重问一遍，"
        "每窗只留下（%s），能数到的 %d 对里 %d 对每窗都过（%.1f%%），%d 对被某一窗拒过"
        "（日级 %d 对 / 年级 %d 对），%d 对历史不够没法问——判词 %s。%s"
        "所以这不是「某些对不稳」而是这道年级线落在刀口上。"
        "过 0.50pp 物质线的 %d 组一共 %s 元的选择成本，其中每一对都过所有窗的只有 %s 元。"
        % (stab["n_pairs"], len(pw), per_win, stab["n_measurable_before"],
           stab["n_held_every_window"], 100.0 * (stab["hold_rate"] or 0.0),
           stab["n_refused_somewhere"], stab["refused_by_gate"]["DAYS_APART"],
           stab["refused_by_gate"]["WALKS_APART"], stab["n_not_measurable"], stab["verdict"],
           tail, n_over, "{:,.0f}".format(total_cny), "{:,.0f}".format(stable_cny))
    )


# ---------------------------------------------------------------- readers

def check(face):
    """Re-derive every published rate from the published rows."""
    problems = []
    stab = face.get("stability") or {}
    n = stab.get("n_pairs")
    if n != (face.get("board") or {}).get("n_accepted_today"):
        problems.append("stability.n_pairs ≠ board.n_accepted_today")
    parts = (stab.get("n_held_every_window") or 0) + (stab.get("n_refused_somewhere") or 0) \
        + (stab.get("n_not_measurable") or 0)
    if parts != n:
        problems.append("三态之和 ≠ 今日接受对数")
    measurable = (stab.get("n_held_every_window") or 0) + (stab.get("n_refused_somewhere") or 0)
    if measurable != stab.get("n_measurable_before"):
        problems.append("可数对数 ≠ 每窗都过 + 被拒过")
    want_rate = None if not measurable else round((stab.get("n_held_every_window") or 0) / measurable, 4)
    got = stab.get("hold_rate")
    if (want_rate is None) != (got is None) or (want_rate is not None and abs(got - want_rate) > 1e-4):
        problems.append("hold_rate ≠ 从三态重算")
    want_verdict = stability_verdict(want_rate)
    if stab.get("verdict") != want_verdict:
        problems.append("判词 ≠ 从 hold_rate 重推（%s）" % want_verdict)
    for pw in stab.get("per_window") or []:
        if pw.get("measured", 0) + pw.get("no_history", 0) != n:
            problems.append("%s: measured+no_history ≠ 对数" % pw.get("label"))
        if pw.get("same_basket", 0) + pw.get("refused_days_apart", 0) \
                + pw.get("refused_walks_apart", 0) != pw.get("measured", 0):
            problems.append("%s: 三态之和 ≠ measured" % pw.get("label"))
        if pw.get("measured") and pw.get("share") is not None:
            want = round(pw["same_basket"] / pw["measured"], 4)
            if abs(pw["share"] - want) > 1e-4:
                problems.append("%s: share ≠ same_basket/measured" % pw.get("label"))
        # Premium history does not exist: a money key inside a prior-year window would be a
        # number nobody measured.
        if "money" in pw or "cost_cny" in pw:
            problems.append("%s: 历史窗不许带金额（溢价只有一天）" % pw.get("label"))
    fam = face.get("families") or {}
    total = sum((r.get("money") or {}).get("cost_cny") or 0.0 for r in fam.get("rows") or [])
    if abs(total - (fam.get("total_cost_cny") or 0.0)) > 0.05:
        problems.append("物质线成本合计 ≠ 各行之和")
    stable = sum((r.get("money") or {}).get("cost_cny") or 0.0 for r in fam.get("rows") or []
                 if (r.get("pair_stability") or {}).get("all_pairs_hold"))
    if abs(stable - (fam.get("cost_where_every_pair_held_cny") or 0.0)) > 0.05:
        problems.append("每窗都过的成本 ≠ 对应行之和")
    for r in fam.get("rows") or []:
        ps = r.get("pair_stability") or {}
        if ps.get("n_held_every_window", 0) > ps.get("n_pairs", 0):
            problems.append("族 %r: 过窗对数大于总对数" % (r.get("names"),))
        if bool(ps.get("all_pairs_hold")) != (ps.get("n_held_every_window") == ps.get("n_pairs")):
            problems.append("族 %r: all_pairs_hold 与计数不符" % (r.get("names"),))

    # by_trials must partition the same pairs the headline counts, and the pooled per-window
    # rate must be the ratio of the published per-window tallies -- not a second estimate.
    bt = stab.get("by_trials") or {}
    if bt:
        if sum(v.get("pairs", 0) for v in bt.values()) != measurable:
            problems.append("by_trials 分档对数之和 ≠ 可数对数")
        if sum(v.get("held_every_window", 0) for v in bt.values()) != (stab.get("n_held_every_window") or 0):
            problems.append("by_trials 分档过窗对数之和 ≠ 每窗都过的对数")
        tot_same = sum(pw.get("same_basket", 0) for pw in stab.get("per_window") or [])
        tot_meas = sum(pw.get("measured", 0) for pw in stab.get("per_window") or [])
        want_pooled = None if not tot_meas else round(tot_same / tot_meas, 4)
        got_pooled = stab.get("pooled_per_window_rate")
        if (want_pooled is None) != (got_pooled is None) or (
                want_pooled is not None and abs(got_pooled - want_pooled) > 1e-4):
            problems.append("pooled_per_window_rate ≠ 逐窗合计重算")
        if want_pooled is not None:
            want_exp = round(sum(want_pooled ** int(k) * v.get("pairs", 0) for k, v in bt.items()), 2)
            if abs((stab.get("held_if_windows_were_independent") or 0.0) - want_exp) > 0.01:
                problems.append("独立抽样期望 ≠ 从每窗通过率重算")

    cc = face.get("crosscheck") or {}
    if cc.get("census_present"):
        if cc.get("same_universe") and cc.get("census_n_in_screen") != (face.get("board") or {}).get("n_in_screen"):
            problems.append("crosscheck 自称同一宇宙但票数不同")
        if cc.get("rule_identity_ok") is False:
            problems.append("同一窗同一宇宙却与普查面给出不同对数（规则漂移）")
        if not cc.get("note"):
            problems.append("crosscheck 缺一行说明两边为什么可比/不可比")
    return {"artifact": face.get("artifact"), "ok": not problems, "problems": problems,
            "n_pairs": n, "verdict": stab.get("verdict")}


def render_md(face):
    stab = face["stability"]
    fam = face["families"]
    rows = ["# 异名同篮：把判词放到前几个年度窗上重问一遍", "",
            "证据 cutoff `%s`（盘口 session %s）。今日窗 %s..%s（%d 个交易日）。" % (
                face["evidence_cutoff"], face["session"], face["panel"]["window_from"],
                face["panel"]["window_to"], face["panel"]["window_days"]), "",
            "## 一句话", "", face["sentence"], "",
            "## 逐窗读数", "",
            "| 窗 | 区间 | 屏幕内票数 | 可数对数 | 判同篮 | 日级拒 | 年级拒 | 无史 | 通过率 |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in face["windows"]:
        rows.append("| %s | %s..%s | %d | — | — | — | — | — | — |"
                    % (r["label"], r["from"], r["to"], r["n_in_screen"]))
    rows += ["", "（今日窗一行只报屏幕规模；重问结果即下表。）", "",
             "| 历史窗 | 可数 | 判同篮 | 日级拒 | 年级拒 | 无史 | 通过率 |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for pw in stab["per_window"]:
        rows.append("| %s | %d | %d | %d | %d | %d | %s |" % (
            pw["label"], pw["measured"], pw["same_basket"], pw["refused_days_apart"],
            pw["refused_walks_apart"], pw["no_history"],
            "—" if pw["share"] is None else "%.1f%%" % (100.0 * pw["share"])))
    rows += ["", "**判词：%s**（今日接受 %d 对；能数到 %d 对，其中每窗都过 %d 对＝%.1f%%，"
             "被拒 %d 对，历史不够 %d 对）。" % (
                 stab["verdict"], stab["n_pairs"], stab["n_measurable_before"],
                 stab["n_held_every_window"], 100.0 * (stab["hold_rate"] or 0.0),
                 stab["n_refused_somewhere"], stab["n_not_measurable"]), ""]
    if stab.get("by_trials"):
        rows += ["## 同一个通过率，不同的考试次数", "",
                 "只有一年历史可问的对只需过一次门，有四年历史的对要过四次。把两者算进同一个"
                 "百分比，读起来就像「四分之三的对不稳」。", "",
                 "| 有几个历史窗可数 | 对数 | 每窗都过 | 通过率 |", "| ---: | ---: | ---: | ---: |"]
        for k in sorted(stab["by_trials"], key=lambda x: int(x)):
            v = stab["by_trials"][k]
            rows.append("| %s | %d | %d | %s |" % (
                k, v["pairs"], v["held_every_window"],
                "—" if v["rate"] is None else "%.1f%%" % (100.0 * v["rate"])))
        rows += ["", "每个历史窗单独看，通过率 %s；把每窗当独立抽样，这些对里应该活下来 %.1f 对，"
                 "实测 %d 对。" % (
                     "%.1f%%" % (100.0 * (stab["pooled_per_window_rate"] or 0.0)),
                     stab.get("held_if_windows_were_independent") or 0.0,
                     stab["n_held_every_window"]), ""]
    if fam["rows"]:
        rows += ["## 过物质线的族，按「每一对是否每窗都过」分", "",
                 "| 族 | 成员数 | 一手最贵比最便宜 | 对数 | 每窗都过 |", "| --- | ---: | ---: | ---: | ---: |"]
        for r in sorted(fam["rows"], key=lambda x: -(x["money"] or {}).get("cost_cny", 0)):
            ps = r["pair_stability"]
            rows.append("| %s | %d | %s | %d | %d%s |" % (
                "/".join(n for n in r["names"] if n), len(r["members"]),
                "{:,.0f}".format((r["money"] or {}).get("cost_cny") or 0.0),
                ps["n_pairs"], ps["n_held_every_window"],
                "" if ps["all_pairs_hold"] else "（有翻转）"))
        rows += ["", "物质线以上合计 **%s 元**；其中每一对都过所有窗的只有 **%s 元**。" % (
            "{:,.0f}".format(fam["total_cost_cny"]),
            "{:,.0f}".format(fam["cost_where_every_pair_held_cny"])), ""]
    rows += ["## 限制（照面内 caveats，一条不改写）", ""]
    rows += ["- " + c for c in face["caveats"]]
    return "\n".join(rows) + "\n"


def write_out(face):
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(face))


def run():
    face = build()
    write_out(face)
    stab = face["stability"]
    print("etf_alias_stability: %d pairs accepted today, %d measurable before, %d held every "
          "window (rate=%s), verdict=%s" % (stab["n_pairs"], stab["n_measurable_before"],
                                            stab["n_held_every_window"], stab["hold_rate"],
                                            stab["verdict"]))
    print(face["sentence"])
    return 0


def load_face():
    with open(OUT_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def main_check():
    face = load_face()
    res = check(face)
    print(json.dumps(res, ensure_ascii=False))
    return 0 if res["ok"] else 1


# ---------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    calm = [0.0] * 60
    walk = [i * 0.02 for i in range(60)]          # 1.18 pp over the run: past the year line
    jumpy = [0.0, 3.0] * 30                       # a 3 pp day every other session: past the day line

    def L1_windows_disjoint():
        cal = ["d%03d" % i for i in range(1000)]
        ws = annual_windows(cal, year=250, n=5)
        assert len(ws) == 4, "1000 个交易日只够 4 个 250 窗：%d" % len(ws)
        assert ws[0][0] == "T" and ws[1][0] == "T-1y", "标签从新到旧：%r" % ([w[0] for w in ws],)
        seen = set()
        for _lbl, w in ws:
            assert len(w) == 250, "每窗必须恰好 250 个交易日"
            assert not (set(w) & seen), "窗之间不许重叠"
            seen |= set(w)
        assert ws[0][1][-1] == "d999", "最新窗结束于面板最后一根 bar"

    def L2_short_panel_drops_window():
        cal = ["d%03d" % i for i in range(300)]
        ws = annual_windows(cal, year=250, n=5)
        assert len(ws) == 1, "只有 300 个交易日时不许拿 50 个交易日的窗口充数：%d" % len(ws)

    def L3_missing_history_named():
        meas = {"pos": {"A": 0, "B": 1}, "shares": np.zeros((2, 2)),
                "logs": np.zeros((2, 10))}
        st = pair_state(meas, "A", "ZZ")
        assert st["state"] == "NO_HISTORY", "没有历史的票要单列：%r" % (st,)
        assert st["share"] is None and st["drift_pp"] is None, "没历史不许印数"

    def L4_gates_agree_on_calm():
        logs = np.array([calm, calm], dtype=float)
        meas = {"pos": {"A": 0, "B": 1}, "shares": np.zeros((2, 2)), "logs": logs}
        assert pair_state(meas, "A", "B")["state"] == "SAME_BASKET", "完全一致的对要判同篮"

    def L5_year_gate_refuses_walk():
        logs = np.array([walk, calm], dtype=float)
        meas = {"pos": {"A": 0, "B": 1}, "shares": np.zeros((2, 2)), "logs": logs}
        st = pair_state(meas, "A", "B")
        assert st["state"] == "WALKS_APART", "一年走开 1.18pp 要被年级拒：%r" % (st,)

    def L6_day_gate_refuses_jump():
        logs = np.array([jumpy, calm], dtype=float)
        shares = np.array([[0.0, 0.9], [0.9, 0.0]])
        meas = {"pos": {"A": 0, "B": 1}, "shares": shares, "logs": logs}
        assert pair_state(meas, "A", "B")["state"] == "DAYS_APART", "隔天跳 3pp 要被日级拒"

    def _hist(states_by_label):
        return [{"label": lbl, "states": st} for lbl, st in states_by_label]

    def L7_planted_flip_is_not_a_hold():
        today = [("A", "B"), ("A", "C")]
        hist = _hist([("T-1y", {("A", "B"): "SAME_BASKET", ("A", "C"): "WALKS_APART"}),
                      ("T-2y", {("A", "B"): "SAME_BASKET", ("A", "C"): "SAME_BASKET"})])
        s = summarise(today, hist)
        assert s["n_held_every_window"] == 1, "植入的翻转不能算过：%r" % (s["n_held_every_window"],)
        assert s["n_refused_somewhere"] == 1, "被拒过的要单列"
        assert s["refused_by_gate"]["WALKS_APART"] == 1, "要说是哪道门拒的"
        assert s["hold_rate"] == 0.5, "通过率=过/可数：%r" % (s["hold_rate"],)

    def L8_no_history_is_not_a_pass():
        today = [("A", "B")]
        hist = _hist([("T-1y", {}), ("T-2y", {})])
        s = summarise(today, hist)
        assert s["n_not_measurable"] == 1 and s["n_held_every_window"] == 0, "缺史不算过"
        assert s["hold_rate"] is None, "无可数对时不许印通过率"
        assert s["verdict"] == "NO_PRIOR_HISTORY", "无可数对=没有历史，不是 STABLE：%r" % (s["verdict"],)

    def L9_no_prior_window_at_all():
        s = summarise([("A", "B")], [])
        assert s["verdict"] == "NO_PRIOR_HISTORY", "一个历史窗都没有时同样不能说稳"

    def L10_thresholds_named():
        assert stability_verdict(0.80) == "STABLE"
        assert stability_verdict(0.79) == "PARTIAL"
        assert stability_verdict(0.50) == "PARTIAL"
        assert stability_verdict(0.49) == "WINDOW_LUCK"
        assert stability_verdict(None) == "NO_PRIOR_HISTORY"

    def L11_per_window_tallies_conserve():
        today = [("A", "B"), ("A", "C"), ("B", "C")]
        hist = _hist([("T-1y", {("A", "B"): "SAME_BASKET", ("A", "C"): "DAYS_APART"}),
                      ("T-2y", {("A", "B"): "SAME_BASKET", ("A", "C"): "SAME_BASKET",
                                ("B", "C"): "SAME_BASKET"})])
        s = summarise(today, hist)
        for pw in s["per_window"]:
            assert pw["measured"] + pw["no_history"] == 3, "每窗都要对数守恒：%r" % (pw,)
            assert pw["same_basket"] + pw["refused_days_apart"] + pw["refused_walks_apart"] \
                == pw["measured"], "窗内三态守恒：%r" % (pw,)

    def L12_check_catches_tampering():
        today = [("A", "B"), ("A", "C")]
        hist = _hist([("T-1y", {("A", "B"): "SAME_BASKET", ("A", "C"): "WALKS_APART"})])
        s = summarise(today, hist)
        face = {"artifact": "x", "board": {"n_accepted_today": 2}, "stability": s,
                "families": {"rows": [], "total_cost_cny": 0.0,
                             "cost_where_every_pair_held_cny": 0.0}}
        assert check(face)["ok"], "干净面应过检：%r" % (check(face)["problems"],)
        bad = json.loads(json.dumps(face))
        bad["stability"]["n_held_every_window"] = 2
        assert not check(bad)["ok"], "把翻转算成过必须被抓"
        bad2 = json.loads(json.dumps(face))
        bad2["stability"]["per_window"][0]["money"] = {"cost_cny": 1.0}
        assert not check(bad2)["ok"], "历史窗里长出一个金额必须被抓"

    def L13_check_catches_family_arithmetic():
        face = {"artifact": "x", "board": {"n_accepted_today": 0},
                "stability": summarise([], []),
                "families": {"rows": [{"names": ["甲"], "money": {"cost_cny": 100.0},
                                       "pair_stability": {"n_pairs": 1, "n_held_every_window": 1,
                                                          "all_pairs_hold": True}}],
                             "total_cost_cny": 100.0, "cost_where_every_pair_held_cny": 100.0}}
        assert check(face)["ok"], "族金额干净时应过：%r" % (check(face)["problems"],)
        face["families"]["total_cost_cny"] = 90.0
        assert not check(face)["ok"], "合计被改小必须被抓"

    def L14_sentence_cites_own_counts():
        s = summarise([("A", "B"), ("A", "C")],
                      _hist([("T-1y", {("A", "B"): "SAME_BASKET",
                                       ("A", "C"): "SAME_BASKET"})]))
        text = sentence(s, 1, 10236.0, 4119.0)
        for token in ("2", "1", "10,236", "4,119", "STABLE"):
            assert token in text, "句子要引用它拿到的数 %s：%s" % (token, text)

    def L15_trials_are_counted_separately():
        today = [("A", "B"), ("A", "C")]
        # A/B can be asked in both earlier windows; A/C only exists in the newest one.
        hist = _hist([("T-1y", {("A", "B"): "SAME_BASKET", ("A", "C"): "SAME_BASKET"}),
                      ("T-2y", {("A", "B"): "SAME_BASKET"})])
        s = summarise(today, hist)
        assert s["by_trials"]["1"]["pairs"] == 1, "只有一窗可数的对要单列：%r" % (s["by_trials"],)
        assert s["by_trials"]["2"]["pairs"] == 1, "两窗可数的对要单列"
        assert s["by_trials"]["1"]["rate"] == 1.0 and s["by_trials"]["2"]["rate"] == 1.0, "分档各自算率"

    def L16_independence_expectation():
        # One pair passes, one fails, in a single window: pooled rate 0.5, one trial each, so
        # the expectation is 0.5 held pair.
        today = [("A", "B"), ("A", "C")]
        hist = _hist([("T-1y", {("A", "B"): "SAME_BASKET", ("A", "C"): "WALKS_APART"})])
        s = summarise(today, hist)
        assert s["pooled_per_window_rate"] == 0.5, "池化通过率=逐窗合计之比：%r" % (s["pooled_per_window_rate"],)
        assert abs((s["held_if_windows_were_independent"] or 0.0) - 1.0) < 1e-9, \
            "独立抽样期望=Σ p^次数：%r" % (s["held_if_windows_were_independent"],)
        # The same pooled 0.5 with four trials on one pair expects 0.0625, not 0.5.
        hist2 = _hist([("T-1y", {("A", "B"): "SAME_BASKET"}), ("T-2y", {("A", "B"): "WALKS_APART"}),
                       ("T-3y", {("A", "B"): "SAME_BASKET"}), ("T-4y", {("A", "B"): "SAME_BASKET"})])
        s2 = summarise([("A", "B")], hist2)
        assert abs(s2["pooled_per_window_rate"] - 0.75) < 1e-9, "三过一拒=0.75"
        assert abs((s2["held_if_windows_were_independent"] or 0.0) - 0.75 ** 4) < 0.01, \
            "四次考试的期望是 p^4：%r" % (s2["held_if_windows_were_independent"],)

    def L17_crosscheck_refuses_rule_drift():
        base = {"artifact": "x", "board": {"n_accepted_today": 1, "n_in_screen": 5},
                "stability": summarise([("A", "B")], _hist([("T-1y", {("A", "B"): "SAME_BASKET"})])),
                "families": {"rows": [], "total_cost_cny": 0.0,
                             "cost_where_every_pair_held_cny": 0.0},
                "crosscheck": {"census_present": True, "same_window": True, "same_universe": True,
                               "census_n_in_screen": 5, "census_same_basket": 1,
                               "rule_identity_ok": True, "note": "同一窗同一宇宙"}}
        assert check(base)["ok"], "两份实现一致时应过：%r" % (check(base)["problems"],)
        drift = json.loads(json.dumps(base))
        drift["crosscheck"]["rule_identity_ok"] = False
        assert not check(drift)["ok"], "同一窗同一宇宙给出不同对数必须被抓"
        liars = json.loads(json.dumps(base))
        liars["crosscheck"]["census_n_in_screen"] = 6
        assert not check(liars)["ok"], "自称同一宇宙却票数不同必须被抓"

    for name, fn in [
        ("L1 年度窗互不重叠且标签从新到旧", L1_windows_disjoint),
        ("L2 面板太短时不许拿短窗充数", L2_short_panel_drops_window),
        ("L3 没有历史=单列，不印数", L3_missing_history_named),
        ("L4 两门都过=同篮", L4_gates_agree_on_calm),
        ("L5 一年走开 1.18pp 被年级拒", L5_year_gate_refuses_walk),
        ("L6 隔天跳 3pp 被日级拒", L6_day_gate_refuses_jump),
        ("L7 植入的翻转不算过窗", L7_planted_flip_is_not_a_hold),
        ("L8 缺史不算通过", L8_no_history_is_not_a_pass),
        ("L9 一个历史窗都没有≠稳", L9_no_prior_window_at_all),
        ("L10 三档判据在 0.80/0.50 上落位", L10_thresholds_named),
        ("L11 每窗对数守恒", L11_per_window_tallies_conserve),
        ("L12 改判/塞金额被抓", L12_check_catches_tampering),
        ("L13 族金额算错被抓", L13_check_catches_family_arithmetic),
        ("L14 句子引用自己的计数", L14_sentence_cites_own_counts),
        ("L15 考试次数分档，不混算", L15_trials_are_counted_separately),
        ("L16 独立抽样期望按 p^次数", L16_independence_expectation),
        ("L17 同窗同宇宙规则漂移被抓", L17_crosscheck_refuses_rule_drift),
    ]:
        leg(name, fn)

    passed = sum(1 for _n, ok, _m in legs if ok)
    for name, ok, msg in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  <- " + msg))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return main_check()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
