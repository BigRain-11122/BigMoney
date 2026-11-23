"""How long the 20% cap has been standing, not just whether it is breached today.

`regime_cap_measure_sizes.py` answers "which reading of the cap is right, and how many CNY
apart are they". `regime_cap_compliance_cost.py` answers "what would it cost to comply now".
Neither answers the question a reader asks after seeing today's number twice: *was this ever
complied with, and what happened next?*

That question is answerable from faces already on disk, per session:

  * `results/paper_export/export-YYYY-MM-DD.json` -- one file per exported session, each
    carrying per-account equity / positions_value (so a position weight per session);
  * `results/regime_state.json` -- the regime label history, so "the cap was binding" can be
    read rather than assumed (R-配3 only caps during the major-bear state);
  * the daily export's own `operations_today` -- the exit/entry legs that moved the weight,
    with quantities, so a compliance episode can be described by what was actually traded.

What this face measures (all read-only, nothing is booked):

  1. per account, the position weight on every exported session, and which of those sessions
     the regime face had labelled as binding;
  2. contiguous compliant episodes *inside* the binding window -- the days the account was at
     or below the cap while the cap applied;
  3. for each such episode, the exit leg that produced it and the entry leg that ended it:
     how much went out, how much came back, and the round-trip friction at the single-source
     one-way rate (`knowledge.cost_spec.X1_SELL_RATE`);
  4. a cross-gate to the published cap face, per account to the fen (r1934: an input that
     moved is STALE, not zero).

Verdicts:

  CANNOT_READ_CAP_FACE                     the published cap face is missing/unreadable
  CANNOT_READ_EXPORT_FACE                  no exported session to measure
  NO_BINDING_SESSIONS_LABELLED             no exported session carries the binding label
                                           (nothing here is a violation; the face refuses to
                                           answer "how long" when it cannot read "when")
  FACES_ARE_ONE_GENERATION_APART           export tail and cap face cutoff disagree -> STALE
  READING_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE   per-account excess disagrees -> STALE
  CAP_NEVER_MET_WHILE_BINDING              every binding session was above the cap
  CAP_MET_AND_HELD                         compliant episode exists and the last session is still
                                           compliant
  CAP_MET_ONCE_THEN_RELEVERAGED             compliant episode exists but the next above-cap
                                           session within `REENTRY_WINDOW_SESSIONS` restored it
  CAP_COMPLIANT_EPISODES_EXIST             compliant sessions exist without a quick reversal

Reads published faces only. Writes its own new json + md. Changes no rule, edits no page,
books nothing. Whether a re-entry lock should exist is not this face's call.
"""

import argparse
import datetime
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from config import PATHS                     # noqa: E402
from knowledge import cost_spec              # noqa: E402  single-source fee schedule

SCHEMA = "regime-cap-breach-timeline/v1"
ARTIFACT = "results/regime_cap_breach_timeline.json"
DOC = "research/REGIME-CAP-BREACH-TIMELINE.md"

OUT = os.path.join(PATHS.results_dir, "regime_cap_breach_timeline.json")
DOC_PATH = os.path.join(_ROOT, "research", "REGIME-CAP-BREACH-TIMELINE.md")
EXPORT_DIR = os.path.join(PATHS.results_dir, "paper_export")
CAPFACE = os.path.join(PATHS.results_dir, "regime_cap_vs_book.json")
REGFACE = os.path.join(PATHS.results_dir, "regime_state.json")

BINDING_STATE = "RED"          # R-配3 caps only while the major-bear state holds
EXCESS_TOL = 0.01              # one fen: published faces print cents
WEIGHT_EPS = 1e-9
EPISODE_GAP_MAX_DAYS = 10      # binding sessions further apart than this are two episodes
REENTRY_WINDOW_SESSIONS = 5
X1_SELL_RATE = float(cost_spec.X1_SELL_RATE)   # 13.041 bp, one way


# --------------------------------------------------------------------------- inputs

def _read_json(path):
    if not os.path.isfile(path):
        return None, "missing: %s" % os.path.relpath(path, _ROOT)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:                                  # unreadable != empty
        return None, "unreadable: %s (%s)" % (os.path.relpath(path, _ROOT), exc)


def load_cap_face(path=None):
    path = path or CAPFACE
    pay, err = _read_json(path)
    if err:
        return {"cap": None, "cutoff": None, "accounts": {}, "problem": err}
    cap = pay.get("ladder_cap")
    if not isinstance(cap, (int, float)):
        return {"cap": None, "cutoff": pay.get("evidence_cutoff"), "accounts": {},
                "problem": "cap face carries no numeric ladder_cap"}
    accounts = {}
    for a in pay.get("accounts") or []:
        if a.get("name") and isinstance(a.get("excess_cny"), (int, float)):
            accounts[a["name"]] = float(a["excess_cny"])
    return {"cap": float(cap), "cutoff": pay.get("evidence_cutoff"),
            "accounts": accounts, "problem": None}


def load_regime_labels(path=None):
    path = path or REGFACE
    pay, err = _read_json(path)
    if err:
        return {"labels": {}, "first": None, "last": None, "problem": err}
    labels = {}
    for h in pay.get("history") or []:
        if h.get("asof") and h.get("state"):
            labels[h["asof"]] = h["state"]
    if not labels and pay.get("asof") and pay.get("state"):
        labels[pay["asof"]] = pay["state"]
    ds = sorted(labels)
    return {"labels": labels, "first": ds[0] if ds else None,
            "last": ds[-1] if ds else None, "problem": None if labels else "no labelled session"}


def load_exports(paths=None):
    """Read every per-session export. Later duplicate of the same date wins (it was re-drawn)."""
    if paths is None:
        paths = sorted(glob.glob(os.path.join(EXPORT_DIR, "export-*.json")))
    by_date = {}
    duplicates, problems = [], []
    for p in paths:
        pay, err = _read_json(p)
        if err:
            problems.append(err)
            continue
        d = pay.get("export_date")
        if not d:
            problems.append("no export_date: %s" % os.path.basename(p))
            continue
        stamp = pay.get("generated_from_state_updated") or ""
        if d in by_date:
            prev = by_date[d]
            duplicates.append({"date": d, "kept": os.path.basename(p),
                               "dropped": prev["file"]})
            if stamp < (prev["stamp"] or ""):
                continue
        by_date[d] = {"file": os.path.basename(p), "stamp": stamp, "payload": pay}

    series = {}
    dates = sorted(by_date)
    for d in dates:
        pay = by_date[d]["payload"]
        for t in pay.get("traders") or []:
            name = t.get("trader")
            cap = t.get("capital_cny") or {}
            eq, dep = cap.get("equity"), cap.get("positions_value")
            if not name or not isinstance(eq, (int, float)) or not isinstance(dep, (int, float)):
                problems.append("trader without equity/positions on %s: %r" % (d, name))
                continue
            series.setdefault(name, {})[d] = {
                "equity_cny": float(eq),
                "deployed_cny": float(dep),
                "cash_cny": float(cap.get("cash") or 0.0),
                "positions": t.get("open_positions") or [],
                "operations": t.get("operations_today") or [],
            }
    return {"dates": dates, "series": series, "duplicates": duplicates, "problems": problems}


# --------------------------------------------------------------------------- measurement

def _gap_days(a, b):
    try:
        return abs((datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days)
    except Exception:
        return 0


def _weight(dep, eq):
    return (dep / eq) if eq else None


def _price_map(export_row):
    out = {}
    for pos in (export_row or {}).get("positions") or []:
        if pos.get("symbol") and isinstance(pos.get("last_close"), (int, float)):
            out[pos["symbol"]] = float(pos["last_close"])
    return out


def _legs(ops, prices, side):
    """Sum one side of the trade log. `side` is 'out' (exits/reduces) or 'in' (entries)."""
    total, detail, unpriced = 0.0, [], []
    for op in ops or []:
        action = op.get("action")
        sym = op.get("symbol")
        qty_prior = op.get("quantity_prior")
        qty = op.get("quantity")
        if side == "out":
            if action not in ("exit", "qty_change"):
                continue
            q = (qty_prior or 0) - (qty or 0) if action == "qty_change" else (qty_prior or 0)
        else:
            if action != "entry":
                continue
            q = qty or 0
        price = op.get("cost_price") if side == "in" else prices.get(sym)
        if not q:
            continue
        if not isinstance(price, (int, float)):
            unpriced.append(sym)
            detail.append({"symbol": sym, "quantity": round(q, 4), "cny": None})
            continue
        amount = float(q) * float(price)
        total += amount
        detail.append({"symbol": sym, "quantity": round(q, 4), "cny": round(amount, 2)})
    return {"cny": round(total, 2), "legs": detail, "unpriced": unpriced}


def measure_account(name, series, labels, cap, rate):
    dates = sorted(series)
    points = []
    for d in dates:
        row = series[d]
        w = _weight(row["deployed_cny"], row["equity_cny"])
        excess = max(0.0, row["deployed_cny"] - cap * row["equity_cny"])
        points.append({"date": d, "weight": w, "equity_cny": row["equity_cny"],
                       "deployed_cny": row["deployed_cny"], "excess_cny": round(excess, 2),
                       "label": labels.get(d),
                       "above": bool(w is not None and w - cap > WEIGHT_EPS)})
    by_date = {p["date"]: p for p in points}

    binding = [p for p in points if p["label"] == BINDING_STATE]

    # compliant episodes inside the binding window: consecutive compliant binding sessions,
    # split when the binding sessions themselves are far apart
    runs = []
    for p in binding:
        if runs and runs[-1]["above"] == p["above"] and \
                _gap_days(runs[-1]["points"][-1]["date"], p["date"]) <= EPISODE_GAP_MAX_DAYS:
            runs[-1]["points"].append(p)
        else:
            runs.append({"above": p["above"], "points": [p]})

    compliant, reversals = [], []
    binding_dates = [p["date"] for p in binding]
    was_above_any = any(p["above"] for p in points)
    compliant_runs_without_prior_above = 0
    for run in runs:
        if run["above"]:
            continue
        ep = run["points"]
        start, end = ep[0]["date"], ep[-1]["date"]
        prior_above = [p for p in points if p["above"] and p["date"] < start]
        prev_above = prior_above[-1] if prior_above else None
        if prev_above is None:
            # nothing was de-risked here: the account simply never held enough to breach
            compliant_runs_without_prior_above += 1
            continue
        after = [p for p in points if p["date"] > end]
        next_above = next((p for p in after if p["above"]), None)

        exited = round(prev_above["deployed_cny"] - ep[0]["deployed_cny"], 2)
        reentered = round(next_above["deployed_cny"] - ep[-1]["deployed_cny"], 2) if next_above else None

        out_leg = _legs(series[start]["operations"], _price_map(series.get(prev_above["date"])), "out")
        in_row = series.get(next_above["date"]) if next_above else None
        in_leg = _legs(in_row["operations"] if in_row else None, None, "in")

        sold = out_leg["cny"] if out_leg["cny"] > 0 else None
        bought = in_leg["cny"] if in_leg["cny"] > 0 else None
        if sold and bought:
            friction = round((sold + bought) * rate, 2)
        elif exited and reentered and exited > 0 and reentered > 0:
            friction = round((exited + reentered) * rate, 2)
        else:
            friction = None

        rec = {
            "start": start, "end": end, "sessions": len(ep),
            "weight_pct_first": round(ep[0]["weight"] * 100, 2),
            "weight_pct_last": round(ep[-1]["weight"] * 100, 2),
            "prior_above_date": prev_above["date"],
            "prior_above_weight_pct": round(prev_above["weight"] * 100, 2),
            "reentry_date": next_above["date"] if next_above else None,
            "reentry_weight_pct": round(next_above["weight"] * 100, 2) if next_above else None,
            "exited_deployed_cny": exited,
            "reentered_deployed_cny": reentered,
            "sold_leg_cny": sold, "sold_legs": out_leg["legs"], "sold_unpriced": out_leg["unpriced"],
            "bought_leg_cny": bought, "bought_legs": in_leg["legs"],
            "carried_back_share": round(bought / sold, 6) if (sold and bought) else None,
            "round_trip_friction_cny": friction,
            "mechanism": "trade_log" if (sold and bought) else "deployed_series_only",
        }
        if next_above:
            peak = max((p for p in points if p["date"] >= next_above["date"]),
                       key=lambda p: p["weight"] or 0.0)
            rec["post_reentry_peak_weight_pct"] = round((peak["weight"] or 0.0) * 100, 2)
            rec["post_reentry_peak_date"] = peak["date"]
        if next_above:
            run_after = 0
            for p in after:
                if p["date"] == next_above["date"]:
                    break
                run_after += 1
            rec["sessions_until_reentry"] = run_after + 1
        compliant.append(rec)
        if next_above and rec.get("sessions_until_reentry") is not None \
                and rec["sessions_until_reentry"] <= REENTRY_WINDOW_SESSIONS:
            reversals.append(rec)

    last = points[-1] if points else None
    since_compliant = None
    if binding:
        compliant_dates = [r["end"] for r in compliant]
        if compliant_dates:
            idx = max(i for i, d in enumerate(binding_dates) if d <= compliant_dates[-1])
            since_compliant = len(binding_dates) - 1 - idx
        else:
            since_compliant = len(binding_dates)

    return {
        "name": name,
        "sessions_exported": len(points),
        "sessions_above_any": sum(1 for p in points if p["above"]),
        "binding_sessions": len(binding),
        "binding_above": sum(1 for p in binding if p["above"]),
        "was_above_any": was_above_any,
        "always_compliant": (not was_above_any) and bool(points),
        "compliant_runs_without_prior_above": compliant_runs_without_prior_above,
        "binding_history": [{"date": p["date"], "weight_pct": round(p["weight"] * 100, 2),
                             "above": p["above"]} for p in binding],
        "compliant_episodes": compliant,
        "reversals": len(reversals),
        "binding_sessions_since_last_compliant": since_compliant,
        "latest": None if not last else {
            "date": last["date"], "equity_cny": round(last["equity_cny"], 2),
            "deployed_cny": round(last["deployed_cny"], 2),
            "weight_pct": round(last["weight"] * 100, 2),
            "excess_cny": last["excess_cny"], "above": last["above"],
        },
        "_derived": {"all_above": all(p["above"] for p in binding),
                     "always_compliant": (not was_above_any) and bool(points),
                     "all_compliant_latest": bool(last and not last["above"])},
    }


def build(exports=None, labels_face=None, cap_face=None, rate=None, notes=None):
    rate = X1_SELL_RATE if rate is None else float(rate)
    exports = exports if exports is not None else load_exports()
    labels_face = labels_face if labels_face is not None else load_regime_labels()
    cap_face = cap_face if cap_face is not None else load_cap_face()

    cap = cap_face.get("cap")
    labels = labels_face.get("labels") or {}
    dates = exports.get("dates") or []
    problems = list(exports.get("problems") or [])
    if cap_face.get("problem"):
        problems.append(cap_face["problem"])
    if labels_face.get("problem"):
        problems.append(labels_face["problem"])

    payload = {
        "schema": SCHEMA,
        "artifact": ARTIFACT,
        "doc": DOC,
        "cap": cap,
        "binding_state": BINDING_STATE,
        "rate_bp_one_way": round(rate * 10000, 4),
        "export_span": {"first": dates[0] if dates else None,
                        "last": dates[-1] if dates else None,
                        "sessions": len(dates)},
        "labels_span": {"first": labels_face.get("first"), "last": labels_face.get("last"),
                        "labelled_sessions": len(labels)},
        "cap_face_cutoff": cap_face.get("cutoff"),
        "binding_sessions": 0,
        "accounts": [],
        "cross_gate_mismatches": [],
        "input_problems": problems,
    }

    if cap is None:
        payload["verdict"] = "CANNOT_READ_CAP_FACE"
        payload["sentence"] = ("读不到已发布的帽子面（%s），本面不猜帽值，也不评价任何账户。"
                               % (cap_face.get("problem") or "no cap"))
        return payload
    if not dates:
        payload["verdict"] = "CANNOT_READ_EXPORT_FACE"
        payload["sentence"] = "没有任何已导出会话可供度量——缺面不等于 0%，本面拒答。"
        return payload

    binding_dates = [d for d in dates if labels.get(d) == BINDING_STATE]
    payload["binding_sessions"] = len(binding_dates)

    accounts = []
    for name in sorted(exports["series"]):
        accounts.append(measure_account(name, exports["series"][name], labels, cap, rate))
    payload["accounts"] = [{k: v for k, v in a.items() if not k.startswith("_")} for a in accounts]
    derived = {a["name"]: a["_derived"] for a in accounts}
    bound = [a["name"] for a in payload["accounts"] if a.get("binding_sessions", 0) > 0]

    latest_date = dates[-1]
    payload["latest_session"] = latest_date

    # cross-gate: the same six accounts must reproduce the published cap face to the fen
    mismatches = []
    for a in payload["accounts"]:
        pub = (cap_face.get("accounts") or {}).get(a["name"])
        if pub is None or not a.get("latest"):
            continue
        if abs(pub - a["latest"]["excess_cny"]) > EXCESS_TOL:
            mismatches.append({"account": a["name"], "published": pub,
                               "here": a["latest"]["excess_cny"]})
    payload["cross_gate_mismatches"] = mismatches

    disputed = [a["name"] for a in payload["accounts"]
                if a["latest"] and a["latest"]["deployed_cny"] > 0]
    payload["n_above_latest"] = sum(1 for a in payload["accounts"]
                                    if a["latest"] and a["latest"]["above"])
    payload["total_excess_latest_cny"] = round(sum(
        (a["latest"]["excess_cny"] or 0.0) for a in payload["accounts"] if a.get("latest")), 2)
    payload["episodes_total"] = sum(len(a["compliant_episodes"]) for a in payload["accounts"])
    payload["reversals_total"] = sum(a["reversals"] for a in payload["accounts"])
    shares = [e["carried_back_share"] for a in payload["accounts"]
              for e in a["compliant_episodes"] if e.get("carried_back_share")]
    payload["carried_back_share_max"] = max(shares) if shares else None
    frictions = [e["round_trip_friction_cny"] for a in payload["accounts"]
                 for e in a["compliant_episodes"] if e.get("round_trip_friction_cny")]
    payload["round_trip_friction_cny"] = round(sum(frictions), 2) if frictions else None

    # verdict, in the order a reader would ask
    if cap_face.get("cutoff") and cap_face["cutoff"] != latest_date:
        payload["verdict"] = "FACES_ARE_ONE_GENERATION_APART"
    elif mismatches:
        payload["verdict"] = "READING_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE"
    elif not binding_dates:
        payload["verdict"] = "NO_BINDING_SESSIONS_LABELLED"
    elif bound and all(derived[a]["all_above"] for a in bound):
        payload["verdict"] = "CAP_NEVER_MET_WHILE_BINDING"
    elif payload["episodes_total"] and all(
            (a["latest"] is None) or (not a["latest"]["above"]) for a in payload["accounts"]):
        payload["verdict"] = "CAP_MET_AND_HELD"
    elif payload["reversals_total"]:
        payload["verdict"] = "CAP_MET_ONCE_THEN_RELEVERAGED"
    elif payload["episodes_total"]:
        payload["verdict"] = "CAP_COMPLIANT_EPISODES_EXIST"
    else:
        payload["verdict"] = "CAP_NEVER_MET_WHILE_BINDING"

    payload["sentence"] = _sentence(payload)
    if notes:
        payload["notes"] = notes
    return payload


def _fmt(x):
    try:
        return "{:,.0f}".format(float(x))
    except Exception:
        return "读不到"


def _sentence(payload):
    cap_pct = "%.0f%%" % (payload["cap"] * 100) if payload["cap"] else "读不到"
    n_bind = payload["binding_sessions"]
    n_above = payload["n_above_latest"]
    total = payload["total_excess_latest_cny"]
    parts = []
    parts.append("帽子（%s）在 %d 个被标注为 %s 的交易日里生效，最近一个会话 %d 户在帽子上方，"
                 "合计超帽 %s 元。"
                 % (cap_pct, n_bind, BINDING_STATE, n_above, _fmt(total)))
    eps = [(a["name"], e) for a in payload["accounts"] for e in a["compliant_episodes"]]
    if not eps:
        parts.append("这些被标注的日子里没有任何账户回到过帽内——不是「今天才超」，是「一直没下来」。")
    else:
        for name, e in eps:
            share = e.get("carried_back_share")
            part = ("%s 在 %s 回到帽内（%.2f%%）" % (name, e["start"], e["weight_pct_first"]))
            if e.get("reentry_date"):
                part += "，%s 又以 %.2f%% 回到帽上方" % (e["reentry_date"], e["reentry_weight_pct"])
            if share:
                part += "，买回金额是卖出金额的 **%.1f%%**" % (share * 100)
            if e.get("post_reentry_peak_weight_pct"):
                part += "，买回后最高到 **%.2f%%**（%s）" % (
                    e["post_reentry_peak_weight_pct"], e.get("post_reentry_peak_date"))
            if e.get("round_trip_friction_cny"):
                part += "，来回摩擦 %s 元" % _fmt(e["round_trip_friction_cny"])
            parts.append(part + "。")
        heavier = [(n, e) for n, e in eps
                   if e.get("post_reentry_peak_weight_pct") is not None
                   and e.get("prior_above_weight_pct") is not None
                   and e["post_reentry_peak_weight_pct"] > e["prior_above_weight_pct"]]
        worst = max(heavier, key=lambda t: t[1]["post_reentry_peak_weight_pct"]) if heavier else None
        tail = "也就是说：帽子被执行过一次（%s 三户同日回到帽内），然后被同一批腿原样买回去了" % (
            eps[0][1].get("end") or "")
        if worst:
            tail += "，%d 户买回后比减仓前更重（最高 %s 到 %.2f%%，减仓前是 %.2f%%）" % (
                len(heavier), worst[0], worst[1]["post_reentry_peak_weight_pct"],
                worst[1]["prior_above_weight_pct"])
        tail += "——规则只约束了「当时的库存」，没有约束「下一笔买入」。"
        parts.append(tail)
        last_since = [a["binding_sessions_since_last_compliant"] for a in payload["accounts"]
                      if a.get("binding_sessions_since_last_compliant") is not None
                      and not a.get("always_compliant")]
        if last_since:
            parts.append("距上一次回到帽内已经 %d 个生效会话。" % min(last_since))
    if payload.get("round_trip_friction_cny"):
        parts.append("全部合规回合的来回摩擦合计 %s 元。" % _fmt(payload["round_trip_friction_cny"]))
    return "".join(parts)


# --------------------------------------------------------------------------- docs

def render_md(payload):
    cap = payload.get("cap")
    lines = ["# 帽子立了多久，被绕过几次", ""]
    lines.append("> 生成：%s ｜ 证据截至：%s ｜ 帽子：%s（仅 %s 生效）｜ 判词：`%s`"
                 % (payload.get("generated", ""), (payload.get("export_span") or {}).get("last"),
                    ("%.0f%%" % (cap * 100)) if cap else "读不到", BINDING_STATE,
                    payload.get("verdict")))
    lines.append("")
    lines.append("## 一句话")
    lines.append("")
    lines.append(payload.get("sentence", ""))
    lines.append("")
    lines.append("## 口径")
    lines.append("")
    lines.append("- 仓位 = `positions_value / equity`，逐会话取自 `results/paper_export/export-*.json`；")
    lines.append("- 「生效」= `results/regime_state.json` 的历史里该会话标为 `%s`"
                 "（R-配3 只在大熊市判定期间）；" % BINDING_STATE)
    lines.append("- 未标注的会话**不计入违规**，也不当作合规——本面分开记，不混算；")
    lines.append("- 来回摩擦 = （卖出腿 + 买回腿）× %.3f bp/边（单源 `knowledge.cost_spec.X1_SELL_RATE`）。"
                 % payload.get("rate_bp_one_way", 0))
    lines.append("- 分类与帽值不手抄：帽值读自已发布帽面，逐户超帽金额做交叉门（容差 1 分）。")
    lines.append("")
    lines.append("## 逐户（以最后一个导出会话为准）")
    lines.append("")
    lines.append("| 账户 | 仓位 | 超帽(元) | 生效会话 | 其中超帽 | 合规回合 | 快速买回 | 距上次合规(会话) |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for a in payload.get("accounts") or []:
        lt = a.get("latest") or {}
        if a.get("always_compliant"):
            since = "—（从未超帽）"
        elif a["binding_sessions_since_last_compliant"] is None:
            since = "—"
        else:
            since = str(a["binding_sessions_since_last_compliant"])
        lines.append("| %s | %s%% | %s | %d | %d | %d | %d | %s |"
                     % (a["name"],
                        ("%.2f" % lt.get("weight_pct")) if lt.get("weight_pct") is not None else "—",
                        _fmt(lt.get("excess_cny")), a["binding_sessions"], a["binding_above"],
                        len(a["compliant_episodes"]), a["reversals"], since))
    lines.append("")
    eps = [(a["name"], e) for a in payload.get("accounts") or []
           for e in a.get("compliant_episodes") or []]
    if eps:
        lines.append("## 每一次「回到帽内」都发生了什么")
        lines.append("")
        lines.append("| 账户 | 减仓前 | 帽内 | 买回当日 | 买回后 | 买回后最高 | 卖出腿(元) | 买回腿(元) | 买回/卖出 | 来回摩擦(元) |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for name, e in eps:
            peak = ("%.2f%%（%s）" % (e["post_reentry_peak_weight_pct"], e.get("post_reentry_peak_date"))
                    if e.get("post_reentry_peak_weight_pct") else "—")
            lines.append("| %s | %s%%（%s） | %s%%（%s） | %s | %s | %s | %s | %s | %s | %s |"
                         % (name,
                            e.get("prior_above_weight_pct"), e.get("prior_above_date"),
                            e.get("weight_pct_last"), e.get("end"),
                            e.get("reentry_date") or "—",
                            ("%s%%" % e.get("reentry_weight_pct")) if e.get("reentry_weight_pct") else "—",
                            peak,
                            _fmt(e.get("sold_leg_cny")) if e.get("sold_leg_cny") else "读不到",
                            _fmt(e.get("bought_leg_cny")) if e.get("bought_leg_cny") else "读不到",
                            ("%.1f%%" % (e["carried_back_share"] * 100)) if e.get("carried_back_share") else "—",
                            _fmt(e.get("round_trip_friction_cny")) if e.get("round_trip_friction_cny") else "—"))
        lines.append("")
        lines.append("卖出腿按「减仓前那一会话的收盘价」计价，买回腿按成交成本计；"
                     "读不到价的腿不当作 0，直接写「读不到」。")
        lines.append("")
    lines.append("## 帽子生效期的逐日仓位")
    lines.append("")
    names = [a["name"] for a in payload.get("accounts") or [] if a.get("binding_history")]
    if names:
        hist = {a["name"]: {h["date"]: h for h in a["binding_history"]}
                for a in payload["accounts"] if a.get("binding_history")}
        dates = sorted({h["date"] for a in payload["accounts"] for h in a.get("binding_history") or []})
        lines.append("| 会话 | " + " | ".join(names) + " |")
        lines.append("|---" * (len(names) + 1) + "|")
        for d in dates:
            cells = []
            for n in names:
                h = hist.get(n, {}).get(d)
                cells.append(("%.2f%%%s" % (h["weight_pct"], "" if h["above"] else " ✔")) if h else "—")
            lines.append("| %s | %s |" % (d, " | ".join(cells)))
        lines.append("")
        lines.append("✔ = 该会话在帽内。")
        lines.append("")
    if payload.get("input_problems"):
        lines.append("## 读不到的输入（如实记，不当作 0）")
        lines.append("")
        for p in payload["input_problems"]:
            lines.append("- %s" % p)
        lines.append("")
    if payload.get("cross_gate_mismatches"):
        lines.append("## 交叉门不成立（STALE，不印裁决）")
        lines.append("")
        for m in payload["cross_gate_mismatches"]:
            lines.append("- %s：已发布 %s 元 / 本面 %s 元" % (m["account"], _fmt(m["published"]), _fmt(m["here"])))
        lines.append("")
    lines.append("## 这不是本面能裁决的事")
    lines.append("")
    lines.append("本面只回答「帽子执行过几次、被买回几次、摩擦多少」。" 
                 "要不要加一条「减仓后 N 个交易日内禁止回补」的锁，属于规则改动（红线域），归 GM/CEO，"
                 "本面只把读数摆出来。")
    lines.append("")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- run / check

def run():
    payload = build()
    payload["generated"] = datetime.datetime.now().isoformat(timespec="seconds")
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_md(payload))
    print("verdict: %s" % payload["verdict"])
    print("binding sessions=%d latest=%s above=%d total_excess=%s"
          % (payload["binding_sessions"], payload.get("latest_session"),
             payload["n_above_latest"], _fmt(payload["total_excess_latest_cny"])))
    print("compliant episodes=%d reversals=%d carried_back=%s friction=%s"
          % (payload["episodes_total"], payload["reversals_total"],
             payload.get("carried_back_share_max"), _fmt(payload.get("round_trip_friction_cny"))))
    print("wrote %s" % os.path.relpath(OUT, _ROOT))
    print("wrote %s" % os.path.relpath(DOC_PATH, _ROOT))
    return 0


CHECK_KEYS = ("verdict", "cap", "binding_sessions", "latest_session", "n_above_latest",
              "total_excess_latest_cny", "episodes_total", "reversals_total",
              "carried_back_share_max", "round_trip_friction_cny")


def _diff(published, fresh):
    diffs = []
    for key in CHECK_KEYS:
        if published.get(key) != fresh.get(key):
            diffs.append("%s: published=%r fresh=%r" % (key, published.get(key), fresh.get(key)))
    pub_a = {a["name"]: (a.get("latest") or {}).get("excess_cny") for a in published.get("accounts") or []}
    fresh_a = {a["name"]: (a.get("latest") or {}).get("excess_cny") for a in fresh.get("accounts") or []}
    if pub_a != fresh_a:
        diffs.append("per-account latest excess moved: %d account(s)" % len(
            [n for n in set(pub_a) | set(fresh_a) if pub_a.get(n) != fresh_a.get(n)]))
    return diffs


def check():
    published, err = _read_json(OUT)
    if err:
        print("check: %s" % err)
        return 3
    fresh = build()
    if fresh.get("verdict") in ("FACES_ARE_ONE_GENERATION_APART",
                                "READING_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE"):
        print("check: STALE face")
        print("  verdict now=%s (published=%s)" % (fresh.get("verdict"), published.get("verdict")))
        for m in fresh.get("cross_gate_mismatches") or []:
            print("  cross-gate %s published=%s here=%s" % (m["account"], _fmt(m["published"]), _fmt(m["here"])))
        return 3
    diffs = _diff(published, fresh)
    if diffs:
        print("check: STALE / mismatch")
        for d in diffs:
            print("  " + d)
        return 3
    print("check ok (verdict=%s binding=%d episodes=%d total_excess=%s)"
          % (published.get("verdict"), published.get("binding_sessions"),
             published.get("episodes_total"), _fmt(published.get("total_excess_latest_cny"))))
    return 0


# --------------------------------------------------------------------------- selftest

def _exp(date, weights, ops=None, positions=None, stamp=None):
    """One export payload: weights = {account: deployed_cny}. equity is 1,000,000 for all."""
    return {
        "export_date": date,
        "generated_from_state_updated": stamp or (date + " 15:40:00"),
        "traders": [{
            "trader": n,
            "capital_cny": {"equity": 1000000.0, "positions_value": dep,
                            "cash": 1000000.0 - dep},
            "open_positions": positions or [],
            "operations_today": (ops or {}).get(n, []),
        } for n, dep in weights.items()],
    }


def _exports(rows):
    """rows = list of (date, {account: deployed}) with optional ops/positions dicts."""
    dates, series = [], {}
    for item in rows:
        d, weights = item[0], item[1]
        ops = item[2] if len(item) > 2 else {}
        positions = item[3] if len(item) > 3 else []
        dates.append(d)
        for n, dep in weights.items():
            series.setdefault(n, {})[d] = {"equity_cny": 1000000.0, "deployed_cny": dep,
                                           "cash_cny": 1000000.0 - dep,
                                           "positions": positions, "operations": ops.get(n, [])}
    return {"dates": sorted(dates), "series": series, "duplicates": [], "problems": []}


CAP_OK = {"cap": 0.2, "cutoff": "2026-11-20", "accounts": {"T-1": 700000.0}, "problem": None}


def _selftest():
    ok, fails = 0, []

    def chk(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(name)

    # 1. the live inputs are readable and the cap is the published one
    live_cap = load_cap_face()
    chk("live cap face carries a numeric cap of 20%", live_cap["cap"] == 0.2)
    live_lab = load_regime_labels()
    chk("live regime face carries labelled sessions", bool(live_lab["labels"]))
    chk("the one-way rate is the single-source constant", abs(X1_SELL_RATE - 0.0013041) < 1e-9)

    # 2. no cap face -> refuse, do not value anything at zero
    p = build(exports=_exports([]), labels_face={"labels": {}, "first": None, "last": None,
                                                "problem": "none"},
              cap_face={"cap": None, "cutoff": None, "accounts": {}, "problem": "missing"})
    chk("missing cap face refuses (CANNOT_READ_CAP_FACE)",
        p["verdict"] == "CANNOT_READ_CAP_FACE" and p["accounts"] == [])

    # 3. no exports -> refuse, not '0% everywhere'
    p = build(exports=_exports([]), labels_face={"labels": {"2026-11-20": "RED"},
                                                "first": "2026-11-20", "last": "2026-11-20",
                                                "problem": None}, cap_face=CAP_OK)
    chk("no exported session refuses (CANNOT_READ_EXPORT_FACE)",
        p["verdict"] == "CANNOT_READ_EXPORT_FACE")

    # 4. no binding label -> refuses to say 'how long', never counts 0 violations
    ex = _exports([("2026-11-19", {"T-1": 900000.0}), ("2026-11-20", {"T-1": 900000.0})])
    p = build(exports=ex, labels_face={"labels": {"2026-11-20": "ORANGE"},
                                       "first": "2026-11-20", "last": "2026-11-20",
                                       "problem": None}, cap_face=CAP_OK)
    chk("no binding label -> NO_BINDING_SESSIONS_LABELLED", p["verdict"] == "NO_BINDING_SESSIONS_LABELLED")
    chk("an ORANGE session above cap is not counted as a violation",
        p["accounts"][0]["binding_above"] == 0 and p["binding_sessions"] == 0)

    # 5. the boundary: exactly 20.00% is compliant (rule says <=20%)
    ex = _exports([("2026-11-20", {"T-1": 200000.0})])
    p = build(exports=ex, labels_face={"labels": {"2026-11-20": "RED"}, "first": "2026-11-20",
                                       "last": "2026-11-20", "problem": None},
              cap_face={"cap": 0.2, "cutoff": "2026-11-20", "accounts": {"T-1": 0.0}, "problem": None})
    chk("exactly 20.00% is NOT above the cap", p["accounts"][0]["latest"]["above"] is False)

    # 6. one fen over is above
    ex = _exports([("2026-11-20", {"T-1": 200000.01})])
    p = build(exports=ex, labels_face={"labels": {"2026-11-20": "RED"}, "first": "2026-11-20",
                                       "last": "2026-11-20", "problem": None},
              cap_face={"cap": 0.2, "cutoff": "2026-11-20", "accounts": {"T-1": 0.01}, "problem": None})
    chk("20.000001% IS above the cap", p["accounts"][0]["latest"]["above"] is True)

    # 7. never compliant while binding
    ex = _exports([("2026-11-19", {"T-1": 900000.0}), ("2026-11-20", {"T-1": 900000.0})])
    p = build(exports=ex, labels_face={"labels": {"2026-11-19": "RED", "2026-11-20": "RED"},
                                       "first": "2026-11-19", "last": "2026-11-20", "problem": None},
              cap_face={"cap": 0.2, "cutoff": "2026-11-20", "accounts": {"T-1": 700000.0}, "problem": None})
    chk("all binding sessions above -> CAP_NEVER_MET_WHILE_BINDING",
        p["verdict"] == "CAP_NEVER_MET_WHILE_BINDING")

    # 8. compliant for one session, bought back the next one -> the reversal verdict + numbers
    positions = [{"symbol": "511010", "last_close": 100.0}]
    rows = [
        ("2026-11-18", {"T-1": 900000.0}, {}, positions),
        ("2026-11-19", {"T-1": 100000.0}, {"T-1": [
            {"action": "exit", "symbol": "511010", "quantity_prior": 8000.0}]}, positions),
        ("2026-11-20", {"T-1": 880000.0}, {"T-1": [
            {"action": "entry", "symbol": "511010", "quantity": 7800.0, "cost_price": 100.0}]}, positions),
    ]
    ex = _exports(rows)
    p = build(exports=ex, labels_face={"labels": {"2026-11-18": "RED", "2026-11-19": "RED",
                                                 "2026-11-20": "RED"},
                                       "first": "2026-11-18", "last": "2026-11-20", "problem": None},
              cap_face={"cap": 0.2, "cutoff": "2026-11-20", "accounts": {"T-1": 680000.0}, "problem": None})
    a = p["accounts"][0]
    e = a["compliant_episodes"][0] if a["compliant_episodes"] else {}
    chk("one compliant session then re-entry -> CAP_MET_ONCE_THEN_RELEVERAGED",
        p["verdict"] == "CAP_MET_ONCE_THEN_RELEVERAGED")
    chk("the exit leg is priced from the prior session's close",
        e.get("sold_leg_cny") == 800000.0)
    chk("the entry leg is priced from cost",
        e.get("bought_leg_cny") == 780000.0)
    chk("carried-back share is 97.5%", abs((e.get("carried_back_share") or 0) - 0.975) < 1e-9)
    chk("round-trip friction = (sold+bought)*rate",
        abs((e.get("round_trip_friction_cny") or 0) - round((800000 + 780000) * X1_SELL_RATE, 2)) < 0.011)
    chk("re-entry is within the window and counted as a reversal", a["reversals"] == 1)
    chk("the reversal session is named", e.get("reentry_date") == "2026-11-20")

    # 9. a sale with no trade log still gets measured, but labelled as such
    rows = [("2026-11-19", {"T-1": 900000.0}),
            ("2026-11-20", {"T-1": 100000.0}),
            ("2026-11-21", {"T-1": 900000.0})]
    ex = _exports(rows)
    p = build(exports=ex, labels_face={"labels": {"2026-11-19": "RED", "2026-11-20": "RED",
                                                 "2026-11-21": "RED"},
                                       "first": "2026-11-19", "last": "2026-11-21", "problem": None},
              cap_face={"cap": 0.2, "cutoff": "2026-11-20", "accounts": {"T-1": 700000.0}, "problem": None})
    e = p["accounts"][0]["compliant_episodes"][0]
    chk("a compliant session without a trade log is measured from the series",
        e["mechanism"] == "deployed_series_only" and e["exited_deployed_cny"] == 800000.0)

    # 10. cross-gate: a published number we cannot reproduce is STALE, not a verdict
    ex = _exports([("2026-11-20", {"T-1": 900000.0})])
    p = build(exports=ex, labels_face={"labels": {"2026-11-20": "RED"}, "first": "2026-11-20",
                                       "last": "2026-11-20", "problem": None},
              cap_face={"cap": 0.2, "cutoff": "2026-11-20", "accounts": {"T-1": 690000.0},
                        "problem": None})
    chk("cross-gate mismatch -> READING_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE",
        p["verdict"] == "READING_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE")

    # 11. generation gaps: export tail vs cap cutoff
    p = build(exports=ex, labels_face={"labels": {"2026-11-20": "RED"}, "first": "2026-11-20",
                                       "last": "2026-11-20", "problem": None},
              cap_face={"cap": 0.2, "cutoff": "2026-11-19", "accounts": {"T-1": 700000.0},
                        "problem": None})
    chk("export tail != cap cutoff -> FACES_ARE_ONE_GENERATION_APART",
        p["verdict"] == "FACES_ARE_ONE_GENERATION_APART")

    # 12. held compliance
    rows = [("2026-11-19", {"T-1": 900000.0}), ("2026-11-20", {"T-1": 150000.0}),
            ("2026-11-21", {"T-1": 150000.0})]
    ex = _exports(rows)
    p = build(exports=ex, labels_face={"labels": {"2026-11-19": "RED", "2026-11-20": "RED",
                                                 "2026-11-21": "RED"},
                                       "first": "2026-11-19", "last": "2026-11-21", "problem": None},
              cap_face={"cap": 0.2, "cutoff": "2026-11-21", "accounts": {"T-1": 0.0}, "problem": None})
    chk("compliant and still compliant -> CAP_MET_AND_HELD", p["verdict"] == "CAP_MET_AND_HELD")

    # 13. a hand-edited published number is caught
    fresh = build(exports=_exports([("2026-11-20", {"T-1": 900000.0})]),
                  labels_face={"labels": {"2026-11-20": "RED"}, "first": "2026-11-20",
                               "last": "2026-11-20", "problem": None},
                  cap_face={"cap": 0.2, "cutoff": "2026-11-20", "accounts": {"T-1": 700000.0},
                            "problem": None})
    tampered = json.loads(json.dumps(fresh))
    tampered["total_excess_latest_cny"] += 1.0
    chk("check catches a hand-edited excess", _diff(tampered, fresh) != [])
    chk("check passes on the untouched payload", _diff(fresh, fresh) == [])

    # 14. the selftest must never write the published face (r1929 lesson)
    before = os.path.getmtime(OUT) if os.path.isfile(OUT) else None
    build(exports=_exports([("2026-11-20", {"T-1": 1.0})]),
          labels_face={"labels": {}, "first": None, "last": None, "problem": "none"},
          cap_face=CAP_OK)
    after = os.path.getmtime(OUT) if os.path.isfile(OUT) else None
    chk("selftest never writes the published face", before == after)

    # 15. partial export (an account missing a session) is not read as 0%
    rows = [("2026-11-19", {"T-1": 900000.0, "T-2": 900000.0}),
            ("2026-11-20", {"T-1": 900000.0})]
    ex = _exports(rows)
    p = build(exports=ex, labels_face={"labels": {"2026-11-19": "RED", "2026-11-20": "RED"},
                                       "first": "2026-11-19", "last": "2026-11-20", "problem": None},
              cap_face={"cap": 0.2, "cutoff": "2026-11-20",
                        "accounts": {"T-1": 700000.0, "T-2": 700000.0}, "problem": None})
    t2 = [a for a in p["accounts"] if a["name"] == "T-2"][0]
    chk("an account missing a session is measured on the sessions it has, not filled with 0",
        t2["sessions_exported"] == 1 and t2["binding_sessions"] == 1)

    print("selftest: %d/%d PASS" % (ok, ok + len(fails)))
    for f in fails:
        print("  FAIL: " + f)
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check"))
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args(argv)
    if ns.selftest:
        return _selftest()
    if ns.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
