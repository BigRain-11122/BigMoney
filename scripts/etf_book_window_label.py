"""The row the operator is told to read prints a 2.8-year number under a 6.3-year header.

The CEO one-pager's "该期待什么" table has a column headed 全窗年化 (full-window annual
return). Its first row is the book the operator actually holds -- 5 names, beta overlay,
8 bp -- and under that header it prints **12.78%**, which is the ticket's own backtest:
683 bars starting 2024-01-02. The same book, priced by the same engine from 2020-01-01,
is **7.71%** over 1525 bars (r1214's band ruler measured both cells and its identity arm
reproduced 12.78 to the digit).

r1214 said "the three rows are not one ruler" in a bullet *under* the table. This face
makes the table itself agree with it: the first row's 全窗年化 is taken from the
full-window cell and 12.78% moves to the column it belongs to (2024 起), where it is
compared with the card's 18.35% on the same stretch. No new estimate is introduced --
both numbers already existed in the published face and the diff between them is what
r1214 priced as the "起点" dial (5.04 pp/yr).

Two laws this face obeys:

  * the number the page prints is read from a cell whose identity arm reproduced the
    ticket's own published 12.78% -- a drifted band-ruler face refuses to quote at all
    (IDENTITY_FAILED), it never falls back to "the number we had before";
  * a missing cell reads as unknown, never as zero and never as the short-window value
    sneaking back into the full-window column.

Usage:
    python scripts/etf_book_window_label.py run
    python scripts/etf_book_window_label.py --check
    python scripts/etf_book_window_label.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_band_ruler as BR

OUT_JSON = os.path.join(ROOT, "results", "etf_book_window_label.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_WINDOW_LABEL.md")
TICKET_LATEST = os.path.join(ROOT, "results", "etf_book_order", "latest.json")

# The smallest move worth naming: a quarter of a point of annual return. Below it the two
# windows are the same reading and relabelling the row would be noise.
TOL_PP = 0.25
# The identity arm is allowed to disagree with the ticket's own published number by an
# eighth of a point -- the same allowance r1214 uses for the same comparison.
IDENT_TOL_PP = 0.125

CRITERIA = {
    "tol_pp_per_year": TOL_PP,
    "identity_tol_pp": IDENT_TOL_PP,
    "row": "该期待什么 / row 1 (5 名·可执行单口径·本单这份账)",
    "header_cell": "全窗年化",
    "printed_value_source": "results/etf_book_order/TICKET-*.json :: metrics.book",
    "full_window_source": "results/etf_book_band_ruler.json :: cells[held/causal/ticket].full",
    "verdict_rule": ("ROW_LABELED_BY_WINDOW iff the value under the 全窗 header and the same book's "
                     "full-window cell differ by >= tol_pp_per_year; SAME_WINDOW if they do not. "
                     "IDENTITY_FAILED refuses every printed row when the cell that supplies the full "
                     "window no longer reproduces the ticket's own published number."),
    "middle_window_source": "results/etf_book_band_ruler.json :: cells[held/causal/ticket].is",
    "segment_additivity_rule": ("the 2020-2023 cell is published only when is.bars + oos.bars == "
                               "full.bars (|delta| <= 1 bar); otherwise it is withheld and the "
                               "page prints a dash -- an unsegmented cell is not a zero"),
    "frozen": "thresholds written before the first run; --check refuses a face whose criteria moved",
}


# ------------------------------------------------------------------ inputs
def _ticket_book(path=TICKET_LATEST):
    """(cagr_pp, bars, window_start) of the executable ticket's own backtest."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        latest = json.load(fh)
    name = latest.get("file")
    if not name:
        return None
    full = os.path.join(os.path.dirname(path), name)
    if not os.path.exists(full):
        return None
    with open(full, encoding="utf-8") as fh:
        tk = json.load(fh)
    book = ((tk.get("metrics") or {}).get("book") or {})
    if book.get("cagr") is None:
        return None
    return {"cagr_pp": round(book["cagr"] * 100, 2),
            "sharpe": round(book.get("sharpe") or 0.0, 3),
            "maxdd_pp": round((book.get("maxdd") or 0.0) * 100, 2),
            "bars": book.get("bars"),
            "artifact": os.path.relpath(full, ROOT).replace(os.sep, "/")}


def _cell(cells, key, seg):
    row = (cells.get(key) or {}).get(seg) or {}
    if row.get("cagr_pp") is None:
        return None
    return {"cagr_pp": row.get("cagr_pp"), "sharpe": row.get("sharpe"),
            "maxdd_pp": row.get("maxdd_pp"), "bars": row.get("bars")}


def _additivity(doc):
    """Do the three windows tile the full one? A cell that does not tile it belongs to
    some other book and is withheld rather than printed beside the two that do."""
    rows = doc.get("rows") or {}
    mid = rows.get("same_book_2020_2023") or {}
    short = rows.get("printed_under_full_header") or {}
    long_ = rows.get("same_book_full_window") or {}
    out = {"middle_bars": mid.get("bars"), "additive": None,
           "rule": CRITERIA["segment_additivity_rule"]}
    if mid.get("bars") is None or short.get("bars") is None or long_.get("bars") is None:
        return out
    total = (mid.get("bars") or 0) + (short.get("bars") or 0)
    out["additive"] = abs(total - (long_.get("bars") or 0)) <= 1
    return out


def build(br_doc=None):
    """Measure the two windows of the operator's own row from the published cells."""
    t0 = time.time()
    if br_doc is None:
        br_doc = BR.read_published()
    doc = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "script": "scripts/etf_book_window_label.py",
           "criteria": CRITERIA, "rows": {}, "identity": {}, "inputs": {}}

    cells = (br_doc or {}).get("cells") or {}
    short = _cell(cells, "held/causal/ticket", "ticket_window")
    long_ = _cell(cells, "held/causal/ticket", "full")
    mid = _cell(cells, "held/causal/ticket", "is")
    tk = _ticket_book()

    doc["inputs"] = {
        "band_ruler_status": (br_doc or {}).get("status"),
        "band_ruler_artifact": (br_doc or {}).get("artifact"),
        "ticket_artifact": (tk or {}).get("artifact"),
        "evidence_cutoff": (br_doc or {}).get("evidence_cutoff"),
    }
    doc["rows"]["printed_under_full_header"] = dict(
        tk or {}, source="the ticket's own backtest, as the page prints it today")
    doc["rows"]["same_book_full_window"] = dict(
        long_ or {}, source="results/etf_book_band_ruler.json :: held/causal/ticket.full")
    doc["rows"]["same_book_2020_2023"] = dict(
        mid or {}, source="results/etf_book_band_ruler.json :: held/causal/ticket.is")
    doc["segments"] = _additivity(doc)

    # identity: the cell that supplies the full window must still reproduce the number the
    # ticket publishes on its own window. If it does not, this face has nothing to say.
    if tk and short:
        delta = round(tk["cagr_pp"] - short["cagr_pp"], 4)
        doc["identity"]["the full-window cell's own window reproduces the ticket"] = {
            "measured_pp": short["cagr_pp"], "published_pp": tk["cagr_pp"],
            "delta_pp": delta, "pass": abs(delta) <= IDENT_TOL_PP}
    else:
        doc["identity"]["the full-window cell's own window reproduces the ticket"] = {
            "measured_pp": None, "published_pp": (tk or {}).get("cagr_pp"),
            "delta_pp": None, "pass": False}

    doc["verdict"] = decide(doc)
    doc["table_row"] = table_row(doc)
    doc["elapsed_sec"] = round(time.time() - t0, 2)
    return doc


# ------------------------------------------------------------------ verdict
def _num(v):
    return v if isinstance(v, (int, float)) else None


def decide(doc):
    """The row's label is a property of the two measures, not of this docstring."""
    ident = doc.get("identity") or {}
    if not all((v or {}).get("pass") for v in ident.values()) or not ident:
        return {"state": "IDENTITY_FAILED",
                "why": ("the band-ruler cell that would supply the full-window number no longer "
                        "reproduces the ticket's own published return; nothing is relabelled"),
                "gap_pp": None}
    short = _num((doc["rows"].get("printed_under_full_header") or {}).get("cagr_pp"))
    long_ = _num((doc["rows"].get("same_book_full_window") or {}).get("cagr_pp"))
    if short is None or long_ is None:
        return {"state": "UNKNOWN", "gap_pp": None,
                "why": "one of the two windows is unreadable; an unread cell is not a zero gap"}
    gap = round(short - long_, 4)
    if abs(gap) >= TOL_PP:
        return {"state": "ROW_LABELED_BY_WINDOW", "gap_pp": gap,
                "why": ("the value under the 全窗 header is the %.2f-year window; the same book over the "
                        "full window reads %.2f%%, i.e. %+.2f pp/yr and the header is not what the cell holds"
                        % (((doc["rows"]["printed_under_full_header"].get("bars") or 0) / 242.0),
                           long_, gap))}
    return {"state": "SAME_WINDOW", "gap_pp": gap,
            "why": "the printed value and the full-window cell agree inside the tolerance"}


def table_row(doc):
    """What the page's first row should print -- None where a number is not published."""
    if (doc.get("verdict") or {}).get("state") != "ROW_LABELED_BY_WINDOW":
        return None
    long_ = doc["rows"].get("same_book_full_window") or {}
    short = doc["rows"].get("printed_under_full_header") or {}
    mid = doc["rows"].get("same_book_2020_2023") or {}
    row = {"full": {"cagr_pct": long_.get("cagr_pp"), "sharpe": long_.get("sharpe"),
                    "maxdd_pct": long_.get("maxdd_pp")},
           "oos": {"cagr_pct": short.get("cagr_pp"), "sharpe": short.get("sharpe"),
                   "maxdd_pct": short.get("maxdd_pp")},
           "full_window_bars": long_.get("bars"),
           "short_window_bars": short.get("bars")}
    # r1216b: the middle window is the same ruler's own cell, so it is published when
    # the three of them tile the full window -- and withheld (the page prints a dash)
    # when they do not, because then it is some other book's segment.
    if mid and (doc.get("segments") or {}).get("additive") is True:
        row["is"] = {"cagr_pct": mid.get("cagr_pp"), "sharpe": mid.get("sharpe"),
                     "maxdd_pct": mid.get("maxdd_pp")}
        row["middle_window_bars"] = mid.get("bars")
    return row


# ------------------------------------------------------------------ publish
def run():
    doc = build()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(doc))
    print("verdict: %s | gap %s pp/yr"
          % (doc["verdict"]["state"], doc["verdict"].get("gap_pp")))
    return 0


def render_md(doc):
    v = doc.get("verdict") or {}
    long_ = doc["rows"].get("same_book_full_window") or {}
    short = doc["rows"].get("printed_under_full_header") or {}
    mid = doc["rows"].get("same_book_2020_2023") or {}
    L = ["# 表头写「全窗」，格子里是 2.8 年", "",
         "证据面：`results/etf_book_window_label.json` ｜ 定价截止 %s"
         % (doc["inputs"].get("evidence_cutoff") or "—"), "",
         "## 研究", "", "**%s**" % v.get("state"), "", "- %s" % (v.get("why") or "—"), "",
         "## 同一本书的两个窗口（你手上这一本：5 名·beta 0.20·8bp）", "",
         "| 窗口 | 年化 | 夏普 | 最大回撤 | bars |", "|---|---|---|---|---|"]
    for label, row in (("页面今天印在「全窗年化」下", short), ("2020-2023 \u5e74\uff08\u540c\u4e00\u628a\u5c3a\u5b50\uff09", mid), ("同一本书从 2020 起（真全窗）", long_)):
        L.append("| %s | %s | %s | %s | %s |"
                 % (label,
                    "—" if row.get("cagr_pp") is None else "%.2f%%" % row["cagr_pp"],
                    "—" if row.get("sharpe") is None else "%.2f" % row["sharpe"],
                    "—" if row.get("maxdd_pp") is None else "%.2f%%" % row["maxdd_pp"],
                    row.get("bars") if row.get("bars") is not None else "—"))
    _seg = doc.get("segments") or {}
    if mid and _seg.get("additive") is True:
        L += ["- 2020-2023 \u6bb5\uff08\u540c\u4e00\u628a\u5c3a\u5b50\uff09\uff1a**%.2f%%**\uff08%s bars\uff09\uff0c\u4e09\u6bb5 bars %s+%s=%s \u6070\u597d\u62fc\u6ee1\u5168\u7a97 \uff08\u5bb9\u5dee\u00b11 bar\uff09\u3002"
              % (mid.get("cagr_pp") or 0.0, mid.get("bars") or 0,
                 _seg.get("middle_bars"), doc["rows"]["printed_under_full_header"].get("bars"),
                 (doc["rows"].get("same_book_full_window") or {}).get("bars"))]
    elif mid:
        L += ["- 2020-2023 \u4e2d\u95f4\u7a97\u8bfb\u5230\u4e86%s bars\uff0c\u4f46\u548c\u53e6\u4e24\u6bb5\u62fc\u4e0d\u6210\u5168\u7a97\uff08\u5bb9\u5dee\u00b11 bar\uff09\uff0c\u56e0\u6b64\u4e0d\u53d1\u5e03\u2014\u2014\u90a3\u662f\u53e6\u4e00\u672c\u4e66\u7684\u4e00\u622a\u3002"
              % (mid.get("bars"),)]
    else:
        L += ["- 2020-2023 \u4e2d\u95f4\u7a97\u6ca1\u6709\u53d1\u5e03\u7684\u5355\u5143\u683c\uff08\u5bf9\u5e94\u9875\u9762\u4e0a\u7684\u7834\u6298\u53f7\uff09\u3002"]
    L += ["", "- 两个格子的差 = **%+.2f pp/年**，就是 r1214 量到的「起点」旋钮："
          "它不是策略变了，是同一本书换了起跑线。" % (v.get("gap_pp") or 0.0), "",
          "## 身份门", ""]
    for k, c in (doc.get("identity") or {}).items():
        L.append("- %s：实测 %s%% / 发表 %s%% / 差 %s pp -> %s"
                 % (k, c.get("measured_pp"), c.get("published_pp"), c.get("delta_pp"),
                    "PASS" if c.get("pass") else "FAIL"))
    L += ["", "## 页面该怎么印", ""]
    tr = doc.get("table_row")
    if not tr:
        L.append("这一节不印新数：判决不是 ROW_LABELED_BY_WINDOW，第一行照旧、不重排。")
    else:
        L.append("- 全窗年化 = **%.2f%%**（%s bars），2024 起 = **%.2f%%**（%s bars）。"
                 % (tr["full"]["cagr_pct"], tr["full_window_bars"],
                    tr["oos"]["cagr_pct"], tr["short_window_bars"]))
    L += ["", "## 冻结（跑之前写的）", "", CRITERIA["verdict_rule"], "",
          "容差：%.2f pp/年；身份门：%.3f pp。" % (TOL_PP, IDENT_TOL_PP), "",
          "数据：`results/etf_book_window_label.json::rows`。"]
    return "\n".join(L) + "\n"


def read_published(path=OUT_JSON):
    """Reader for the page: serve the row only if the stored verdict still recomputes."""
    if not os.path.exists(path):
        return {"status": "missing",
                "artifact": os.path.relpath(path, ROOT).replace(os.sep, "/")}
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if (doc.get("criteria") or {}).get("tol_pp_per_year") != TOL_PP:
        return {"status": "drifted", "artifact": os.path.relpath(path, ROOT).replace(os.sep, "/"),
                "detail": "the stored face was frozen at a different tolerance"}
    redo = decide(doc)
    stored = (doc.get("verdict") or {}).get("state")
    redo_row = table_row(dict(doc, verdict=redo))
    if (redo_row or None) != (doc.get("table_row") or None):
        return {"status": "drifted", "artifact": os.path.relpath(path, ROOT).replace(os.sep, "/"),
                "detail": "the stored row does not match the row this face recomputes (a segment or a criterion moved)"}
    if redo.get("state") != stored:
        return {"status": "drifted", "artifact": os.path.relpath(path, ROOT).replace(os.sep, "/"),
                "detail": "stored verdict %s, recomputed %s" % (stored, redo.get("state"))}
    return {"status": "ok",
            "artifact": os.path.relpath(path, ROOT).replace(os.sep, "/"),
            "verdict": redo, "table_row": doc.get("table_row"),
            "rows": doc.get("rows"), "identity": doc.get("identity"),
            "evidence_cutoff": (doc.get("inputs") or {}).get("evidence_cutoff")}


def check():
    doc = read_published()
    if doc.get("status") != "ok":
        print("CHECK FAILED: %s (%s)" % (doc.get("status"), doc.get("detail")))
        return 1
    print("check OK: %s | gap %+.2f pp/yr | full %.2f%% / 2020-2023 %s / 2024+ %.2f%%"
          % (doc["verdict"]["state"], doc["verdict"].get("gap_pp") or 0.0,
             ((doc.get("table_row") or {}).get("full") or {}).get("cagr_pct") or 0.0,
             ((doc.get("table_row") or {}).get("is") or {}).get("cagr_pct"),
             ((doc.get("table_row") or {}).get("oos") or {}).get("cagr_pct") or 0.0))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    ok = 0
    fail = []

    def chk(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append(name)

    def fixture(short_pp, long_pp, ident_pp, pass_ident=True):
        return {"rows": {"printed_under_full_header": {"cagr_pp": short_pp, "bars": 683},
                         "same_book_full_window": {"cagr_pp": long_pp, "bars": 1525}},
                "identity": {"leg": {"measured_pp": ident_pp, "published_pp": short_pp,
                                     "delta_pp": (ident_pp - short_pp) if ident_pp is not None else None,
                                     "pass": pass_ident}}}

    # L1: a five-point window gap under one header is named, and the row is re-laid out
    d = fixture(12.78, 7.71, 12.78)
    chk("a window gap under one header is named",
        decide(d)["state"] == "ROW_LABELED_BY_WINDOW")
    tr = table_row(dict(d, verdict=decide(d)))
    chk("the relaid row puts the full window in the full column",
        tr["full"]["cagr_pct"] == 7.71 and tr["oos"]["cagr_pct"] == 12.78)

    # L2: the same two numbers inside tolerance is one window -- the verdict is not always red
    d2 = fixture(7.71, 7.60, 7.71)
    chk("inside the tolerance the row is one window", decide(d2)["state"] == "SAME_WINDOW")
    chk("and nothing is relaid out", table_row(dict(d2, verdict=decide(d2))) is None)

    # L3: a drifted identity arm refuses every printed number (never falls back)
    d3 = fixture(12.78, 7.71, 12.40, pass_ident=False)
    v3 = decide(d3)
    chk("a failed identity arm refuses to relabel", v3["state"] == "IDENTITY_FAILED")
    chk("and publishes no row", table_row(dict(d3, verdict=v3)) is None)

    # L4: an unreadable cell is unknown, never zero and never the short-window value
    d4 = fixture(12.78, None, 12.78)
    v4 = decide(d4)
    chk("an unreadable full window reads UNKNOWN", v4["state"] == "UNKNOWN"
        and v4["gap_pp"] is None)
    chk("and does not hand the short window to the full column",
        table_row(dict(d4, verdict=v4)) is None)

    # L5: the tolerance is inclusive at the line, exclusive below it
    d5 = fixture(10.0, 10.0 - TOL_PP, 10.0)
    chk("at the tolerance line the rows are named",
        decide(d5)["state"] == "ROW_LABELED_BY_WINDOW")
    d6 = fixture(10.0, 10.0 - TOL_PP + 0.01, 10.0)
    chk("below the tolerance line they are one window",
        decide(d6)["state"] == "SAME_WINDOW")

    # L7: the verdict rule is echoed into the payload, so --check can refuse a moved face
    chk("the criteria are frozen in the payload",
        CRITERIA.get("tol_pp_per_year") == TOL_PP and "ROW_LABELED_BY_WINDOW" in
        CRITERIA.get("verdict_rule", ""))

    # L8-L10 (r1216b): the middle window is the same ruler's own cell. It is published
    # only when the three windows tile the full one, and a missing cell is unknown --
    # never a zero and never a silently dropped column.
    d7 = fixture(12.78, 7.71, 12.78)
    d7["rows"]["same_book_2020_2023"] = {"cagr_pp": 3.29, "sharpe": 0.883,
                                        "maxdd_pp": -3.3, "bars": 842}
    d7["segments"] = _additivity(d7)
    tr7 = table_row(dict(d7, verdict=decide(d7)))
    chk("the row carries the middle window when the three segments tile the full one",
        ((tr7 or {}).get("is") or {}).get("cagr_pct") == 3.29
        and (d7["segments"] or {}).get("additive") is True)
    d8 = fixture(12.78, 7.71, 12.78)
    d8["rows"]["same_book_2020_2023"] = {"cagr_pp": 3.29, "bars": 900}
    d8["segments"] = _additivity(d8)
    tr8 = table_row(dict(d8, verdict=decide(d8)))
    chk("a middle window that does not tile the full one is withheld, not printed",
        (d8["segments"] or {}).get("additive") is False and "is" not in (tr8 or {}))
    d9 = fixture(12.78, 7.71, 12.78)
    d9["segments"] = _additivity(d9)
    chk("a missing middle window reads unknown, never zero",
        (d9["segments"] or {}).get("additive") is None
        and "is" not in (table_row(dict(d9, verdict=decide(d9))) or {}))
    # L11: the note's arithmetic is the evidence that the three windows tile the full
    # one. Printing the middle bar count twice looks like it adds up and does not --
    # exactly the mistake this face exists to stop, so the note is pinned here.
    _v7 = decide(d7)
    _md7 = render_md(dict(d7, verdict=_v7, inputs={}, identity=d7["identity"],
                          table_row=table_row(dict(d7, verdict=_v7))))
    chk("the note quotes the middle window and adds the three bar counts to the full "
        "one", "842+683=1525" in _md7 and "3.29" in _md7)
    print("selftest %d/%d" % (ok, ok + len(fail)))
    for f in fail:
        print("  FAIL: %s" % f)
    return 0 if not fail else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))