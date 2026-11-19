"""ETF book -- the capacity veto is a number, and its margin is thinner than a day's turnover.

r1684 replaced the year checks with three measurable veto readings, the third of which is
K1: one day's own order may not exceed 1% of the weakest slot's ADV. On 2026-11-17 that
reading is 1.0087% at the 1,000,000 CNY lens, so the face prints DENY -- and the page stops
there, because a veto is a yes/no.

A veto that misses by 0.87% of its own line is not the same object as one that misses by
40%. This face asks the three questions the yes/no cannot answer:

  * HOW FAR. Back the line out of the published reading: the largest capital whose order
    still fits in 1% of that slot's turnover. Reported in CNY, next to the lens it is being
    compared with. "DENY at 1,000,000" and "ADMIT at 991,000" are the same measurement.
  * WHICH DAY. The same book, the same five names, the same trade -- re-measured against
    each of the last 60 sessions' own ADV. If the verdict flips inside that window, then
    today's DENY answers "which day did you look", not "how big can this book be".
  * HOW COARSE. The gate's ADV is the 20-bar median of a 20-bar median of close x volume,
    so it moves in steps, not continuously. The number of distinct values it took inside
    the window is published beside the pass count: a reading that can only land on 12
    values cannot resolve a 0.87% margin.

Nothing here re-decides the gate: the line, the capital lens, the name count and the ADV
lens are imported from `candidate_year_gate` / `etf_composite_pf` (never hand-copied), and
the leg refuses to publish if its own reproduction of the published reading drifts.

Read the verdict as a statement about the ruler, not about the book: BELOW_LINE_EVERY_SESSION
means the gate would have denied on every session of the window (a capacity fact);
COIN_FLIP_AT_THE_LINE means the gate would have admitted on some sessions and denied on
others with nothing about the book changing (a calendar fact).

Usage:
    python scripts/etf_book_capacity_edge.py run
    python scripts/etf_book_capacity_edge.py check
    python scripts/etf_book_capacity_edge.py selftest
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

OUT_JSON = os.path.join(ROOT, "results", "etf_book_capacity_edge.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_capacity_edge.md")
GATE_FACE = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")

WINDOW_SESSIONS = 60        # frozen: how far back the same trade is re-measured
REPRO_TOL_PCT = 0.0005      # published reading is rounded to 4 dp of a percent
COIN_FLIP_LO = 0.20         # frozen: a pass rate inside [0.20, 0.80] is a coin flip
COIN_FLIP_HI = 0.80
ADV_BARS = 20


# ---------------------------------------------------------------- input faces

def load_gate(path=GATE_FACE):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def gate_picks(face):
    return list(((face.get("data") or {}).get("live_picks") or []))


def published_reading(face):
    """The K1 reading the gate published, in percent, plus its lens."""
    reads = ((face.get("decision") or {}).get("reads") or {})
    lens = reads.get("capacity_veto_lens") or "1M"
    blk = ((reads.get("capacity_by_capital") or {}).get(lens) or {})
    return {"lens": lens,
            "capital_cny": blk.get("capital_cny"),
            "per_name_cny": blk.get("per_name_cny"),
            "impact_pct_of_adv": blk.get("impact_pct_of_adv"),
            "within_1pct": blk.get("within_1pct"),
            "line_pct": reads.get("impact_max_pct_of_adv")}


def panel_adv():
    """The gate's own ADV face: `close x volume`, rolling 20-bar median, then the median
    of the last 20 such values when it is read. Both steps are causal, so slicing the
    series at an earlier date is a legitimate historical reading (no lookahead)."""
    import etf_composite_pf as E
    close, openp, amt, _feats = E.build_panel()
    return close, amt


# ---------------------------------------------------------------- measurement

def adv20_at(amt, sym, d, bars=ADV_BARS):
    """The ADV as it was readable on session `d`: median of that slot's last 20 values."""
    if sym not in amt.columns:
        return None
    s = amt[sym].loc[:d]
    s = s.dropna()
    if len(s) < bars:
        return None
    med = float(s.tail(bars).median())
    if not (med == med) or med <= 0:      # NaN or non-positive
        return None
    return med


def measure(picks, capital, line, adv_by_sym):
    """One trading decision, priced against one day's ADV face.

    Equal weight (the gate's lens): every slot must be filled with capital / n.
    Returns per-slot rows and the deciding reading (the worst slot, not the average).
    """
    n = len(picks)
    if n == 0 or capital is None or capital <= 0:
        return {"rows": [], "n_names": n, "per_name_cny": None,
                "reading": None, "binding": None, "unmeasurable": list(picks)}
    per_name = float(capital) / float(n)
    rows, unmeasurable = [], []
    for sym in picks:
        adv = adv_by_sym.get(sym)
        if adv is None:
            unmeasurable.append(sym)
            rows.append({"sym": sym, "adv": None, "share": None,
                         "capital_where_at_line_cny": None})
            continue
        share = per_name / adv
        rows.append({"sym": sym, "adv": round(adv, 2), "share": share,
                     "capital_where_at_line_cny": round(float(line) * adv * n, 2)})
    measured = [r for r in rows if r["share"] is not None]
    if not measured:
        return {"rows": rows, "n_names": n, "per_name_cny": round(per_name, 2),
                "reading": None, "binding": None, "unmeasurable": unmeasurable}
    worst = max(measured, key=lambda r: r["share"])
    return {"rows": rows, "n_names": n, "per_name_cny": round(per_name, 2),
            "reading": worst["share"], "binding": worst["sym"],
            "capital_where_at_line_cny": worst["capital_where_at_line_cny"],
            "unmeasurable": unmeasurable}


def sessions(amt, picks, capital, line, bars=WINDOW_SESSIONS):
    """The same trade, re-priced against each of the last `bars` sessions' own ADV."""
    idx = amt.index
    out = []
    for d in idx[-bars:]:
        adv_map = {}
        for sym in picks:
            adv_map[sym] = adv20_at(amt, sym, d)
        m = measure(picks, capital, line, adv_map)
        out.append({"bar": str(d)[:10], "reading": m["reading"], "binding": m["binding"],
                    "capital_where_at_line_cny": m.get("capital_where_at_line_cny"),
                    "unmeasurable": m["unmeasurable"]})
    return out


def summarise(rows, capital, line):
    """Everything the sentences are allowed to say, derived from the rows only."""
    meas = [r for r in rows if r.get("reading") is not None]
    passes = [r for r in meas if r["reading"] <= line]
    caps = [r["capital_where_at_line_cny"] for r in meas
            if r.get("capital_where_at_line_cny") is not None]
    advs = sorted({r["reading"] for r in meas})
    caps_sorted = sorted(caps)
    out = {
        "n_sessions": len(rows),
        "n_measurable": len(meas),
        "n_unmeasurable": len(rows) - len(meas),
        "n_passes": len(passes),
        "pass_rate": (round(len(passes) / float(len(meas)), 4) if meas else None),
        "reading_today_pct": (round(meas[-1]["reading"] * 100.0, 4) if meas else None),
        "binding_today": (meas[-1]["binding"] if meas else None),
        "capital_where_at_line_today_cny": (meas[-1]["capital_where_at_line_cny"]
                                           if meas else None),
        "reading_worst_pct": (round(max(r["reading"] for r in meas) * 100.0, 4) if meas else None),
        "reading_best_pct": (round(min(r["reading"] for r in meas) * 100.0, 4) if meas else None),
        "capital_min_cny": caps_sorted[0] if caps_sorted else None,
        "capital_median_cny": (caps_sorted[len(caps_sorted) // 2] if caps_sorted else None),
        "capital_max_cny": caps_sorted[-1] if caps_sorted else None,
        "n_distinct_readings": len(advs),
        "distinct_readings_pct": [round(v * 100.0, 4) for v in advs],
        "binding_names": sorted({r["binding"] for r in meas if r.get("binding")}),
        "lens_cny": float(capital) if capital is not None else None,
        "line_pct": float(line) * 100.0,
    }
    out["gap_to_lens_cny"] = (None if out["capital_where_at_line_today_cny"] is None
                              else round(float(capital) - out["capital_where_at_line_today_cny"], 2))
    out["verdict"] = verdict_name(out)
    return out


def verdict_name(s):
    """Frozen: the name is decided by the pass count, never written by hand."""
    n = s.get("n_measurable") or 0
    if n == 0:
        return "NO_MEASURABLE_SESSION"
    rate = s["pass_rate"]
    if rate == 0.0:
        return "BELOW_LINE_EVERY_SESSION"
    if rate == 1.0:
        return "ABOVE_LINE_EVERY_SESSION"
    if COIN_FLIP_LO <= rate <= COIN_FLIP_HI:
        return "COIN_FLIP_AT_THE_LINE"
    if rate < COIN_FLIP_LO:
        return "BELOW_LINE_MOST_SESSIONS"
    return "ABOVE_LINE_MOST_SESSIONS"


# ---------------------------------------------------------------- check leg

def check(payload):
    """Re-derive every published number from the published rows."""
    problems = []
    s = payload.get("summary") or {}
    rows = payload.get("sessions") or []
    line = (payload.get("criteria") or {}).get("line_pct")
    if line is None:
        problems.append("criteria.line_pct 缺失，无法复算")
        return {"ok": False, "problems": problems}
    line_frac = float(line) / 100.0
    capital = (payload.get("criteria") or {}).get("lens_cny")
    if capital is None:
        problems.append("criteria.lens_cny 缺失，无法复算")

    meas = [r for r in rows if r.get("reading") is not None]
    passes = [r for r in meas if r["reading"] <= line_frac]
    if s.get("n_sessions") != len(rows):
        problems.append("n_sessions %r != rows %r" % (s.get("n_sessions"), len(rows)))
    if s.get("n_measurable") != len(meas):
        problems.append("n_measurable %r != rows %r" % (s.get("n_measurable"), len(meas)))
    if s.get("n_passes") != len(passes):
        problems.append("n_passes %r != 复算 %r" % (s.get("n_passes"), len(passes)))
    rate = (len(passes) / float(len(meas))) if meas else None
    pr = s.get("pass_rate")
    if rate is not None and (pr is None or abs(float(pr) - rate) > 5e-4):
        problems.append("pass_rate %r != 复算 %r" % (pr, rate))

    caps = sorted(r["capital_where_at_line_cny"] for r in meas
                  if r.get("capital_where_at_line_cny") is not None)
    if caps and s.get("capital_min_cny") is not None:
        if abs(s["capital_min_cny"] - caps[0]) > 1.0:
            problems.append("capital_min_cny 与行不符")
    if caps and s.get("capital_max_cny") is not None:
        if abs(s["capital_max_cny"] - caps[-1]) > 1.0:
            problems.append("capital_max_cny 与行不符")

    # every session's own ceiling must follow from its own reading and the lens:
    # cap = line * adv * n, per_name = cap / n, reading = per_name / adv  =>  cap = line * lens / reading
    if capital is not None:
        for r in meas:
            cap = r.get("capital_where_at_line_cny")
            if cap is None or not r.get("reading"):
                continue
            expect = line_frac * float(capital) / r["reading"]
            if abs(cap - expect) > max(1.0, 1e-6 * expect):
                problems.append("bar %s 的阈值资本与该行读数不自洽（%r vs %r）"
                                % (r.get("bar"), cap, round(expect, 2)))
                break

    # today's row must be the gate's own reading
    pub = payload.get("published") or {}
    if meas and pub.get("impact_pct_of_adv") is not None:
        got = meas[-1]["reading"] * 100.0
        if abs(got - float(pub["impact_pct_of_adv"])) > REPRO_TOL_PCT:
            problems.append("今日读数 %.4f%% 与闸面 %r%% 差超容差"
                            % (got, pub["impact_pct_of_adv"]))
    if s.get("verdict") != verdict_name(s):
        problems.append("判词名与自己的计数不符：%r" % (s.get("verdict"),))
    if (s.get("verdict") == "COIN_FLIP_AT_THE_LINE"
            and not (COIN_FLIP_LO <= (s.get("pass_rate") or 0) <= COIN_FLIP_HI)):
        problems.append("判词落在区间外")

    # r1850: every number above is re-derived from this face's own rows, so the check was
    # green on a face that had been sitting at 2026-11-17 while the gate walked to 11-19 --
    # the CEO page then printed "not the same day as the ticket" in place of a reading for
    # two rounds and nobody was told.  A check that only re-derives its own arithmetic can
    # never notice it is quoting an old day, so the face is asked whether the gate still
    # stands on the bar it priced.  Cheap (one JSON read, no panel), and it fails loud.
    fresh = freshness_problem(payload)
    if fresh:
        problems.append(fresh)
    return {"ok": not problems, "problems": problems}


def freshness_problem(payload):
    """r1850: is this face still standing on the gate's own session?

    Only real faces are asked (a synthetic fixture built inside selftest has no
    `artifact` marker and a placeholder bar, and must stay green).  Returns None when
    the face cannot be aged -- an unreadable gate is reported by the leg that reads it,
    not turned into a second, quieter "stale" claim here.
    """
    if (payload.get("artifact") or "") != "etf_book_capacity_edge":
        return None
    face_day = str(payload.get("evidence_cutoff") or "")[:10]
    if len(face_day) != 10 or face_day[4] != "-":
        return None
    try:
        gate = load_gate()
        gate_day = str(((gate.get("data") or {}).get("last")) or "")[:10]
    except Exception:
        return None
    if len(gate_day) == 10 and face_day < gate_day:
        # the word STALE is the chain's repair contract: run_leg pays the declared refresh
        # only when the probe names itself stale, so a Chinese-only complaint here would be
        # read as a plain red the chain is not allowed to fix (r1345/r1850).
        return ("STALE FACE_BEHIND_GATE：面停在 %s，闸面已经到 %s（先跑 run 再来 check）"
                % (face_day, gate_day))
    return None


# ---------------------------------------------------------------- report

def sentence(s):
    """One line, quoting this face's own counts only."""
    if s.get("verdict") == "COIN_FLIP_AT_THE_LINE":
        head = ("同一笔单子（%s 元、%d 个名字等权），按最近 %d 个交易日各自的成交额重量一遍，"
                "有 %d 天过线、%d 天不过线（%.1f%%）——判决翻在了日历上，不是翻在这本书上。"
                % ("{:,.0f}".format(s["lens_cny"]), s.get("n_names") or 0, s["n_measurable"],
                   s["n_passes"], s["n_measurable"] - s["n_passes"], s["pass_rate"] * 100.0))
    else:
        head = ("同一笔单子（%s 元、%d 个名字等权），最近 %d 个交易日里有 %d 天过线、%d 天不过线。"
                % ("{:,.0f}".format(s["lens_cny"]), s.get("n_names") or 0, s["n_measurable"],
                   s["n_passes"], s["n_measurable"] - s["n_passes"]))
    if s.get("reading_today_pct") is not None and s.get("reading_best_pct") is not None \
            and s["reading_today_pct"] <= s["reading_best_pct"]:
        where = "今天还是这段窗里最好的一天（读数最低），所以这个 DENY 不是当天的运气。"
    elif s.get("reading_today_pct") is not None and s.get("reading_worst_pct") is not None \
            and s["reading_today_pct"] >= s["reading_worst_pct"]:
        where = "今天还是这段窗里最差的一天（读数最高），所以这个 DENY 也不代表平常的日子。"
    else:
        where = ("这段窗里读数从 %.4f%% 到 %.4f%%，今天落在中间。"
                 % (s.get("reading_best_pct") or 0.0, s.get("reading_worst_pct") or 0.0))
    tail = ("今天这一行是 %.4f%%（最弱的是 %s），闸线 %.2f%%；把这把尺子倒过来读，"
            "在今天的成交额上能过的资本上限是 %s 元，离 %s 元差 %s 元。"
            "%s按这段窗的中位算，上限是 %s 元；按最差的一天算，只有 %s 元——"
            "「装不下 100 万」这句要换成「平常装得下多少」。"
            % (s.get("reading_today_pct") or 0.0, s.get("binding_today") or "?",
               s.get("line_pct") or 0.0,
               "{:,.0f}".format(s.get("capital_where_at_line_today_cny") or 0),
               "{:,.0f}".format(s["lens_cny"]),
               "{:,.0f}".format(s.get("gap_to_lens_cny") or 0), where,
               "{:,.0f}".format(s.get("capital_median_cny") or 0),
               "{:,.0f}".format(s.get("capital_min_cny") or 0)))
    return head + tail


def render_md(payload):
    s = payload["summary"]
    L = ["# 容量那条闸，离翻转有多远", "",
         "证据 cutoff `%s`（盘口 session `%s`）。" % (payload.get("evidence_cutoff"),
                                              payload.get("session")), "",
         "## 一句话", "", sentence(s), "",
         "## 判词：%s" % s["verdict"], "",
         "| 项 | 读数 |", "| --- | ---: |",
         "| 闸线（单名单日） | %.2f%% ADV |" % s["line_pct"],
         "| 今天的读数（最弱席位） | %.4f%%（%s） |" % (s["reading_today_pct"], s["binding_today"]),
         "| 今天能过的资本上限 | %s 元 |" % "{:,.0f}".format(s["capital_where_at_line_today_cny"]),
         "| 与 %s 元这个数差 | %s 元 |" % ("{:,.0f}".format(s["lens_cny"]),
                                    "{:,.0f}".format(s["gap_to_lens_cny"])),
         "| 最近 %d 个交易日里过线 | %d / %d（%.1f%%） |" % (s["n_measurable"], s["n_passes"],
                                                      s["n_measurable"], s["pass_rate"] * 100.0),
         "| 这段窗里资本上限最低/中位/最高 | %s / %s / %s 元 |"
         % ("{:,.0f}".format(s["capital_min_cny"]), "{:,.0f}".format(s["capital_median_cny"]),
            "{:,.0f}".format(s["capital_max_cny"])),
         "| 读数在窗内只落在几个值上 | %d 个（%.4f%% ～ %.4f%%） |"
         % (s["n_distinct_readings"], min(s["distinct_readings_pct"]), max(s["distinct_readings_pct"])),
         "| 读过的最弱席位 | %s |" % "、".join(s["binding_names"]), "",
         "## 逐日（最近 %d 个交易日，同一笔单子）" % s["n_sessions"], "",
         "| 交易日 | 最弱席位 | 读数% | 在该日能过的资本上限（元） | 过线 |",
         "| --- | --- | ---: | ---: | --- |"]
    for r in payload["sessions"]:
        if r.get("reading") is None:
            L.append("| %s | 读不到 | — | — | 不算过 |" % r["bar"])
            continue
        L.append("| %s | %s | %.4f | %s | %s |"
                 % (r["bar"], r["binding"], r["reading"] * 100.0,
                    "{:,.0f}".format(r["capital_where_at_line_cny"] or 0),
                    "是" if r["reading"] <= s["line_pct"] / 100.0 else "否"))
    L += ["", "## 限制", ""]
    for c in payload.get("caveats") or []:
        L.append("- " + c)
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- run

def run():
    face = load_gate()
    picks = gate_picks(face)
    pub = published_reading(face)
    close, amt = panel_adv()
    capital = pub.get("capital_cny")
    line_pct = pub.get("line_pct")
    if not picks or capital is None or line_pct is None:
        raise SystemExit("闸面缺 live_picks / 资本透镜 / 闸线，无法测量")
    line = float(line_pct) / 100.0

    rows = sessions(amt, picks, float(capital), line)
    s = summarise(rows, float(capital), line)
    s["n_names"] = len(picks)

    payload = {
        "artifact": "etf_book_capacity_edge",
        "face": "results/etf_book_capacity_edge.json",
        "script": "scripts/etf_book_capacity_edge.py",
        "evidence_cutoff": str(amt.index[-1])[:10],
        "session": str(amt.index[-1])[:10],
        "published": pub,
        "criteria": {"line_pct": float(line_pct), "lens_cny": float(capital),
                     "lens_tag": pub.get("lens"), "window_sessions": WINDOW_SESSIONS,
                     "adv_bars": ADV_BARS, "adv_face": "close x volume, rolling 20 median; read as the median of its last 20 values",
                     "verdict_rule": ("rate==0 BELOW_LINE_EVERY_SESSION / rate==1 ABOVE_LINE_EVERY_SESSION / "
                                      "0.20<=rate<=0.80 COIN_FLIP_AT_THE_LINE / else minority side"),
                     "coin_flip_band": [COIN_FLIP_LO, COIN_FLIP_HI]},
        "picks": picks,
        "summary": s,
        "sessions": rows,
        "caveats": [
            "这笔单子固定成今天的选票、等权：量的是尺子的余量，不是「重新选票后那些天会填成什么样」",
            "成交额用的是闸自己的口径（收盘价×成交量、中位再取中位），不是成交明细：它是估计值而且是阶梯状的，所以读数一格一格跳",
            "「1% ADV」是闸选定的线，不是量出来的线；换一条线，这里每个数按同一比例移动",
            "读数在窗内上下走是市场成交额在走，不是这本书在走；这里没有一句话说明天会读到什么",
            "资本上限是一个资本数，不是一张能下的单：整数手与 8% 波动目标都可能把它压得更低（见 etf_book_ticket_floor / etf_book_lot_floor）",
        ],
    }
    payload["sentence"] = sentence(s)

    with io.open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    with io.open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(payload))

    chk = check(payload)
    print(json.dumps({"artifact": "etf_book_capacity_edge", "ok": chk["ok"],
                      "problems": chk["problems"], "verdict": s["verdict"],
                      "reading_today_pct": s["reading_today_pct"],
                      "capital_today_cny": s["capital_where_at_line_today_cny"],
                      "passes": "%d/%d" % (s["n_passes"], s["n_measurable"])},
                     ensure_ascii=False))
    return 0 if chk["ok"] else 2


def main_check():
    with io.open(OUT_JSON, encoding="utf-8") as f:
        payload = json.load(f)
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

    def L1_scales_with_capital():
        adv = {"A": 20e6, "B": 40e6}
        m1 = measure(["A", "B"], 1e6, LINE, adv)
        m2 = measure(["A", "B"], 2e6, LINE, adv)
        assert abs(m2["reading"] - 2 * m1["reading"]) < 1e-12, "资本翻倍读数应翻倍"
        assert m1["binding"] == "A", "最弱的是 A"

    def L2_flip_capital_round_trips():
        adv = {"A": 19.82841685e6, "B": 90e6, "C": 80e6, "D": 70e6, "E": 60e6}
        m = measure(list(adv), 1e6, LINE, adv)
        cap = m["capital_where_at_line_cny"]
        at = measure(list(adv), cap, LINE, adv)["reading"]
        assert abs(at - LINE) < 1e-10, "阈值资本应当正好落在闸线上：%r" % (at,)
        over = measure(list(adv), cap * (1 + 1e-6), LINE, adv)["reading"]
        assert over > LINE, "高一丁点就该过线"

    def L3_gap_matches_lens():
        adv = {"A": 19.82841685e6, "B": 90e6, "C": 80e6, "D": 70e6, "E": 60e6}
        rows = [{"bar": "d1", "reading": measure(list(adv), 1e6, LINE, adv)["reading"],
                 "binding": "A", "capital_where_at_line_cny": None, "unmeasurable": []}]
        m = measure(list(adv), 1e6, LINE, adv)
        rows[0]["capital_where_at_line_cny"] = m["capital_where_at_line_cny"]
        s = summarise(rows, 1e6, LINE)
        assert abs(s["gap_to_lens_cny"] - (1e6 - m["capital_where_at_line_cny"])) < 0.01, "差额应等于透镜减上限"

    def L4_binding_is_argmax_not_first():
        adv = {"A": 100e6, "B": 5e6}
        m = measure(["A", "B"], 1e6, LINE, adv)
        assert m["binding"] == "B", "第一个名字不是最弱的那个：%r" % (m["binding"],)

    def L5_missing_adv_is_counted_not_skipped():
        adv = {"A": 50e6, "B": None}
        m = measure(["A", "B"], 1e6, LINE, adv)
        assert m["unmeasurable"] == ["B"], "缺 ADV 的名字必须点名：%r" % (m["unmeasurable"],)
        assert m["binding"] == "A", "缺的那个不能顶替最弱席位"
        rows = [{"bar": "d1", "reading": None, "binding": None,
                 "capital_where_at_line_cny": None, "unmeasurable": ["A", "B"]}]
        s = summarise(rows, 1e6, LINE)
        assert s["n_measurable"] == 0 and s["verdict"] == "NO_MEASURABLE_SESSION", "读不到不是过线"

    def L6_pass_count_and_verdict_names():
        def rows_with(passes, n):
            out = []
            for i in range(n):
                out.append({"bar": "d%d" % i, "reading": 0.009 if i < passes else 0.011,
                            "binding": "A", "capital_where_at_line_cny": 5e6, "unmeasurable": []})
            return out
        a = summarise(rows_with(0, 10), 1e6, LINE)
        assert a["verdict"] == "BELOW_LINE_EVERY_SESSION", a["verdict"]
        b = summarise(rows_with(10, 10), 1e6, LINE)
        assert b["verdict"] == "ABOVE_LINE_EVERY_SESSION", b["verdict"]
        c = summarise(rows_with(5, 10), 1e6, LINE)
        assert c["verdict"] == "COIN_FLIP_AT_THE_LINE", c["verdict"]
        d = summarise(rows_with(1, 10), 1e6, LINE)
        assert d["verdict"] == "BELOW_LINE_MOST_SESSIONS", d["verdict"]
        e = summarise(rows_with(9, 10), 1e6, LINE)
        assert e["verdict"] == "ABOVE_LINE_MOST_SESSIONS", e["verdict"]

    def L7_worst_day_capital_is_the_min():
        adv_hi = {"A": 30e6, "B": 30e6}
        adv_lo = {"A": 10e6, "B": 30e6}
        r1 = measure(["A", "B"], 1e6, LINE, adv_hi)
        r2 = measure(["A", "B"], 1e6, LINE, adv_lo)
        rows = [{"bar": "d1", "reading": r1["reading"], "binding": r1["binding"],
                 "capital_where_at_line_cny": r1["capital_where_at_line_cny"], "unmeasurable": []},
                {"bar": "d2", "reading": r2["reading"], "binding": r2["binding"],
                 "capital_where_at_line_cny": r2["capital_where_at_line_cny"], "unmeasurable": []}]
        s = summarise(rows, 1e6, LINE)
        assert abs(s["capital_min_cny"] - r2["capital_where_at_line_cny"]) < 0.01, "最差日=最小上限"
        assert abs(s["capital_max_cny"] - r1["capital_where_at_line_cny"]) < 0.01, "最好日=最大上限"

    def L8_quantized_input_repeats():
        # the gate's ADV is a median of medians: it lands on a handful of values
        vals = [19.82841685e6] * 3 + [20.060088e6] * 4 + [20.876018e6] * 3
        rows = []
        for i, v in enumerate(vals):
            m = measure(["A"], 1e6, LINE, {"A": v})
            rows.append({"bar": "d%d" % i, "reading": m["reading"], "binding": "A",
                         "capital_where_at_line_cny": m["capital_where_at_line_cny"],
                         "unmeasurable": []})
        s = summarise(rows, 1e6, LINE)
        assert s["n_distinct_readings"] == 3, "只应落在 3 个值上：%r" % (s["n_distinct_readings"],)

    def L9_check_catches_tampering():
        adv = {"A": 19.82841685e6, "B": 90e6}
        m = measure(["A", "B"], 1e6, LINE, adv)
        rows = [{"bar": "d1", "reading": m["reading"], "binding": "A",
                 "capital_where_at_line_cny": m["capital_where_at_line_cny"], "unmeasurable": []}]
        s = summarise(rows, 1e6, LINE)
        s["n_names"] = 2
        base = {"criteria": {"line_pct": 1.0, "lens_cny": 1e6}, "summary": s, "sessions": rows,
                "published": {"impact_pct_of_adv": round(m["reading"] * 100.0, 4)}}
        assert check(base)["ok"], "干净载荷应过：%r" % (check(base)["problems"],)
        lie = json.loads(json.dumps(base))
        lie["summary"]["n_passes"] = 1
        assert not check(lie)["ok"], "改通过数必须被抓"
        flip = json.loads(json.dumps(base))
        flip["summary"]["verdict"] = "COIN_FLIP_AT_THE_LINE"
        assert not check(flip)["ok"], "判词名与计数不符必须被抓"
        drift = json.loads(json.dumps(base))
        drift["published"]["impact_pct_of_adv"] = 1.5
        assert not check(drift)["ok"], "与闸面读数不符必须被抓"

    def L10_sentence_cites_own_counts():
        adv = {"A": 19.82841685e6, "B": 90e6}
        m = measure(["A", "B"], 1e6, LINE, adv)
        rows = [{"bar": "d1", "reading": m["reading"], "binding": "A",
                 "capital_where_at_line_cny": m["capital_where_at_line_cny"], "unmeasurable": []}]
        s = summarise(rows, 1e6, LINE)
        s["n_names"] = 2
        t = sentence(s)
        assert "{:,.0f}".format(s["capital_where_at_line_today_cny"]) in t, "上限数应出现在句子里"
        assert "1,000,000" in t, "透镜应出现在句子里"

    def L11_stale_face_is_named():
        # r1850: the leg has to fire on a face that is standing on an old day, and it has
        # to stay quiet when the face is not behind -- otherwise the round after this one
        # gets a permanently red leg and learns to read it as background noise (r1789).
        adv = {"A": 19.82841685e6, "B": 90e6}
        m = measure(["A", "B"], 1e6, LINE, adv)
        rows = [{"bar": "d1", "reading": m["reading"], "binding": "A",
                 "capital_where_at_line_cny": m["capital_where_at_line_cny"],
                 "unmeasurable": []}]
        s = summarise(rows, 1e6, LINE)
        s["n_names"] = 2
        base = {"artifact": "etf_book_capacity_edge",
                "evidence_cutoff": "2000-01-01",
                "criteria": {"line_pct": 1.0, "lens_cny": 1e6}, "summary": s,
                "sessions": rows,
                "published": {"impact_pct_of_adv": round(m["reading"] * 100.0, 4)}}
        old = check(base)
        assert not old["ok"], "停在 2000-01-01 的面必须被抓"
        assert any("FACE_BEHIND_GATE" in p for p in old["problems"]), \
            "要指名 FACE_BEHIND_GATE，而不是一句泛红：%r" % (old["problems"],)
        ahead = json.loads(json.dumps(base))
        ahead["evidence_cutoff"] = "2099-01-01"
        assert not any("FACE_BEHIND_GATE" in p for p in check(ahead)["problems"]), \
            "在闸面前面的日子不该被这条腿判红：%r" % (check(ahead)["problems"],)
        fixture = json.loads(json.dumps(base))
        fixture.pop("artifact")
        assert not any("FACE_BEHIND_GATE" in p for p in check(fixture)["problems"]), \
            "自检夹具（无 artifact 标记）不该被现状腿拦"

    for name, fn in [
        ("L1 读数随资本线性", L1_scales_with_capital),
        ("L2 阈值资本落在闸线上", L2_flip_capital_round_trips),
        ("L3 差额=透镜减上限", L3_gap_matches_lens),
        ("L4 最弱席位是 argmax 不是第一个", L4_binding_is_argmax_not_first),
        ("L5 缺 ADV 点名且不算过", L5_missing_adv_is_counted_not_skipped),
        ("L6 判词名由计数决定（五态）", L6_pass_count_and_verdict_names),
        ("L7 最差日=最小上限", L7_worst_day_capital_is_the_min),
        ("L8 量化读数只落在少数值上", L8_quantized_input_repeats),
        ("L9 改判/塞数/漂移被抓", L9_check_catches_tampering),
        ("L10 句子引用自己的计数", L10_sentence_cites_own_counts),
        ("L11 停在旧日的面会被点名（r1850）", L11_stale_face_is_named),
    ]:
        leg(name, fn)

    passed = sum(1 for _n, ok, _m in legs if ok)
    for n, ok, msg in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", n, "" if ok else "  <- " + msg))
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
