"""Freeze the drawdown-depth sign on 2022-2023, then let it pick 2024-2026 quarters.

r2133 (scripts/etf_book_cadence_regime_predict.py) found the one observable that
survives its own gates: the equal-weight book universe's trailing 60-bar
drawdown depth ranks the quarters (rho=-0.67, family p=0.080), and the direction
carried out of the first half of the calendar still made money on the second
half (+1.65 pp/q) while using the full-sample sign lost (E222: a direction found
after the fact is not a rule).

That face stopped at *naming* it. This face does the two things that make it
usable, and it does them cheaply by re-reading the same panels:

  1. FREEZE. The sign and the split point are learned on quarters that closed on
     or before 2023-12-31 and are then written into the face as an explicit
     constant block with its training evidence. Nothing dated 2024 or later may
     touch them; `check` re-derives the block from the train window only and
     fails if it moved.
  2. PAPER TRACK. Every quarter opening on or after 2024-01-01 is scored with the
     frozen rule on the SAME grid the split face uses (six start dates, n_hold=5,
     8bp, fast=R10 vs slow=R20). The quarter's realised gap is the median of the
     six same-grid start pairs; the rule's money for that quarter is
     +gap if it picked fast and -gap if it picked slow. Always-fast is the
     baseline, so the ledger's own column is the only claim made.

Both 2026Q1..2026Q3 (closed, not part of the split face's frozen quarter list)
and 2026Q4 (open, partial slice) are built here from the engine, so the rule is
scored on quarters it was never fitted to and the reader can see the picks
rather than a summary of them.

usage:
  self  python scripts/etf_book_cadence_sign_freeze.py selftest
  run   python scripts/etf_book_cadence_sign_freeze.py run
  check python scripts/etf_book_cadence_sign_freeze.py check
"""
import json
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "results", "etf_book_cadence_sign_freeze.json")
FACE = "results/etf_book_cadence_sign_freeze.json"
SCHEMA = "etf-book-cadence-sign-freeze/v1"
UPSTREAM_PREDICT = os.path.join(ROOT, "results", "etf_book_cadence_regime_predict.json")
UPSTREAM_SPLIT = os.path.join(ROOT, "results", "etf_book_cadence_regime_split.json")

COST_KEY, COST = "8bp", 0.0008
OBSERVABLE = "trail_dd60"

# the freeze window: quarters that CLOSED on or before this date may teach the sign
TRAIN_HI_EXCLUSIVE = "2024-01-01"
# scoring window: quarters that OPEN on or after this date are out of the freeze
SCORE_LO = "2024-01-01"
# the split face's own quarter list stops at 2025Q4; these are added by this face
EXTRA_QUARTERS = ["2026Q1", "2026Q2", "2026Q3", "2026Q4"]

PICK_FAST, PICK_SLOW = "FAST_R10", "SLOW_R20"
MIN_TRAIN_QUARTERS = 6

WORDS_TRACKED = "DD_DEPTH_SIGN_FROZEN_AND_PAPER_TRACKED"
WORDS_DOUBTFUL = "FROZEN_RULE_DOES_NOT_BEAT_ALWAYS_FAST_ON_TRACKED_QUARTERS"
WORDS_THIN = "TRACK_WINDOW_TOO_THIN_TO_SCORE"


# ------------------------------------------------------------------ pure logic


def quarter_bounds(labels):
    """'2026Q3' -> ('2026-07-01', '2026-10-01'); no calendar library needed."""
    out = {}
    for lab in labels:
        y, q = int(lab[:4]), int(lab[-1])
        m0 = (q - 1) * 3 + 1
        m1 = m0 + 3
        out[lab] = ["%04d-%02d-01" % (y, m0),
                    "%04d-%02d-01" % (y + (1 if m1 > 12 else 0), (1 if m1 > 12 else m1))]
    return out


def learn_sign(train_rows, observable=OBSERVABLE):
    """fit (direction, split point) on the train window only.

    train_rows: [{quarter, gap_pp, <observable>}]. Returns None when the window
    is too thin or the observable is missing, so the caller refuses to freeze
    rather than freezing a coin flip.
    """
    rows = [r for r in train_rows if r.get("gap_pp") is not None
            and r.get(observable) is not None]
    if len(rows) < MIN_TRAIN_QUARTERS:
        return None
    xs = [float(r[observable]) for r in rows]
    ys = [float(r["gap_pp"]) for r in rows]

    def average_ranks(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        out = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                out[order[k]] = avg
            i = j + 1
        return out

    rx, ry = average_ranks(xs), average_ranks(ys)
    mx, my = st.fmean(rx), st.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    if dx == 0.0 or dy == 0.0:
        return None
    rho = num / (dx * dy)
    direction = 1 if rho > 0 else -1
    # deeper drawdown than the train median -> the side the train rho points to
    return {"observable": observable, "train_n": len(rows),
            "train_rho": rho, "direction": direction,
            "split_point": st.median(xs),
            "train_quarters": [r["quarter"] for r in rows],
            "train_gap_median_pp": st.median(ys)}


def pick_for(value, frozen):
    """the frozen rule, as a pure function of one observable reading."""
    if value is None or frozen is None:
        return None
    above = float(value) > float(frozen["split_point"])
    # direction>0 means "higher observable -> better for fast"; deeper drawdown is
    # a HIGHER depth number, so direction<0 sends the deep quarters to slow.
    goat_fast = (above and frozen["direction"] > 0) or ((not above) and frozen["direction"] < 0)
    return PICK_FAST if goat_fast else PICK_SLOW


def quarter_money(pick, gap_pp):
    """what the pick made in that quarter, pp, signed so always-fast is +gap."""
    if pick is None or gap_pp is None:
        return None
    return gap_pp if pick == PICK_FAST else -gap_pp


def ledger(rows, frozen):
    scored = [r for r in rows if r.get("pick") is not None and r.get("gap_pp") is not None]
    if not scored:
        return {"n": 0, "words": WORDS_THIN}
    rule_pp = st.fmean([quarter_money(r["pick"], r["gap_pp"]) for r in scored])
    fast_pp = st.fmean([r["gap_pp"] for r in scored])
    hits = sum(1 for r in scored if quarter_money(r["pick"], r["gap_pp"]) > 0)
    return {"n": len(scored), "rule_pp_per_q": rule_pp, "always_fast_pp_per_q": fast_pp,
            "improvement_pp_per_q": rule_pp - fast_pp,
            "hit_share": hits / float(len(scored)),
            "slow_picks": sum(1 for r in scored if r["pick"] == PICK_SLOW),
            "words": (WORDS_TRACKED if rule_pp - fast_pp > 0 else WORDS_DOUBTFUL)}


# ------------------------------------------------------------------ panels


def quarter_gaps(cells, quarters, starts, min_starts=2):
    """median of the same-grid start pairs inside each quarter, per quarter.

    Two starts is the floor, matching the split face's own MIN_BOOKS_PER_SEGMENT=2:
    below two there is no pair at all, and one start is one path, not the quarter.
    How many starts carried each quarter is printed on the row, so a two-start
    quarter reads as thin instead of hiding behind a median.
    """
    gaps, holes = {}, []
    for lab in quarters:
        vals, used = [], []
        for s in starts:
            got = [c for c in cells
                   if c["segment"] == lab and c["start"] == s and c["cost"] == COST_KEY]
            if not got:
                continue
            vals.append(float(got[0]["delta_pp"]))
            used.append(s)
        if len(vals) < min_starts:
            holes.append({"quarter": lab, "why": "only %d start(s) on the same grid, need %d"
                          % (len(vals), min_starts), "starts": used})
            continue
        gaps[lab] = {"gap_pp": st.median(vals), "n_starts": len(vals), "starts": used,
                     "min_pp": min(vals), "max_pp": max(vals)}
    return gaps, holes


def build_extra_cells(quarters, starts):
    """engine cells for quarters the split face never built (2026Q*)."""
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from scripts import etf_book_cadence_regime_split as RS

    F, V, close, openp, cols, score = RS.build_inputs()
    bounds = quarter_bounds(quarters)
    cells, holes = [], []
    for start in starts:
        runs = {}
        for cad in (RS.CADENCE_FAST, RS.CADENCE_SLOW):
            ser, _turn, _gap = V.fast_next_open(score, close[cols], openp[cols], cad,
                                                n_hold=RS.N_HOLD, cost=COST, start=start)
            if ser is None or len(ser) < RS.MIN_BARS:
                holes.append({"start": start, "cadence": cad,
                              "why": "run empty or shorter than %d bars" % RS.MIN_BARS})
                runs[cad] = None
                continue
            runs[cad] = ser
        if runs.get(RS.CADENCE_FAST) is None or runs.get(RS.CADENCE_SLOW) is None:
            continue
        for lab, (lo, hi) in sorted(bounds.items()):
            rf, nf = RS.slice_ret(runs[RS.CADENCE_FAST], lo, hi)
            rs, ns = RS.slice_ret(runs[RS.CADENCE_SLOW], lo, hi)
            if rf is None or rs is None:
                holes.append({"start": start, "segment": lab,
                              "why": "slice too thin (%d/%d bars < %d)"
                                     % (nf, ns, RS.MIN_BARS)})
                continue
            cells.append({"start": start, "cost": COST_KEY, "segment": lab,
                          "bars": min(nf, ns), "ret_fast_pct": rf * 100.0,
                          "ret_slow_pct": rs * 100.0, "delta_pp": (rf - rs) * 100.0})
    return cells, holes, close, cols


# ------------------------------------------------------------------ cross-checks


def target_cross_check(cells, starts, split_face, rows):
    """the same depth reading, two targets and two windows -- because the size of
    the r2133 finding depends on which one you ask about.

    target A = the two-way median polish column effect on the window's own subgrid
               (what r2133 used: it strips the start-date channel out)
    target B = the per-quarter median of the paired start deltas (what one book
               actually experiences, start-date channel included)
    windows  = the freeze window (quarters closed on/before 2023-12-31) and the
               window r2133 itself trained on (read from its face, not hard-coded)
    """
    sys.path.insert(0, ROOT)
    from scripts import etf_book_cadence_regime_predict as RP

    order = [r["quarter"] for r in rows]
    dd = {r["quarter"]: r.get(OBSERVABLE) for r in rows}
    gap = {r["quarter"]: r.get("gap_pp") for r in rows}
    with open(UPSTREAM_PREDICT, "r", encoding="utf-8") as fh:
        pred = json.load(fh)
    r2133 = (((pred.get("read") or {}).get("observables") or {}).get(OBSERVABLE) or {})
    w_r2133 = list(((r2133.get("out_of_sample") or {}).get("train_segments") or []))

    windows = {
        "freeze_2022_2023": [q for q in order if q in dd
                             and (quarter_bounds([q])[q][1] <= TRAIN_HI_EXCLUSIVE)],
        "r2133_train": [q for q in w_r2133 if q in dd],
    }
    out = {"target_a": "two-way median polish column effect on the window's own subgrid",
           "target_b": "per-quarter median of the paired same-grid start deltas",
           "r2133_published_rho": r2133.get("rho"),
           "cells": {}, "window_slide": []}

    # the same reading with its window slid by one quarter: a rank order that moves
    # this much when two quarters join or leave is not a rule, it is a fit
    def _rho_b(qs):
        xs = [float(dd[q]) for q in qs if dd.get(q) is not None and gap.get(q) is not None]
        ys = [float(gap[q]) for q in qs if dd.get(q) is not None and gap.get(q) is not None]
        if len(xs) < 5:
            return None
        return RP.spearman(xs, ys)

    fw = list(windows["freeze_2022_2023"])
    for label, qs in (("freeze_window", fw),
                      ("drop_first_quarter", fw[1:]),
                      ("drop_first_two", fw[2:]),
                      ("add_first_post_2023", None)):
        if qs is None:
            after = [r["quarter"] for r in rows
                     if quarter_bounds([r["quarter"]])[r["quarter"]][1] > TRAIN_HI_EXCLUSIVE
                     and r.get("gap_pp") is not None]
            qs = fw + (after[:1] if after else [])
        out["window_slide"].append({"variant": label, "quarters": qs,
                                    "n": len(qs), "target_b_rho": _rho_b(qs)})
    for wname, qs in windows.items():
        if len(qs) < 5:
            out["cells"][wname] = {"quarters": qs, "why": "fewer than 5 quarters with an observable"}
            continue
        sub = [c for c in cells if c["cost"] == COST_KEY and c["segment"] in qs
               and c["start"] in starts]
        grid = {(c["start"], c["segment"]): float(c["delta_pp"]) for c in sub}
        pol = RP.polish(grid) if grid else None
        a, b = [], []
        xa, xb = [], []
        for q in qs:
            if dd.get(q) is None:
                continue
            if pol is not None and q in (pol.get("col") or {}):
                xa.append(float(dd[q]))
                a.append(float(pol["col"][q]))
            if gap.get(q) is not None:
                xb.append(float(dd[q]))
                b.append(float(gap[q]))
        out["cells"][wname] = {
            "quarters": qs,
            "target_a_n": len(a), "target_a_rho": RP.spearman(xa, a) if len(a) >= 5 else None,
            "target_b_n": len(b), "target_b_rho": RP.spearman(xb, b) if len(b) >= 5 else None,
        }
    return out


def concentration(scored):
    """how much of the ledger rides on one quarter -- a rule that only paid twice
    is a coincidence with a story attached."""
    pairs = [(r["quarter"], quarter_money(r["pick"], r["gap_pp"])) for r in scored
             if quarter_money(r["pick"], r["gap_pp"]) is not None]
    if not pairs:
        return {"n": 0}
    pairs.sort(key=lambda t: -t[1])
    total = sum(v for _q, v in pairs)
    rest = pairs[1:]
    return {"n": len(pairs), "total_pp": total,
            "best_quarter": pairs[0][0], "best_pp": pairs[0][1],
            "best_share_of_total": (pairs[0][1] / total) if total else None,
            "improvement_pp_per_q_without_best":
                (sum(v for _q, v in rest) / len(rest)) if rest else None,
            "drops_below_zero_without_best": (
                bool(rest) and (sum(v for _q, v in rest) / len(rest)) <= 0.0)}


# ------------------------------------------------------------------ driver


def compute():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from scripts import etf_book_cadence_regime_split as RS
    from scripts import etf_book_cadence_regime_predict as RP

    with open(UPSTREAM_SPLIT, "r", encoding="utf-8") as fh:
        split_face = json.load(fh)
    starts = split_face["starts"]
    base_quarters = list(split_face["segments"])

    extra_cells, extra_holes, close, cols = build_extra_cells(EXTRA_QUARTERS, starts)
    all_cells = list(split_face["cells"]) + extra_cells
    every_quarter = base_quarters + EXTRA_QUARTERS
    bounds = quarter_bounds(every_quarter)
    gaps, gap_holes = quarter_gaps(all_cells, every_quarter, starts)

    obs, obs_holes = RP.market_observables(close, cols, bounds)

    rows = []
    for lab in every_quarter:
        row = {"quarter": lab, "bounds": bounds[lab],
               "gap_pp": (gaps.get(lab) or {}).get("gap_pp"),
               "n_starts": (gaps.get(lab) or {}).get("n_starts"),
               "gap_min_pp": (gaps.get(lab) or {}).get("min_pp"),
               "gap_max_pp": (gaps.get(lab) or {}).get("max_pp")}
        o = obs.get(lab) or {}
        row["asof"] = o.get("asof")
        for key in ("trail_dd60", "trail_ret60", "trail_vol60", "xs_disp60"):
            row[key] = o.get(key)
        rows.append(row)

    train = [r for r in rows if r["bounds"][1] <= TRAIN_HI_EXCLUSIVE]
    frozen = learn_sign(train)
    if frozen is None:
        print("FATAL train window gives no sign to freeze (%d rows)" % len(train))
        return 2

    scored = []
    for r in rows:
        if r["bounds"][0] < SCORE_LO:
            continue
        r["pick"] = pick_for(r.get(OBSERVABLE), frozen)
        r["rule_pp"] = quarter_money(r.get("pick"), r.get("gap_pp"))
        r["baseline_pp"] = r.get("gap_pp")
        r["status"] = ("SCORED" if r["rule_pp"] is not None
                       else ("PENDING_CELLS" if r["pick"] is not None
                             else "NO_OBSERVABLE"))
        scored.append(r)

    led = ledger(scored, frozen)
    conc = concentration(scored)
    cross = target_cross_check(all_cells, starts, split_face, rows)
    live = [r for r in rows if r["bounds"][0] <= (close.index[-1].date().isoformat())
            and r["bounds"][1] > close.index[-1].date().isoformat()]
    now_pick = live[0].get("pick") if live else None

    body = {
        "schema": SCHEMA,
        "face": FACE,
        "question": "can the drawdown-depth sign found in 2022-2023 be frozen and then "
                    "score the quarters it never saw, including 2026?",
        "rule": {
            "R1_observable": "trail_dd60 of the equal-weight book universe, measured strictly "
                             "on bars dated before the quarter's lo bound",
            "R2_freeze": "direction and split point are learned on quarters that CLOSED on or "
                         "before %s and are copied into frozen_rule verbatim" % TRAIN_HI_EXCLUSIVE,
            "R3_target": "per-quarter realised gap = median over the same-grid start pairs of "
                         "(fast %d / slow %d, n_hold=%d, %s); a quarter needs >=2 paired starts"
                         " (the split face's own floor) and its start count is printed"
                         % (RS.CADENCE_FAST, RS.CADENCE_SLOW, RS.N_HOLD, COST_KEY),
            "R4_money": "the pick earns +gap when it picked fast and -gap when it picked slow; "
                        "always-fast is the baseline",
            "R5_scope": "2026Q1..2026Q3 are built by this face because the split face's quarter "
                        "list stops at 2025Q4; 2026Q4 is a partial slice",
            "frozen": "R1-R5 written before the first read of the 2026 cells in this round",
        },
        "upstream": {"split_face": split_face.get("face"),
                     "split_cutoff": split_face.get("evidence_cutoff"),
                     "predict_face": "results/etf_book_cadence_regime_predict.json",
                     "starts": starts, "cost": COST_KEY},
        "evidence_cutoff": split_face.get("evidence_cutoff"),
        "frozen_rule": frozen,
        "quarters": rows,
        "tracked": scored,
        "holes": gap_holes + obs_holes + extra_holes,
        "ledger": led,
        "ledger_concentration": conc,
        "target_cross_check": cross,
        "now": {"quarter": live[0]["quarter"] if live else None,
                "asof": live[0].get("asof") if live else None,
                "dd60": live[0].get(OBSERVABLE) if live else None,
                "pick": now_pick},
        "headline": {"words": led["words"],
                     "rule_pp_per_q": led.get("rule_pp_per_q"),
                     "always_fast_pp_per_q": led.get("always_fast_pp_per_q"),
                     "improvement_pp_per_q": led.get("improvement_pp_per_q"),
                     "hit_share": led.get("hit_share"),
                     "n_tracked": led.get("n"),
                     "train_rho": frozen["train_rho"],
                     "now_pick": now_pick},
        "desk_sentence": desk_sentence(frozen, led, live, rows, cross, conc),
        "honest": [
            "the tracked window is short: %d scored quarters is a ledger, not a verdict"
            % led.get("n", 0),
            "2026Q4 is an open quarter, so its gap is a partial slice and its row is marked by "
            "the bounds it carries, not by a promise",
            "the gap is a total-return difference between two cadences on one book, not an "
            "annual return; no leverage, no capacity model",
            "the observable is measured on the equal-weight book universe, so a different "
            "universe would move the depth number on the same dates",
        ],
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(body, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("WROTE", FACE)
    print(desk_sentence(frozen, led, live, rows, cross, conc))
    return 0


def desk_sentence(frozen, led, live, rows, cross=None, conc=None):
    head = ("把 2022-2023 定下的「跌得越深→慢节奏」符号冻住（真实成交口径 ρ=%+.2f，训练 %d 个季度，"
            "分界点深度 %.2f%%）后，它在 %d 个季度上的账：规则 %s pp/季 vs 一直快 %s pp/季，"
            "改善 %s pp/季，命中 %s。"
            % (frozen["train_rho"], frozen["train_n"], frozen["split_point"], led.get("n", 0),
               _fmt(led.get("rule_pp_per_q")), _fmt(led.get("always_fast_pp_per_q")),
               _fmt(led.get("improvement_pp_per_q")),
               "n/a" if led.get("hit_share") is None else "%.0f%%" % (led["hit_share"] * 100)))
    if cross:
        slide = [s for s in (cross.get("window_slide") or []) if s.get("target_b_rho") is not None]
        if slide:
            lo = min(slide, key=lambda s: s["target_b_rho"])
            hi = max(slide, key=lambda s: s["target_b_rho"])
            head += ("**这个排序怕窗口**：同一批深跌读数、同一个真实成交口径，窗口只挪一两个季度，"
                     "ρ 从 %s（%d 季）滑到 %s（%d 季）——上游 -0.67 与更弱的 %s 都是同一个排序的不同截面，"
                     "所以能用的是下面打在没参与拟合的季度上的账，不是相关系数。"
                     % (_fmt3(lo["target_b_rho"]), lo["n"], _fmt3(hi["target_b_rho"]), hi["n"],
                        _fmt3((cross.get("cells") or {}).get("freeze_2022_2023", {})
                              .get("target_b_rho"))))
    if conc and conc.get("n"):
        head += ("账里最大的一季是 %s（%+.2f pp，占总额 %s）；剔掉它剩 %s pp/季。"
                 % (conc["best_quarter"], conc["best_pp"],
                    "n/a" if conc.get("best_share_of_total") is None
                    else "%.0f%%" % (conc["best_share_of_total"] * 100),
                    _fmt(conc.get("improvement_pp_per_q_without_best"))))
    tail = []
    for r in rows:
        if r.get("pick") is None:
            continue
        who = ("开季中" if r.get("n_starts") is None else "%d 起跑" % r["n_starts"])
        tail.append("%s（%s）深度 %s%%→%s，实际 %s"
                    % (r["quarter"], who,
                       "n/a" if r.get(OBSERVABLE) is None else "%.1f" % r[OBSERVABLE],
                       "快" if r["pick"] == PICK_FAST else "慢",
                       "待算" if r.get("gap_pp") is None else "%+.2f pp" % r["gap_pp"]))
    now = ("；此刻开着的是 %s（截至 %s 深度 %s，规则选%s）"
           % (live[0]["quarter"], live[0].get("asof"),
              "n/a" if live[0].get(OBSERVABLE) is None else "%.1f%%" % live[0][OBSERVABLE],
              "快" if live[0].get("pick") == PICK_FAST else "慢") if live else "")
    return head + now + "；" + "；".join(tail)


def _fmt(v):
    return "n/a" if v is None else "%+.2f" % v


def _fmt3(v):
    return "n/a" if v is None else "%+.2f" % v


# ------------------------------------------------------------------ check


def check():
    if not os.path.exists(OUT_PATH):
        print("FACE MISSING run first")
        return 2
    with open(OUT_PATH, "r", encoding="utf-8") as fh:
        body = json.load(fh)
    with open(UPSTREAM_SPLIT, "r", encoding="utf-8") as fh:
        split_face = json.load(fh)
    if body.get("evidence_cutoff") != split_face.get("evidence_cutoff"):
        print("STALE upstream cutoff %r != %r"
              % (body.get("evidence_cutoff"), split_face.get("evidence_cutoff")))
        return 3
    stored_train = [r for r in body.get("quarters") or []
                    if (r.get("bounds") or ["", ""])[1] <= TRAIN_HI_EXCLUSIVE]
    again = learn_sign(stored_train)
    got = body.get("frozen_rule") or {}
    bad = []
    for field in ("train_rho", "direction", "split_point", "train_n"):
        a, b = (again or {}).get(field), got.get(field)
        if isinstance(a, float) and isinstance(b, float):
            if abs(a - b) > 1e-9:
                bad.append("frozen.%s %.12f != %.12f" % (field, a, b))
        elif a != b:
            bad.append("frozen.%s %r != %r" % (field, a, b))
    for r in body.get("tracked") or []:
        p = pick_for(r.get(OBSERVABLE), again)
        if p != r.get("pick"):
            bad.append("%s pick %r != %r" % (r.get("quarter"), p, r.get("pick")))
        m = quarter_money(r.get("pick"), r.get("gap_pp"))
        if isinstance(m, float) and isinstance(r.get("rule_pp"), float):
            if abs(m - r["rule_pp"]) > 1e-9:
                bad.append("%s rule_pp %.12f != %.12f" % (r.get("quarter"), m, r["rule_pp"]))
        elif m != r.get("rule_pp"):
            bad.append("%s rule_pp %r != %r" % (r.get("quarter"), m, r.get("rule_pp")))
    led_again = ledger(body.get("tracked") or [], again)
    stored_led = body.get("ledger") or {}
    if led_again.get("n") != stored_led.get("n"):
        bad.append("ledger.n %r != %r" % (led_again.get("n"), stored_led.get("n")))
    for field in ("rule_pp_per_q", "improvement_pp_per_q"):
        a, b = led_again.get(field), stored_led.get(field)
        if isinstance(a, float) and isinstance(b, float):
            if abs(a - b) > 1e-9:
                bad.append("ledger.%s %.12f != %.12f" % (field, a, b))
        elif a != b:
            bad.append("ledger.%s %r != %r" % (field, a, b))
    if led_again.get("words") != stored_led.get("words"):
        bad.append("ledger.words %r != %r" % (led_again.get("words"), stored_led.get("words")))
    if bad:
        print("CHECK FAILED " + "; ".join(bad[:6]))
        return 1
    print("CHECK OK frozen_rho=%+.3f tracked=%d words=%s"
          % (got.get("train_rho"), led_again.get("n"), led_again.get("words")))
    return 0


# ------------------------------------------------------------------ selftest


def selftest():
    legs, fails = [], []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))
        if not ok:
            fails.append(name)

    # 1 bounds arithmetic: quarter labels are the only calendar here
    b = quarter_bounds(["2026Q1", "2026Q4"])
    leg("bounds_q1", b["2026Q1"] == ["2026-01-01", "2026-04-01"], str(b["2026Q1"]))
    leg("bounds_q4_closes_next_year", b["2026Q4"] == ["2026-10-01", "2027-01-01"], str(b["2026Q4"]))

    # 2 the sign is learned from the train window, and a deeper drawdown moves the pick
    train = [{"quarter": "2022Q%d" % i, "gap_pp": -float(i), OBSERVABLE: float(i)}
             for i in range(1, 7)]
    fz = learn_sign(train)
    leg("learn_sign_fits_a_negative_direction", fz is not None and fz["direction"] < 0,
        str(fz and round(fz["train_rho"], 3)))
    leg("deep_quarter_goes_slow", pick_for(99.0, fz) == PICK_SLOW, str(pick_for(99.0, fz)))
    leg("shallow_quarter_goes_fast", pick_for(-99.0, fz) == PICK_FAST, str(pick_for(-99.0, fz)))

    # 3 a positive direction must invert the pick (the rule is data, not a hard-coded bias)
    pos = learn_sign([{"quarter": "q%d" % i, "gap_pp": float(i), OBSERVABLE: float(i)}
                      for i in range(1, 7)])
    leg("positive_direction_inverts_the_pick",
        pos["direction"] > 0 and pick_for(99.0, pos) == PICK_FAST and pick_for(-99.0, pos) == PICK_SLOW)

    # 4 the freeze refuses a thin window instead of freezing noise
    leg("thin_train_window_refuses", learn_sign(train[:3]) is None)
    leg("flat_observable_refuses",
        learn_sign([{"quarter": "q%d" % i, "gap_pp": float(i), OBSERVABLE: 1.0}
                    for i in range(1, 7)]) is None)

    # 5 money math: picking slow in a quarter where fast won must lose by exactly the gap
    leg("slow_pick_loses_the_gap", quarter_money(PICK_SLOW, 2.5) == -2.5)
    leg("fast_pick_earns_the_gap", quarter_money(PICK_FAST, 2.5) == 2.5)
    leg("missing_gap_earns_nothing", quarter_money(PICK_FAST, None) is None)

    # 6 the ledger compares to always-fast and can say it lost
    win = [{"quarter": "a", "pick": PICK_SLOW, "gap_pp": -3.0},
           {"quarter": "b", "pick": PICK_FAST, "gap_pp": 1.0}]
    led = ledger(win, fz)
    leg("ledger_improvement_is_rule_minus_baseline",
        abs(led["improvement_pp_per_q"] - (led["rule_pp_per_q"] - led["always_fast_pp_per_q"])) < 1e-12,
        "imp=%+.3f" % led["improvement_pp_per_q"])
    leg("ledger_counts_hits_by_money", abs(led["hit_share"] - 1.0) < 1e-12, str(led["hit_share"]))
    lose = [{"quarter": "a", "pick": PICK_SLOW, "gap_pp": 3.0},
            {"quarter": "b", "pick": PICK_SLOW, "gap_pp": 1.0}]
    lled = ledger(lose, fz)
    leg("ledger_says_doubtful_when_the_rule_loses", lled["words"] == WORDS_DOUBTFUL, lled["words"])
    leg("empty_ledger_is_thin", ledger([], fz)["words"] == WORDS_THIN)

    # 7 quarter gaps need paired starts: one start is one path, not the quarter
    cells = [{"start": "s1", "cost": COST_KEY, "segment": "2026Q1", "delta_pp": 1.0},
             {"start": "s2", "cost": COST_KEY, "segment": "2026Q1", "delta_pp": 3.0},
             {"start": "s3", "cost": COST_KEY, "segment": "2026Q1", "delta_pp": 100.0}]
    gaps, holes = quarter_gaps(cells, ["2026Q1", "2026Q2"], ["s1", "s2", "s3"])
    leg("gap_is_the_median_of_starts", abs(gaps["2026Q1"]["gap_pp"] - 3.0) < 1e-12,
        str(gaps.get("2026Q1")))
    leg("quarter_without_pairs_is_a_named_hole",
        "2026Q2" not in gaps and holes and holes[0]["quarter"] == "2026Q2", str(holes[:1]))
    one, _h = quarter_gaps(cells[:1], ["2026Q1"], ["s1", "s2", "s3"])
    leg("one_start_is_not_the_quarter", "2026Q1" not in one)
    two, _h = quarter_gaps(cells[:2], ["2026Q1"], ["s1", "s2", "s3"])
    leg("two_starts_are_the_floor_and_the_midpoint",
        abs(two["2026Q1"]["gap_pp"] - 2.0) < 1e-12 and two["2026Q1"]["n_starts"] == 2,
        str(two.get("2026Q1")))

    print("SELFTEST %d/%d %s" % (len(legs) - len(fails), len(legs),
                                 "PASS" if not fails else "FAIL " + ",".join(fails)))
    return 0 if not fails else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        return compute()
    print("usage: selftest | run | check")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
