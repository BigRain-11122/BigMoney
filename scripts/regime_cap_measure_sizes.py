"""The page says "equity exposure", the iron rule says "total position (stocks+ETF combined)" --
this face prices that wording gap in CNY instead of letting a reader discover it after the fact.

The chain today:

  * `firm/risk/iron_rules.md` R-配3 (CEO red line O-20260923-1820, T0): "大熊市判定期间组合权益
    总仓位 ≤20%（股票+ETF 合计），现金/逆回购 ≥80%";
  * `firm/risk/regime.py` says the same in English: "total equity position <= 20%
    (stocks+ETF combined)";
  * `scripts/ceo_live_usage.LADDER` renders the CEO page line as "红色急跌/熔断态：股票敞口上限 20%".

The rule counts a government-bond ETF as position; the page's word "股票敞口" tells a reader it
does not. Three governed accounts hold 31-58% government-bond ETFs today, so the two readings
part by more than a million CNY -- and a reader who takes the page's word for it would sell that
much less.

Which reading is right is NOT this face's call to make up: it is read from the rule files on
every run. This face:

  1. confirms the rule text is still on disk and says what it says (missing rule text = refuse);
  2. reads the ladder note the CEO page actually renders and records which measure it names;
  3. measures the same six accounts under both readings, with the asset classification taken
     from the ONE existing classifier (`scripts/etf_equity_alpha.py::load_class_map`);
  4. cross-gates reading A against the published cap face per account, to the fen (r1934:
     an input that moved is STALE, not zero);
  5. prices the wording gap: how many CNY a reader would under-count by following the page.

Verdicts:

  CANNOT_READ_RULE_TEXT                neither rule file states the measure -> refuse
  CANNOT_READ_LADDER_NOTE              the ladder carries no note for this state -> refuse
  CANNOT_MEASURE_UNCLASSIFIED_SYMBOL   a holding has no class (named, never counted as 0)
  FACES_ARE_ONE_GENERATION_APART       cap face and export face carry different cutoffs
  READING_A_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE   cross-gate failed -> STALE
  FACES_DISAGREE_ON_AN_ACCOUNT_COUNT   published n_above vs this face's count
  PAGE_AND_RULE_READ_THE_SAME_MEASURE  no wording gap to price
  PAGE_SAYS_EQUITY_EXPOSURE_RULE_SAYS_TOTAL   the gap; its CNY price is printed

Reads published faces + the two rule files only. Writes its own new json + md. Books nothing,
changes no rule, edits no page. The cap value itself is read from the published cap face.
"""

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from config import PATHS

SCHEMA = "regime-cap-wording-gap/v1"
ARTIFACT = "results/regime_cap_measure_sizes.json"
DOC = "research/REGIME-CAP-MEASURE.md"

OUT = os.path.join(PATHS.results_dir, "regime_cap_measure_sizes.json")
DOC_PATH = os.path.join(_ROOT, "research", "REGIME-CAP-MEASURE.md")
EXPORT = os.path.join(PATHS.results_dir, "paper_export", "latest.json")
CAPFACE = os.path.join(PATHS.results_dir, "regime_cap_vs_book.json")

RULE_CN = os.path.join(_ROOT, "firm", "risk", "iron_rules.md")
RULE_EN = os.path.join(_ROOT, "firm", "risk", "regime.py")

MONEY_TOL = 0.01          # one fen: the published faces print cents
ZERO_BETA = ("bond", "money", "commodity")

MEASURE_TOTAL = "total_position_incl_bond_etf"
MEASURE_EQUITY = "equity_exposure_only"

RULE_MARKERS = [
    (RULE_CN, "股票+ETF 合计"),
    (RULE_EN, "stocks+ETF combined"),
]


# --------------------------------------------------------------------------- inputs

def _read_json(path):
    if not os.path.isfile(path):
        return None, "missing: %s" % os.path.relpath(path, _ROOT)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:                                    # unreadable != empty
        return None, "unreadable: %s (%s)" % (os.path.relpath(path, _ROOT), exc)


def read_rule(markers=None):
    """Confirm the rule files still state the counted measure. Missing text = refuse."""
    markers = RULE_MARKERS if markers is None else markers
    hits = []
    for path, marker in markers:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh, 1):
                    if marker in line:
                        hits.append({"file": os.path.relpath(path, _ROOT), "line": i,
                                     "text": line.strip()[:220], "marker": marker})
                        break
        except Exception:
            continue
    problem = None if hits else "no rule file on disk still states the counted measure"
    return {"measure": MEASURE_TOTAL if hits else None,
            "evidence": hits, "problem": problem}


def read_ladder_note(state="RED", ladder=None):
    """Read the note the CEO page actually renders and record which measure it names."""
    if ladder is None:
        try:
            from scripts.ceo_live_usage import LADDER as ladder
        except Exception as exc:
            return {"measure": None, "note": None,
                    "problem": "cannot import the page ladder (%s)" % exc}
    for row in ladder or []:
        name, cap, note = row[0], row[1], (row[2] if len(row) > 2 else "")
        if str(name).upper().startswith(state.upper()):
            note = note or ""
            if "敞口" in note:
                measure = MEASURE_EQUITY
            elif "总仓位" in note or "仓位" in note:
                measure = MEASURE_TOTAL
            else:
                measure = None
            return {"measure": measure, "note": note, "cap": cap,
                    "problem": None if measure else "ladder note names no measure"}
    return {"measure": None, "note": None, "problem": "state %s not in the ladder" % state}


def class_of(symbol, cmap):
    """Map a holding symbol to its asset class using the upstream classifier's map."""
    key = str(symbol).strip().lower()
    for pre in ("sh", "sz"):
        if key.startswith(pre):
            key = key[len(pre):]
    key = key[:6]
    cls, name = cmap.get(key, ("unclassified", ""))
    return cls, name


# --------------------------------------------------------------------------- measurement

def measure_account(trader, cap, cmap):
    """Return both readings for one account. Absent inputs are None, never zero."""
    cap_cny = trader.get("capital_cny") or {}
    equity = cap_cny.get("equity")
    positions = cap_cny.get("positions_value")
    if equity is None or positions is None:
        return {"name": trader.get("trader"), "measurable": False,
                "why": "capital block missing equity or positions_value"}
    equity = float(equity)
    positions = float(positions)

    by_class = {}
    unclassified = []
    rows = []
    for pos in trader.get("open_positions") or []:
        sym = pos.get("symbol")
        mv = pos.get("market_value_cny")
        cls, name = class_of(sym, cmap)
        if mv is None:
            unclassified.append({"symbol": sym, "why": "no market value"})
            continue
        mv = float(mv)
        by_class[cls] = by_class.get(cls, 0.0) + mv
        if cls == "unclassified":
            unclassified.append({"symbol": sym, "why": "no class in the upstream map",
                                 "name": name})
        rows.append({"symbol": sym, "name": name, "class": cls,
                     "market_value_cny": round(mv, 2)})

    equity_exp = by_class.get("equity", 0.0)
    conv = by_class.get("convertible", 0.0)
    zero_beta = sum(by_class.get(c, 0.0) for c in ZERO_BETA)

    def _reading(exposure):
        w = exposure / equity if equity > 0 else None
        excess = max(0.0, exposure - cap * equity)
        above = (exposure > cap * equity + MONEY_TOL) if equity > 0 else None
        return {"exposure_cny": round(exposure, 2),
                "weight": (None if w is None else round(w, 6)),
                "weight_pct": (None if w is None else round(100.0 * w, 4)),
                "excess_cny": round(excess, 2),
                "above_cap": above}

    return {
        "name": trader.get("trader"),
        "measurable": True,
        "equity_cny": round(equity, 2),
        "deployed_cny": round(positions, 2),
        "by_class_cny": {k: round(v, 2) for k, v in sorted(by_class.items())},
        "zero_beta_cny": round(zero_beta, 2),
        "zero_beta_share_of_deployed": (round(zero_beta / positions, 6) if positions > 0 else None),
        "unclassified": unclassified,
        "holdings": rows,
        "total_position": _reading(positions),
        "equity_exposure": _reading(equity_exp),
        "equity_plus_convertible": _reading(equity_exp + conv),
    }


def build(export=None, capface=None, cmap=None, rule=None, ladder_note=None):
    """Pure build from published faces, the rule files and the page's own ladder note."""
    problems = []
    if export is None:
        export, err = _read_json(EXPORT)
        if err:
            problems.append(err)
    if capface is None:
        capface, err = _read_json(CAPFACE)
        if err:
            problems.append(err)
    if cmap is None:
        from etf_equity_alpha import load_class_map
        cmap = load_class_map()
    if rule is None:
        rule = read_rule()
    if ladder_note is None:
        ladder_note = read_ladder_note()

    cap = None
    state = None
    published = {}
    cap_cutoff = None
    if capface:
        cap = capface.get("ladder_cap")
        state = (capface.get("engine") or {}).get("state") or capface.get("state")
        cap_cutoff = capface.get("evidence_cutoff")
        for acc in capface.get("accounts") or []:
            if acc.get("kind") == "ladder" and acc.get("name"):
                published[acc["name"]] = acc
    if ladder_note and ladder_note.get("cap") is not None and cap is not None:
        if abs(float(ladder_note["cap"]) - float(cap)) > 1e-9:
            problems.append("page ladder cap %r != published cap %r"
                            % (ladder_note["cap"], cap))

    export_cutoff = None
    accounts = []
    if export:
        for trader in export.get("traders") or []:
            sc = trader.get("state_cutoff")
            if sc and export_cutoff is None:
                export_cutoff = sc
        if cap is not None:
            for trader in export.get("traders") or []:
                accounts.append(measure_account(trader, cap, cmap))
        else:
            problems.append("cap face carries no ladder_cap")

    measurable = [a for a in accounts if a.get("measurable")]

    # cross-gate: the total-position reading must reproduce the published face, to the fen
    gate_mismatches = []
    for acc in measurable:
        pub = published.get(acc["name"])
        if not pub:
            continue
        mine = acc["total_position"]["excess_cny"]
        theirs = pub.get("excess_cny")
        if theirs is None:
            gate_mismatches.append({"name": acc["name"],
                                    "why": "published face has no excess_cny"})
        elif abs(mine - float(theirs)) > MONEY_TOL:
            gate_mismatches.append({"name": acc["name"],
                                    "mine_cny": mine, "published_cny": round(float(theirs), 2),
                                    "delta_cny": round(mine - float(theirs), 2)})

    unclassified_hits = [(a["name"], u["symbol"]) for a in measurable
                         for u in a["unclassified"]]
    n_above_total = sum(1 for a in measurable if a["total_position"]["above_cap"])
    n_above_equity = sum(1 for a in measurable if a["equity_exposure"]["above_cap"])
    tot_total = round(sum(a["total_position"]["excess_cny"] for a in measurable), 2)
    tot_equity = round(sum(a["equity_exposure"]["excess_cny"] for a in measurable), 2)
    tot_eqc = round(sum(a["equity_plus_convertible"]["excess_cny"] for a in measurable), 2)
    gap = round(tot_total - tot_equity, 2)
    above = [a for a in measurable if a["total_position"]["above_cap"]]
    bond_in_above = round(sum(a["zero_beta_cny"] for a in above), 2)

    published_n_above = capface.get("n_above") if capface else None
    if published_n_above is None and capface:
        published_n_above = sum(1 for a in (capface.get("accounts") or [])
                                if a.get("kind") == "ladder" and a.get("status") == "above_cap")

    rule_measure = (rule or {}).get("measure")
    page_measure = (ladder_note or {}).get("measure")

    if problems:
        verdict = "CANNOT_MEASURE_INPUT_FACE"
    elif not rule_measure:
        verdict = "CANNOT_READ_RULE_TEXT"
    elif not page_measure:
        verdict = "CANNOT_READ_LADDER_NOTE"
    elif unclassified_hits:
        verdict = "CANNOT_MEASURE_UNCLASSIFIED_SYMBOL"
    elif cap_cutoff and export_cutoff and cap_cutoff != export_cutoff:
        verdict = "FACES_ARE_ONE_GENERATION_APART"
    elif gate_mismatches:
        verdict = "READING_A_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE"
    elif published_n_above is not None and int(published_n_above) != n_above_total:
        verdict = "FACES_DISAGREE_ON_AN_ACCOUNT_COUNT"
    elif rule_measure == page_measure:
        verdict = "PAGE_AND_RULE_READ_THE_SAME_MEASURE"
    else:
        verdict = "PAGE_SAYS_EQUITY_EXPOSURE_RULE_SAYS_TOTAL"

    per_acct = "；".join(
        "%s 总仓位 %.2f%%（超 %s）／股票敞口 %.2f%%（其中 %s 元是债券·货币·商品）"
        % (a["name"], a["total_position"]["weight_pct"] or 0.0,
           _fmt(a["total_position"]["excess_cny"]),
           a["equity_exposure"]["weight_pct"] or 0.0, _fmt(a["zero_beta_cny"]))
        for a in above) or "无超帽户"

    if verdict == "PAGE_SAYS_EQUITY_EXPOSURE_RULE_SAYS_TOTAL":
        sentence = (
            "规则原件（firm/risk/iron_rules.md R-配3，CEO 红线 O-20260923-1820）写的是"
            "「组合权益总仓位 ≤%.0f%%（**股票+ETF 合计**）」；CEO 页的阶梯注写的是「**股票敞口**上限 %.0f%%」。"
            "按规则原件，今天 %d 户超帽、合计 %s 元；照页面那句「股票敞口」读，只有 %d 户、%s 元——"
            "**照页面理解会少卖 %s 元**。为什么差这么多：这 %d 个超帽户里合计 %s 元是国债 ETF，"
            "规则要求把它们计入仓位。逐户（按规则原件的总仓位读法）：%s。"
            % ((cap or 0) * 100, (cap or 0) * 100, n_above_total, _fmt(tot_total),
               n_above_equity, _fmt(tot_equity), _fmt(gap), len(above), _fmt(bond_in_above), per_acct))
    elif verdict == "PAGE_AND_RULE_READ_THE_SAME_MEASURE":
        sentence = ("规则原件与 CEO 页阶梯注点名的是同一个量，两种读法在每一户上同解："
                    "合计超 %s 元（%d 户）。逐户：%s。" % (_fmt(tot_total), n_above_total, per_acct))
    elif verdict.startswith("CANNOT_READ"):
        sentence = "本面拒绝读数：%s。先把规则原文或页面阶梯注补齐。" % (
            (rule or {}).get("problem") or (ladder_note or {}).get("problem")
            or problems[0] if (problems or not rule_measure or not page_measure) else "输入不全")
    elif verdict == "CANNOT_MEASURE_UNCLASSIFIED_SYMBOL":
        sentence = "本面拒绝读数：有标的在既有分类器里没有类别（%s）。缺面不是零。" % (
            ", ".join("%s/%s" % h for h in unclassified_hits))
    elif verdict == "FACES_ARE_ONE_GENERATION_APART":
        sentence = ("两张面差一代（帽面切到 %s，持仓面切到 %s），不跨代比数。旧的那张跑一次即可对齐。"
                    % (cap_cutoff, export_cutoff))
    elif verdict == "READING_A_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE":
        sentence = ("本面的总仓位读法无法复现已发布帽面的逐户超额（%d 户不符），输入面动过或算术分叉——"
                    "按 r1934 判例记 STALE，不印裁决。" % len(gate_mismatches))
    else:
        sentence = "输入面不全或户数不一致（发布=%s，本面=%d），先对齐再读数。" % (
            published_n_above, n_above_total)

    return {
        "schema": SCHEMA,
        "artifact": ARTIFACT,
        "doc": DOC,
        "evidence_cutoff": export_cutoff,
        "cap": cap,
        "state": state,
        "cap_face_cutoff": cap_cutoff,
        "export_face_cutoff": export_cutoff,
        "rule": {
            "measure": rule_measure,
            "evidence": (rule or {}).get("evidence") or [],
            "problem": (rule or {}).get("problem"),
        },
        "page": {
            "measure": page_measure,
            "note": (ladder_note or {}).get("note"),
            "problem": (ladder_note or {}).get("problem"),
        },
        "readings_defined": {
            "total_position": "positions_value / equity — what iron_rules R-配3 counts (股票+ETF 合计)",
            "equity_exposure": "equity-class holdings / equity — what the page's word 股票敞口 names",
            "equity_plus_convertible": "equity + convertible / equity — convertible bonds are equity-like",
        },
        "classifier": "scripts/etf_equity_alpha.py::load_class_map (name keywords, single source)",
        "accounts": accounts,
        "n_above_total": n_above_total,
        "n_above_equity": n_above_equity,
        "total_excess_total_cny": tot_total,
        "total_excess_equity_cny": tot_equity,
        "total_excess_equity_plus_convertible_cny": tot_eqc,
        "wording_gap_cny": gap,
        "zero_beta_inside_above_cap_cny": bond_in_above,
        "published_n_above": published_n_above,
        "cross_gate_mismatches": gate_mismatches,
        "unclassified_hits": [{"account": a, "symbol": s} for a, s in unclassified_hits],
        "input_problems": problems,
        "verdict": verdict,
        "sentence": sentence,
    }


def _fmt(x):
    try:
        return "{:,.0f}".format(float(x))
    except Exception:
        return "读不到"


# --------------------------------------------------------------------------- docs

def render_md(payload):
    cap = payload.get("cap")
    lines = ["# 一顶帽子，两种写法", ""]
    lines.append("> 生成：%s ｜ 证据截至：%s ｜ 帽子：%s ｜ 判词：`%s`"
                 % (payload.get("generated", ""), payload.get("evidence_cutoff"),
                    ("%.0f%%" % (cap * 100)) if cap else "读不到", payload.get("verdict")))
    lines.append("")
    lines.append("## 一句话")
    lines.append("")
    lines.append(payload.get("sentence", ""))
    lines.append("")
    lines.append("## 两个量分别出自哪里")
    lines.append("")
    for ev in (payload.get("rule") or {}).get("evidence") or []:
        lines.append("- 规则原件 `%s` L%d：「%s」" % (ev["file"], ev["line"], ev["text"]))
    page = payload.get("page") or {}
    if page.get("note"):
        lines.append("- CEO 页阶梯注：「%s」" % page["note"])
    if (payload.get("rule") or {}).get("problem"):
        lines.append("- 规则原件：**读不到**（%s）" % payload["rule"]["problem"])
    if page.get("problem"):
        lines.append("- 页面阶梯注：**读不到**（%s）" % page["problem"])
    lines.append("")
    lines.append("## 为什么这两个量今天不是同一个数")
    lines.append("")
    lines.append("账户里只要有国债 ETF，两个量就分叉：「总仓位」把它算进去，「股票敞口」不算。"
                 "今天三个超帽户合计 **%s 元**是债券·货币·商品，所以两种读法差 **%s 元**。"
                 % (_fmt(payload.get("zero_beta_inside_above_cap_cny")),
                    _fmt(payload.get("wording_gap_cny"))))
    lines.append("")
    lines.append("分类取自既有分类器 `%s`，本面不另写符号表。" % payload.get("classifier"))
    lines.append("")
    lines.append("## 逐户")
    lines.append("")
    lines.append("| 账户 | 权益(元) | 总仓位（规则读法） | 超帽(元) | 股票敞口（页面字面） | 其中债券·货币·商品(元) |")
    lines.append("|---|---|---|---|---|---|")
    for a in payload.get("accounts") or []:
        if not a.get("measurable"):
            lines.append("| %s | — | — | — | — | — |" % a.get("name"))
            continue
        T, E = a["total_position"], a["equity_exposure"]
        lines.append("| %s | %s | %.2f%%%s | %s | %.2f%%%s | %s |" % (
            a["name"], _fmt(a["equity_cny"]),
            T["weight_pct"] or 0.0, "（超帽）" if T["above_cap"] else "",
            _fmt(T["excess_cny"]),
            E["weight_pct"] or 0.0, "（超帽）" if E["above_cap"] else "",
            _fmt(a["zero_beta_cny"])))
    lines.append("")
    lines.append("## 合计")
    lines.append("")
    lines.append("- 规则读法（总仓位，股票+ETF 合计）：**%d 户**超帽，**%s 元**（与已发布帽面 %s）"
                 % (payload.get("n_above_total"), _fmt(payload.get("total_excess_total_cny")),
                    "逐户相符" if not payload.get("cross_gate_mismatches") else "**不一致**"))
    lines.append("- 页面字面读法（股票敞口）：**%d 户**超帽，**%s 元**"
                 % (payload.get("n_above_equity"), _fmt(payload.get("total_excess_equity_cny"))))
    lines.append("- 若可转债也算股性：**%s 元**（本窗无转债持仓时与上行相同）"
                 % _fmt(payload.get("total_excess_equity_plus_convertible_cny")))
    lines.append("- 两种读法差额（照页面理解会少卖的钱）：**%s 元**"
                 % _fmt(payload.get("wording_gap_cny")))
    lines.append("")
    lines.append("## 本面不做什么")
    lines.append("")
    lines.append("- 不改规则、不改页面文案、不下推荐、不记账（改文案属共享面动作，需无竞争窗）；")
    lines.append("- 不替规则选边：规则读法每次从 `iron_rules.md` / `regime.py` 实读，页面读法每次从"
                 " `ceo_live_usage.LADDER` 的注实读；两处缺一即拒答；")
    lines.append("- 有标的分类不出来时拒答，不把它当 0。")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- run / check

def run():
    import datetime
    payload = build()
    payload["generated"] = datetime.datetime.now().isoformat(timespec="seconds")
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    with open(DOC_PATH, "w", encoding="utf-8") as fh:
        fh.write(render_md(payload))
    print("verdict: %s" % payload["verdict"])
    print("rule=%s page=%s" % (payload["rule"]["measure"], payload["page"]["measure"]))
    print("total=%s (%d above) | equity-only=%s (%d above) | wording gap=%s" % (
        _fmt(payload["total_excess_total_cny"]), payload["n_above_total"],
        _fmt(payload["total_excess_equity_cny"]), payload["n_above_equity"],
        _fmt(payload["wording_gap_cny"])))
    print("wrote %s" % os.path.relpath(OUT, _ROOT))
    print("wrote %s" % os.path.relpath(DOC_PATH, _ROOT))
    return 0


def check():
    published, err = _read_json(OUT)
    if err:
        print("check: %s" % err)
        return 3
    fresh = build()
    diffs = []
    for key in ("verdict", "evidence_cutoff", "cap", "n_above_total", "n_above_equity",
                "total_excess_total_cny", "total_excess_equity_cny", "wording_gap_cny",
                "zero_beta_inside_above_cap_cny"):
        if published.get(key) != fresh.get(key):
            diffs.append("%s: published=%r fresh=%r" % (key, published.get(key), fresh.get(key)))
    if (published.get("rule") or {}).get("measure") != (fresh.get("rule") or {}).get("measure"):
        diffs.append("rule measure moved: %r -> %r"
                     % ((published.get("rule") or {}).get("measure"),
                        (fresh.get("rule") or {}).get("measure")))
    if (published.get("page") or {}).get("measure") != (fresh.get("page") or {}).get("measure"):
        diffs.append("page measure moved: %r -> %r"
                     % ((published.get("page") or {}).get("measure"),
                        (fresh.get("page") or {}).get("measure")))
    if fresh.get("cross_gate_mismatches"):
        diffs.append("cross-gate no longer holds: %d account(s)"
                     % len(fresh["cross_gate_mismatches"]))
    if diffs:
        print("check: STALE / mismatch")
        for d in diffs:
            print("  " + d)
        return 3
    print("check ok (verdict=%s total=%s equity=%s gap=%s)"
          % (published.get("verdict"), _fmt(published.get("total_excess_total_cny")),
             _fmt(published.get("total_excess_equity_cny")),
             _fmt(published.get("wording_gap_cny"))))
    return 0


# --------------------------------------------------------------------------- selftest

def _fixture(bonds=600000.0, equities=300000.0, equity=1000000.0):
    return {"traders": [{
        "trader": "T-1",
        "capital_cny": {"equity": equity, "positions_value": bonds + equities,
                        "cash": equity - bonds - equities},
        "open_positions": [
            {"symbol": "511010", "market_value_cny": bonds * 0.6},
            {"symbol": "511260", "market_value_cny": bonds * 0.4},
            {"symbol": "510300", "market_value_cny": equities},
        ],
        "state_cutoff": "2026-11-20",
    }]}


FAKE_CMAP = {
    "511010": ("bond", "国债ETF"),
    "511260": ("bond", "十年国债ETF"),
    "510300": ("equity", "沪深300ETF"),
    "999999": ("unclassified", ""),
}

RULE_OK = {"measure": MEASURE_TOTAL,
           "evidence": [{"file": "firm/risk/iron_rules.md", "line": 12, "text": "总仓位 ≤20%（股票+ETF 合计）"}],
           "problem": None}
RULE_NONE = {"measure": None, "evidence": [], "problem": "no rule file states the measure"}
NOTE_EQUITY = {"measure": MEASURE_EQUITY, "note": "红色急跌/熔断态：股票敞口上限 20%",
               "cap": 0.20, "problem": None}
NOTE_TOTAL = {"measure": MEASURE_TOTAL, "note": "红色急跌/熔断态：总仓位上限 20%",
              "cap": 0.20, "problem": None}
NOTE_NONE = {"measure": None, "note": "", "cap": 0.20, "problem": "ladder note names no measure"}


def _capface(excess, cutoff="2026-11-20", n_above=1):
    return {"ladder_cap": 0.20, "evidence_cutoff": cutoff, "engine": {"state": "RED"},
            "n_above": n_above,
            "accounts": [{"name": "T-1", "kind": "ladder", "excess_cny": excess,
                          "status": "above_cap"}]}


def _selftest():
    ok = 0
    fails = []

    def chk(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(name)

    # 1. the shipped rule files must still state the counted measure
    live_rule = read_rule()
    chk("the rule files on disk still state 股票+ETF 合计", live_rule["measure"] == MEASURE_TOTAL
        and bool(live_rule["evidence"]))
    chk("both rule files are cited when both exist",
        len(live_rule["evidence"]) == 2)

    # 2. the live ladder note still names a measure the face can read
    live_note = read_ladder_note()
    chk("the live ladder note names a measure", live_note["measure"] in (MEASURE_TOTAL, MEASURE_EQUITY))

    # 3. bond ETFs never enter the equity reading
    p = build(export=_fixture(), capface=_capface(700000.0), cmap=FAKE_CMAP,
              rule=RULE_OK, ladder_note=NOTE_EQUITY)
    a = p["accounts"][0]
    chk("bond ETFs stay out of the equity reading",
        abs(a["equity_exposure"]["exposure_cny"] - 300000.0) < 0.01)
    chk("bonds are counted in the total-position reading",
        abs(a["total_position"]["exposure_cny"] - 900000.0) < 0.01)
    chk("total excess = 700k, equity excess = 100k",
        abs(a["total_position"]["excess_cny"] - 700000.0) < 0.01
        and abs(a["equity_exposure"]["excess_cny"] - 100000.0) < 0.01)

    # 4. the wording gap is the core verdict and its price is printed
    chk("page-wider-than-rule direction yields PAGE_SAYS_EQUITY_EXPOSURE_RULE_SAYS_TOTAL",
        p["verdict"] == "PAGE_SAYS_EQUITY_EXPOSURE_RULE_SAYS_TOTAL")
    chk("wording gap equals total minus equity excess", abs(p["wording_gap_cny"] - 600000.0) < 0.01)
    chk("sentence names the rule file and prices the gap",
        "iron_rules" in p["sentence"] and "少卖" in p["sentence"])

    # 5. when the page names the same measure there is no gap to price
    p2 = build(export=_fixture(), capface=_capface(700000.0), cmap=FAKE_CMAP,
               rule=RULE_OK, ladder_note=NOTE_TOTAL)
    chk("page and rule agreeing yields PAGE_AND_RULE_READ_THE_SAME_MEASURE",
        p2["verdict"] == "PAGE_AND_RULE_READ_THE_SAME_MEASURE")

    # 6. missing rule text -> refuse, not a zero
    p3 = build(export=_fixture(), capface=_capface(700000.0), cmap=FAKE_CMAP,
               rule=RULE_NONE, ladder_note=NOTE_EQUITY)
    chk("missing rule text refuses (CANNOT_READ_RULE_TEXT)", p3["verdict"] == "CANNOT_READ_RULE_TEXT")
    chk("the refusal sentence explains what is missing", "拒绝读数" in p3["sentence"])

    # 7. missing ladder note -> refuse
    p4 = build(export=_fixture(), capface=_capface(700000.0), cmap=FAKE_CMAP,
               rule=RULE_OK, ladder_note=NOTE_NONE)
    chk("missing ladder note refuses (CANNOT_READ_LADDER_NOTE)",
        p4["verdict"] == "CANNOT_READ_LADDER_NOTE")

    # 8. unclassified holding -> refuse, named
    bad = _fixture()
    bad["traders"][0]["open_positions"].append({"symbol": "999999", "market_value_cny": 1000.0})
    p5 = build(export=bad, capface=_capface(700000.0), cmap=FAKE_CMAP,
               rule=RULE_OK, ladder_note=NOTE_EQUITY)
    chk("unclassified holding refuses and is named",
        p5["verdict"] == "CANNOT_MEASURE_UNCLASSIFIED_SYMBOL"
        and p5["unclassified_hits"][0]["symbol"] == "999999")

    # 9. a generation gap is its own verdict
    p6 = build(export=_fixture(), capface=_capface(700000.0, cutoff="2026-11-19"), cmap=FAKE_CMAP,
               rule=RULE_OK, ladder_note=NOTE_EQUITY)
    chk("generation mismatch is FACES_ARE_ONE_GENERATION_APART",
        p6["verdict"] == "FACES_ARE_ONE_GENERATION_APART")

    # 10. the cross-gate must trip on a 1 CNY disagreement -> STALE, not a verdict
    p7 = build(export=_fixture(), capface=_capface(700001.0), cmap=FAKE_CMAP,
               rule=RULE_OK, ladder_note=NOTE_EQUITY)
    chk("1 CNY disagreement trips the cross-gate into the STALE verdict",
        p7["verdict"] == "READING_A_DOES_NOT_REPRODUCE_THE_PUBLISHED_FACE"
        and bool(p7["cross_gate_mismatches"]))

    # 11. an all-equity account makes the two readings identical (no fake gap)
    p8 = build(export=_fixture(bonds=0.0, equities=900000.0), capface=_capface(700000.0),
               cmap=FAKE_CMAP, rule=RULE_OK, ladder_note=NOTE_EQUITY)
    chk("all-equity account: both readings give the same excess",
        abs(p8["total_excess_total_cny"] - p8["total_excess_equity_cny"]) < 0.01)

    # 12. an account below the cap under the equity reading is not reported above
    p9 = build(export=_fixture(bonds=700000.0, equities=100000.0), capface=_capface(700000.0),
               cmap=FAKE_CMAP, rule=RULE_OK, ladder_note=NOTE_EQUITY)
    a9 = p9["accounts"][0]
    chk("10% equity exposure is NOT above the 20% cap under the equity reading",
        a9["equity_exposure"]["above_cap"] is False and a9["equity_exposure"]["excess_cny"] == 0.0)

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
