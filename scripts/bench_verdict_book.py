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
        "rows": cards,
    }


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

    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    print(f"selftest {len(checks) - len(bad)}/{len(checks)}")
    return 0 if not bad else 3


def _strip_volatile(report):
    r = json.loads(json.dumps(report, ensure_ascii=False))
    r.pop("generated", None)
    return r


def verify():
    prev_path = OUT_JSON
    if not os.path.exists(prev_path):
        print(f"STALE: face missing {os.path.relpath(prev_path, ROOT)}")
        return 3
    prev = _load(prev_path)
    fresh = build(supply.build(supply._load(supply.BANK), supply._load(supply.QUEUE)))
    a, b = _strip_volatile(prev), _strip_volatile(fresh)
    if a == b:
        print(f"OK {os.path.relpath(prev_path, ROOT)} re-derives byte-for-byte (modulo generated)")
        return 0
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
