"""Price the one obstacle the answer book keeps naming: a face verdict.

Why this exists
---------------
r2221 taught the answer book to name "脸级判词" as a blocker: a card whose own
evidence face says something other than GO is not orderable, whatever the row
verdict says. r2223 put that line on the CEO page. The next question a reader
asks is the only one that costs money:

    is this obstacle worth another burn?

A face word is two different things wearing one shirt, and the cost of
"clearing" it is not the same for either:

  * a **space** word (``CENSUS_LEANS_POSITIVE``) describes a population, not a
    ticket. Whether it is evidence *against* the card is a question its own
    arms already answer, and ``bench_census_arm_contradiction`` already
    publishes that answer. If the space word is backed by arms that passed,
    then re-running the space buys a third restatement of a measurement that
    already happened -- the obstacle is the missing ticket, not the face.
  * a **range** word (``UNSTABLE_ACROSS_PARAMS``) is a reading on the card's
    own parameter grid. "Unstable" is not a direction; the price of the
    obstacle is the weakest grid cell's distance from its own resolution line
    and from the card's target edge.

Both prices are arithmetic on numbers the faces already publish (``mde_pp``,
``ann_pct``, ``powered_for_target``, ``target_edge_pp``, the checks' booleans).
Nothing is re-estimated, no panel is reloaded, no verdict is re-issued: a cell
that failed keeps its word.

The one derived number is ``years_to_resolve``: resolution improves like
1/sqrt(T), so lifting a cell from its published ``mde`` down to a target needs
``(mde/target)**2`` times the data it already has. When that lands beyond any
horizon a book would wait for, the honest sentence is "measured, and still
empty" -- more of the same data will not move it.

Usage
-----
  python scripts/bench_face_verdict_cost.py            # write the face
  python scripts/bench_face_verdict_cost.py --check    # selftest, offline
  python scripts/bench_face_verdict_cost.py --verify   # re-derive and diff
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OUT_JSON = os.path.join(ROOT, "results", "bench_face_verdict_cost.json")
CONTRADICTION = os.path.join(ROOT, "results", "bench_census_arm_contradiction.json")

# words this book treats as "already a ticket word"
ALIVE_WORDS = ("GO", "SIGNIFICANT")
# words that describe a population rather than a ticket
SPACE_PREFIXES = ("CENSUS_",)

MEASURED_AND_EMPTY = "MEASURED_AND_EMPTY"
SHORT_OF_RESOLUTION = "SHORT_OF_RESOLUTION"
NO_READING = "NO_READING"

FACE_WORD_BACKED = "FACE_WORD_BACKED_SO_NOT_THE_OBSTACLE"
FACE_WORD_CONTRADICTED = "FACE_WORD_CONTRADICTED_BY_ITS_ARMS"
FACE_WORD_AGREES_EMPTY = "FACE_WORD_AGREES_AND_THE_SPACE_IS_EMPTY"
FACE_WORD_EXHAUSTED = "FACE_WORD_IS_A_FINISHED_NEGATIVE_NOT_A_QUEUE_ITEM"
FACE_WORD_MEASURED = "FACE_WORD_IS_THE_OBSTACLE_AND_ALREADY_MEASURED"
FACE_WORD_SHORT = "FACE_WORD_IS_THE_OBSTACLE_BUT_SHORT_OF_RESOLUTION"
FACE_WORD_UNMEASURED = "FACE_WORD_CANNOT_BE_PRICED_HERE"

# a horizon beyond which "wait for more data" is not a plan, it is a wish
MAX_WAIT_YEARS = 20.0
BARS_PER_YEAR = 245.0


def _load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def digest_of(path):
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    try:
        with open(full, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except OSError:
        return None


def _ann(arm):
    v = (arm.get("common_window") or {}).get("ann_pct")
    return v if isinstance(v, (int, float)) else None


def _mde(arm):
    v = arm.get("mde_pp")
    return v if isinstance(v, (int, float)) else None


def _name(arm):
    tags = arm.get("tags") or {}
    variant = tags.get("variant") or arm.get("name") or "-"
    if isinstance(variant, dict):
        variant = "|".join(str(v) for v in variant.values())
    return str(variant)


def _years(payload, arms):
    """Window length in years, read off the face, never assumed.

    ``coverage.start/end`` is the issuer's own statement; when it is absent the
    bar count over the trading-year constant is the fallback, and both are
    labelled in the returned tuple so a reader can see which one was used.
    """
    cov = payload.get("coverage") or {}
    start, end = cov.get("start"), cov.get("end")
    if isinstance(start, str) and isinstance(end, str):
        try:
            d0 = datetime.date.fromisoformat(start[:10])
            d1 = datetime.date.fromisoformat(end[:10])
            return round((d1 - d0).days / 365.25, 2), "coverage.start/end"
        except ValueError:
            pass
    bars = None
    for a in arms:
        n = (a.get("common_window") or {}).get("n")
        if isinstance(n, (int, float)) and n > 0:
            bars = n
            break
    if bars is None and isinstance(cov.get("bars"), (int, float)):
        bars = cov["bars"]
    if isinstance(bars, (int, float)) and bars > 0:
        return round(bars / BARS_PER_YEAR, 2), "common_window.n"
    return None, None


def _target_edge(payload):
    cfg = payload.get("config") or {}
    for bag in (cfg, payload.get("criteria") or {}, payload.get("crit") or {}):
        if isinstance(bag, dict):
            for key in ("target_edge_pp", "H1_full_pct"):
                v = bag.get(key)
                if isinstance(v, (int, float)):
                    return float(v), key
    return None, None


def contradiction_index(path=CONTRADICTION):
    """cell -> {verdict, n_arms, n_clears_h1} from the face that already asked
    "is this space word supported by its own arms?"  Absent file -> {} and the
    caller must say unmeasured, never "backed".
    """
    if not os.path.exists(path):
        return {}
    try:
        d = _load(path)
    except (OSError, ValueError):
        return {}
    out = {}
    for f in d.get("faces") or []:
        if isinstance(f, dict) and f.get("cell"):
            out[f["cell"]] = {
                "verdict": f.get("verdict"),
                "n_arms": f.get("n_arms"),
                "n_clears_h1": f.get("n_clears_h1"),
                "median_ann_pct": f.get("median_ann_pct"),
            }
    return out


def price_cell(payload, cell=None, contra=None):
    """One card's face word, priced. Read-only over the published face."""
    payload = payload or {}
    word = payload.get("verdict")
    word = word if isinstance(word, str) else json.dumps(word, ensure_ascii=False, sort_keys=True)
    arms = [a for a in (payload.get("arms") or []) if isinstance(a, dict)]
    go = [a for a in arms if str(a.get("verdict") or "").upper() == "GO"]
    clears_h1 = 0
    for a in arms:
        h1 = (a.get("checks") or {}).get("H1_full_ge")
        if h1 is True:
            clears_h1 += 1
    target, target_src = _target_edge(payload)
    years, years_src = _years(payload, arms)
    is_space = str(word or "").upper().startswith(SPACE_PREFIXES)

    row = {
        "cell": cell or payload.get("cell"),
        "face": (payload.get("cell") or cell),
        "face_verdict": word,
        "kind": "space" if is_space else "range",
        "arms": len(arms),
        "arms_go": len(go),
        "arms_clear_h1": clears_h1,
        "target_edge_pp": target,
        "target_edge_source": target_src,
        "years_covered": years,
        "years_covered_source": years_src,
        "backed": None,
        "backed_by": None,
        "weakest": None,
        "resolution": NO_READING,
        "years_to_resolve": None,
        "reverify_worth_it": None,
        "verdict_cost": FACE_WORD_UNMEASURED,
        "reading": "",
    }

    # --- is the space word supported by its own arms? --------------------
    if is_space and contra is not None:
        c = contra.get(row["cell"]) if isinstance(contra, dict) else None
        if c is None:
            row["backed_by"] = None
        else:
            cw = str(c.get("verdict") or "").upper()
            # AGREES alone is not enough: a space that agrees while no arm passed
            # is still a face saying "nothing here" (CENSUS_UNPOWERED agrees with
            # its own arms too).  Backed means "passed arms exist".
            row["backed"] = bool(cw == "AGREES" and row["arms_go"] > 0)
            row["backed_by"] = "bench_census_arm_contradiction.json"
            row["contradiction_verdict"] = c.get("verdict")
            row["contradiction_n_clears_h1"] = c.get("n_clears_h1")

    # --- the weakest arm that did not pass ------------------------------
    blocked = [a for a in arms if str(a.get("verdict") or "").upper() != "GO"]
    measured = [a for a in blocked if _ann(a) is not None]
    near = max(measured, key=_ann) if measured else None
    if near is not None:
        failed = sorted(k for k, v in (near.get("checks") or {}).items() if v is False)
        row["weakest"] = {
            "name": _name(near),
            "ann_pct": _ann(near),
            "mde_pp": _mde(near),
            "powered_for_target": near.get("powered_for_target"),
            "failed_checks": failed,
        }
        ann, mde = _ann(near), _mde(near)
        if mde is not None and target is not None:
            if mde <= target:
                row["resolution"] = MEASURED_AND_EMPTY
            else:
                row["resolution"] = SHORT_OF_RESOLUTION
                mult = (mde / target) ** 2
                if years is not None:
                    row["years_to_resolve"] = round(mult * years, 1)
                row["resolution_multiple"] = round(mult, 2)
        elif mde is not None and ann is not None:
            # no declared target: ask what it takes to resolve the arm's own number
            row["resolution"] = SHORT_OF_RESOLUTION if mde > abs(ann) else MEASURED_AND_EMPTY
            if mde > abs(ann) and ann > 0 and years is not None:
                row["years_to_resolve"] = round((mde / ann) ** 2 * years, 1)

    # --- the sentence a reader can act on -------------------------------
    # NO_EDGE is first on purpose: the answer book already dispositions it as
    # EXHAUSTED ("re-running the same recipe buys a second negative"). A pricing
    # face that answered "worth it, in 14.8 years" would contradict a decision
    # that already lives in one place (r1779), so the number is printed as
    # information and the recommendation stays "no".
    if str(word or "").upper().startswith("NO_EDGE"):
        row["reverify_worth_it"] = False
        row["verdict_cost"] = FACE_WORD_EXHAUSTED
        w = row["weakest"] or {}
        info = (f"按 1/sqrt(T) 要 {row['years_to_resolve']:g} 年数据才可能看见它"
                if isinstance(row.get("years_to_resolve"), (int, float))
                else "分辨率已经够，读出来就是没有")
        row["reading"] = (
            f"面判 **{word}**：这条配方已被答案簿判为已烧完（EXHAUSTED），"
            f"再跑同一套参数只会得到第二个负数；{info}——这是信息，不是复验计划"
        )
    elif row["backed"] is True:
        row["reverify_worth_it"] = False
        row["verdict_cost"] = FACE_WORD_BACKED
        row["reading"] = (
            f"面判 **{word}** 说的是空间，不是这张票；它自己的臂里已有 {row['arms_go']}/{row['arms']} 臂 GO、"
            f"{row['arms_clear_h1']} 臂过 H1 线，矛盾面判 **{row.get('contradiction_verdict')}** —— "
            "为这句话再烧一次只会得到第三次复述，缺的是一张票，不是证据"
        )
    elif is_space and contra is not None and row["cell"] in contra and row["backed"] is False:
        row["reverify_worth_it"] = False
        cw = str((contra.get(row["cell"]) or {}).get("verdict") or "").upper()
        if cw == "AGREES" and row["arms_go"] == 0:
            # the face already says "nothing here" and its arms agree: that is a
            # finished negative, not a disagreement, and it is not orderable either
            row["verdict_cost"] = FACE_WORD_AGREES_EMPTY
            row["reading"] = (
                f"面判 **{word}**，它自己的 {row['arms']} 臂里 0 臂 GO —— 面与臂一致，"
                "这个空间是空的；不是判词和证据打架，是没有东西可烧"
            )
        else:
            row["verdict_cost"] = FACE_WORD_CONTRADICTED
            row["reading"] = (
                f"面判 **{word}**，而它自己的臂 {row['arms_go']}/{row['arms']} GO、{row['arms_clear_h1']} 臂过 H1 —— "
                "面的话比臂的读数乐观，这一关是真障碍"
            )
    elif row["resolution"] == MEASURED_AND_EMPTY and near is not None:
        row["reverify_worth_it"] = False
        row["verdict_cost"] = FACE_WORD_MEASURED
        w = row["weakest"]
        row["reading"] = (
            f"面判 **{word}**，最弱的未过臂 {w['name']} 年化 {w['ann_pct']:g}%、"
            f"它自己的分辨率线 {w['mde_pp']:g}pp 已细于目标 {target:g}pp —— "
            "分辨率已经够，读出来就是没有；再烧一遍同样的配方只会得到第二个负数"
        )
    elif row["resolution"] == SHORT_OF_RESOLUTION and near is not None:
        w = row["weakest"]
        yrs = row["years_to_resolve"]
        waitable = isinstance(yrs, (int, float)) and yrs <= MAX_WAIT_YEARS
        row["reverify_worth_it"] = bool(waitable)
        row["verdict_cost"] = FACE_WORD_SHORT
        tail = (f"按 1/sqrt(T) 要把它拉进目标分辨率需约 {yrs:g} 年数据" if yrs is not None
                else "本面读不到它的窗口长度，算不出要等多久")
        row["reading"] = (
            f"面判 **{word}**，最弱的未过臂 {w['name']} 年化 {w['ann_pct']}%、分辨率线 {w['mde_pp']}pp"
            f" 粗于目标 {target}pp —— {tail}" + ("" if waitable else "；超过二十年不是计划，是愿望")
        )
    else:
        row["reading"] = (
            f"面判 **{word}**：盘上没有能给它定价的读数（臂与分辨率线不齐），"
            "所以这里不猜「值得/不值得」"
        )
    row["price_line"] = _price_line(row)
    return row


def _price_line(r):
    """One short sentence, for the pages that already quote the face word."""
    vc, w = r["verdict_cost"], (r.get("weakest") or {})
    if vc == FACE_WORD_BACKED:
        return f"不值得再烧——面的话由自家 {r['arms_go']}/{r['arms']} 臂 GO 支撑，缺的是票不是证据"
    if vc == FACE_WORD_CONTRADICTED:
        return f"面比臂乐观（{r['arms_go']}/{r['arms']} 臂 GO），这一关是真障碍；同配方重烧不解"
    if vc == FACE_WORD_AGREES_EMPTY:
        return "面与臂一致：这个空间是空的，没有东西可烧"
    if vc == FACE_WORD_EXHAUSTED:
        return "这条配方已判已烧完（EXHAUSTED），等数据不是复验"
    if vc == FACE_WORD_MEASURED:
        return (f"不值得再烧——分辨率 {w.get('mde_pp'):g}pp 已细于目标 {r['target_edge_pp']:g}pp，"
                f"读出 {w.get('ann_pct'):g}%：测得够，却没有 edge")
    if vc == FACE_WORD_SHORT:
        yrs = r.get("years_to_resolve")
        head = f"要 {yrs:g} 年数据才拉进目标分辨率" if isinstance(yrs, (int, float)) else "算不出要等多久"
        return head + ("→在计划窗内，值得一次复验" if r["reverify_worth_it"] else "→超过二十年，不是计划")
    return "本面定不了价（臂与分辨率线不齐），不猜"


def _candidates():
    """Every published bench face whose own verdict is not a ticket word."""
    out = []
    res = os.path.join(ROOT, "results")
    if not os.path.isdir(res):
        return out
    for fn in sorted(os.listdir(res)):
        if not (fn.startswith("bench_") and fn.endswith(".json")):
            continue
        if fn.startswith("bench_face_verdict_cost") or fn == "bench_verdict_book.json":
            continue
        if fn == "bench_census_arm_contradiction.json" or fn == "bench_cmdty_capacity.json":
            continue
        if fn == "bench_basis_capacity.json":
            continue
        p = os.path.join(res, fn)
        try:
            d = _load(p)
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict) or not d.get("arms"):
            continue
        v = d.get("verdict")
        word = v if isinstance(v, str) else ""
        if word.upper() in ALIVE_WORDS or not word:
            continue
        out.append((fn, d))
    return out


def build():
    contra = contradiction_index()
    rows = []
    for fn, payload in _candidates():
        rel = "results/" + fn
        r = price_cell(payload, cell=payload.get("cell") or fn[:-5], contra=contra)
        r["face_path"] = rel
        r["face_digest"] = digest_of(rel)
        r["evidence_cutoff"] = payload.get("evidence_cutoff")
        r["face_generated"] = payload.get("generated")
        rows.append(r)

    worth = [r["cell"] for r in rows if r["reverify_worth_it"] is True]
    not_worth = [r["cell"] for r in rows if r["reverify_worth_it"] is False]
    unpriced = [r["cell"] for r in rows if r["reverify_worth_it"] is None]
    cutoffs = sorted({r.get("evidence_cutoff") for r in rows if r.get("evidence_cutoff")})
    return {
        "schema": "bench_face_verdict_cost.v1",
        "cutoff_rule": "the newest evidence_cutoff among the faces read",
        "evidence_cutoff": cutoffs[-1] if cutoffs else None,
        "n_faces": len(rows),
        "faces": rows,
        "worth_another_burn": worth,
        "not_worth_another_burn": not_worth,
        "cannot_be_priced_here": unpriced,
        "sentence": (
            f"{len(rows)} 张面判词里 {len(not_worth)} 张不值得再烧（其中 "
            f"{sum(1 for r in rows if r['verdict_cost'] == FACE_WORD_BACKED)} 张根本不是在说这张票）、"
            f"{len(worth)} 张值得、{len(unpriced)} 张本面定不了价"
        ),
        "not_claimed": [
            "不复算任何臂，不改任何判词；读数全部取自面自己已发布的字段",
            "years_to_resolve 是 1/sqrt(T) 的算术外推，不是承诺：数据质量不变、edge 不变的前提下才成立",
            "「不值得再烧」只针对同一个配方；换参数区间=新问题，须另行预注册",
            "空间词被判「被自家臂支持」不等于这张票可下——资本线、成本、容量各自还要过",
            "二十年计划窗是本司设定的门槛（MAX_WAIT_YEARS），不是统计量；改窗会改变判词",
        ],
    }


def _strip(report):
    r = json.loads(json.dumps(report, ensure_ascii=False))
    r.pop("generated", None)
    return r


def verify():
    if not os.path.exists(OUT_JSON):
        print("STALE: face missing " + os.path.relpath(OUT_JSON, ROOT))
        return 3
    prev = _load(OUT_JSON)
    fresh = build()
    a, b = _strip(prev), _strip(fresh)
    if a == b:
        print("OK " + os.path.relpath(OUT_JSON, ROOT) + " re-derives byte-for-byte (modulo generated)")
        return 0
    moved = [c for c in {x["cell"] for x in a["faces"]} | {x["cell"] for x in b["faces"]}
             if next((x for x in a["faces"] if x["cell"] == c), None)
             != next((x for x in b["faces"] if x["cell"] == c), None)]
    digests_moved = [c for c in moved
                     if (next((x for x in a["faces"] if x["cell"] == c), {}) or {}).get("face_digest")
                     != (next((x for x in b["faces"] if x["cell"] == c), {}) or {}).get("face_digest")]
    if digests_moved:
        print("STALE: input faces moved since this pricing was published (" + ", ".join(digests_moved) + ")")
        return 3
    print("CHECK FAILED: same inputs, different arithmetic on " + (", ".join(moved) or "(summary)"))
    return 3


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------

def _arm(name, ann, mde, verdict="NO_EDGE", checks=None, powered=None):
    return {
        "tags": {"variant": name},
        "common_window": {"ann_pct": ann, "n": 4599},
        "mde_pp": mde,
        "powered_for_target": powered,
        "checks": checks or {},
        "verdict": verdict,
    }


def selftest():
    checks = []

    def add(name, ok):
        checks.append((name, bool(ok)))

    # 1. a powered cell that reads empty: resolution is already finer than target
    p = {"cell": "robust_x", "verdict": "UNSTABLE_ACROSS_PARAMS",
         "config": {"type": "robust", "target_edge_pp": 5.0},
         "coverage": {"start": "2008-01-09", "end": "2026-11-26", "bars": 4599},
         "arms": [_arm("60d", 1.52, 3.86), _arm("120d", 4.99, 3.78, "GO"), _arm("250d", 5.19, 3.66, "GO")]}
    r = price_cell(p, cell="robust_x")
    add("a cell whose resolution line is already finer than target is MEASURED_AND_EMPTY",
        r["resolution"] == MEASURED_AND_EMPTY)
    add("and it is not worth another burn of the same recipe", r["reverify_worth_it"] is False)
    add("the sentence names the weakest arm and both numbers",
        "60d" in r["reading"] and "1.52" in r["reading"] and "3.86" in r["reading"])
    add("no years_to_resolve is invented when the cell is already resolvable",
        r["years_to_resolve"] is None)

    # 2. a cell short of resolution: years scale as (mde/target)^2
    p2 = {"cell": "range_y", "verdict": "UNSTABLE_ACROSS_PARAMS",
          "config": {"type": "robust", "target_edge_pp": 5.0},
          "coverage": {"start": "2016-01-01", "end": "2026-01-01"},
          "arms": [_arm("a", 4.0, 12.0), _arm("b", 6.0, 4.0, "GO")]}
    r2 = price_cell(p2, cell="range_y")
    add("mde 12 vs target 5 needs (12/5)^2 = 5.76x the data",
        r2["resolution"] == SHORT_OF_RESOLUTION and abs(r2["resolution_multiple"] - 5.76) < 1e-9)
    add("years_to_resolve = multiple x years covered (~57.6 over 10 years)",
        isinstance(r2["years_to_resolve"], (int, float)) and abs(r2["years_to_resolve"] - 57.6) < 0.6)
    add("a wait beyond twenty years is priced as not worth it",
        r2["reverify_worth_it"] is False)

    # 3. space word backed by its own arms -> the obstacle is not the face
    p3 = {"cell": "census_x", "verdict": "CENSUS_LEANS_POSITIVE",
          "config": {"type": "census", "target_edge_pp": 5.0},
          "coverage": {"start": "2008-01-01", "end": "2026-01-01"},
          "arms": [_arm("a", 4.9, 3.8, "GO"), _arm("b", 1.5, 3.9)]}
    contra = {"census_x": {"verdict": "AGREES", "n_arms": 2, "n_clears_h1": 1}}
    r3 = price_cell(p3, cell="census_x", contra=contra)
    add("a space word agreeing with passing arms is backed, not an obstacle",
        r3["verdict_cost"] == FACE_WORD_BACKED and r3["reverify_worth_it"] is False)
    add("its sentence says re-burning would be a third restatement",
        "第三次复述" in r3["reading"])

    # 4. the same space word with zero passing arms is NOT backed
    p4 = dict(p3, arms=[_arm("a", 2.1, 4.1), _arm("b", 3.2, 4.0)])
    contra0 = {"census_x": {"verdict": "AGREES", "n_arms": 2, "n_clears_h1": 2}}
    r4 = price_cell(p4, cell="census_x", contra=contra0)
    add("agreement without a single passing arm must not read as backed", r4["backed"] is False)
    add("a face that agrees while its arms are empty is a finished negative, not a disagreement",
        r4["verdict_cost"] == FACE_WORD_AGREES_EMPTY and r4["reverify_worth_it"] is False)

    # 4b. a face that is optimistic against its own arms is flagged as contradicted
    p4b = {"cell": "census_y", "verdict": "CENSUS_LEANS_POSITIVE",
           "config": {"type": "census", "target_edge_pp": 5.0},
           "coverage": {"start": "2008-01-01", "end": "2026-01-01"},
           "arms": [_arm("a", 3.2, 4.0), _arm("b", 1.9, 4.1)]}
    r4b = price_cell(p4b, cell="census_y",
                     contra={"census_y": {"verdict": "LEANS_WITHOUT_A_PASS", "n_arms": 2, "n_clears_h1": 1}})
    add("a leaning headline with zero GO arms is the real obstacle",
        r4b["verdict_cost"] == FACE_WORD_CONTRADICTED and r4b["reverify_worth_it"] is False)

    # 4c. NO_EDGE is a finished negative; a pricing face must not queue it
    p4c = {"cell": "done_1arm", "verdict": "NO_EDGE", "config": {"target_edge_pp": 5.0},
           "coverage": {"start": "2010-01-01", "end": "2020-01-01"},
           "arms": [_arm("only", 3.0, 8.0)]}
    r4c = price_cell(p4c, cell="done_1arm")
    add("NO_EDGE is priced as already-exhausted even when more data would help",
        r4c["verdict_cost"] == FACE_WORD_EXHAUSTED and r4c["reverify_worth_it"] is False)
    add("its years figure survives as information, never as a plan",
        isinstance(r4c["years_to_resolve"], (int, float)) and "不是复验计划" in r4c["reading"])

    # 4d. an unstable grid cell within the wait horizon is the one 'worth it' case
    p4d = {"cell": "near_miss", "verdict": "UNSTABLE_ACROSS_PARAMS",
           "config": {"type": "robust", "target_edge_pp": 5.0},
           "coverage": {"start": "2016-01-01", "end": "2026-01-01"},
           "arms": [_arm("a", 4.0, 6.0), _arm("b", 6.0, 4.0, "GO")]}
    r4d = price_cell(p4d, cell="near_miss")
    add("a grid cell that needs ~14 years is still inside the twenty-year plan window",
        14.0 <= r4d["years_to_resolve"] <= 15.0 and r4d["reverify_worth_it"] is True)

    # 5. no contradiction face -> unknown, never "backed"
    r5 = price_cell(p3, cell="census_x", contra=None)
    add("a missing contradiction face leaves the question open (not backed)",
        r5["backed"] is None and r5["verdict_cost"] != FACE_WORD_BACKED)

    # 6. a negative arm with no target: more data will not turn it positive
    p6 = {"cell": "neg", "verdict": "UNSTABLE_ACROSS_PARAMS", "config": {"type": "robust"},
          "coverage": {"start": "2010-01-01", "end": "2020-01-01"},
          "arms": [_arm("a", -2.0, 6.0), _arm("b", 5.0, 3.0, "GO")]}
    r6 = price_cell(p6, cell="neg")
    add("a negative cell gets no years_to_resolve (more samples do not flip a sign)",
        r6["years_to_resolve"] is None)

    # 7. no arms -> cannot be priced, and the face says so instead of guessing
    p7 = {"cell": "empty", "verdict": "UNSTABLE_ACROSS_PARAMS", "config": {}, "arms": []}
    r7 = price_cell(p7, cell="empty")
    add("a face with no arms is priced as unknown, not worth-it",
        r7["verdict_cost"] == FACE_WORD_UNMEASURED and r7["reverify_worth_it"] is None)

    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
    print(f"{passed}/{len(checks)} PASS")
    return 0 if passed == len(checks) else 1


def render(report):
    lines = ["# 面判词值不值得再烧（纯读出）", ""]
    lines.append(f"- {report['sentence']}")
    lines.append(f"- 取证截止 {report.get('evidence_cutoff')}；本面只读已发布字段，不复算任何臂")
    lines.append("")
    lines.append("| 卡 | 面判词 | 臂 GO | 最弱未过臂 | 分辨率 | 要多少年 | 值得再烧 |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in report["faces"]:
        w = r.get("weakest") or {}
        weak = f"{w.get('name')} {w.get('ann_pct')}% / 线 {w.get('mde_pp')}pp" if w else "-"
        yrs = f"{r['years_to_resolve']:g}" if isinstance(r.get("years_to_resolve"), (int, float)) else "-"
        worth = {True: "值得", False: "不值得", None: "定不了价"}[r["reverify_worth_it"]]
        lines.append(f"| {r['cell']} | {r['face_verdict']} | {r['arms_go']}/{r['arms']} | {weak} | "
                     f"{r['resolution']} | {yrs} | {worth} |")
    lines.append("")
    for r in report["faces"]:
        lines.append(f"- **{r['cell']}**：{r['reading']}")
    lines.append("")
    lines.append("**本面不主张**：")
    for n in report["not_claimed"]:
        lines.append(f"- {n}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        return selftest()
    if a.verify:
        return verify()

    report = build()
    report["generated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    md = OUT_JSON.replace(".json", ".md").replace("results" + os.sep, "research" + os.sep + "BENCH-FACE-VERDICT-COST")
    md = os.path.join(ROOT, "research", "BENCH-FACE-VERDICT-COST.md")
    with io.open(md, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(report))
    if not a.quiet:
        print(report["sentence"])
        print("worth=" + ",".join(report["worth_another_burn"]) or "worth=-")
        print("-> " + os.path.relpath(OUT_JSON, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
