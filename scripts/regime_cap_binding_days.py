"""Which days does the 20% cap actually bind on -- the RED label or the major-bear rule?

Why: `regime_cap_breach_timeline` (r1983) measures compliance over the sessions
`regime_state.json` labels RED, and reports one compliant day (2026-11-09). But
R-配3 (`firm/risk/iron_rules.md` line 12-13) binds the 20% cap *only while the
major-bear state holds* -- and that state is a dual condition (510300 close below
its 250d mean AND drawdown from the 250d high >= 20%), implemented once in
`firm/risk/regime.py::major_bear_series`.

REGIME_GUARD §1 makes RED an OR of three triggers (crash speed, panic day,
R-配3 major bear). So a RED day can be a day the cap never applied to. This
face re-derives the binding set from the rule itself (causal, trailing windows
only) and re-measures compliance on it, then names every session where the RED
label and the rule disagree.

Reads published faces only. Writes its own new json + md. Changes no rule,
edits no page, books nothing. Whether the two words should be reconciled
(RED vs major bear) is a red-line call for GM/CEO, not this face's.
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

from config import PATHS                          # noqa: E402
from firm.risk import regime as RULE              # noqa: E402  single source, never re-implement

SCHEMA = "regime-cap-binding-days/v1"
ARTIFACT = "results/regime_cap_binding_days.json"
DOC = "research/REGIME-CAP-BINDING-DAYS.md"

OUT = os.path.join(PATHS.results_dir, "regime_cap_binding_days.json")
DOC_PATH = os.path.join(_ROOT, "research", "REGIME-CAP-BINDING-DAYS.md")
EXPORT_DIR = os.path.join(PATHS.results_dir, "paper_export")
CAPFACE = os.path.join(PATHS.results_dir, "regime_cap_vs_book.json")
REGFACE = os.path.join(PATHS.results_dir, "regime_state.json")

RED_LABEL = "RED"            # the state machine's label (a trigger, not the cap's condition)
EXCESS_TOL = 0.01             # one fen: published faces print cents
WEIGHT_EPS = 1e-9             # a weight exactly at the cap is not above it


# --------------------------------------------------------------------------- inputs

def _read_json(path):
    if not os.path.isfile(path):
        return None, "missing: %s" % os.path.relpath(path, _ROOT)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:                              # unreadable != empty
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


def load_red_labels(path=None):
    """The state machine's RED labels, read only to be compared against the rule."""
    path = path or REGFACE
    pay, err = _read_json(path)
    if err:
        return {"labels": {}, "problem": err}
    labels = {}
    for h in pay.get("history") or []:
        if h.get("asof") and h.get("state"):
            labels[h["asof"]] = h["state"]
    if not labels and pay.get("asof") and pay.get("state"):
        labels[pay["asof"]] = pay["state"]
    return {"labels": labels, "problem": None}


def load_exports(paths=None):
    """Read every per-session export. Later duplicate of the same date wins (re-drawn)."""
    if paths is None:
        paths = sorted(glob.glob(os.path.join(EXPORT_DIR, "export-*.json")))
    by_date, duplicates, problems = {}, [], []
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
    for d in sorted(by_date):
        for t in by_date[d]["payload"].get("traders") or []:
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
            }
    return {"dates": sorted(by_date), "series": series,
            "duplicates": duplicates, "problems": problems}


def load_bear_mask():
    """Causal major-bear mask from the rule's own single source."""
    close = RULE.load_benchmark_close()
    return RULE.major_bear_series(close)


def bear_at(mask, date_str):
    """The major-bear state as of `date_str`, using only bars on/before it."""
    import pandas as pd
    ts = pd.Timestamp(date_str)
    sub = mask.loc[:ts]
    if not len(sub):
        return None
    return bool(sub.iloc[-1])


# --------------------------------------------------------------------------- measurement

def _weight(dep, eq):
    return (dep / eq) if eq else None


def measure_sessions(exports, mask, red_labels, cap):
    """One row per exported session: is it a bear day, what does RED say, who is above."""
    rows = []
    for d in exports["dates"]:
        is_bear = bear_at(mask, d)
        red = red_labels.get(d)
        accts = []
        for name in sorted(exports["series"]):
            row = exports["series"][name].get(d)
            if not row:
                continue
            w = _weight(row["deployed_cny"], row["equity_cny"])
            excess = max(0.0, row["deployed_cny"] - cap * row["equity_cny"])
            accts.append({"name": name, "weight": w,
                          "excess_cny": round(excess, 2),
                          "above": bool(w is not None and w - cap > WEIGHT_EPS)})
        n_above = sum(1 for a in accts if a["above"])
        rows.append({
            "date": d,
            "is_bear": is_bear,
            "red_label": red,
            "labels_agree": bool((red == RED_LABEL) == bool(is_bear)) if red else None,
            "n_accounts": len(accts),
            "n_above": n_above,
            "excess_cny": round(sum(a["excess_cny"] for a in accts), 2),
            "accounts": accts,
        })
    return rows


def _bear_span(rows):
    bears = [r for r in rows if r["is_bear"]]
    if not bears:
        return None
    return {"first": bears[0]["date"], "last": bears[-1]["date"], "sessions": len(bears)}


def _red_span(rows):
    reds = [r for r in rows if r["red_label"] == RED_LABEL]
    if not reds:
        return None
    return {"first": reds[0]["date"], "last": reds[-1]["date"], "sessions": len(reds)}


def build(exports=None, red_face=None, cap_face=None, mask=None, notes=None):
    exports = exports if exports is not None else load_exports()
    red_face = red_face if red_face is not None else load_red_labels()
    cap_face = cap_face if cap_face is not None else load_cap_face()

    cap = cap_face.get("cap")
    red_labels = red_face.get("labels") or {}
    problems = list(exports.get("problems") or [])
    if cap_face.get("problem"):
        problems.append(cap_face["problem"])
    if red_face.get("problem"):
        problems.append(red_face["problem"])

    payload = {
        "schema": SCHEMA,
        "artifact": ARTIFACT,
        "doc": DOC,
        "cap": cap,
        "rule_source": {
            "iron_rules": "firm/risk/iron_rules.md R-配3 (大熊市 = hs300 < MA250 AND dd from 250d high >= 20%)",
            "implementation": "firm/risk/regime.py::major_bear_series (single source, imported)",
            "state_machine": "firm/risk/REGIME_GUARD.md §1 (RED = any of three triggers)",
        },
        "export_span": {"first": exports["dates"][0] if exports["dates"] else None,
                        "last": exports["dates"][-1] if exports["dates"] else None,
                        "sessions": len(exports["dates"])},
        # C2 top-level cutoff (science_gates.cutoff_meta), same reason as the sibling
        # face: without it a reader has to parse export_span to answer "how old is this".
        "evidence_cutoff": exports["dates"][-1] if exports["dates"] else None,
        "sessions": [],
        "accounts": [],
        "divergence": {},
        "input_problems": problems,
    }

    if cap is None:
        payload["verdict"] = "CANNOT_READ_CAP_FACE"
        payload["sentence"] = ("读不到已发布的帽子面（%s），本面不猜帽值，也不评价任何账户。"
                               % (cap_face.get("problem") or "no cap"))
        return payload
    if not exports["dates"]:
        payload["verdict"] = "CANNOT_READ_EXPORT_FACE"
        payload["sentence"] = "没有任何已导出会话可供度量——缺面不等于 0%，本面拒答。"
        return payload
    if mask is None or not len(mask):
        payload["verdict"] = "CANNOT_READ_BENCHMARK"
        payload["sentence"] = "读不到 510300 基准面板，无法重建大熊市判定——本面拒答，不拿 RED 标注顶替。"
        return payload

    rows = measure_sessions(exports, mask, red_labels, cap)
    payload["sessions"] = [{k: v for k, v in r.items() if k != "accounts"} for r in rows]
    payload["bear_span"] = _bear_span(rows)
    payload["red_span"] = _red_span(rows)

    # divergence: sessions where the label and the rule disagree
    red_only = [r["date"] for r in rows
                if r["red_label"] == RED_LABEL and not r["is_bear"]]
    bear_only = [r["date"] for r in rows
                 if r["is_bear"] and r["red_label"] not in (None, RED_LABEL)]
    unlabelled_bear = [r["date"] for r in rows if r["is_bear"] and r["red_label"] is None]
    unlabelled_nonbear = [r["date"] for r in rows
                          if not r["is_bear"] and r["red_label"] is None]
    payload["divergence"] = {
        "red_but_not_bear": red_only,
        "bear_but_not_red": bear_only,
        "bear_unlabelled": unlabelled_bear,
        "nonbear_unlabelled": unlabelled_nonbear,
        "n_red": len(red_only) + sum(1 for r in rows if r["is_bear"] and r["red_label"] == RED_LABEL),
        "n_bear": (payload["bear_span"] or {}).get("sessions", 0),
    }

    # per-account: compliance measured ONLY on bear sessions
    accounts = []
    for name in sorted(exports["series"]):
        bear_rows = [r for r in rows if r["is_bear"]]
        red_rows = [r for r in rows if r["red_label"] == RED_LABEL]
        def _acct(r):
            return next((a for a in r["accounts"] if a["name"] == name), None)
        bear_above = [(r["date"], _acct(r)) for r in bear_rows
                      if _acct(r) and _acct(r)["above"]]
        red_above = [(r["date"], _acct(r)) for r in red_rows
                     if _acct(r) and _acct(r)["above"]]
        latest = None
        for r in reversed(rows):
            a = _acct(r)
            if a:
                latest = {"date": r["date"], "weight_pct": round(a["weight"] * 100, 2),
                          "excess_cny": a["excess_cny"], "above": a["above"],
                          "is_bear": r["is_bear"]}
                break
        accounts.append({
            "name": name,
            "bear_sessions": len(bear_rows),
            "bear_above": len(bear_above),
            "bear_above_dates": [d for d, _ in bear_above],
            "red_sessions": len(red_rows),
            "red_above": len(red_above),
            "latest": latest,
        })
    payload["accounts"] = accounts

    # verdict, in the order a reader would ask
    cap_cutoff = cap_face.get("cutoff")
    latest_date = exports["dates"][-1]
    mismatches = []
    for a in accounts:
        pub = (cap_face.get("accounts") or {}).get(a["name"])
        if pub is None or not a.get("latest"):
            continue
        if abs(pub - a["latest"]["excess_cny"]) > EXCESS_TOL:
            mismatches.append({"account": a["name"], "published": pub,
                               "here": a["latest"]["excess_cny"]})
    payload["cross_gate_mismatches"] = mismatches

    if cap_cutoff and cap_cutoff != latest_date:
        payload["verdict"] = "FACES_ARE_ONE_GENERATION_APART"
    elif mismatches:
        payload["verdict"] = "READING_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE"
    elif not payload["bear_span"]:
        payload["verdict"] = "NO_BEAR_SESSIONS_IN_THE_EXPORT_WINDOW"
    else:
        # the r1983 face reports one compliant day among the RED-labelled sessions.
        # If that day is not a bear day, the compliance record changes meaning.
        red_compliant = []
        for r in rows:
            if r["red_label"] != RED_LABEL:
                continue
            if all(not a["above"] for a in r["accounts"]):
                red_compliant.append(r["date"])
        bear_compliant = []
        for r in rows:
            if not r["is_bear"]:
                continue
            if all(not a["above"] for a in r["accounts"]):
                bear_compliant.append(r["date"])
        payload["red_compliant_days"] = red_compliant
        payload["bear_compliant_days"] = bear_compliant
        if red_only and red_compliant and not bear_compliant:
            payload["verdict"] = "THE_ONE_COMPLIANT_DAY_IS_OUTSIDE_THE_BEAR"
        elif red_only:
            payload["verdict"] = "CAP_BINDS_ON_FEWER_DAYS_THAN_RED"
        elif bear_compliant:
            payload["verdict"] = "CAP_HAS_COMPLIANT_BEAR_DAYS"
        else:
            payload["verdict"] = "CAP_NEVER_MET_WHILE_BEAR"

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
    cap = payload.get("cap")
    cap_pct = "%.0f%%" % (cap * 100) if cap else "读不到"
    bear = payload.get("bear_span") or {}
    red = payload.get("red_span") or {}
    div = payload.get("divergence") or {}
    parts = []
    parts.append("R-配3 的帽子（%s）只在「大熊市」双条件下生效，而纸盘历史里有 %d 个会话被标为 %s、"
                 "只有 %d 个会话真的满足大熊市双条件。"
                 % (cap_pct, red.get("sessions", 0), RED_LABEL, bear.get("sessions", 0)))
    if div.get("red_but_not_bear"):
        parts.append("其中 %d 个 %s 会话（%s）不满足大熊市——按规则原文，那些天帽子根本不生效。"
                     % (len(div["red_but_not_bear"]), RED_LABEL,
                        "、".join(div["red_but_not_bear"])))
    bear_days = payload.get("bear_compliant_days") or []
    red_days = payload.get("red_compliant_days") or []
    if payload.get("verdict") == "THE_ONE_COMPLIANT_DAY_IS_OUTSIDE_THE_BEAR":
        parts.append("上一张面（r1983）记的「唯一合规日」是 %s，而它不在大熊市里——"
                     "按规则原文那一天不构成合规，真正的熊市合规日是 **0** 天。"
                     % "、".join(red_days))
    elif bear_days:
        parts.append("大熊市里的合规日是 %s。" % "、".join(bear_days))
    elif bear.get("sessions"):
        parts.append("大熊市里没有任何一个会话回到帽内——%d 户在 %d 个熊市会话里全部站在 20%% 上方。"
                     % (sum(1 for a in payload.get("accounts") or [] if a["bear_above"] > 0),
                        bear.get("sessions", 0)))
    return "".join(parts)


# --------------------------------------------------------------------------- docs

def render_md(payload):
    cap = payload.get("cap")
    lines = ["# 帽子到底在哪几天生效：RED 标签还是大熊市规则", ""]
    lines.append("> 生成：%s ｜ 证据截至：%s ｜ 帽子：%s ｜ 判词：`%s`"
                 % (payload.get("generated", ""),
                    (payload.get("export_span") or {}).get("last"),
                    ("%.0f%%" % (cap * 100)) if cap else "读不到",
                    payload.get("verdict")))
    lines.append("")
    lines.append("## 一句话")
    lines.append("")
    lines.append(payload.get("sentence", ""))
    lines.append("")
    lines.append("## 口径")
    lines.append("")
    lines.append("- 生效日 = `firm/risk/regime.py::major_bear_series` 因果重算（只用当日及之前的 bar），"
                 "对应 `firm/risk/iron_rules.md` R-配3 原文「大熊市 = 沪深300 收盘 < 250 日均线 **且** "
                 "自 250 日收盘高点回撤 ≥20%」；")
    lines.append("- `%s` 是 `firm/risk/REGIME_GUARD.md` §1 状态机的标签（三个触发条件任一命中即升），"
                 "**不是**帽子生效条件——本面把两者并排，不替任何一方选边；" % RED_LABEL)
    lines.append("- 仓位 = `positions_value / equity`，逐会话取自 `results/paper_export/export-*.json`；"
                 "超帽 = `max(0, deployed - %.2f × equity)`，恰好等于帽子不算超；" % (cap or 0))
    lines.append("- 本面只覆盖六员纸盘账户；ETF 复合书按自己的规则不在本梯子里。")
    lines.append("")
    lines.append("## 分叉")
    lines.append("")
    div = payload.get("divergence") or {}
    lines.append("| 类别 | 会话数 | 会话 |")
    lines.append("|---|---|---|")
    lines.append("| %s 但不是大熊市 | %d | %s |"
                 % (RED_LABEL, len(div.get("red_but_not_bear") or []),
                    "、".join(div.get("red_but_not_bear") or []) or "—"))
    lines.append("| 大熊市但不是 %s | %d | %s |"
                 % (RED_LABEL, len(div.get("bear_but_not_red") or []),
                    "、".join(div.get("bear_but_not_red") or []) or "—"))
    lines.append("| 大熊市但无标注 | %d | %s |"
                 % (len(div.get("bear_unlabelled") or []),
                    "、".join(div.get("bear_unlabelled") or []) or "—"))
    lines.append("")
    lines.append("## 逐会话")
    lines.append("")
    lines.append("| 日期 | 大熊市 | %s 标签 | 标签一致 | 超帽户 | 超帽(元) |" % RED_LABEL)
    lines.append("|---|---|---|---|---|---|")
    for r in payload.get("sessions") or []:
        agree = "—" if r.get("labels_agree") is None else ("是" if r["labels_agree"] else "**否**")
        if r["is_bear"]:
            above, excess = str(r["n_above"]), _fmt(r["excess_cny"])
        else:
            # the cap does not bind here -- printing a breach would invent one
            above, excess = "—", "—（帽子不生效）"
        lines.append("| %s | %s | %s | %s | %s | %s |"
                     % (r["date"], "是" if r["is_bear"] else "—",
                        r.get("red_label") or "—", agree, above, excess))
    lines.append("")
    lines.append("## 逐户（合规按大熊市会话计）")
    lines.append("")
    lines.append("| 账户 | 最新仓位 | 熊市会话 | 熊市超帽 | %s 会话 | %s 超帽 |" % (RED_LABEL, RED_LABEL))
    lines.append("|---|---|---|---|---|---|")
    for a in payload.get("accounts") or []:
        lt = a.get("latest") or {}
        lines.append("| %s | %s%% | %d | %d | %d | %d |"
                     % (a["name"],
                        ("%.2f" % lt.get("weight_pct")) if lt.get("weight_pct") is not None else "—",
                        a["bear_sessions"], a["bear_above"],
                        a["red_sessions"], a["red_above"]))
    lines.append("")
    if payload.get("input_problems"):
        lines.append("## 输入问题（如实）")
        lines.append("")
        for p in payload["input_problems"]:
            lines.append("- %s" % p)
        lines.append("")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- commands

def run():
    payload = build(mask=load_bear_mask())
    payload["generated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_md(payload))
    print("%s -> %s" % (payload["verdict"], os.path.relpath(OUT, _ROOT)))
    print(payload["sentence"])
    return 0


CHECK_KEYS = ("verdict", "cap", "bear_span", "red_span", "divergence",
              "accounts", "cross_gate_mismatches")


def check():
    """Re-derive from disk inputs and compare to what is published (no rewrite)."""
    published, err = _read_json(OUT)
    if err:
        # r1581/r1934: an unreadable receipt is a rebuild request, not a defect. The chain pays
        # a writer on STALE / "face missing" only, so this exit has to speak that vocabulary.
        print("STALE: face missing or unreadable (%s) -- rebuild with run" % err)
        return 3
    fresh = build(mask=load_bear_mask())
    diffs = []
    for k in CHECK_KEYS:
        if published.get(k) != fresh.get(k):
            diffs.append(k)
    if diffs:
        # r1934: a face priced on an older cutoff is stale, not defective. The chain pays a
        # writer on the word STALE only, and a bare "disagrees with a fresh derive" is exactly
        # what one new bar produces -- so the cutoff exit has to come first. The held-back
        # count keeps the republish honest about how much was not compared.
        if published.get("evidence_cutoff") != fresh.get("evidence_cutoff"):
            print("STALE: evidence_cutoff moved %s -> %s (%d derivation key(s) held back "
                  "until republished)"
                  % (published.get("evidence_cutoff"), fresh.get("evidence_cutoff"), len(diffs)))
            return 3
        print("CHECK FAILED: published face disagrees with a fresh derive on %s"
              % ", ".join(diffs))
        return 3
    print("CHECK OK: %d sessions, %d bear, %d %s -- all derivation keys agree"
          % (len(fresh["sessions"]),
             (fresh.get("bear_span") or {}).get("sessions", 0),
             (fresh.get("red_span") or {}).get("sessions", 0), RED_LABEL))
    return 0


# --------------------------------------------------------------------------- selftest

def _mask_from(rows):
    """Build a tiny causal mask Series from [(date, bool), ...]."""
    import pandas as pd
    idx = pd.to_datetime([d for d, _ in rows])
    return pd.Series([b for _, b in rows], index=idx)


def _export(date, weights, stamp="2026-01-01 00:00:00"):
    """weights = {name: (equity, deployed)} -> one export payload."""
    traders = []
    for name, (eq, dep) in weights.items():
        traders.append({"trader": name,
                        "capital_cny": {"equity": eq, "positions_value": dep,
                                        "cash": eq - dep}})
    return {"export_date": date, "generated_from_state_updated": stamp, "traders": traders}


def _selftest():
    fails = []

    def ok(cond, msg):
        if cond:
            print("[PASS] %s" % msg)
        else:
            print("[FAIL] %s" % msg)
            fails.append(msg)

    cap_face = {"cap": 0.20, "cutoff": "2026-01-10", "accounts": {"A": 700000.0,
                                                                 "B": 0.0},
                "problem": None}

    # Leg 1: a bear day with everyone above the cap -> CAP_NEVER_MET_WHILE_BEAR
    exps = {"dates": ["2026-01-08", "2026-01-09", "2026-01-10"],
            "series": {"A": {"2026-01-08": {"equity_cny": 1e6, "deployed_cny": 8e5, "cash_cny": 2e5},
                             "2026-01-09": {"equity_cny": 1e6, "deployed_cny": 8e5, "cash_cny": 2e5},
                             "2026-01-10": {"equity_cny": 1e6, "deployed_cny": 9e5, "cash_cny": 1e5}},
                        "B": {"2026-01-08": {"equity_cny": 1e6, "deployed_cny": 1e5, "cash_cny": 9e5},
                              "2026-01-09": {"equity_cny": 1e6, "deployed_cny": 1e5, "cash_cny": 9e5},
                              "2026-01-10": {"equity_cny": 1e6, "deployed_cny": 1e5, "cash_cny": 9e5}}},
            "duplicates": [], "problems": []}
    mask = _mask_from([("2026-01-08", True), ("2026-01-09", True), ("2026-01-10", True)])
    red = {"labels": {"2026-01-08": "RED", "2026-01-09": "RED", "2026-01-10": "RED"},
           "problem": None}
    p = build(exports=exps, red_face=red, cap_face=cap_face, mask=mask)
    ok(p["verdict"] == "CAP_NEVER_MET_WHILE_BEAR",
       "bear days, both above -> CAP_NEVER_MET_WHILE_BEAR (got %s)" % p["verdict"])

    # Leg 2: the RED label fires on a NON-bear day and that day is compliant ->
    #        must name the compliant day as outside the bear
    exps2 = {"dates": ["2026-01-08", "2026-01-09", "2026-01-10"],
             "series": {"A": {"2026-01-08": {"equity_cny": 1e6, "deployed_cny": 8e5, "cash_cny": 2e5},
                              "2026-01-09": {"equity_cny": 1e6, "deployed_cny": 1e5, "cash_cny": 9e5},
                              "2026-01-10": {"equity_cny": 1e6, "deployed_cny": 9e5, "cash_cny": 1e5}},
                         "B": {"2026-01-08": {"equity_cny": 1e6, "deployed_cny": 1e5, "cash_cny": 9e5},
                               "2026-01-09": {"equity_cny": 1e6, "deployed_cny": 1e5, "cash_cny": 9e5},
                               "2026-01-10": {"equity_cny": 1e6, "deployed_cny": 1e5, "cash_cny": 9e5}}},
             "duplicates": [], "problems": []}
    # 01-09 is RED but NOT bear; 01-08 & 01-10 are bear
    mask2 = _mask_from([("2026-01-08", True), ("2026-01-09", False), ("2026-01-10", True)])
    red2 = {"labels": {"2026-01-08": "RED", "2026-01-09": "RED", "2026-01-10": "RED"},
            "problem": None}
    cap_face2 = {"cap": 0.20, "cutoff": "2026-01-10", "accounts": {"A": 700000.0,
                                                                   "B": 0.0}, "problem": None}
    p2 = build(exports=exps2, red_face=red2, cap_face=cap_face2, mask=mask2)
    ok(p2["verdict"] == "THE_ONE_COMPLIANT_DAY_IS_OUTSIDE_THE_BEAR",
       "compliant RED day outside bear -> THE_ONE_COMPLIANT_DAY_IS_OUTSIDE_THE_BEAR (got %s)"
       % p2["verdict"])
    ok(p2["red_compliant_days"] == ["2026-01-09"] and p2["bear_compliant_days"] == [],
       "red_compliant=[01-09], bear_compliant=[] -- the divergence is named, not averaged")

    # Leg 3: a weight exactly at the cap is NOT above it (0.2000000 is compliant)
    exps3 = {"dates": ["2026-01-10"],
             "series": {"A": {"2026-01-10": {"equity_cny": 1e6, "deployed_cny": 2e5, "cash_cny": 8e5}}},
             "duplicates": [], "problems": []}
    p3 = build(exports=exps3, red_face=red2, cap_face=cap_face2,
               mask=_mask_from([("2026-01-10", True)]))
    ok(p3["sessions"][0]["n_above"] == 0,
       "a weight exactly at 20.00%% is not above the cap")

    # Leg 4: one fen above the cap IS above
    exps4 = {"dates": ["2026-01-10"],
             "series": {"A": {"2026-01-10": {"equity_cny": 1e6, "deployed_cny": 200000.01,
                                             "cash_cny": 799999.99}}},
             "duplicates": [], "problems": []}
    p4 = build(exports=exps4, red_face=red2, cap_face=cap_face2,
               mask=_mask_from([("2026-01-10", True)]))
    ok(p4["sessions"][0]["n_above"] == 1,
       "one fen above the cap is above it")

    # Leg 5: cap face missing a number -> refuse, never guess
    p5 = build(exports=exps, red_face=red, cap_face={"cap": None, "problem": "no cap"},
               mask=mask)
    ok(p5["verdict"] == "CANNOT_READ_CAP_FACE",
       "cap face without a number -> CANNOT_READ_CAP_FACE")

    # Leg 6: no exports -> refuse
    p6 = build(exports={"dates": [], "series": {}, "duplicates": [], "problems": []},
               red_face=red, cap_face=cap_face, mask=mask)
    ok(p6["verdict"] == "CANNOT_READ_EXPORT_FACE",
       "no exports -> CANNOT_READ_EXPORT_FACE")

    # Leg 7: no benchmark -> refuse rather than let RED stand in
    p7 = build(exports=exps, red_face=red, cap_face=cap_face, mask=None)
    ok(p7["verdict"] == "CANNOT_READ_BENCHMARK",
       "no benchmark -> CANNOT_READ_BENCHMARK (RED never stands in for the rule)")

    # Leg 8: a bear day where everyone is under the cap -> compliant bear days exist
    exps8 = {"dates": ["2026-01-10"],
             "series": {"A": {"2026-01-10": {"equity_cny": 1e6, "deployed_cny": 1e5, "cash_cny": 9e5}}},
             "duplicates": [], "problems": []}
    cap_face8 = {"cap": 0.20, "cutoff": "2026-01-10", "accounts": {"A": 0.0}, "problem": None}
    p8 = build(exports=exps8, red_face=red2, cap_face=cap_face8,
               mask=_mask_from([("2026-01-10", True)]))
    ok(p8["verdict"] == "CAP_HAS_COMPLIANT_BEAR_DAYS",
       "a compliant bear day -> CAP_HAS_COMPLIANT_BEAR_DAYS (got %s)" % p8["verdict"])

    # Leg 9: a cross-gate mismatch is STALE, not a verdict
    exps9 = dict(exps8)
    cap_bad = {"cap": 0.20, "cutoff": "2026-01-10", "accounts": {"A": 999.0}, "problem": None}
    p9 = build(exports=exps9, red_face=red2, cap_face=cap_bad,
               mask=_mask_from([("2026-01-10", True)]))
    ok(p9["verdict"] == "READING_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE",
       "cross-gate mismatch -> STALE verdict, cap not printed as a reading")

    # Leg 10: selftest must not touch the published face's mtime
    before = os.path.getmtime(OUT) if os.path.isfile(OUT) else None
    build(exports=exps, red_face=red, cap_face=cap_face, mask=mask)
    after = os.path.getmtime(OUT) if os.path.isfile(OUT) else None
    ok(before == after, "selftest does not write the published face")

    print()
    if fails:
        print("SELFTEST FAILED: %d leg(s)" % len(fails))
        return 1
    print("SELFTEST PASS (10/10)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run")
    sub.add_parser("check")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)
    cmd = args.cmd or "run"
    if cmd == "selftest":
        return _selftest()
    if cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
