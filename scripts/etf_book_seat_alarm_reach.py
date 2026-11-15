"""Does the pool alarm on the ticket ever ring? (r1757)

The ticket prints, for a 20M liquidity cut: "中位 262 只可挑, 最薄的一天也还有 51 只" and then
"最薄那天是这本书位置的 10.2 倍, 离座位线还有 46 只缓冲". r1755 added an alarm branch for the
case where the thinnest day falls at or below the seat count. That branch has never fired on
real data -- and nobody asked whether it CAN fire on this book.

A branch that cannot fire is not a safety net; it is a sentence the reader will never see,
and its presence quietly implies "the pool has been close to thin before". This face answers
two questions with the same panel the entry gate already builds:

  (1) REACH -- how thin would the pool have to get, and how tight would the cut have to be,
      before the thinnest day in this window falls under the book's seat count? The reach is
      printed as a ladder of gates (20M x {1,2,5,10,20,50,100,200}) with each rung's own
      thinnest day and its date.
  (2) ATTRIBUTION -- the book DOES carry empty seats (the volatility target de-levers into
      cash). If the pool has never been thin, then every empty seat on this book comes from
      the de-levering, not from a shortage of names. The two numbers are printed side by side
      and never added together.

Control (frozen before the run): the 20M rung's per-bar series must reproduce the published
entry-gate row exactly (min/median/bars) -- otherwise this face is not about that book.

No prices, no returns, no engine: this face only counts names that clear a gate.

Usage:
  python scripts/etf_book_seat_alarm_reach.py run
  python scripts/etf_book_seat_alarm_reach.py --selftest
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import etf_book_entry_gate as G   # noqa: E402  (one universe builder, one width expression)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_seat_alarm_reach.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_SEAT_ALARM_REACH.md")
FACE_ENTRY_GATE = os.path.join(ROOT, "results", "etf_book_entry_gate.json")
FACE_IDLE_CASH = os.path.join(ROOT, "results", "etf_book_idle_cash.json")

SHIPPED = G.SHIPPED                      # 20M -- the cut the ticket prints
LADDER = [1, 2, 5, 10, 20, 50, 100, 200]  # multiples of the shipped cut, in that order


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def seat_count():
    """The book's own seat count -- read from the published face, never typed in here.

    `etf_book_idle_cash.json` prices a book with an explicit `n_hold`; that is the same book
    whose seats the ticket prints. A missing face returns None and the caller must refuse to
    print a reach sentence instead of borrowing a number.
    """
    try:
        face = _load(FACE_IDLE_CASH)
    except (OSError, ValueError):
        return None, None
    book = face.get("book") or {}
    readings = face.get("readings") or {}
    n_hold = book.get("n_hold")
    idle = readings.get("idle_share_mean")
    return (int(n_hold) if n_hold else None), (float(idle) if idle is not None else None)


def control_row():
    """The published 20M row this face must reproduce (min/median/bars)."""
    try:
        face = _load(FACE_ENTRY_GATE)
    except (OSError, ValueError):
        return None
    for row in face.get("rows") or []:
        if abs(float(row.get("min_amt_cny") or 0.0) - SHIPPED) < 1.0:
            return row
    return None


def scan(close, amt):
    """One pass per gate rung: thinnest day, its date, median, bars."""
    rows = []
    for mult in LADDER:
        gate = SHIPPED * mult
        series = G.eligible_series(close, amt, gate)
        if series.empty:
            rows.append({"mult": mult, "gate_cny": gate, "gate_m": gate / 1e6,
                         "bars": 0, "thin": None, "thin_date": None, "median": None})
            continue
        thin = int(series.min())
        rows.append({
            "mult": mult,
            "gate_cny": gate,
            "gate_m": round(gate / 1e6, 1),
            "bars": int(len(series)),
            "thin": thin,
            "thin_date": series.idxmin().date().isoformat(),
            "median": int(np.median(series.values)),
        })
    return rows


def yearly_thin(series):
    """Per-year thinnest day of the shipped rung -- the trend, not only the global min."""
    out = []
    for year, chunk in series.groupby(series.index.year):
        if chunk.empty:
            continue
        out.append({"year": int(year), "thin": int(chunk.min()),
                    "thin_date": chunk.idxmin().date().isoformat(),
                    "bars": int(len(chunk))})
    return out


def reach_verdict(thin, seats):
    """Three-way reading of the shipped rung against the seat count (r1755's own split)."""
    if thin is None or seats is None:
        return {"verdict": "CANNOT_JUDGE_NO_INPUT",
                "sentence": "座位数或最薄日名数读不出来，这条腿不印倍数也不印告警"}
    if thin < seats:
        return {"verdict": "ALARM_REACHABLE_IN_WINDOW",
                "short": seats - thin, "buffer": 0, "multiple": None,
                "sentence": ("最薄那天只有 %d 只，比 %d 个位置还少 %d 只——这条告警腿在这个窗口里"
                             "真的会响" % (thin, seats, seats - thin))}
    if thin == seats:
        return {"verdict": "ALARM_AT_BOUNDARY",
                "short": 0, "buffer": 0, "multiple": 1.0,
                "sentence": ("最薄那天正好 %d 只对上 %d 个位置——余量为零，再少一只就响"
                             % (thin, seats))}
    return {"verdict": "ALARM_UNREACHABLE",
            "short": 0, "buffer": thin - seats,
            "multiple": round(float(thin) / float(seats), 3),
            "drop_needed": thin - seats + 1,
            "sentence": ("最薄那天是 %d 只，对 %d 个位置是 %.1f 倍——这条告警腿要在"
                         "同一天再消失 %d 只票才会响，这个窗口里它一次都没响过"
                         % (thin, seats, float(thin) / float(seats), thin - seats + 1))}


def edge_reading(series, k=20):
    """Is the "thinnest day" a liquidity event, or the window's own warm-up edge?

    r1757 finding: the shipped rung's minimum sits on the FIRST bar of the window
    (2020-01-02, 51 names), because that is where the panel just cleared MIN_HIST and has
    the fewest listed names. A minimum that lands inside the first k bars measures the
    book's start, not a shortage -- the sentence "the thinnest day still had 51" then means
    "the first day had 51", which is a different claim. The interior minimum is printed
    beside it so the reader keeps both.
    """
    if series is None or series.empty:
        return {"verdict": "CANNOT_JUDGE_NO_SERIES"}
    thin_idx = series.idxmin()
    pos = int(series.index.get_loc(thin_idx))
    core = series.iloc[k:]
    out = {"thin_position_in_window": pos,
           "thin_is_warmup_edge": pos < k,
           "warmup_edge_bars": int(k)}
    if not core.empty:
        out["core_thin"] = int(core.min())
        out["core_thin_date"] = core.idxmin().date().isoformat()
        out["core_bars"] = int(len(core))
    out["verdict"] = ("THINNEST_AT_WARMUP_EDGE" if out["thin_is_warmup_edge"]
                      else "THINNEST_INTERIOR")
    if out["thin_is_warmup_edge"] and out.get("core_thin") is not None:
        out["sentence"] = ("最薄的那一天是窗口的第一根 bar（%s，%d 只），那是面板刚够历史长度的"
                           "暖机边界；去掉前 %d 根之后，运行期最薄是 %d 只（%s）"
                           % (thin_idx.date().isoformat(), int(series.min()), int(k),
                              out["core_thin"], out["core_thin_date"]))
    return out


def first_reachable(rows, seats):
    """The loosest rung in the ladder that would actually trip the alarm, or None."""
    if seats is None:
        return None
    for row in rows:
        if row.get("thin") is not None and row["thin"] < seats:
            return row
    return None


def decide(ctrl_row, shipped_row, seats, idle_share):
    """Frozen argument order; the verdict is re-derived from the readings, never typed."""
    if ctrl_row is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "没有已发布的 20M 行可比对，这张面不是关于这本书的"}
    try:
        ctrl_min = int(ctrl_row.get("min"))
    except (TypeError, ValueError):
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "已发布的那一行没有最薄日数，控制腿断"}
    if shipped_row is None or shipped_row.get("thin") is None:
        return {"verdict": "CANNOT_JUDGE_NO_SERIES",
                "sentence": "20M 档的逐日序列算不出来"}
    if int(shipped_row["thin"]) != ctrl_min:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": ("重算的 20M 最薄日 %d 只与已发布 %d 只不等，控制腿败"
                             % (shipped_row["thin"], ctrl_min))}
    base = reach_verdict(int(shipped_row["thin"]), seats)
    out = dict(base)
    out["pool_empty_seats"] = max(0, (seats or 0) - int(shipped_row["thin"]))
    if idle_share is not None:
        out["observed_empty_seats"] = round(float(seats or 0) * float(idle_share), 3)
        if out["pool_empty_seats"] == 0 and out["observed_empty_seats"] > 0:
            out["attribution"] = "EMPTY_SEATS_ARE_DELEVERAGING"
            out["attribution_sentence"] = (
                "账上平均空着 %.1f 个位置，而池子从来没有薄到座位线以下——空座全部来自"
                "波动目标降杠杆，不是没票可选" % out["observed_empty_seats"])
    return out


def run():
    close, openp, amt, feats, n_flip = G.build_universe()
    rows = scan(close, amt)
    seats, idle_share = seat_count()
    ctrl = control_row()
    shipped_row = next((r for r in rows if r["mult"] == 1), None)
    verdict = decide(ctrl, shipped_row, seats, idle_share)
    tripped = first_reachable(rows, seats)
    series = G.eligible_series(close, amt, SHIPPED)
    edge = edge_reading(series)
    payload = {
        "face": "etf_book_seat_alarm_reach",
        "evidence_cutoff": close.index[-1].date().isoformat(),
        "window": {"start": series.index[0].date().isoformat(),
                   "end": series.index[-1].date().isoformat(),
                   "bars": int(len(series))},
        "question": ("票价面印的「离座位线还有 46 只缓冲」是余量还是一句永远不响的告警？"
                     "池子要薄到什么程度、闸要抬到哪一档，这条腿才会真的响？"),
        "seats": seats,
        "idle_share_mean": idle_share,
        "shipped_gate_cny": SHIPPED,
        "control": {"published_min": (ctrl or {}).get("min"),
                    "published_median": (ctrl or {}).get("median"),
                    "published_bars": (ctrl or {}).get("bars"),
                    "panel_universe": int(len(close.columns)),
                    "panel_flips_repaired": int(n_flip)},
        "shipped_row": shipped_row,
        "edge_reading": edge,
        "ladder": rows,
        "first_reachable_rung": tripped,
        "yearly_thin": yearly_thin(series),
        "verdict": verdict,
        "not_priced": ("抬闸的收益代价：本面只数名数，不重算收益；已发布的六档扫描里"
                       "200M 档的年化是 5.42%（20M 是 8.41%），更高档只会更差"),
        "generated": pd.Timestamp.now().isoformat(timespec="seconds"),
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)
    print(json.dumps({"verdict": verdict.get("verdict"),
                      "sentence": verdict.get("sentence"),
                      "first_reachable_rung": (tripped or {}).get("gate_m"),
                      "bars": payload["window"]["bars"]}, ensure_ascii=False))
    return payload


def write_md(p):
    v = p["verdict"]
    lines = ["# 池子告警腿的可达性（r1757）", "",
             "- 窗口：%s → %s（%d 根 bar）"
             % (p["window"]["start"], p["window"]["end"], p["window"]["bars"]),
             "- 图书座位数：%s（读自 `etf_book_idle_cash.book.n_hold`）" % p["seats"],
             "- 已发布控制行：20M 档最薄 %s 只 / 中位 %s 只 / %s 根"
             % (p["control"]["published_min"], p["control"]["published_median"],
                p["control"]["published_bars"]),
             "", "## 判决", "", "**%s** — %s" % (v.get("verdict"), v.get("sentence")), ""]
    e = p.get("edge_reading") or {}
    if e.get("sentence"):
        lines += ["**最薄日的位置：%s** — %s" % (e.get("verdict"), e["sentence"]), ""]
    if v.get("attribution"):
        lines += ["**空座归因：%s** — %s" % (v["attribution"], v["attribution_sentence"]), ""]
    lines += ["## 闸档梯子（20M × 倍数）", "",
              "| 倍数 | 闸(M) | 最薄日(只) | 最薄日 | 中位(只) |",
              "|---|---|---|---|---|"]
    for r in p["ladder"]:
        lines.append("| ×%d | %g | %s | %s | %s |"
                     % (r["mult"], r["gate_m"], r["thin"], r["thin_date"], r["median"]))
    lines += ["", "## 20M 档逐年最薄", "", "| 年 | 最薄(只) | 日期 | bar |", "|---|---|---|---|"]
    for y in p["yearly_thin"]:
        lines.append("| %d | %d | %s | %d |" % (y["year"], y["thin"], y["thin_date"], y["bars"]))
    if p.get("first_reachable_rung"):
        rr = p["first_reachable_rung"]
        lines += ["", "## 要抬到哪一档才会响", "",
                  "闸抬到 **%gM**（20M × %d）时最薄日 **%d 只**，第一次低于 %s 个位置。"
                  % (rr["gate_m"], rr["mult"], rr["thin"], p["seats"])]
    else:
        lines += ["", "## 要抬到哪一档才会响", "",
                  "梯子抬到 **%gM** 最薄日仍是 **%s 只**，没有一档低到 %s 个位置以下。"
                  % (p["ladder"][-1]["gate_m"], p["ladder"][-1]["thin"], p["seats"])]
    lines += ["", "## 没有定价的部分", "", p["not_priced"], ""]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- selftest
def _chk(name, ok, detail=""):
    print(("PASS  %s" % name) if ok else ("FAIL  %s  [%s]" % (name, detail)))
    return 0 if ok else 1


def selftest():
    fails = 0

    # L1 - the width series and its aggregate cannot drift apart
    NB = 400   # > MIN_HIST, otherwise the warm-up filter empties the fixture
    idx = pd.date_range("2020-01-01", periods=NB, freq="B")
    close = pd.DataFrame(np.arange(NB * 3, dtype=float).reshape(NB, 3) + 10.0, index=idx)
    amt = pd.DataFrame(np.where(np.arange(NB)[:, None] % 4 == 0, 5e6, 50e6)
                       * np.ones((NB, 3)), index=idx, columns=close.columns)
    agg = G.eligible_counts(close, amt, 20e6)
    ser = G.eligible_series(close, amt, 20e6)
    fails += _chk("L1 eligible_counts derives from eligible_series (min/median/bars agree)",
                  agg["bars"] == int(len(ser)) and agg["min"] == int(ser.min())
                  and agg["median"] == int(np.median(ser.values)),
                  "agg=%s series_min=%s" % (agg, ser.min()))

    # L2 - control failure is named, not papered over
    v = decide({"min": 50}, {"thin": 51}, 5, 0.30)
    fails += _chk("L2 a shipped rung that disagrees with the published row is CANNOT_JUDGE",
                  v["verdict"] == "CANNOT_JUDGE_CONTROL", v.get("verdict"))
    v = decide(None, {"thin": 51}, 5, 0.30)
    fails += _chk("L3 a missing published row is CANNOT_JUDGE_NO_CONTROL",
                  v["verdict"] == "CANNOT_JUDGE_NO_CONTROL", v.get("verdict"))

    # L4 - unreachable reading carries the real gap and the drop that would be needed
    v = decide({"min": 51}, {"thin": 51}, 5, 0.3032)
    fails += _chk("L4 51 names vs 5 seats reads UNREACHABLE with buffer 46 and a 47-name drop",
                  v["verdict"] == "ALARM_UNREACHABLE" and v["buffer"] == 46
                  and v["drop_needed"] == 47 and abs(v["multiple"] - 10.2) < 0.001,
                  "%s" % {k: v.get(k) for k in ("verdict", "buffer", "drop_needed", "multiple")})

    # L5 - the boundary and the below-boundary readings are the r1755 split, not a multiple
    vb = decide({"min": 5}, {"thin": 5}, 5, None)
    vv = decide({"min": 4}, {"thin": 4}, 5, None)
    fails += _chk("L5 thin==seats is the zero-buffer reading and thin<seats is the alarm",
                  vb["verdict"] == "ALARM_AT_BOUNDARY"
                  and vv["verdict"] == "ALARM_REACHABLE_IN_WINDOW" and vv["short"] == 1,
                  "%s / %s" % (vb["verdict"], vv["verdict"]))

    # L6 - empty seats are attributed to de-levering only when the pool never got thin
    v = decide({"min": 51}, {"thin": 51}, 5, 0.3032)
    fails += _chk("L6 empty seats read as de-levering, with the observed count printed",
                  v.get("attribution") == "EMPTY_SEATS_ARE_DELEVERAGING"
                  and abs(v["observed_empty_seats"] - 1.516) < 0.001
                  and v["pool_empty_seats"] == 0,
                  "%s" % {k: v.get(k) for k in ("attribution", "observed_empty_seats")})
    vp = decide({"min": 3}, {"thin": 3}, 5, 0.30)
    fails += _chk("L7 a genuinely thin pool is NOT blamed on de-levering",
                  "attribution" not in vp and vp["pool_empty_seats"] == 2,
                  "%s" % vp.get("verdict"))

    # L8 - reach ladder picks the first rung that trips, and says so when none does
    rows = [{"mult": 1, "gate_m": 20.0, "thin": 51}, {"mult": 2, "gate_m": 40.0, "thin": 30},
            {"mult": 5, "gate_m": 100.0, "thin": 4}]
    r = first_reachable(rows, 5)
    fails += _chk("L8 the first rung below the seat count is named (100M at 4 names)",
                  r is not None and r["gate_m"] == 100.0,
                  "%s" % (r or {}).get("gate_m"))
    fails += _chk("L9 a ladder that never trips returns None (no invented rung)",
                  first_reachable(rows[:2], 5) is None)

    # L10/L11 - a minimum on the window's first bar is the warm-up edge, not a thin pool
    s_edge = pd.Series([51] + [200] * 60, index=pd.date_range("2020-01-02", periods=61))
    e1 = edge_reading(s_edge, k=20)
    fails += _chk("L10 a minimum on the first bar is named as the warm-up edge and the "
                  "interior minimum is printed beside it",
                  e1["verdict"] == "THINNEST_AT_WARMUP_EDGE"
                  and e1["thin_position_in_window"] == 0 and e1["core_thin"] == 200,
                  "%s" % {k: e1.get(k) for k in ("verdict", "thin_position_in_window", "core_thin")})
    s_mid = pd.Series([200] * 30 + [40] + [200] * 30,
                      index=pd.date_range("2020-01-02", periods=61))
    fails += _chk("L11 a minimum in the middle of the window is NOT blamed on the warm-up",
                  edge_reading(s_mid, k=20)["verdict"] == "THINNEST_INTERIOR")

    print("selftest %d/%d" % (11 - fails, 11))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    run()
