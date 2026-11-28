"""The answer book for every bench question that already has a verdict.

Why this exists
---------------
`work_bank_supply_truth.py` answered "is there work left in the bank?" and the
answer was no: 18 of 20 cards are ANSWERED, two are data-blocked, and nobody
has authored card #21. That fixed the *supply* reading. It did not fix the
*consumption* reading, which is the more expensive miss: 18 verdicts sit in
`results/bench_*.json` and every later round has to open them one by one to
find out what was already asked, what it returned, and how much of the case it
closed.

This module turns those loose files into one book a reader (or the next
pre-registration) can consume in one pass:

  * one row per verdict -- question, verdict, the first arm's numbers, which
    gate failed, the evidence file and its byte digest;
  * a disposition -- EXHAUSTED (NO_EDGE: do not re-run the same recipe),
    CANDIDATE (GO/HOLD: still alive), DATA_GAP (blocked: needs a panel), or
    REVALIDATED (a re-check pass, not a strategy);
  * a question fingerprint per card, so a future pre-registration can ask
    "have I already paid for this question?" before burning another batch.

Read-only with respect to every input: it never writes the bank, the queue, or
any bench result.

Usage
-----
  python scripts/bench_verdict_book.py            # write json + page
  python scripts/bench_verdict_book.py --check    # selftest, offline
  python scripts/bench_verdict_book.py --verify   # recompute and diff the json
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import os
import re
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import work_bank_supply_truth as supply  # same-source join, never re-implemented

OUT_JSON = os.path.join(ROOT, "results", "bench_verdict_book.json")
OUT_MD = os.path.join(ROOT, "research", "BENCH-VERDICT-BOOK.md")

EXHAUSTED = "EXHAUSTED"
CANDIDATE = "CANDIDATE"
DATA_GAP = "DATA_GAP"
REVALIDATED = "REVALIDATED"
OTHER = "OTHER"
UNKNOWN = "UNKNOWN"

FAMILY_LABELS = {
    "pair": "横截面配对（多最强空最弱）",
    "trend": "单品种趋势",
    "fut": "期货趋势族",
    "bond": "国债/债券",
    "astock": "A 股选股",
    "revalidate": "复验通行证（不是策略）",
}

# numbers worth quoting, in the order they should be read
HEADLINE_KEYS = ("ann_pct", "net_ann_pct", "excess_pp", "vol_pct", "sharpe", "mdd_pct", "t_stat")

# a face that keeps its numbers under products[P].weighted uses these spellings
PRODUCT_ALIASES = {
    "carry_ann_pct": "ann_pct",
    "net_ann_pct": "ann_pct",
    "weighted_ann_pct": "ann_pct",
    "carry_mdd_pct": "mdd_pct",
    "difference_pp": "excess_pp",
    "ann_sharpe": "sharpe",
}

# r2221: a GO row on this page is a verdict, not a ticket. For each card still alive,
# name what stands between the number and an order -- read from the faces that already
# own that question, never re-typed here. No face = "未测", never a zero.
TO_ORDER_FACES = {
    "basis_timing_size": {
        "capital": "results/idx_fut_carry_open_capital.json",
        "capacity": "results/bench_basis_capacity.json",
        "accounts": ("IC", "IM"),
    },
    "basis_timing_perm": {
        "capital": "results/idx_fut_carry_open_capital.json",
        "capacity": "results/bench_basis_capacity.json",
        "accounts": ("IC", "IM"),
    },
    # r2222: the commodity pair's size was the one line this page could only fill with
    # "未测". scripts/bench_cmdty_capacity.py now prices it from the contracts' own volume
    # and open interest, on the card's own vol-target notional (not the raw book).
    "census_commodity": {"capital": None, "capacity": "results/bench_cmdty_capacity.json", "accounts": ()},
    "robust_tsmom_commodity": {"capital": None, "capacity": "results/bench_cmdty_capacity.json", "accounts": ()},
}

# the two words this book treats as "still alive"
ALIVE_WORDS = ("GO", "SIGNIFICANT")


def _load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def digest_of(path):
    """sha256[:12] of the evidence file, or None when the file is absent.
    Absent must not read as zero -- a missing face is not a zero result."""
    if not path:
        return None
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    try:
        with open(full, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except OSError:
        return None


def headline_of(payload, arm=None):
    """Numbers for one arm. Missing keys are omitted, never printed as 0."""
    if not isinstance(payload, dict):
        return {}
    if arm is not None:
        nums = window_numbers(arm)
        if nums:
            return nums
    arms = payload.get("arms") or []
    if isinstance(arms, dict):
        # older faces key their arms by name; newer ones use a list
        arms = [arms[k] for k in sorted(arms)]
    if arms and isinstance(arms[0], dict):
        nums = window_numbers(arms[0])
        if nums:
            return nums
    out = {k: payload[k] for k in HEADLINE_KEYS if isinstance(payload.get(k), (int, float))}
    if out:
        return out
    # r2221: two live conclusions (the basis-timing pair) keep their numbers one level
    # deeper, under products[P].weighted -- so the page printed "-" in every numeric
    # column of a GO row. Read that shape instead of leaving the card blank.
    prods = payload.get("products")
    if isinstance(prods, dict):
        for name in sorted(prods):
            p = prods[name]
            if not isinstance(p, dict):
                continue
            bag = {}
            for src in (p.get("weighted"), p):
                if not isinstance(src, dict):
                    continue
                for k, v in src.items():
                    key = PRODUCT_ALIASES.get(k)
                    if key and isinstance(v, (int, float)) and not isinstance(v, bool) and key not in bag:
                        bag[key] = v
            if bag:
                return bag
    return out


def window_numbers(obj):
    if not isinstance(obj, dict):
        return {}
    win = obj.get("common_window") or obj.get("net_window") or obj.get("window") or {}
    if not isinstance(win, dict):
        win = {}
    out = {k: win[k] for k in HEADLINE_KEYS if isinstance(win.get(k), (int, float))}
    if out:
        return out
    return {k: obj[k] for k in HEADLINE_KEYS if isinstance(obj.get(k), (int, float))}


def arm_key(arm, i):
    parts = [arm[k] for k in ("pair", "style") if isinstance(arm.get(k), str)]
    if parts:
        return ":".join(parts)
    for k in ("name", "label", "variant", "arm"):
        if isinstance(arm.get(k), str):
            return arm[k]
    tags = arm.get("tags")
    if isinstance(tags, dict) and tags:
        return ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
    return f"arm{i + 1}"


def arms_of(payload):
    arms = payload.get("arms") if isinstance(payload, dict) else None
    if isinstance(arms, dict):
        return [dict(arms[k]) for k in sorted(arms)]
    if isinstance(arms, list):
        return [a for a in arms if isinstance(a, dict)]
    return []


def checks_of(payload):
    """Boolean gate table -> (how many gates, which ones failed).
    Returns None when the face carries no flat boolean table."""
    if not isinstance(payload, dict):
        return None
    ch = payload.get("checks")
    if isinstance(ch, dict) and ch and all(isinstance(v, bool) for v in ch.values()):
        return {"n": len(ch), "failed": [k for k, v in ch.items() if not v]}
    return None


def verdict_rows(verdict):
    """A verdict can be one word, one word per arm, or a small reading table.

    Older faces pack the one-word verdict *and* its numbers into the same
    dict (`{"verdict": "NO_EDGE", "ann_pct": 6.12, ...}`). Expanding that into
    one row per key would print a strategy row per decimal, so: only string
    values that look like a verdict word become their own row; everything else
    stays a reading.
    """
    if verdict is None:
        return [(None, None)]
    if isinstance(verdict, str):
        return [(None, verdict)]
    if isinstance(verdict, dict):
        if "verdict" in verdict and isinstance(verdict["verdict"], str):
            return [(None, verdict["verdict"])]
        words = [(k, v) for k, v in verdict.items() if isinstance(v, str) and WORD_RE.match(v)]
        if words:
            return words
        return [(None, json.dumps(verdict, ensure_ascii=False, sort_keys=True))]
    return [(None, str(verdict))]


def reading_of(verdict):
    """Numbers carried inside a verdict dict, for faces that have no arms."""
    if not isinstance(verdict, dict):
        return {}
    return {k: verdict[k] for k in HEADLINE_KEYS if isinstance(verdict.get(k), (int, float))}


def disposition(verdict_word):
    """EXHAUSTED is the expensive label: it says the same recipe already ran
    and came back with nothing, so re-running it buys a second negative."""
    s = (verdict_word or "").upper()
    if not s:
        return UNKNOWN
    if s.startswith("NO_EDGE") or s.startswith("UNSTABLE_"):
        return EXHAUSTED
    if s.startswith("CENSUS_UNPOWERED") or s.startswith("CENSUS_SIGN_MIXED"):
        return EXHAUSTED
    if s.startswith("CENSUS_LEANS_POSITIVE"):
        return CANDIDATE
    if s.startswith("GO") or s.startswith("SIGNIFICANT"):
        return CANDIDATE
    if s.startswith("ALL_HOLD") or s.startswith("REVALIDATED"):
        return REVALIDATED
    return OTHER


WORD_RE = re.compile(r"^[A-Z][A-Z0-9_:/() .%\-]+$")


def family_of(cid):
    key = (cid or "").split("_")[0].lower()
    return key, FAMILY_LABELS.get(key, key)


def fingerprint(text):
    """Character bigrams over the question with whitespace removed. Two cards
    that ask the same thing in different words still collide on most grams."""
    t = re.sub(r"\s+", "", text or "")
    return {t[i:i + 2] for i in range(len(t) - 1)}


def similarity(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def build(supply_report, loader=_load, digester=digest_of):
    """Join the supply truth with the evidence files, one row per verdict."""
    entries = []
    for row in supply_report.get("rows") or []:
        entries.append({
            "id": row.get("id"),
            "state": row.get("state"),
            "verdict": row.get("verdict"),
            "result": row.get("result"),
            "question": row.get("question"),
            "finished": row.get("finished"),
            "off_bank": False,
        })
    for row in supply_report.get("off_bank") or []:
        entries.append({
            "id": row.get("id"),
            "state": supply.ANSWERED if (row.get("cell_status") or "").lower() == "done" else supply.IN_FLIGHT,
            "verdict": row.get("verdict"),
            "result": row.get("result"),
            "question": None,
            "finished": row.get("finished"),
            "off_bank": True,
        })

    cards = []
    for e in entries:
        payload = None
        if e["result"]:
            try:
                payload = loader(os.path.join(ROOT, e["result"]) if not os.path.isabs(e["result"]) else e["result"])
            except (OSError, ValueError):
                payload = None
        head = headline_of(payload)
        if not head:
            head = reading_of(e["verdict"])
        gates = checks_of(payload)
        fam_key, fam_label = family_of(e["id"])
        fp = fingerprint(e["question"] or "")
        arms = arms_of(payload)
        if arms:
            # a face that carries per-arm numbers must print per-arm rows:
            # six bond pairs sharing one headline is how a book lies.
            per_arm = []
            for i, arm in enumerate(arms):
                word = arm.get("verdict")
                if not isinstance(word, str):
                    fb = verdict_rows(e["verdict"])
                    word = fb[0][1] if fb else None
                per_arm.append((arm_key(arm, i), word, headline_of(payload, arm) or head, checks_of(arm) or gates))
        else:
            per_arm = [(arm, word, head, gates) for arm, word in verdict_rows(e["verdict"])]
        for arm, word, arm_head, arm_gates in per_arm:
            cards.append({
                "id": e["id"],
                "arm": arm,
                "family": fam_key,
                "family_label": fam_label,
                "state": e["state"],
                "verdict": word,
                "disposition": disposition(word) if word else (DATA_GAP if e["state"] == supply.BLOCKED else UNKNOWN),
                "question": e["question"],
                "headline": arm_head,
                "gates": arm_gates,
                "result": e["result"],
                "evidence_digest": digester(e["result"]) if e["result"] else None,
                "result_present": payload is not None,
                "finished": e["finished"],
                "off_bank": e["off_bank"],
                "fingerprint_size": len(fp),
            })

    # duplicate-question guard: the whole point of the book is to stop paying
    # twice for one question, so say it out loud when two cards look alike.
    # Compare per CARD, not per arm row -- the arms of one card share a
    # question by construction, and every such pair would read as a duplicate.
    dups = []
    seen = {}
    for c in cards:
        if (c["question"] or "").strip() and c["id"] not in seen:
            seen[c["id"]] = c
    items = list(seen.values())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            sim = similarity(fingerprint(a["question"]), fingerprint(b["question"]))
            if sim >= 0.80:
                dups.append({"a": a["id"], "b": b["id"], "similarity": round(sim, 3)})

    disp = {}
    for c in cards:
        disp[c["disposition"]] = disp.get(c["disposition"], 0) + 1

    fin = [c["finished"] for c in cards if c.get("finished")]

    # r2221: one row per card still alive, naming the obstacle between the number and
    # a ticket. Built from the faces that own each question so it re-derives with them.
    to_order = {}
    first_by_id = {}
    for c in cards:
        if c["disposition"] != CANDIDATE:
            continue
        first_by_id.setdefault(c["id"], c)
    for cid in sorted(first_by_id):
        c = first_by_id[cid]
        payload = None
        if c.get("result"):
            p = c["result"] if os.path.isabs(c["result"]) else os.path.join(ROOT, c["result"])
            try:
                payload = loader(p)
            except (OSError, ValueError):
                payload = None
        rows = to_order_blockers(cid, c.get("verdict"), payload, loader, face_rel=c.get("result"))
        if rows:
            to_order[cid] = rows

    return {
        "schema": "bench-verdict-book/v1",
        "evidence_cutoff": max(fin)[:10] if fin else None,
        "generated": None,
        "cards": len(cards),
        "sources": len(entries),
        "source_digest": hashlib.sha256(
            json.dumps(supply_report, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()[:12],
        "dispositions": disp,
        "duplicate_questions": dups,
        "missing_evidence": [c["id"] for c in cards if c["result"] and not c["result_present"]],
        "to_order": to_order,
        "rows": cards,
    }


def to_order_blockers(card_id, row_verdict, payload, loader=None, face_rel=None):
    """What stands between a live verdict and a ticket, quoted from the faces that own it.

    Nothing here judges the strategy: each line either quotes the card's own evidence
    face, or names the face that would answer the question and says it is not on disk.
    """
    loader = loader or _load
    spec = TO_ORDER_FACES.get(card_id) or {}
    face_rel = face_rel or spec.get("face")
    out = []

    fv = payload.get("verdict") if isinstance(payload, dict) else None
    if isinstance(fv, str) and fv.upper() not in ALIVE_WORDS:
        gap = face_verdict_gap(payload)
        out.append({
            "what": "脸级判词",
            "text": f"这张卡自己的证据面判 **{fv}**，行上的 {row_verdict or '-'} 是单臂/单相读数——面自己没认这个 GO"
                    + (f"。差在哪：{gap}" if gap else ""),
            "source": face_rel,
        })

    cost = None
    for bag in ((payload or {}).get("criteria"), (payload or {}).get("config"),
                (payload or {}).get("rule")):
        if isinstance(bag, dict) and isinstance(bag.get("cost_bp_side"), (int, float)):
            cost = bag["cost_bp_side"]
            break
    if cost is not None:
        out.append({"what": "成本", "text": f"按 {cost:g} bp/边计；无冲击曲线、无保证金资金成本",
                    "source": face_rel})

    cap_rel = spec.get("capital")
    if cap_rel:
        try:
            cap = loader(os.path.join(ROOT, cap_rel))
        except (OSError, ValueError):
            cap = None
        if cap is None:
            out.append({"what": "资本线", "text": "面不在盘上（不是「不差钱」，是没读到）", "source": cap_rel})
        else:
            for acct in spec.get("accounts") or ():
                a = ((cap.get("accounts") or {}).get(acct) or {})
                fund = a.get("funding") or {}
                if not fund:
                    continue
                state = (a.get("executable_ticket") or {}).get("state")
                out.append({
                    "what": f"资本线 {acct}",
                    "text": (f"首档 1 手要 ￥{fund.get('first_rung_cny'):,.0f}，"
                             f"本金 ￥{a.get('capital_cny'):,.0f}，差 ￥{fund.get('gap_cny'):,.0f}"
                             f"（{fund.get('gap_pct_of_capital'):.2f}%）；可执行票状态 {state}"),
                    "source": f"{cap_rel} @{cap.get('generated')}",
                    "stamp": f"{cap_rel}#{digest_of(os.path.join(ROOT, cap_rel))}",
                })

    q_rel = spec.get("capacity")
    if q_rel:
        try:
            q = loader(os.path.join(ROOT, q_rel))
        except (OSError, ValueError):
            q = None
        if q is None:
            out.append({"what": "容量", "text": "面不在盘上（未测，不是零）", "source": q_rel})
        else:
            mult = q.get("total_capacity_multiple_of_book")
            out.append({
                "what": "容量",
                "text": f"{q.get('verdict')}·总容量 {mult:g}× 本书" if isinstance(mult, (int, float))
                        else f"{q.get('verdict')}",
                "source": f"{q_rel} @{q.get('generated')}",
                "stamp": f"{q_rel}#{digest_of(os.path.join(ROOT, q_rel))}",
            })
    elif card_id and not spec.get("capacity"):
        out.append({"what": "容量", "text": "没有任何面量过这本书的容量（未测，不是零）", "source": None})
    cond = order_condition(out)
    if cond:
        out.append(cond)
    return out


def order_condition(rows):
    """Fold the lines above into the one sentence a reader can act on.

    A GO row plus four obstacle lines still leaves the reader to combine them by hand,
    and two readers combine them differently (r1779: a decision must live in one place).
    So the same rows -- never a new judgement -- are read back as conditions:
    "下得去" requires every one of them, and the sentence names the ones standing in
    the way today. Unknown stays unknown: an unmeasured line is not a passing line.
    """
    if not rows:
        return None
    parts, blocked, unknown = [], [], []

    def add(label, ok, note="", scope=""):
        parts.append((label, ok, note, scope))

    for r in rows:
        what = r.get("what") or ""
        text = r.get("text") or ""
        if what == "脸级判词":
            add("面认这个结论", False, "面自己判的是另一个词")
            blocked.append("面判词")
        elif what == "成本":
            add("成本按声明的 bp 计", True, text.split("；")[0])
        elif what.startswith("资本线"):
            acct = what.split(" ", 1)[1] if " " in what else ""
            if "面不在盘上" in text:
                add("首档 1 手买得起", None, "资本面没读到", acct)
                unknown.append("资本线")
            else:
                ok = "WITHDRAW" not in text.upper()
                add("首档 1 手买得起", ok, text.split("；")[-1] if "；" in text else text, acct)
                if not ok:
                    blocked.append(f"资本线 {acct}".strip())
        elif what == "容量":
            if "面不在盘上" in text or "没有任何面量过" in text:
                add("容量至少 1 倍本书", None, "未测")
                unknown.append("容量")
            else:
                ok = "CAPACITY_OK" in text.upper() or ("BOOK_TOO_BIG" not in text.upper()
                                                       and "CAPACITY_TIGHT" not in text.upper())
                add("容量至少 1 倍本书", ok, text)
                if not ok:
                    blocked.append("容量")
    if not parts:
        return None
    # One condition may be quoted once per account (IC and IM share "1 手买得起"); putting it
    # on the page twice reads as two separate obstacles.
    grouped, order = {}, []
    for label, ok, note, scope in parts:
        key = (label, ok)
        if key not in grouped:
            grouped[key] = {"notes": [], "scopes": []}
            order.append(key)
        if note and note not in grouped[key]["notes"]:
            grouped[key]["notes"].append(note)
        if scope and scope not in grouped[key]["scopes"]:
            grouped[key]["scopes"].append(scope)
    shapes = []
    for key in order:
        label, ok = key
        g = grouped[key]
        head = (("/".join(g["scopes"]) + " ") if g["scopes"] else "") + label
        word = "" if ok is True else ("（未测）" if ok is None else "（未过）")
        shapes.append(head + word)
    tail = (f"今天卡在：{'、'.join(blocked)}" if blocked
            else ("今天错在：没有面回答 " + "、".join(unknown) if unknown
                  else "今天每个条件都过——剩下的只是下单动作本身"))
    if blocked and unknown:
        tail += "；另有未测：" + "、".join(unknown)
    return {"what": "可下单条件", "text": " 且 ".join(shapes) + "。" + tail, "source": None}


_CHECK_ZH = {
    "H1_full_ge": "H1 全程",
    "H2_oos_ge": "H2 样本外",
    "H3_both_halves": "H3 两半段",
    "H4_drop_best": "H4 去最好年",
    "H5_control": "H5 置换",
}
# a census arm is named "tsmom|{'lookback': 250, 'skip': 21}|ls": true and unreadable.
_PARAMS_RE = re.compile(r"\{\s*['\"]([a-z_]+)['\"]\s*:\s*(-?\d+)\s*"
                        r"(?:,\s*['\"]([a-z_]+)['\"]\s*:\s*(-?\d+)\s*)?\}")


def _short_name(raw):
    s = _PARAMS_RE.sub(
        lambda m: f"{m.group(1)}={m.group(2)}" + (f",{m.group(3)}={m.group(4)}" if m.group(3) else ""),
        str(raw))
    s = s.replace("|", " ").replace("'", "").replace('"', "").strip()
    return s if len(s) <= 46 else s[:45] + "…"


def face_verdict_gap(payload):
    """Say the distance between a face verdict and the arms underneath it.

    r2223 shipped "the face says another word", and the next question is always
    "差多少". Nothing new is judged here: the face already publishes every arm's
    annualised return, its own resolution (mde_pp) and each check's boolean, so the
    sentence is read off those fields. A face with fewer than two arms says nothing —
    one arm has nothing to be unstable against.
    """
    if not isinstance(payload, dict):
        return None
    arms = [a for a in (payload.get("arms") or []) if isinstance(a, dict)]
    if len(arms) < 2:
        return None

    def name(a):
        tags = a.get("tags") or {}
        return _short_name(tags.get("variant") or a.get("name") or "-")

    def ann(a):
        v = (a.get("common_window") or {}).get("ann_pct")
        return v if isinstance(v, (int, float)) else None

    def is_go(a):
        return str(a.get("verdict") or "").upper() == "GO"

    go = [a for a in arms if is_go(a)]
    head = f"{len(arms)} 臂里 {len(go)} 臂 GO"
    ctype = str((payload.get("config") or {}).get("type") or "").lower()
    if ctype == "census":
        head += "，面判词描述的是空间、不下单，看臂"
    blocked = [a for a in arms if not is_go(a)]
    if not blocked:
        return head
    measured = [a for a in blocked if ann(a) is not None]
    if not measured:
        return head + "；挡路的臂没有公布年化（未测不是零）"
    near = max(measured, key=ann)
    bits = [f"最近的未过臂 {name(near)} 年化 {ann(near):g}%"]
    m = near.get("mde_pp")
    if isinstance(m, (int, float)) and m > ann(near):
        bits.append(f"低于它自己的分辨率线 {m:g}%（还差 {m - ann(near):.2f}pp）")
    failed = [k for k, v in (near.get("checks") or {}).items() if v is False]
    if failed:
        bits.append("挡它的检查 " + "、".join(_CHECK_ZH.get(k, k) for k in failed))
    p = (near.get("control") or {}).get("p_value")
    if isinstance(p, (int, float)):
        bits.append(f"置换 p={p:g}")
    if not failed:
        # a face that publishes only a verdict leaves the reader guessing why a
        # positive number failed; print the readings it did publish, and say that
        # the check detail is missing rather than inventing one.
        windows = near.get("common_window") or {}
        oos = (near.get("oos_2024_after") or {}).get("ann_pct")
        sharpe = windows.get("sharpe")
        tail = []
        if isinstance(sharpe, (int, float)):
            tail.append(f"夏普 {sharpe:g}")
        if isinstance(oos, (int, float)):
            tail.append(f"样本外年化 {oos:g}%")
        if tail:
            bits.append("它的面没公布检查明细，只给读数：" + "、".join(tail))
    if go:
        more = "等" if len(go) > 2 else ""
        bits.insert(0, "已 GO 的 " + "、".join(name(a) for a in go[:2]) + more)
    return head + "；" + "，".join(bits)


def _num(head, key, suffix=""):
    if key not in head:
        return "-"
    v = head[key]
    if isinstance(v, int) and not isinstance(v, bool):
        return f"{v}{suffix}"
    return f"{v:g}{suffix}"


def render(report):
    d = report["dispositions"]
    lines = []
    lines.append(f"generated {report['generated']}")
    lines.append(f"evidence_cutoff {report['evidence_cutoff']}")
    lines.append("")
    lines.append(f"门票面 {report['sources']} 张 → 判词行 {report['cards']} 行")
    lines.append("")
    lines.append(
        "| 处置 | 行数 | 意思 |"
        "\n|---|---|---|"
        f"\n| EXHAUSTED | {d.get(EXHAUSTED, 0)} | 同一配方跑过并给出了负结论——再跑一遍买的是第二个负结论 |"
        f"\n| CANDIDATE | {d.get(CANDIDATE, 0)} | 还活着，值得往钱的方向推 |"
        f"\n| DATA_GAP | {d.get(DATA_GAP, 0)} | 没算，缺面板 |"
        f"\n| REVALIDATED | {d.get(REVALIDATED, 0)} | 复验通行证，不是策略 |"
        f"\n| OTHER | {d.get(OTHER, 0)} | 判词不在这四类里，按原词读 |"
    )
    lines.append("")

    # r2220: six candidate rows are three questions, each asked twice (a 120d/250d pair,
    # and two implementations of the same commodity TSMOM). A reader deciding what to
    # push should see conclusions, not a row count -- one line per card, arms folded.
    alive = {}
    for c in report["rows"]:
        if c["disposition"] != CANDIDATE:
            continue
        slot = alive.setdefault(c["id"], {"arms": [], "verdicts": [],
                                          "evidence": c["result"], "digest": c["evidence_digest"]})
        if c["arm"]:
            slot["arms"].append(str(c["arm"]))
        if c["verdict"] and c["verdict"] not in slot["verdicts"]:
            slot["verdicts"].append(c["verdict"])
    if alive:
        lines.append(f"## 还活着的结论（{d.get(CANDIDATE, 0)} 行压成 {len(alive)} 个问题）")
        lines.append("")
        lines.append("| 问题卡 | 臂 | 判词 | 证据 |")
        lines.append("|---|---|---|---|")
        for cid, slot in sorted(alive.items()):
            arms = ", ".join(slot["arms"]) if slot["arms"] else "-"
            verdicts = "/".join(slot["verdicts"]) or "-"
            lines.append(f"| {cid} | {arms} | {verdicts} | {slot['evidence']} @{slot['digest']} |")
        lines.append("")
        lines.append("这一节只搬判词与证据，不追加任何新判定；行级数字与关卡在上面的分族表里。")
        lines.append("")

    # r2221: a GO on this page is a verdict, not a ticket. Say what still stands in the way.
    if report.get("to_order"):
        lines.append("## 离下单还差什么（每个活结论一行）")
        lines.append("")
        for cid in sorted(report["to_order"]):
            lines.append(f"**{cid}**")
            for b in report["to_order"][cid]:
                src = f"（{b['source']}）" if b.get("source") else ""
                lines.append(f"- {b['what']}：{b['text']}{src}")
            lines.append("")
        lines.append("读法：这些行不是新的判词，是把「还差什么」从各自的面上取过来——"
                     "写着「未测」的地方是没有人量过，不是量出来是零。")
        lines.append("")

    families = {}
    for c in report["rows"]:
        families.setdefault((c["family"], c["family_label"]), []).append(c)

    for (key, label), rows in sorted(families.items()):
        lines.append(f"## {label}（{key}）· {len(rows)} 行")
        lines.append("")
        lines.append("| 卡 | 臂 | 判词 | 处置 | 净年化 | 超额 | 夏普 | 回撤 | 关卡 | 证据 |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for c in rows:
            h = c["headline"]
            gates = c["gates"]
            gate_txt = "-"
            if gates:
                gate_txt = f"{gates['n'] - len(gates['failed'])}/{gates['n']}"
                if gates["failed"]:
                    gate_txt += " 缺 " + ",".join(gates["failed"])
            ev = f"{c['result']} @{c['evidence_digest']}" if c["result_present"] else (
                f"{c['result']} **MISSING**" if c["result"] else "-")
            lines.append(
                f"| {c['id']} | {c['arm'] or '-'} | {c['verdict'] or '-'} | {c['disposition']} "
                f"| {_num(h, 'ann_pct', '%')} | {_num(h, 'excess_pp', 'pp')} | {_num(h, 'sharpe')} "
                f"| {_num(h, 'mdd_pct', '%')} | {gate_txt} | {ev} |"
            )
        lines.append("")

    lines.append("## 已问过的问题（同一问别付两次钱）")
    lines.append("")
    if report["duplicate_questions"]:
        for p in report["duplicate_questions"]:
            lines.append(f"- **{p['a']} ≈ {p['b']}**（相似度 {p['similarity']}）——两张卡问的是同一件事，答案只买一次")
    else:
        lines.append("- 本册内没有相似度 ≥ 0.80 的重复问句；跨册查重仍需按问题文本自行比对。")
    lines.append("")
    lines.append("## 缺证据的行")
    lines.append("")
    if report["missing_evidence"]:
        for i in report["missing_evidence"]:
            lines.append(f"- {i}：结果面不在盘上（不是零收益，是没读到）")
    else:
        lines.append("- 无：每张有结果路径的卡都能打开并取到字节摘要。")
    lines.append("")
    lines.append("读法：EXHAUSTED 的行是本司已经付过钱的知识，它的价值不是「再试一次」而是"
                 "「写下一张卡时先看这里」。CANDIDATE 的 0 行如果一直不动，说明钱不在银行这一侧——"
                 "在赚钱线（基差 carry/容量/时点）那一侧。")
    return "\n".join(lines) + "\n"


def selftest():
    bank = {"items": [
        {"id": "pair_index_60d", "status": "queued", "question": "四个股指期货之间做横截面强弱对冲，扣费后有没有净收成？"},
        {"id": "pair_all10_60d", "status": "queued", "question": "四个股指期货之间做横截面强弱对冲，扣费后有没有净收成？"},
        {"id": "trend_single_IC_long", "status": "queued", "question": "单做中证500期货的均线趋势，净后与买入持有比有没有超额？"},
        {"id": "blocked_card", "status": "blocked", "question": "需要一个本司没有的面板"},
    ]}
    queue = {"cells": [
        {"id": "pair_index_60d", "status": "done", "verdict": "NO_EDGE", "result": "results/bench_pair_index_60d.json", "finished": "2026-11-24T21:24:50+08:00"},
        {"id": "pair_all10_60d", "status": "done", "verdict": {"a": "NO_EDGE", "b": "GO"}, "result": "results/bench_missing.json", "finished": "2026-11-24T21:25:19+08:00"},
        {"id": "trend_single_IC_long", "status": "done", "verdict": "NO_EDGE", "result": "results/bench_trend.json", "finished": "2026-11-24T21:25:34+08:00"},
    ]}
    payloads = {
        "results/bench_pair_index_60d.json": {
            "arms": [
                {"pair": "IC-IF", "style": "zrev", "verdict": "NO_EDGE",
                 "common_window": {"ann_pct": 2.92, "vol_pct": 14.69, "sharpe": 0.269, "mdd_pct": -37.8},
                 "checks": {"H1": True, "H2": False}},
                {"pair": "IC-IM", "style": "trend", "verdict": "GO",
                 "common_window": {"ann_pct": 9.5, "vol_pct": 11.0, "sharpe": 0.86, "mdd_pct": -12.1},
                 "checks": {"H1": True, "H2": True}},
            ],
            "checks": {"H1": True, "H2": False},
        },
        "results/bench_trend.json": {"ann_pct": 2.99, "sharpe": 0.408},
    }
    supply_report = supply.build(bank, queue)

    def loader(path):
        key = os.path.relpath(path, ROOT).replace(os.sep, "/")
        if key not in payloads:
            raise OSError(key)
        return payloads[key]

    rep = build(supply_report, loader=loader, digester=lambda p: "deadbeefcafe" if p in ("results/bench_pair_index_60d.json", "results/bench_missing.json", "results/bench_trend.json") else None)
    rows = {(c["id"], c["arm"]): c for c in rep["rows"]}
    checks = []

    checks.append(("a face with per-arm numbers prints one row per arm",
                   ("pair_index_60d", "IC-IF:zrev") in rows and ("pair_index_60d", "IC-IM:trend") in rows))
    checks.append(("each arm quotes its own numbers, not the first arm's",
                   rows[("pair_index_60d", "IC-IF:zrev")]["headline"]["ann_pct"] == 2.92
                   and rows[("pair_index_60d", "IC-IM:trend")]["headline"]["ann_pct"] == 9.5))
    checks.append(("a dict verdict expands to one row per arm",
                   ("pair_all10_60d", "a") in rows and ("pair_all10_60d", "b") in rows))
    checks.append(("NO_EDGE reads as EXHAUSTED",
                   rows[("pair_index_60d", "IC-IF:zrev")]["disposition"] == EXHAUSTED))
    checks.append(("GO reads as CANDIDATE",
                   rows[("pair_all10_60d", "b")]["disposition"] == CANDIDATE
                   and rows[("pair_index_60d", "IC-IM:trend")]["disposition"] == CANDIDATE))
    checks.append(("a blocked card with no cell reads as DATA_GAP",
                   any(c["id"] == "blocked_card" and c["disposition"] == DATA_GAP for c in rep["rows"])))
    checks.append(("the first arm's window numbers are quoted",
                   rows[("pair_index_60d", "IC-IF:zrev")]["headline"].get("ann_pct") == 2.92))
    checks.append(("top-level numbers are quoted when there are no arms",
                   rows[("trend_single_IC_long", None)]["headline"].get("sharpe") == 0.408))
    checks.append(("a failing gate is named, not hidden in a count",
                   rows[("pair_index_60d", "IC-IF:zrev")]["gates"]["failed"] == ["H2"]
                   and rows[("pair_index_60d", "IC-IM:trend")]["gates"]["failed"] == []))
    checks.append(("a missing evidence file is flagged, not read as zero",
                   "pair_all10_60d" in rep["missing_evidence"]
                   and rows[("pair_all10_60d", "a")]["result_present"] is False))
    checks.append(("missing evidence still keeps its path in the row",
                   rows[("pair_all10_60d", "a")]["result"] == "results/bench_missing.json"))
    checks.append(("the same question in two cards is caught as a duplicate",
                   any(p["a"] == "pair_index_60d" and p["b"] == "pair_all10_60d"
                       for p in rep["duplicate_questions"])))
    checks.append(("a different question is not flagged",
                   not any("trend_single_IC_long" in (p["a"], p["b"]) for p in rep["duplicate_questions"])))
    checks.append(("missing digests never print a value",
                   rows[("blocked_card", None)]["evidence_digest"] is None if ("blocked_card", None) in rows else True))
    checks.append(("dispositions add up to the row count",
                   sum(rep["dispositions"].values()) == rep["cards"]))
    checks.append(("evidence_cutoff is the newest finished date",
                   rep["evidence_cutoff"] == "2026-11-24"))
    checks.append(("a NO_EDGE row never prints an empty number as 0",
                   _num(rows[("pair_index_60d", "IC-IF:zrev")]["headline"], "excess_pp") == "-"))

    # r2220: the chain pays for a rebuild only when the probe says STALE, so a
    # moved input and a wrong number must not share one word (r1850/r1934).
    rep2 = json.loads(json.dumps(rep, ensure_ascii=False))
    checks.append(("an unchanged book classifies as OK",
                   classify_drift(rep2, rep2) == "OK"))
    moved = json.loads(json.dumps(rep2, ensure_ascii=False))
    moved["rows"][0]["evidence_digest"] = "a1b2c3d4e5f6"
    checks.append(("a moved evidence file speaks STALE, not CHECK FAILED",
                   classify_drift(rep2, moved) == "STALE"))
    wrong = json.loads(json.dumps(rep2, ensure_ascii=False))
    for row in wrong["rows"]:
        if row.get("headline"):
            for k, v in list(row["headline"].items()):
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    row["headline"][k] = v + 1
            break
    checks.append(("a number that does not re-derive stays CHECK FAILED (no STALE word)",
                   classify_drift(rep2, wrong) == "FAILED"))

    # r2221: "alive" is a verdict on this page, not a ticket. The obstacle between the
    # number and an order must be printed, and a face that is not on disk must say so.
    def _missing(_p):
        raise OSError("not on disk")

    b_rob = to_order_blockers("robust_tsmom_commodity", "GO",
                              {"verdict": "UNSTABLE_ACROSS_PARAMS", "criteria": {"cost_bp_side": 3.0}},
                              loader=_missing)
    checks.append(("a GO row whose own face withdrew it says so",
                   any(b["what"] == "脸级判词" and "UNSTABLE_ACROSS_PARAMS" in b["text"] for b in b_rob)))
    checks.append(("a family nobody measured says 未测, not zero",
                   any(b["what"] == "容量" and "未测" in b["text"] for b in b_rob)))
    b_bas = to_order_blockers("basis_timing_size", "GO", {"verdict": "GO"}, loader=_missing)
    checks.append(("a capital face that is not on disk is named, never a zero",
                   any(b["what"] == "资本线" and "面不在盘上" in b["text"] for b in b_bas)))
    cap_fake = {"generated": "2026-11-28T09:13:00+08:00",
                "accounts": {"IC": {"capital_cny": 1000000.0,
                                    "funding": {"first_rung_cny": 1159598.62, "gap_cny": 159598.62,
                                                "gap_pct_of_capital": 15.9599},
                                    "executable_ticket": {"state": "WITHDRAWN"}}}}

    def _cap_loader(p):
        return cap_fake if p.endswith("idx_fut_carry_open_capital.json") else (_ for _ in ()).throw(OSError(p))

    b_cap = to_order_blockers("basis_timing_size", "GO", {"verdict": "GO"}, loader=_cap_loader)
    checks.append(("the capital line is quoted from its own face, with the gap",
                   any(b["what"] == "资本线 IC" and "159,599" in b["text"] and "WITHDRAWN" in b["text"]
                       for b in b_cap)))
    checks.append(("a GO face that agrees with its row is not flagged as a contradiction",
                   not any(b["what"] == "脸级判词" for b in b_cap)))

    base_o = json.loads(json.dumps(rep2, ensure_ascii=False))
    base_o["to_order"] = {"x": [{"what": "容量", "text": "t", "source": "s", "stamp": "f#bbbb"}]}
    moved_o = json.loads(json.dumps(base_o, ensure_ascii=False))
    moved_o["to_order"]["x"][0]["stamp"] = "f#aaaa"
    checks.append(("a face behind the to-order block moving speaks STALE",
                   classify_drift(base_o, moved_o) == "STALE"))

    # r2222: four obstacle lines still leave the reader to combine them by hand, and two
    # readers combine them differently. The same lines fold into one condition sentence;
    # an unmeasured line must read as 未测, never as a passing one.
    cond_bas = [b for b in b_bas if b["what"] == "可下单条件"]
    checks.append(("the obstacles fold into one condition sentence", len(cond_bas) == 1))
    checks.append(("a capital face that is not on disk reads 未测 in that sentence",
                   bool(cond_bas) and "未测" in cond_bas[0]["text"]))
    b_withdrawn = to_order_blockers("basis_timing_size", "GO",
                                    {"verdict": "CENSUS_LEANS_POSITIVE"}, loader=_cap_loader)
    cond_w = [b for b in b_withdrawn if b["what"] == "可下单条件"]
    checks.append(("a withdrawn ticket and a withdrawn face are both named as blockers",
                   bool(cond_w) and "面判词" in cond_w[0]["text"].split("今天卡在")[-1]
                   and "资本线" in cond_w[0]["text"].split("今天卡在")[-1]))
    all_pass = order_condition([
        {"what": "成本", "text": "按 3 bp/边计；无冲击曲线", "source": "f"},
        {"what": "资本线 IC", "text": "首档 1 手要 ￥100，本金 ￥200，差 ￥-100（-50.00%）；可执行票状态 FUNDED",
         "source": "f"},
        {"what": "容量", "text": "CAPACITY_OK_FOR_THIS_BOOK·总容量 4,293.7× 本书", "source": "f"},
    ])
    checks.append(("a card whose every line passes says the conditions are met, not 'blocked'",
                   all_pass is not None and "都过" in all_pass["text"]
                   and "未过" not in all_pass["text"] and "未测" not in all_pass["text"]))
    unknown_only = order_condition([{"what": "容量", "text": "面不在盘上（未测，不是零）", "source": "f"}])
    checks.append(("'no face answered' is its own outcome, not a pass and not a failure",
                   unknown_only is not None and "未测" in unknown_only["text"]
                   and "都过" not in unknown_only["text"]))
    two_accounts = order_condition([
        {"what": "资本线 IC", "text": "首档 1 手要 ￥1，本金 ￥0，差 ￥1（100.00%）；可执行票状态 WITHDRAWN",
         "source": "f"},
        {"what": "资本线 IM", "text": "首档 1 手要 ￥2，本金 ￥0，差 ￥2（100.00%）；可执行票状态 WITHDRAWN",
         "source": "f"},
    ])
    checks.append(("one condition quoted per account prints once, not twice",
                   two_accounts is not None and two_accounts["text"].count("首档 1 手买得起") == 1))

    # r2223: "面自己判的是另一个词" is not actionable — the face already publishes the
    # distance, so the same sentence names the arm in the way and how far it is.
    gap_rob = face_verdict_gap({"config": {"type": "robust"}, "arms": [
        {"tags": {"variant": "60d"}, "common_window": {"ann_pct": 1.52}, "mde_pp": 3.86,
         "checks": {"H1_full_ge": False, "H4_drop_best": True}, "control": {"p_value": 0.45},
         "verdict": "NO_EDGE"},
        {"tags": {"variant": "120d"}, "common_window": {"ann_pct": 4.99}, "mde_pp": 3.78,
         "checks": {}, "verdict": "GO"},
        {"tags": {"variant": "250d"}, "common_window": {"ann_pct": 5.19}, "mde_pp": 3.66,
         "checks": {}, "verdict": "GO"},
    ]})
    checks.append(("the face verdict names the arm in the way and how far it is",
                   bool(gap_rob) and "60d" in gap_rob and "3.86" in gap_rob and "2.34" in gap_rob))
    checks.append(("the arms that already passed are named, so the reader sees what is left",
                   bool(gap_rob) and "120d" in gap_rob and "250d" in gap_rob))
    checks.append(("a failed check is printed in words, not as a bare key",
                   bool(gap_rob) and "H1 全程" in gap_rob and "H4" not in gap_rob))
    gap_census = face_verdict_gap({"config": {"type": "census"}, "arms": [
        {"tags": {"variant": "a"}, "common_window": {"ann_pct": 1.0}, "verdict": "NO_EDGE"},
        {"tags": {"variant": "b"}, "common_window": {"ann_pct": 2.0}, "verdict": "NO_EDGE"},
    ]})
    checks.append(("a census face says it is a description of the space, not a veto",
                   bool(gap_census) and "空间" in gap_census and "0 臂 GO" in gap_census))
    checks.append(("a one-arm face invents no distance",
                   face_verdict_gap({"arms": [{"tags": {"variant": "x"}}]}) is None))
    checks.append(("an arm named by its parameter dict is short-named for the reader",
                   _short_name("tsmom|{'lookback': 250, 'skip': 21}|ls") == "tsmom lookback=250,skip=21 ls"))
    gap_blind = face_verdict_gap({"config": {"type": "census"}, "arms": [
        {"tags": {"variant": "a"}, "common_window": {"ann_pct": 4.54, "sharpe": 0.752},
         "oos_2024_after": {"ann_pct": 3.1}, "verdict": "NO_EDGE"},
        {"tags": {"variant": "b"}, "common_window": {"ann_pct": 1.0}, "verdict": "GO"},
    ]})
    checks.append(("a face that publishes no check detail says so and prints its readings",
                   bool(gap_blind) and "没公布检查明细" in gap_blind and "夏普 0.752" in gap_blind))

    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    print(f"selftest {len(checks) - len(bad)}/{len(checks)}")
    return 0 if not bad else 3


def _strip_volatile(report):
    r = json.loads(json.dumps(report, ensure_ascii=False))
    r.pop("generated", None)
    return r


def _input_stamps(rep):
    """The stamps that belong to the inputs, not to our own arithmetic."""
    rows = rep.get("rows") or []
    return (rep.get("source_digest"),
            # r2221: the to-order block is read from other faces, so a face that moved
            # must read as STALE, not as "we compute differently now".
            tuple(sorted({r.get("stamp") for v in (rep.get("to_order") or {}).values()
                          for r in v if r.get("stamp")})),
            tuple(sorted({(c.get("id"), str(c.get("arm")), c.get("evidence_digest"))
                          for c in rows})))


def classify_drift(prev, fresh):
    """OK / STALE (an input moved) / FAILED (same inputs, different arithmetic)."""
    a, b = _strip_volatile(prev), _strip_volatile(fresh)
    if a == b:
        return "OK"
    if _input_stamps(a) != _input_stamps(b):
        return "STALE"
    return "FAILED"


def verify():
    prev_path = OUT_JSON
    if not os.path.exists(prev_path):
        print(f"STALE: face missing {os.path.relpath(prev_path, ROOT)}")
        return 3
    prev = _load(prev_path)
    fresh = build(supply.build(supply._load(supply.BANK), supply._load(supply.QUEUE)))
    verdict = classify_drift(prev, fresh)
    if verdict == "OK":
        print(f"OK {os.path.relpath(prev_path, ROOT)} re-derives byte-for-byte (modulo generated)")
        return 0
    if verdict == "STALE":
        old, new = _input_stamps(prev), _input_stamps(fresh)
        print("STALE: inputs moved since this book was published "
              f"(source_digest {old[0]} -> {new[0]}); rebuild pays for the new verdicts")
        return 3
    a, b = _strip_volatile(prev), _strip_volatile(fresh)
    diffs = [k for k in set(a) | set(b) if a.get(k) != b.get(k)]
    print("CHECK FAILED: published book disagrees with a fresh derive on " + ", ".join(sorted(diffs)))
    return 3


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

    report = build(supply.build(supply._load(supply.BANK), supply._load(supply.QUEUE)))
    report["generated"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(report))

    if not a.quiet:
        d = report["dispositions"]
        print(f"cards {report['cards']} from {report['sources']} sources · "
              + " · ".join(f"{k}={v}" for k, v in sorted(d.items())))
        print(f"missing evidence {len(report['missing_evidence'])} · duplicates {len(report['duplicate_questions'])}")
        print(f"-> {os.path.relpath(OUT_JSON, ROOT)}")
        print(f"-> {os.path.relpath(OUT_MD, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
