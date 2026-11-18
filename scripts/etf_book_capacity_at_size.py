"""ETF book -- the size the desk is actually holding, measured on its own five names.

r1826 put the capacity reading on the reader's page and, in the same breath, refused to
say whether today's order fits through the market: the face measured the 1,000,000 lens
with 200,000 in each of ITS five names, while the desk holds 431,880 across a DIFFERENT
five (only one code in common on 2026-11-17). Two things were therefore never measured --
this size, and these names -- and the honest answer was "do not print".

This face measures exactly those two things, with the gate's own ruler (the ADV series is
imported from `etf_book_capacity_edge`, never re-derived here):

  * WHAT THIS ORDER IS. Each of the ticket's own names, its own amount, over its own ADV
    read on the ticket's pricing bar. Printed per name, so the reader can see which
    position is the one that stops the order.
  * HOW MUCH ROOM IS LEFT. Re-using that same per-name reading: the total capital whose
    binding name would sit exactly on the line.
  * WHETHER THE TWO NUMBERS ARE THE SAME BOOK. The published reading's names are compared
    with the ticket's names; when they differ, the page must say "a different five", not
    put the two readings side by side as if one confirmed the other.

Refusals (each is a selftest leg):
  * no ticket -> NO_TICKET, a reason and no number;
  * ticket priced on a bar the panel does not carry -> BAR_MISMATCH, both dates printed,
    no number (r1781: a section fed by another trip stamps itself or it lies);
  * any name without an ADV -> that share is `null`, the aggregate verdict is refused
    (r98: an unmeasured name is not a passing name);
  * a non-positive amount -> the row is rejected by name, never silently dropped from
    the sum.

Usage:
    python scripts/etf_book_capacity_at_size.py run
    python scripts/etf_book_capacity_at_size.py check
    python scripts/etf_book_capacity_at_size.py selftest
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_capacity_at_size.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_capacity_at_size.md")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
STATUS_FACE = os.path.join(ROOT, "results", "etf_wide_update_status.json")
REPRO_TOL_PCT = 0.0005      # the published reading is rounded to 4 dp of a percent
# Verdicts this face is allowed to answer without rebuilding. NO_TICKET and BAR_MISMATCH
# are excluded on purpose: they are the states where "no number" is the product, and a
# stale copy of them must not be allowed to look like a fresh answer.
GATED_VERDICTS = ("ADMIT_AT_THIS_SIZE", "DENY_AT_THIS_SIZE", "UNMEASURABLE_AT_THIS_SIZE")


# ---------------------------------------------------------------- inputs

def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return None


def latest_ticket(dirpath=TICKET_DIR):
    """The newest `TICKET-*.json` by its own date in the file name (not mtime)."""
    paths = sorted(glob.glob(os.path.join(dirpath, "TICKET-*.json")))
    if not paths:
        return None, None
    path = paths[-1]
    stem = os.path.basename(path)[len("TICKET-"):-len(".json")]
    return path, stem


def _sha_file(path):
    """Bytes of one file, or None when it is not readable (never a stand-in value)."""
    if not path:
        return None
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def input_signature(daily_dir=None, ticket_path=None, status_path=None, script_path=None):
    """Fingerprint of what `build` reads, taken without parsing any of it.

    The expensive half of this face is the panel build (~44s: 1,725 csv under data/daily).
    What decides whether that build could return a different number is cheap: the bytes of
    the ticket, the gate face and the collector's own status face, a name/size/mtime census
    of the panel directory (an add, a delete or a rewrite moves one of the three) and this
    script's own bytes, so an edit cannot ride the face it did not rebuild.

    Inputs only, no wall clock: a key that moves with the clock is a gate that never fires.
    """
    if daily_dir is None:
        from config import PATHS
        daily_dir = PATHS.daily_dir
    if ticket_path is None:
        ticket_path, _stem = latest_ticket()
    status_path = STATUS_FACE if status_path is None else status_path
    script_path = os.path.abspath(__file__) if script_path is None else script_path

    names = hashlib.sha256()
    n, size, newest = 0, 0, 0
    if daily_dir and os.path.isdir(daily_dir):
        for fn in sorted(os.listdir(daily_dir)):
            if not fn.endswith(".csv"):
                continue
            try:
                st = os.stat(os.path.join(daily_dir, fn))
            except OSError:
                continue
            n += 1
            size += st.st_size
            newest = max(newest, st.st_mtime_ns)
            names.update(fn.encode("utf-8"))
    return {
        "daily_files": n,
        "daily_bytes": size,
        "daily_newest_mtime_ns": newest,
        "daily_names_sha": names.hexdigest()[:16],
        "ticket": (os.path.basename(ticket_path) if ticket_path else None),
        "ticket_sha": _sha_file(ticket_path),
        "status_sha": _sha_file(status_path),
        "script_sha": _sha_file(script_path),
    }


def input_key(sig):
    return hashlib.sha256(json.dumps(sig, sort_keys=True).encode("utf-8")).hexdigest()


def gate_decision(prev, key):
    """Rebuild unless the face on disk already answered exactly these inputs.

    Conservative on purpose: a missing face, a verdict this face does not gate, or a face
    written before this key existed all rebuild. Skipping leaves both files untouched, so
    the only thing a reader can lose is the wait.
    """
    if not isinstance(prev, dict) or not prev:
        return False, "NO_PREVIOUS_FACE"
    verdict = prev.get("verdict")
    if verdict not in GATED_VERDICTS:
        return False, "PREVIOUS_VERDICT_%s" % verdict
    stored = (prev.get("inputs") or {}).get("key")
    if not stored:
        return False, "PREVIOUS_FACE_HAS_NO_INPUT_KEY"
    if stored != key:
        return False, "INPUTS_CHANGED"
    return True, "SAME_INPUTS"


def ticket_rows(ticket):
    """The sheet's own rows: code, amount, lots. Prices are carried for display only."""
    t = ticket or {}
    tk = t.get("ticket") or {}
    rows = []
    for r in (tk.get("order") or []):
        rows.append({"sym": str(r.get("symbol") or "").strip(),
                     "amount_cny": r.get("amount"),
                     "lots": r.get("lots"),
                     "shares": r.get("shares"),
                     "price": r.get("price"),
                     "weight": r.get("weight")})
    bar = ((t.get("card_agreement") or {}).get("ticket_priced_bar")
           or tk.get("priced_bar"))
    return rows, (str(bar)[:10] if bar else None), tk.get("book_weight"), tk.get("cash_amount")


def load_gate():
    """The gate's published reading + the names it was measured on.  Read-only."""
    import etf_book_capacity_edge as CE
    face = CE.load_gate()
    return {"picks": CE.gate_picks(face), "published": CE.published_reading(face)}


def panel_amt():
    import etf_composite_pf as E
    close, openp, amt, _feats = E.build_panel()
    return amt


# ---------------------------------------------------------------- measurement

def shares_at_size(rows, adv_by_sym):
    """Per name: my amount over that name's ADV, read on the same bar the ADV is read on.

    No averaging and no scaling to an equal-weight lens: the ticket's own amounts are the
    numerator (they differ by rounding to whole lots), and a name with no ADV is `null`
    rather than zero (zero would read as "fits easily").
    """
    out, missing, bad = [], [], []
    for r in rows:
        amt = r.get("amount_cny")
        if amt is None or not isinstance(amt, (int, float)) or amt <= 0:
            bad.append(r.get("sym"))
            continue
        adv = adv_by_sym.get(r["sym"])
        if adv is None or adv <= 0:
            missing.append(r["sym"])
            out.append({"sym": r["sym"], "amount_cny": round(float(amt), 2),
                        "lots": r.get("lots"), "adv_cny": None, "share": None})
            continue
        out.append({"sym": r["sym"], "amount_cny": round(float(amt), 2),
                    "lots": r.get("lots"), "adv_cny": round(float(adv), 2),
                    "share": float(amt) / float(adv)})
    return out, missing, bad


def summarise(measured, line, spent_cny):
    """Everything the sentences may say, derived from the measured rows only."""
    have = [r for r in measured if r.get("share") is not None]
    summary = {
        "n_names": len(measured),
        "n_measurable": len(have),
        "line_pct": round(line * 100.0, 6),
        "spent_cny": (round(float(spent_cny), 2) if spent_cny else None),
        "reading_pct": None,
        "binding": None,
        "headroom_cny_at_line": None,
        "verdict": "UNMEASURABLE_AT_THIS_SIZE",
    }
    if not have:
        return summary
    worst = max(have, key=lambda r: r["share"])
    summary["reading_pct"] = round(worst["share"] * 100.0, 4)
    summary["binding"] = worst["sym"]
    summary["binding_amount_cny"] = worst["amount_cny"]
    # Back the line out of the binding name: the scale factor that would put it exactly
    # on the line, applied to the whole sheet (amounts keep their own proportions).
    factor = (line * worst["adv_cny"]) / worst["amount_cny"]
    summary["headroom_cny_at_line"] = round(sum(r["amount_cny"] for r in have) * factor, 2)
    summary["headroom_multiple"] = factor
    if len(have) < len(measured):
        # a name we could not measure could be the binding one -> no verdict
        summary["verdict"] = "UNMEASURABLE_AT_THIS_SIZE"
    elif worst["share"] <= line:
        summary["verdict"] = "ADMIT_AT_THIS_SIZE"
    else:
        summary["verdict"] = "DENY_AT_THIS_SIZE"
    return summary


def name_set(ticket_syms, published_syms):
    a, b = set(ticket_syms), set(published_syms or [])
    return {"same_book": bool(a) and a == b,
            "n_overlap": len(a & b),
            "only_in_ticket": sorted(a - b),
            "only_in_published": sorted(b - a)}


def sentence(summary, ns, published_pct):
    """One plain sentence, and it never compares two readings that are not one ruler."""
    if summary.get("reading_pct") is None:
        return "今天这张单没有量出读数（有名字读不到成交额），所以不印「过线/没过线」。"
    head = ("按今天这张单自己的五个名字、自己的金额量：最紧的一席 %s 占它自己成交额的 "
            "%.4f%%，闸线 %.2f%% → **%s**。" % (
                summary["binding"], summary["reading_pct"], summary["line_pct"],
                "过线" if summary["verdict"] == "ADMIT_AT_THIS_SIZE" else
                ("没过线" if summary["verdict"] == "DENY_AT_THIS_SIZE" else "不给判词")))
    if ns.get("same_book"):
        return head + "这张单与准入面量的是同一组五个名字。"
    return (head + "注意：准入面印的 %.4f%% 是**另一组名字**量的（只有 %d 个重合，"
            "它量的是 %s），两个数不是同一把尺子上的同一件事。" % (
                published_pct or 0.0, ns.get("n_overlap") or 0,
                "、".join(ns.get("only_in_published") or []) or "不同名单"))


# ---------------------------------------------------------------- rendering

def render_md(payload):
    s = payload["summary"]
    ns = payload["name_set"]
    L = ["# 今天这张单，在它自己的名字里占多大", "",
         "票面 `%s`（计价 bar `%s`），盘口截止 `%s`。" % (
             payload.get("ticket_file") or "—", payload.get("bar") or "—",
             payload.get("panel_bar") or "—"), "",
         "## 一句话", "", payload.get("sentence") or "", "",
         "## 判词：%s" % s["verdict"], "",
         "| 项 | 读数 |", "| --- | ---: |",
         "| 闸线（单名单日） | %.2f%% ADV |" % (s.get("line_pct") or 0.0),
         "| 今天这张单的读数（最紧一席） | %s |" % (
             ("%.4f%%（%s）" % (s["reading_pct"], s["binding"]))
             if s.get("reading_pct") is not None else "量不出来"),
         "| 这张单买入金额 | %s 元 |" % ("{:,.2f}".format(s.get("spent_cny") or 0)),
         "| 按这张单的比例还能放大到 | %s 元（x%.4f） |" % (
             "{:,.0f}".format(s.get("headroom_cny_at_line") or 0),
             s.get("headroom_multiple") or 0.0),
         "| 准入面印的是 | %s%%（%s） |" % (
             payload["published"].get("impact_pct_of_adv"),
             "同一组名字" if ns.get("same_book") else
             "另一组名字，仅 %d 个重合" % (ns.get("n_overlap") or 0)), ""]
    L += ["## 逐名", "", "| 代码 | 买入金额（元） | 手数 | 该名成交额（元） | 占比% |",
          "| --- | ---: | ---: | ---: | ---: |"]
    for r in payload["rows"]:
        if r.get("share") is None:
            L.append("| %s | %s | %s | 读不到 | — |" % (
                r["sym"], "{:,.2f}".format(r.get("amount_cny") or 0), r.get("lots") or "—"))
            continue
        L.append("| %s | %s | %s | %s | %.4f |" % (
            r["sym"], "{:,.2f}".format(r["amount_cny"]), r.get("lots") or "—",
            "{:,.0f}".format(r["adv_cny"]), r["share"] * 100.0))
    L += ["", "## 限制", ""]
    for c in payload.get("caveats") or []:
        L.append("- " + c)
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- run

def build():
    """Everything up to (not including) writing: keeps `run` testable and honest."""
    path, stem = latest_ticket()
    ticket = _read_json(path)
    if not ticket:
        return {"artifact": "etf_book_capacity_at_size", "verdict": "NO_TICKET",
                "summary": {"verdict": "NO_TICKET", "reading_pct": None},
                "sentence": "票面不存在（`results/etf_book_order/TICKET-*.json` 缺席）——"
                            "没有单子就没有可量的规模，今天不印数。",
                "rows": [], "name_set": {}}
    rows, bar, book_weight, cash = ticket_rows(ticket)
    gate = load_gate()
    pub = gate.get("published") or {}
    line_pct = pub.get("line_pct")
    if not rows or line_pct is None:
        return {"artifact": "etf_book_capacity_at_size", "verdict": "NO_TICKET",
                "summary": {"verdict": "NO_TICKET", "reading_pct": None},
                "sentence": "票面上没有可执行的持仓行，或闸面没有闸线——今天不印数。",
                "rows": [], "name_set": {}}

    import etf_book_capacity_edge as CE
    amt = panel_amt()
    panel_bar = str(amt.index[-1])[:10]
    payload = {
        "artifact": "etf_book_capacity_at_size",
        "face": "results/etf_book_capacity_at_size.json",
        "script": "scripts/etf_book_capacity_at_size.py",
        "ticket_file": os.path.relpath(path, ROOT).replace("\\", "/"),
        "ticket_stem": stem,
        "bar": bar,
        "panel_bar": panel_bar,
        "evidence_cutoff": panel_bar,
        "book_weight": book_weight,
        "cash_cny": cash,
        "published": {"lens": pub.get("lens"), "capital_cny": pub.get("capital_cny"),
                      "per_name_cny": pub.get("per_name_cny"),
                      "impact_pct_of_adv": pub.get("impact_pct_of_adv")},
        "criteria": {"line_pct": float(line_pct),
                     "adv_face": "close x volume, rolling 20 median, read as the median "
                                 "of its last 20 values (imported from etf_book_capacity_edge)",
                     "numerator": "the ticket's own per-name amount, not an equal-weight lens",
                     "verdict_rule": "binding share <= line ADMIT / > line DENY / any name "
                                     "without ADV UNMEASURABLE"},
    }
    if bar and bar != panel_bar:
        payload.update({
            "verdict": "BAR_MISMATCH",
            "summary": {"verdict": "BAR_MISMATCH", "reading_pct": None,
                        "line_pct": float(line_pct)},
            "rows": [{"sym": r["sym"], "amount_cny": r["amount_cny"], "lots": r.get("lots"),
                      "adv_cny": None, "share": None} for r in rows],
            "name_set": name_set([r["sym"] for r in rows], gate.get("picks")),
            "sentence": "票面计价在 %s，盘口最新是 %s——不是同一天，今天不印这个数。" % (
                bar, panel_bar),
        })
        return payload

    adv_by_sym = {}
    for r in rows:
        adv_by_sym[r["sym"]] = CE.adv20_at(amt, r["sym"], amt.index[-1])
    measured, missing, bad = shares_at_size(rows, adv_by_sym)
    summary = summarise(measured, float(line_pct) / 100.0,
                        sum(r["amount_cny"] for r in measured if r.get("amount_cny")))
    summary["unmeasurable"] = missing
    summary["rejected_amounts"] = bad
    ns = name_set([r["sym"] for r in measured], gate.get("picks"))
    payload.update({
        "verdict": summary["verdict"],
        "rows": measured,
        "summary": summary,
        "name_set": ns,
        "sentence": sentence(summary, ns, (pub.get("impact_pct_of_adv") or 0.0)),
        "caveats": [
            "成交额用的是闸自己的口径（收盘价×成交量，中位再取中位），是估计值而且是阶梯状的",
            "「1% ADV」是闸选的线，不是量出来的线；换线，每个数按同一比例移动",
            "这里量的是「这张单能不能从这个市场的成交额里过」，不是「下单后价格会被推到哪」："
            "冲击成本是另一条腿（既有回测里按 8bp/边记）",
            "放大倍数 x%.4f 是一个资本比例，不是一张能下的单：整数手与波动目标都可能把它压得更低" %
            (summary.get("headroom_multiple") or 0.0),
        ],
    })
    return payload


def check(payload):
    problems = []
    s = payload.get("summary") or {}
    v = payload.get("verdict")
    # r1830: a face that only re-derives from its own rows reads perfectly consistent while
    # it answers a ticket the desk no longer holds (r1788/r1311 family: the tooth is "does
    # the face still sit on the bytes that are on disk", not "is the face internally tidy").
    # The chain runs `run` immediately before this check, so this guard is what makes that
    # pairing worth having: a face whose ticket_stem is not the newest TICKET-* on disk is
    # STALE however tidy its rows are.
    _path, _stem = latest_ticket()
    if _stem and payload.get("ticket_stem") and payload["ticket_stem"] != _stem:
        problems.append("面回答的是 %s 的票面，盘上最新是 %s（陈旧面：先跑 run）"
                        % (payload["ticket_stem"], _stem))
    if v in ("ADMIT_AT_THIS_SIZE", "DENY_AT_THIS_SIZE"):
        if s.get("reading_pct") is None or s.get("binding") is None:
            problems.append("给了判词却没有读数/最紧席位")
        rows = payload.get("rows") or []
        if any(r.get("share") is None for r in rows):
            problems.append("有名字没量到成交额，却给了过线/没过线的判词")
        have = [r for r in rows if r.get("share") is not None]
        if have:
            worst = max(have, key=lambda r: r["share"])
            # published reading is rounded to 4 dp of a percent, so the reproduction
            # tolerance has to be that rounding, not machine epsilon
            if abs(worst["share"] * 100.0 - s["reading_pct"]) > 5e-5:
                problems.append("读数不是逐名最大占比（binding 与 rows 不一致）")
            if worst["sym"] != s["binding"]:
                problems.append("最紧席位与逐名表不一致")
            line = (s.get("line_pct") or 0.0)
            want = "ADMIT_AT_THIS_SIZE" if worst["share"] * 100.0 <= line else "DENY_AT_THIS_SIZE"
            if want != v:
                problems.append("判词与读数对不上：%s vs %s" % (want, v))
        if s.get("n_measurable") != len(have):
            problems.append("n_measurable 与逐名表不一致")
    if v == "UNMEASURABLE_AT_THIS_SIZE" and not (s.get("unmeasurable") or []):
        problems.append("判 UNMEASURABLE 却没点名读不到的名字")
    return {"ok": not problems, "problems": problems, "verdict": v,
            "reading_pct": s.get("reading_pct")}


def run(force=False):
    # r1832: this leg costs 43.6s (measured on bm-c r1830) and rides the chain every round,
    # while its inputs move about once a trading day. The gate is what makes it affordable
    # per round: same ticket bytes + same gate face + same panel census + same script bytes
    # => the face on disk is already the answer, so print that it is and touch nothing.
    sig = input_signature()
    key = input_key(sig)
    prev = _read_json(OUT_JSON)
    skip, why = gate_decision(prev, key)
    if skip and not force:
        chk = check(prev)
        print(json.dumps({"artifact": "etf_book_capacity_at_size", "ok": chk["ok"],
                          "no_op": True, "reason": why, "input_key": key,
                          "problems": chk["problems"], "verdict": prev.get("verdict"),
                          "reading_pct": chk["reading_pct"],
                          "binding": (prev.get("summary") or {}).get("binding"),
                          "same_book": (prev.get("name_set") or {}).get("same_book")},
                         ensure_ascii=False))
        return 0 if chk["ok"] else 2
    payload = build()
    payload["inputs"] = {"signature": sig, "key": key}
    with io.open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    with io.open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(payload))
    chk = check(payload)
    print(json.dumps({"artifact": "etf_book_capacity_at_size", "ok": chk["ok"],
                      "no_op": False, "reason": why, "input_key": key,
                      "problems": chk["problems"], "verdict": payload["verdict"],
                      "reading_pct": chk["reading_pct"],
                      "binding": (payload.get("summary") or {}).get("binding"),
                      "same_book": (payload.get("name_set") or {}).get("same_book")},
                     ensure_ascii=False))
    if payload["verdict"] == "NO_TICKET":
        return 2
    return 0 if chk["ok"] else 2


def main_check():
    payload = _read_json(OUT_JSON)
    if not payload:
        print(json.dumps({"ok": False, "problems": ["面未产出"]}, ensure_ascii=False))
        return 2
    chk = check(payload)
    print(json.dumps(chk, ensure_ascii=False))
    return 0 if chk["ok"] else 1


# ---------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as e:
            legs.append((name, False, str(e)))

    LINE = 0.01

    def L1_share_is_amount_over_adv():
        rows = [{"sym": "A", "amount_cny": 100000.0, "lots": 800},
                {"sym": "B", "amount_cny": 50000.0, "lots": 400}]
        m, miss, bad = shares_at_size(rows, {"A": 20e6, "B": 20e6})
        assert abs(m[0]["share"] - 0.005) < 1e-12, m
        assert abs(m[1]["share"] - 0.0025) < 1e-12, m
        assert not miss and not bad

    def L2_binding_is_the_max_not_the_average():
        rows = [{"sym": "A", "amount_cny": 100000.0}, {"sym": "B", "amount_cny": 100000.0}]
        m, _miss, _bad = shares_at_size(rows, {"A": 50e6, "B": 8e6})
        s = summarise(m, LINE, 200000.0)
        assert s["binding"] == "B", s
        assert abs(s["reading_pct"] - 1.25) < 1e-9, s
        # the average (0.725%) would have passed; the max is what the line is about
        assert sum(r["share"] for r in m) / 2 * 100.0 < 1.0 < s["reading_pct"], s
        assert s["verdict"] == "DENY_AT_THIS_SIZE", s

    def L3_verdict_uses_the_fractional_line():
        rows = [{"sym": "A", "amount_cny": 99000.0}]
        s = summarise(shares_at_size(rows, {"A": 10e6})[0], LINE, 99000.0)
        assert s["verdict"] == "ADMIT_AT_THIS_SIZE", s
        rows = [{"sym": "A", "amount_cny": 101000.0}]
        s = summarise(shares_at_size(rows, {"A": 10e6})[0], LINE, 101000.0)
        assert s["verdict"] == "DENY_AT_THIS_SIZE", s

    def L4_a_missing_adv_blocks_the_verdict():
        rows = [{"sym": "A", "amount_cny": 50000.0}, {"sym": "B", "amount_cny": 50000.0}]
        m, miss, _bad = shares_at_size(rows, {"A": 20e6})
        s = summarise(m, LINE, 100000.0)
        assert miss == ["B"], miss
        assert s["verdict"] == "UNMEASURABLE_AT_THIS_SIZE", s
        assert s["reading_pct"] is not None, "已量的名字仍要印出来"

    def L5_zero_or_negative_amount_is_rejected_by_name():
        rows = [{"sym": "A", "amount_cny": 0.0}, {"sym": "B", "amount_cny": -5.0},
                {"sym": "C", "amount_cny": 1000.0}]
        m, _miss, bad = shares_at_size(rows, {"A": 1e6, "B": 1e6, "C": 1e6})
        assert bad == ["A", "B"], bad
        assert [r["sym"] for r in m] == ["C"], m

    def L6_headroom_round_trips_to_the_line():
        rows = [{"sym": "A", "amount_cny": 60000.0}, {"sym": "B", "amount_cny": 40000.0}]
        adv = {"A": 8e6, "B": 400e6}
        m, _miss, _bad = shares_at_size(rows, adv)
        s = summarise(m, LINE, 100000.0)
        cap = s["headroom_cny_at_line"]
        scaled = [{"sym": r["sym"], "amount_cny": r["amount_cny"] * s["headroom_multiple"]}
                  for r in m]
        s2 = summarise(shares_at_size(scaled, adv)[0], LINE, cap)
        assert abs(s2["reading_pct"] - 1.0) < 1e-6, s2
        assert abs(cap - 100000.0 * s["headroom_multiple"]) < 0.01, (cap, s)

    def L7_name_set_difference_is_named():
        ns = name_set(["A", "B", "C"], ["C", "D", "E"])
        assert ns["same_book"] is False
        assert ns["n_overlap"] == 1
        assert ns["only_in_ticket"] == ["A", "B"]
        assert ns["only_in_published"] == ["D", "E"]

    def L8_same_book_is_not_called_different():
        ns = name_set(["A", "B"], ["B", "A"])
        assert ns["same_book"] is True and ns["n_overlap"] == 2

    def L9_sentence_refuses_to_compare_different_names():
        rows = [{"sym": "A", "amount_cny": 100000.0}]
        m, _miss, _bad = shares_at_size(rows, {"A": 20e6})
        s = summarise(m, LINE, 100000.0)
        text = sentence(s, name_set(["A"], ["X", "Y"]), 1.0087)
        assert "另一组名字" in text, text
        assert "1.0087" in text, "另一组名单时仍要点名那个数是谁量出来的"
        text2 = sentence(s, name_set(["A"], ["A"]), 1.0087)
        assert "另一组名字" not in text2 and "同一组" in text2, text2

    def L10_percent_is_percent_not_ratio():
        rows = [{"sym": "A", "amount_cny": 87200.0}]
        m, _miss, _bad = shares_at_size(rows, {"A": 20e6})
        s = summarise(m, LINE, 87200.0)
        assert abs(s["reading_pct"] - 0.436) < 1e-9, s
        assert "%.4f%%" % s["reading_pct"] == "0.4360%"

    def L11_other_bar_prints_both_dates_and_no_number():
        payload = {"artifact": "etf_book_capacity_at_size", "verdict": "BAR_MISMATCH",
                   "summary": {"verdict": "BAR_MISMATCH", "reading_pct": None},
                   "rows": [], "name_set": {}, "bar": "2026-11-11", "panel_bar": "2026-11-17",
                   "published": {}, "sentence": "票面计价在 2026-11-11，盘口最新是 "
                                                 "2026-11-17——不是同一天，今天不印这个数。"}
        md = render_md(payload)
        assert "2026-11-11" in md and "2026-11-17" in md
        assert "量不出来" in md

    def L12_missing_ticket_prints_no_reading():
        payload = {"artifact": "etf_book_capacity_at_size", "verdict": "NO_TICKET",
                   "summary": {"verdict": "NO_TICKET", "reading_pct": None},
                   "rows": [], "name_set": {}, "published": {},
                   "sentence": "票面不存在——今天不印数。"}
        md = render_md(payload)
        assert "今天不印数" in md
        assert "0.0000%" not in md

    def L13_check_catches_a_reading_that_is_not_the_max():
        payload = {"verdict": "ADMIT_AT_THIS_SIZE",
                   "summary": {"verdict": "ADMIT_AT_THIS_SIZE", "reading_pct": 0.5,
                               "binding": "A", "line_pct": 1.0, "n_measurable": 2,
                               "unmeasurable": []},
                   "rows": [{"sym": "A", "share": 0.005}, {"sym": "B", "share": 0.004}]}
        assert check(payload)["ok"] is True, check(payload)
        payload["summary"]["reading_pct"] = 2.0
        assert check(payload)["ok"] is False, "读数与逐名表不符应被抓"

    def L14_check_refuses_a_verdict_on_unmeasured_names():
        payload = {"verdict": "ADMIT_AT_THIS_SIZE",
                   "summary": {"verdict": "ADMIT_AT_THIS_SIZE", "reading_pct": 0.4,
                               "binding": "A", "line_pct": 1.0, "n_measurable": 2,
                               "unmeasurable": []},
                   "rows": [{"sym": "A", "share": 0.004}, {"sym": "B", "share": None}]}
        chk = check(payload)
        assert chk["ok"] is False, "有名字没量到却给判词应被抓"
        assert any("没量到" in p for p in chk["problems"]), chk

    def L15_a_face_answering_an_older_ticket_is_stale():
        payload = {"verdict": "ADMIT_AT_THIS_SIZE", "ticket_stem": "2026-11-17",
                   "summary": {"verdict": "ADMIT_AT_THIS_SIZE", "reading_pct": 0.4,
                               "binding": "A", "line_pct": 1.0, "n_measurable": 1,
                               "unmeasurable": []},
                   "rows": [{"sym": "A", "share": 0.004}]}
        real = globals()["latest_ticket"]
        try:
            globals()["latest_ticket"] = lambda dirpath=None: (
                "results/etf_book_order/TICKET-2026-11-18.json", "2026-11-18")
            chk = check(payload)
            assert chk["ok"] is False, "回答旧票面的面看起来自洽，必须被拒"
            assert any("盘上最新" in p for p in chk["problems"]), chk
            # the other direction: the same payload on the newest ticket is accepted, so
            # the leg fails only when the tooth fires and never when it should not
            payload["ticket_stem"] = "2026-11-18"
            assert check(payload)["ok"] is True, check(payload)
        finally:
            globals()["latest_ticket"] = real

    def L16_the_input_key_carries_no_clock():
        import tempfile
        d = tempfile.mkdtemp()
        daily = os.path.join(d, "daily")
        os.makedirs(daily)
        sig = input_signature(daily_dir=daily, ticket_path=None, status_path="",
                              script_path="")
        assert "generated" not in sig and "ts" not in sig, sig
        assert input_key(sig) == input_key(dict(sig)), "同一份输入必须给同一个键"

    def L17_a_new_ticket_moves_the_key():
        import tempfile
        d = tempfile.mkdtemp()
        ticket = os.path.join(d, "TICKET-2026-11-17.json")
        status = os.path.join(d, "status.json")
        daily = os.path.join(d, "daily")
        os.makedirs(daily)
        with io.open(ticket, "w", encoding="utf-8") as f:
            f.write('{"ticket": {"order": []}}')
        with io.open(status, "w", encoding="utf-8") as f:
            f.write("{}")
        with io.open(os.path.join(daily, "sh510300.csv"), "w", encoding="utf-8") as f:
            f.write("date,close\n2026-11-17,4.0\n")
        kw = dict(daily_dir=daily, ticket_path=ticket, status_path=status, script_path="")
        k1 = input_key(input_signature(**kw))
        with io.open(ticket, "w", encoding="utf-8") as f:
            f.write('{"ticket": {"order": [{"symbol": "sh510300"}]}}')
        k2 = input_key(input_signature(**kw))
        assert k1 != k2, "票面换了内容，键必须换"

    def L18_a_panel_add_or_rewrite_moves_the_key():
        import tempfile
        d = tempfile.mkdtemp()
        daily = os.path.join(d, "daily")
        os.makedirs(daily)
        a = os.path.join(daily, "sh510300.csv")
        with io.open(a, "w", encoding="utf-8") as f:
            f.write("date,close\n2026-11-17,4.0\n")
        kw = dict(daily_dir=daily, ticket_path=None, status_path="", script_path="")
        k0 = input_key(input_signature(**kw))
        # a rewrite: same name, different length
        with io.open(a, "w", encoding="utf-8") as f:
            f.write("date,close,volume\n2026-11-17,4.0,1\n")
        k1 = input_key(input_signature(**kw))
        assert k0 != k1, "面板文件被重写，键必须换"
        # an add: the name census has to see a file the size total alone would hide
        with io.open(os.path.join(daily, "sh510500.csv"), "w", encoding="utf-8") as f:
            f.write("date,close\n2026-11-17,6.0\n")
        k2 = input_key(input_signature(**kw))
        assert k1 != k2, "面板新增一只票，键必须换"

    def L19_only_the_same_inputs_skip_the_build():
        prev = {"verdict": "ADMIT_AT_THIS_SIZE", "inputs": {"key": "K"}}
        assert gate_decision(prev, "K") == (True, "SAME_INPUTS"), gate_decision(prev, "K")
        assert gate_decision(prev, "K2")[0] is False, "输入变了不许跳过"
        assert gate_decision({"verdict": "NO_TICKET", "inputs": {"key": "K"}}, "K")[0] is False, \
            "「没有票面」不是可以筛掉的答案"
        assert gate_decision({"verdict": "BAR_MISMATCH", "inputs": {"key": "K"}}, "K")[0] is False
        assert gate_decision({"verdict": "ADMIT_AT_THIS_SIZE"}, "K")[0] is False, \
            "没有输入键的旧面必须重建"
        assert gate_decision({}, "K")[0] is False
        assert gate_decision(None, "K")[0] is False

    def L20_an_unreadable_ticket_is_not_a_standin():
        import tempfile
        d = tempfile.mkdtemp()
        sig = input_signature(daily_dir=d, ticket_path=os.path.join(d, "nope.json"),
                              status_path=os.path.join(d, "nope2.json"), script_path="")
        assert sig["ticket_sha"] is None and sig["status_sha"] is None, sig
        # a missing file must not hash the same as an empty one
        empty = os.path.join(d, "empty.json")
        with io.open(empty, "w", encoding="utf-8") as f:
            f.write("")
        sig2 = input_signature(daily_dir=d, ticket_path=empty, status_path="", script_path="")
        assert sig2["ticket_sha"] is not None and sig2["ticket_sha"] != sig["ticket_sha"]

    for name, fn in [("L1 占比=金额/成交额", L1_share_is_amount_over_adv),
                     ("L2 最紧席位是最大值不是均值", L2_binding_is_the_max_not_the_average),
                     ("L3 判词用分数闸线", L3_verdict_uses_the_fractional_line),
                     ("L4 缺成交额的名字挡掉判词", L4_a_missing_adv_blocks_the_verdict),
                     ("L5 零/负金额按名拒收", L5_zero_or_negative_amount_is_rejected_by_name),
                     ("L6 资本上限往返落在闸线上", L6_headroom_round_trips_to_the_line),
                     ("L7 名单不同要点名", L7_name_set_difference_is_named),
                     ("L8 同一组名单不许说成不同", L8_same_book_is_not_called_different),
                     ("L9 另一组名字的读数不并列", L9_sentence_refuses_to_compare_different_names),
                     ("L10 百分比不当比率", L10_percent_is_percent_not_ratio),
                     ("L11 异 bar 印两个日期不印数", L11_other_bar_prints_both_dates_and_no_number),
                     ("L12 缺票面不印 0", L12_missing_ticket_prints_no_reading),
                     ("L13 读数不是最大占比时自检抓", L13_check_catches_a_reading_that_is_not_the_max),
                     ("L14 未量全不留判词", L14_check_refuses_a_verdict_on_unmeasured_names),
                     ("L15 回答旧票面的面判陈旧", L15_a_face_answering_an_older_ticket_is_stale),
                     ("L16 输入键里没有钟", L16_the_input_key_carries_no_clock),
                     ("L17 新票面移动输入键", L17_a_new_ticket_moves_the_key),
                     ("L18 面板增/改移动输入键", L18_a_panel_add_or_rewrite_moves_the_key),
                     ("L19 只有同一份输入才跳过重建", L19_only_the_same_inputs_skip_the_build),
                     ("L20 读不出的票面不给假指纹", L20_an_unreadable_ticket_is_not_a_standin)]:
        leg(name, fn)

    ok = all(p for _n, p, _m in legs)
    for n, p, m in legs:
        print("%s %s%s" % ("PASS" if p else "FAIL", n, "" if p else " :: " + m))
    print("etf_book_capacity_at_size selftest %d/%d %s" % (
        sum(1 for _n, p, _m in legs if p), len(legs), "PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    ap.add_argument("--force", action="store_true",
                    help="rebuild even when the inputs are unchanged")
    ns = ap.parse_args(argv)
    if ns.cmd == "selftest":
        return selftest()
    if ns.cmd == "check":
        return main_check()
    return run(force=ns.force)


if __name__ == "__main__":
    raise SystemExit(main())
