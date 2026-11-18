#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SUPPLY CANDIDATE FACE -- is the empty pool a broken mechanism, or no work?

The compute_audit supply_floor flag has been red for 21 hours (ready 0,
floor 3, streak 1256 min). A floor flag measures ONE thing: the number of
`status=ready` entries in the pool. It cannot tell apart the two states that
produce that number, and they need opposite responses:

  * work exists and nobody put it in the pool  -> enqueue it (mechanism fault)
  * no startable work exists at all            -> generate a topic (agenda debt)

Reporting both as "supply_floor" made a red that nobody could act on and that
therefore stayed red; the honest fix is not to relax the floor (E-series law:
a loosened assertion is the cheapest way to lose the signal) but to publish
the second half of the reading.

This face counts candidates from the sources that own them, names each one,
and says which are startable *today*:

  pool        status=ready entries (lane-merged view, via compute_audit so
              there is exactly one pool reader -- never a second parser)
  tickets     fleet/tasks/*.json status=open and unclaimed (README sec.4:
              claimed_by is a lock, not a candidate)
  backlog     fleet/backlog.md lines with neither claimed@ nor done@ --
              counted, but NOT startable for this company: the row says
              which company owns it and the file is cross-company
  queue       state/queue/{tech,explore}.md rows not marked done -- drafts,
              each still needs a prereg freeze, so they are not startable

  startable_now = pool_ready_unclaimed + tickets_open_unclaimed

Verdict:
  SUPPLY_OK      ready >= floor
  SUPPLY_BROKEN  startable_now >= floor - ready   (work to enqueue, name it)
  AGENDA_DEBT    startable_now <  floor - ready   (nothing to enqueue: the
                                                  red names topic generation)
  UNKNOWN        the pool could not be read (r98: unknown is not empty)

  python scripts/supply_candidate_face.py run
  python scripts/supply_candidate_face.py --selftest
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "supply_candidates.json")
QUEUES = ("state/queue/tech.md", "state/queue/explore.md")


def _audit():
    """compute_audit is the single owner of the pool and ticket readers."""
    sdir = os.path.join(ROOT, "scripts")
    if sdir not in sys.path:
        sys.path.insert(0, sdir)
    import compute_audit
    return compute_audit


def _calendar():
    """supply_calendar_face is the single owner of the calendar reading."""
    sdir = os.path.join(ROOT, "scripts")
    if sdir not in sys.path:
        sys.path.insert(0, sdir)
    import supply_calendar_face
    return supply_calendar_face


def agenda_cause(verdict, startable, shortfall, calendar_verdict):
    """Why the red exists when the pool is short. Pure -- pinned by selftest.

    r1199 split the pool red into 'mechanism' vs 'agenda debt'. This splits
    agenda debt one layer further (r1421): 'nobody wrote a topic' and 'every
    topic we have fails its own calendar' read the same word and need
    opposite responses.

      mechanism  startable work exists and was not enqueued
      calendar   no startable work, and every judged candidate was refused
                 by its own calendar gauge
      no_topics  no startable work, no calendar refusals to blame
      unknown    the reading could not be made (never reads as no_topics)
    """
    if verdict == "SUPPLY_OK":
        return None
    if startable is None or shortfall is None:
        return "unknown"
    if startable >= shortfall:
        return "mechanism"
    if calendar_verdict == "NO_CANDIDATE_PASSES_CALENDAR":
        return "calendar"
    if calendar_verdict == "ADMITTED_CANDIDATE_EXISTS":
        return "no_topics"
    if calendar_verdict == "NO_CANDIDATES":
        return "no_topics"
    return "unknown"


CAPACITY_RECEIPT = "results/etf_book_capacity_floor_gap.json"


def _capacity_floor_owner():
    """The gate that owns the floor number (never copy a second 20,000,000)."""
    sdir = os.path.join(ROOT, "scripts")
    if sdir not in sys.path:
        sys.path.insert(0, sdir)
    import candidate_year_gate
    return candidate_year_gate.CAPACITY_FLOOR_CNY


def capacity_layer(path=None):
    """The level the calendar cannot answer.

    supply_calendar_face answers "did any judged candidate pass its own
    calendar". It cannot answer "would passing change the floor question":
    every priced width tops out below the floor, so "wait for the calendar"
    is not the whole order and an operator who reads only the calendar keeps
    waiting for a door that does not exist. Numbers are copied from the
    capacity receipt (single owner scripts/etf_book_capacity_floor_gap.py);
    that receipt's floor is cross-checked against the gate that owns it, and
    a disagreement is flagged instead of silently preferring one. An
    unreadable receipt is unreadable -- never a zero gap (r98).
    """
    path = path or os.path.join(ROOT, CAPACITY_RECEIPT)
    if not os.path.exists(path):
        return {"readable": False,
                "why": "no capacity receipt at %s" % CAPACITY_RECEIPT}
    try:
        with io.open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as exc:                       # noqa: BLE001 - reported
        return {"readable": False,
                "why": "capacity receipt unreadable: %s" % exc}
    floor = d.get("floor_cny")
    ceiling = d.get("best_capacity_5pct_cny")
    if floor is None or ceiling is None:
        return {"readable": False,
                "why": "capacity receipt lacks floor_cny / "
                       "best_capacity_5pct_cny"}
    try:
        owner_floor = float(_capacity_floor_owner())
    except Exception:                              # noqa: BLE001 - reported
        owner_floor = None
    return {
        "readable": True,
        "floor_cny": floor,
        "ceiling_cny": ceiling,
        "gap_cny": d.get("gap_to_floor_cny"),
        "share_of_floor": d.get("best_share_of_floor"),
        "verdict": d.get("verdict"),
        "best_reading": d.get("best_reading"),
        "receipt": CAPACITY_RECEIPT,
        "floor_owner": d.get("floor_owner"),
        "floor_matches_owner": (None if owner_floor is None
                                else abs(float(floor) - owner_floor) < 1e-6),
        "generated": d.get("generated"),
    }


def _cny(v):
    return "{:,.0f}".format(v) if v is not None else "读不到"


def _share(v):
    return ("%.1f%%" % (100.0 * v)) if v is not None else "读不到"


def capacity_sentence(cap):
    """One sentence built from the receipt's own numbers (pinned by selftest).

    It exists because the calendar sentence and this one answer different
    questions: "no candidate passes its calendar" invites waiting, while
    "the top priced ceiling is 69% of the floor" says waiting cannot finish
    the job.
    """
    if not cap or not cap.get("readable"):
        return ("已定价的天花板读不到（%s）——读不到不等于没有缺口（r98）"
                % ((cap or {}).get("why") or "unknown"))
    s = ("即使有一个候选过闸，已定价的最高上限 %s 也只有地板的 %s（差 %s）"
         % (_cny(cap.get("ceiling_cny")), _share(cap.get("share_of_floor")),
            _cny(cap.get("gap_cny"))))
    if cap.get("best_reading"):
        s += "，该上限出自 %s" % cap["best_reading"]
    if cap.get("floor_matches_owner") is False:
        s += "（注意：收据上的地板与 %s 不一致）" % (cap.get("floor_owner") or "属主门")
    return s


def count_backlog(path):
    """(unclaimed, claimed) rows of a claim-by-file backlog.

    A row is a numbered list item; `claimed@` or `done@` anywhere on the line
    makes it non-claimable. Unreadable file -> (None, None), never (0, 0).
    """
    if not os.path.exists(path):
        return None, None
    unclaimed, claimed = 0, 0
    with io.open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s or not s[0].isdigit() or "." not in s[:4]:
                continue
            if "claimed@" in s or "done@" in s:
                claimed += 1
            else:
                unclaimed += 1
    return unclaimed, claimed


CONSUMED_PREFIXES = ("done", "closed")
LIVE_PREFIXES = ("open", "pending", "draft", "queued")


def row_status(cell):
    """`consumed` / `live` / `unreadable` -- never guesses a fourth state.

    Real rows carry a suffix (`done（r873 bm-b）`) or a result where a status
    belongs (`0.455 > null family p95`). Exact-match `== "done"` reads the
    first kind as a live draft, which is how this face reported 19 drafts
    when the queue held zero; a measurement in the status column is not a
    status, so it is reported by name instead of being counted either way.
    """
    s = (cell or "").strip().lower()
    if not s:
        return "unreadable"
    if s.startswith(CONSUMED_PREFIXES):
        return "consumed"
    if s.startswith(LIVE_PREFIXES):
        return "live"
    return "unreadable"


def scan_queue(path):
    """Per-row classification of a queue table.

    Rows are `| <id> | <text> | <pointer> | <status> |`. Returns None when the
    file is missing (unknown is not empty, r98).
    """
    if not os.path.exists(path):
        return None
    out = {"total": 0, "consumed": 0, "live": [], "unreadable": []}
    with io.open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s.startswith("| "):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 4:
                continue
            rid = cells[0]
            if not (rid[:1] in ("T", "E") and rid[1:].isdigit()):
                continue
            out["total"] += 1
            kind = row_status(cells[-1])
            if kind == "consumed":
                out["consumed"] += 1
            elif kind == "live":
                out["live"].append((rid, cells[1][:80]))
            else:
                out["unreadable"].append((rid, cells[-1][:80]))
    return out


def open_queue_rows(path):
    """[(rid, first 80 chars)] for rows that are still live drafts."""
    sc = scan_queue(path)
    return None if sc is None else sc["live"]


def classify(ready, tickets, floor):
    """(verdict, startable_now). Pure -- the selftest pins this mapping."""
    if ready is None or tickets is None:
        return "UNKNOWN", None
    startable = ready + tickets
    if ready >= floor:
        return "SUPPLY_OK", startable
    if startable >= floor - ready:
        return "SUPPLY_BROKEN", startable
    return "AGENDA_DEBT", startable


def build(pool_ready=None, pool_ids=None, tickets=None, backlog_path=None,
          queue_paths=None, floor=None, calendar=None, capacity=None):
    """Assemble the face. Every input may be injected (selftest hermeticity)."""
    ca = _audit()
    floor = ca.SUPPLY_FLOOR_READY if floor is None else floor
    if pool_ready is None:
        entries = ca.pool_ready_entries()
        pool_ready = None if entries is None else len(entries)
        pool_ids = [e[0] for e in entries] if entries else []
    pool_ids = pool_ids or []
    if tickets is None:
        tickets = ca.fleet_open_tasks()
    backlog_path = backlog_path or os.path.join(ROOT, "fleet", "backlog.md")
    queue_paths = queue_paths or [os.path.join(ROOT, q) for q in QUEUES]
    b_unclaimed, b_claimed = count_backlog(backlog_path)
    queue = {}
    live = {}
    unreadable = {}
    consumed = {}
    for p in queue_paths:
        name = os.path.basename(p)
        sc = scan_queue(p)
        queue[name] = None if sc is None else len(sc["live"]) + len(sc["unreadable"])
        live[name] = None if sc is None else len(sc["live"])
        consumed[name] = None if sc is None else sc["consumed"]
        unreadable[name] = [] if sc is None else sc["unreadable"]
        if sc and sc["live"]:
            queue.setdefault("_rows", {})[name] = sc["live"]
    verdict, startable = classify(pool_ready, tickets, floor)
    if calendar is None:
        cal_face = _calendar().build()
    else:
        cal_face = calendar
    shortfall = (None if pool_ready is None else max(0, floor - pool_ready))
    cause = agenda_cause(verdict, startable, shortfall, cal_face.get("verdict"))
    cap = capacity_layer() if capacity is None else capacity
    return {
        "tool": "supply_candidate_face",
        "floor": floor,
        "pool_ready": pool_ready,
        "pool_ready_ids": pool_ids,
        "tickets_unclaimed": tickets,
        # startable = what can be ignited today without a new freeze
        "startable_now": startable,
        "shortfall": shortfall,
        # one layer under AGENDA_DEBT: did anything we already judged get
        # refused by its own calendar? (single owner: supply_calendar_face)
        "agenda_cause": cause,
        "calendar": {
            "verdict": cal_face.get("verdict"),
            "n_candidates": cal_face.get("n_candidates"),
            "n_refused": cal_face.get("n_refused"),
            "receipts_declared": cal_face.get("receipts_declared"),
            "receipts_unreadable": cal_face.get("receipts_unreadable"),
            "candidates": [
                {"candidate": c.get("candidate"), "state": c.get("state"),
                 "failing_checks": c.get("failing_checks"),
                 # r1836: the columns the receipt never measured (None). A
                 # reader one layer up used to see only the False ones and read
                 # "the rest passed" out of "the rest was never looked at".
                 "unchecked_checks": c.get("unchecked_checks"),
                 "receipt": c.get("receipt"),
                 # r1657: carry the numbers that make the third word a fact
                 # rather than a label. Without them a reader one layer up
                 # (audit floor, daily page) could only repeat
                 # "UNADJUDICABLE_PHASE" and had no way to tell "the noise is
                 # wider than the margin" from "the phases disagree".
                 "phases": c.get("phases"),
                 "spread_pp": c.get("spread_pp"),
                 "margin_pp": c.get("margin_pp"),
                 "undecidable_because": c.get("undecidable_because")}
                for c in (cal_face.get("candidates") or [])],
        },
        # counted, deliberately NOT startable: cross-company, or needs prereg
        "backlog_unclaimed_cross_company": b_unclaimed,
        "backlog_claimed": b_claimed,
        # Rows whose status cell is not `done`/`closed`: live drafts plus rows
        # whose status column holds something unreadable (named, not counted
        # as drafts -- a measurement in the status column is not a status).
        "queue_rows_not_marked_done": {k: v for k, v in queue.items()
                                       if k != "_rows"},
        "queue_live_drafts": live,
        "queue_consumed": consumed,
        "queue_status_unreadable": unreadable,
        "queue_open_names": queue.get("_rows", {}),
        "verdict": verdict,
        "agenda_cause": cause,
        # one layer under 'calendar': would passing its calendar reach the
        # floor at all? Single owner = scripts/etf_book_capacity_floor_gap.py.
        "capacity": cap,
        "capacity_sentence": capacity_sentence(cap),
        "reading": _reading(verdict, cause, cal_face, cap),
    }


READINGS = {
    "SUPPLY_OK": "pool holds floor-many ready batches",
    "SUPPLY_BROKEN": "startable work exists and is not in the pool: "
                     "enqueue it, this is a mechanism fault",
    "AGENDA_DEBT": "nothing to enqueue: the red names topic "
                   "generation, not the pool",
    "UNKNOWN": "pool unreadable -- unknown is not empty (r98)",
}


def _reading(verdict, cause, cal_face, cap=None):
    """The sentence an operator acts on. For AGENDA_DEBT the calendar layer
    replaces the generic wording, because 'write a topic' and 'wait for the
    book to pass its calendar' are different orders -- and 'waiting cannot
    finish the job' is a third, which the capacity sentence carries."""
    if verdict == "AGENDA_DEBT" and cause == "calendar":
        try:
            cal = _calendar()
            s = cal.summary_line(cal_face)
        except Exception:                          # noqa: BLE001 - reported
            names = [c.get("candidate") for c in cal_face.get("candidates") or []]
            s = ("no candidate passes its calendar (%d refused: %s)"
                 % (len(names), ", ".join(names)))
        # r1308: the calendar alone reads as "keep waiting"; the level says
        # whether waiting can ever be enough.
        return s + "。另一层：" + capacity_sentence(cap)
    if verdict == "AGENDA_DEBT" and cause == "unknown":
        return ("nothing to enqueue, and the calendar reading could not be "
                "made -- unknown is not 'no topics' (r98)")
    return READINGS[verdict]


def write_md(face, path):
    lines = [
        "# 供给面：池子空着，是因为没有活，还是因为没人把活放进池子",
        "",
        "判词 **%s** —— %s" % (face["verdict"], face["reading"]),
        "",
        "| 来源 | 数 | 能不能立刻点火 |",
        "|---|---|---|",
        "| 池内 ready | %s | 是（已入池） |" % face["pool_ready"],
        "| 任务板 open 未认领 | %s | 是（认领即开动） |" % face["tickets_unclaimed"],
        "| 队列活草稿（状态列是 open/pending/draft） | %s | 否，每行还要先过预注册冻结 |"
        % json.dumps(face.get("queue_live_drafts"), ensure_ascii=False),
        "| 队列已消耗行（状态列 done/closed，含 rNNN 后缀） | %s | 无需动作 |"
        % json.dumps(face.get("queue_consumed"), ensure_ascii=False),
        "| 队列状态不可读行（状态列里是测量值，按名列出） | %s | 不是草稿，是队列卫生项 |"
        % json.dumps(face.get("queue_status_unreadable"), ensure_ascii=False),
        "| backlog 未认领行 | %s | 否，跨公司 backlog，行内有属主 |"
        % face["backlog_unclaimed_cross_company"],
        "",
        "地板 %d，当前差 **%s** 个批次。" % (face["floor"], face["shortfall"]),
        "",
        "读法：池子空是一种状态，两种原因。有活没入池=机制故障（该入池）；"
        "根本没活=选题债（该开题）。把两种都印成 supply_floor，红就一直红着、"
        "而且没人能对着它做事。",
        "",
    ]
    cal = face.get("calendar") or {}
    if face.get("agenda_cause"):
        lines += ["## 归因：%s" % face["agenda_cause"], ""]
        if face["agenda_cause"] == "calendar":
            lines += ["已判过的候选，一个都没过自己的日历闸：", "",
                      "| 候选 | 判决 | 未过的检查 | 没测的列 | 收据 |",
                      "|---|---|---|---|---|"]
            for c in cal.get("candidates") or []:
                # r1836: "未过的检查" alone reads as "the rest passed". A column
                # the receipt never measured has its own place on the row.
                lines.append("| %s | %s | %s | %s | %s |" % (
                    c.get("candidate"), c.get("state"),
                    ", ".join(c.get("failing_checks") or []) or "—",
                    ", ".join(c.get("unchecked_checks") or []) or "—",
                    c.get("receipt")))
            lines.append("")
        elif face["agenda_cause"] == "no_topics":
            lines.append("日历面里没有「被判过但被拒」的候选：确实是没人写题（开题）。")
        elif face["agenda_cause"] == "mechanism":
            lines.append("有活没入池：机制故障，该入池。")
        else:
            lines.append("日历面读不出来——未知不是「没题」（r98）。")
        if cal.get("receipts_unreadable"):
            lines.append("读不到的收据：%s"
                         % json.dumps(cal["receipts_unreadable"], ensure_ascii=False))
        lines.append("")
    cap = face.get("capacity") or {}
    if cap.get("readable"):
        lines += ["## 地板：日历过了也不够", "",
                  "| 读法 | 数 | 出处 |", "|---|---|---|",
                  "| 地板（产能门槛） | %s | %s |" % (
                      _cny(cap.get("floor_cny")),
                      cap.get("floor_owner") or "—"),
                  "| 已定价的最高上限 | %s | %s |" % (
                      _cny(cap.get("ceiling_cny")),
                      cap.get("best_reading") or "—"),
                  "| 缺口 | %s | %s |" % (_cny(cap.get("gap_cny")),
                                          cap.get("receipt") or "—"),
                  "| 上限／地板 | %s | %s |" % (_share(cap.get("share_of_floor")),
                                              cap.get("verdict") or "—"),
                  "",
                  face.get("capacity_sentence") or "",
                  ""]
        if cap.get("floor_matches_owner") is False:
            lines += ["**地板与属主门不一致**：收据写着 %s，属主是 %s。"
                      "先修这个差，别在同一页上比较两个地板。" % (
                          _cny(cap.get("floor_cny")),
                          cap.get("floor_owner") or "—"), ""]
    else:
        lines += ["## 地板：读不到", "",
                  "产能收据读不到（%s）。读不到不等于没有缺口（r98）。"
                  % (cap.get("why") or "unknown"), ""]
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


# ----------------------------------------------------------------- selftest
def _selftest():
    ok = [0, 0]

    def check(name, got, want):
        ok[1] += 1
        if got == want:
            ok[0] += 1
            print("  PASS %s" % name)
        else:
            print("  FAIL %s -> %r != %r" % (name, got, want))

    # (1) classification is the whole contract
    check("ready=3 floor=3 -> OK", classify(3, 0, 3), ("SUPPLY_OK", 3))
    check("ready=0 + 3 unclaimed tickets -> BROKEN",
          classify(0, 3, 3), ("SUPPLY_BROKEN", 3))
    check("ready=1 with nothing to enqueue -> AGENDA_DEBT",
          classify(1, 0, 3), ("AGENDA_DEBT", 1))
    check("ready=1 + exactly 2 tickets reaches floor -> BROKEN",
          classify(1, 2, 3), ("SUPPLY_BROKEN", 3))
    check("unreadable pool never reads as agenda debt",
          classify(None, 0, 3), ("UNKNOWN", None))

    # (1b) the layer under AGENDA_DEBT (r1421): "write a topic" and "every
    # candidate we judged fails its own calendar" are different orders.
    CHECK_WORD = "NO_CANDIDATE_PASSES_CALENDAR"
    check("startable work -> mechanism",
          agenda_cause("SUPPLY_BROKEN", 3, 3, None), "mechanism")
    check("all candidates refused by calendar -> calendar",
          agenda_cause("AGENDA_DEBT", 0, 3, CHECK_WORD), "calendar")
    check("no candidate declared -> no_topics",
          agenda_cause("AGENDA_DEBT", 0, 3, "NO_CANDIDATES"), "no_topics")
    check("admitted candidate but nothing enqueued -> no_topics",
          agenda_cause("AGENDA_DEBT", 0, 3, "ADMITTED_CANDIDATE_EXISTS"),
          "no_topics")
    check("unreadable calendar is not no_topics",
          agenda_cause("AGENDA_DEBT", 0, 3, "UNKNOWN"), "unknown")
    check("unreadable pool -> unknown cause",
          agenda_cause("UNKNOWN", None, None, "NO_CANDIDATES"), "unknown")
    check("no cause when the floor is satisfied",
          agenda_cause("SUPPLY_OK", 3, 0, None), None)

    # (2) backlog parser: claimed/done rows are not candidates
    import tempfile
    d = tempfile.mkdtemp(prefix="supplyface-")
    bl = os.path.join(d, "backlog.md")
    with io.open(bl, "w", encoding="utf-8") as f:
        f.write("# backlog\n\n1. free row\n2. taken row claimed@bm-c@10-01\n"
                "3. finished row done@10-02\n4. another free row\nnot a row\n")
    check("backlog counts only unclaimed rows", count_backlog(bl), (2, 2))
    check("missing backlog is unknown, not zero",
          count_backlog(os.path.join(d, "nope.md")), (None, None))

    # (3) queue parser: done rows are consumed, malformed rows ignored
    q = os.path.join(d, "tech.md")
    with io.open(q, "w", encoding="utf-8") as f:
        f.write("| T1 | draft one | ptr | open |\n"
                "| T2 | consumed | ptr | done |\n"
                "| T3 | draft three | ptr | open |\n"
                "| not | a row |\n")
    check("queue counts only non-done rows", len(open_queue_rows(q)), 2)
    check("queue row id kept", open_queue_rows(q)[0][0], "T1")
    check("missing queue is unknown", open_queue_rows(os.path.join(d, "x.md")),
          None)

    # (3b) a `done` row carrying its commit note is still consumed (this face
    # once read `done（r873 bm-b）` as a live draft and reported 19 of them)
    check("suffixed done is consumed", row_status("done（r873 bm-b）"),
          "consumed")
    check("closed is consumed", row_status("closed"), "consumed")
    check("bare open is live", row_status("open"), "live")
    check("a measurement in the status column is not a status",
          row_status("0.455 > null family p95 0.077"), "unreadable")
    check("empty cell is unreadable, not live", row_status("  "), "unreadable")
    q2 = os.path.join(d, "explore.md")
    with io.open(q2, "w", encoding="utf-8") as f:
        f.write("| E1 | consumed with note | ptr | done（r873 bm-b） |\n"
                "| E2 | live | ptr | open |\n"
                "| E3 | result as status | ptr | 0.455 > null p95 0.077 |\n"
                "| E4 | really closed | ptr | closed |\n")
    sc2 = scan_queue(q2)
    check("scan separates live from consumed", (len(sc2["live"]), sc2["consumed"]),
          (1, 2))
    check("scan names the unreadable row", sc2["unreadable"][0][0], "E3")
    check("open_queue_rows returns only the live row",
          [r[0] for r in open_queue_rows(q2)], ["E2"])

    # (3c) the level under the calendar (r1308): a calendar sentence invites
    # waiting, this one says whether waiting can finish the job. Numbers are
    # copied from the receipt; an unreadable receipt is not a zero gap.
    cap_path = os.path.join(d, "cap.json")

    def _write_cap(floor, ceiling, share, gap, owner):
        with io.open(cap_path, "w", encoding="utf-8") as f:
            json.dump({"floor_cny": floor, "best_capacity_5pct_cny": ceiling,
                       "gap_to_floor_cny": gap, "best_share_of_floor": share,
                       "verdict": "FLOOR_BEYOND_PRICED_ENVELOPE",
                       "best_reading": "priced_envelope_R20",
                       "floor_owner": owner,
                       "generated": "fixture"}, f)

    _write_cap(20000000.0, 5000000.0, 0.25, 15000000.0,
               "scripts/candidate_year_gate.py::CAPACITY_FLOOR_CNY")
    cap1 = capacity_layer(cap_path)
    check("receipt numbers are carried, not recomputed",
          (cap1["ceiling_cny"], cap1["share_of_floor"]), (5000000.0, 0.25))
    check("a receipt whose floor equals the owning gate agrees",
          cap1["floor_matches_owner"], True)
    check("the capacity sentence prints the receipt's own ratio",
          "25.0%" in capacity_sentence(cap1), True)
    check("the capacity sentence prints the ceiling it read",
          "5,000,000" in capacity_sentence(cap1), True)
    _write_cap(25000000.0, 7000000.0, 0.28, 18000000.0, "somewhere-else")
    cap2 = capacity_layer(cap_path)
    check("a different receipt moves the sentence (not a constant)",
          "7,000,000" in capacity_sentence(cap2), True)
    check("a floor that disagrees with the owning gate is flagged",
          cap2["floor_matches_owner"], False)
    check("the disagreement is said out loud",
          "不一致" in capacity_sentence(cap2), True)
    cap3 = capacity_layer(os.path.join(d, "nope.json"))
    check("missing receipt is unreadable, not a zero gap",
          cap3["readable"], False)
    check("unreadable says so instead of printing 0",
          "读不到" in capacity_sentence(cap3), True)

    # (4) end to end on fixtures, then the same call twice must be identical
    NO_TOPICS = {"verdict": "NO_CANDIDATES", "n_candidates": 0,
                 "n_refused": 0, "candidates": [], "receipts_unreadable": []}
    f1 = build(pool_ready=0, pool_ids=[], tickets=0, backlog_path=bl,
               queue_paths=[q], floor=3, calendar=NO_TOPICS, capacity=cap1)
    f2 = build(pool_ready=0, pool_ids=[], tickets=0, backlog_path=bl,
               queue_paths=[q], floor=3, calendar=NO_TOPICS, capacity=cap1)
    check("fixture verdict", f1["verdict"], "AGENDA_DEBT")
    check("fixture cause is no_topics", f1["agenda_cause"], "no_topics")
    check("deterministic", json.dumps(f1, sort_keys=True),
          json.dumps(f2, sort_keys=True))
    check("startable excludes queue drafts", f1["startable_now"], 0)
    check("shortfall named", f1["shortfall"], 3)

    # (4b) the live shape r1421 exists for: same verdict, different sentence
    REFUSED = {"verdict": CHECK_WORD, "n_candidates": 1, "n_refused": 1,
               "candidates": [{"candidate": "nobond_vt08_adopted",
                               "state": "CONDITIONAL",
                               "failing_checks": ["Y4_top2_share"],
                               "receipt": "results/x.json"}],
               "receipts_unreadable": []}
    f3 = build(pool_ready=0, pool_ids=[], tickets=0, backlog_path=bl,
               queue_paths=[q], floor=3, calendar=REFUSED, capacity=cap1)
    check("refused calendar keeps the same verdict", f3["verdict"],
          "AGENDA_DEBT")
    check("refused calendar changes the cause", f3["agenda_cause"], "calendar")
    check("the sentence names the candidate and its failing check",
          ("nobond_vt08_adopted" in f3["reading"]
           and "Y4_top2_share" in f3["reading"]), True)
    check("the cause sentence is not the generic agenda wording",
          f3["reading"] == READINGS["AGENDA_DEBT"], False)
    check("the calendar sentence also carries the level (r1308)",
          "5,000,000" in f3["reading"], True)

    print("selftest %d/%d PASS" % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


def check_published(path=None):
    """Re-derive the verdict from the published rows (falsifiability leg).

    A face that prints a verdict nobody recomputes is a claim, not a
    measurement; this refuses a published file whose verdict does not follow
    from its own numbers.
    """
    path = path or OUT
    if not os.path.exists(path):
        print("supply_candidate_face: no published face at %s" % path)
        return 2
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    want, startable = classify(d.get("pool_ready"), d.get("tickets_unclaimed"),
                               d.get("floor"))
    problems = []
    if d.get("verdict") != want:
        problems.append("verdict %r != recomputed %r"
                        % (d.get("verdict"), want))
    if startable is not None and d.get("startable_now") != startable:
        problems.append("startable_now %r != recomputed %r"
                        % (d.get("startable_now"), startable))
    if d.get("pool_ready") is not None:
        want_short = max(0, d["floor"] - d["pool_ready"])
        if d.get("shortfall") != want_short:
            problems.append("shortfall %r != recomputed %r"
                            % (d.get("shortfall"), want_short))
        want_cause = agenda_cause(
            want, startable, want_short,
            (d.get("calendar") or {}).get("verdict"))
        if d.get("agenda_cause") != want_cause:
            problems.append("agenda_cause %r != recomputed %r"
                            % (d.get("agenda_cause"), want_cause))
    # r1308: the level is a copy of a receipt that another script writes, so a
    # published number that no longer matches it is a stale claim, and a
    # sentence that does not follow from the published capacity is a constant
    # pretending to be a reading.
    cap = d.get("capacity") or {}
    now_cap = capacity_layer()
    if bool(cap.get("readable")) != bool(now_cap.get("readable")):
        problems.append("capacity readability %r != receipt %r"
                        % (cap.get("readable"), now_cap.get("readable")))
    elif cap.get("readable"):
        for k in ("floor_cny", "ceiling_cny", "gap_cny", "share_of_floor"):
            if cap.get(k) != now_cap.get(k):
                problems.append("capacity.%s %r != receipt %r"
                                % (k, cap.get(k), now_cap.get(k)))
        if d.get("capacity_sentence") != capacity_sentence(cap):
            problems.append("capacity_sentence does not follow from the "
                            "published capacity")
    if problems:
        print("supply_candidate_face: FAIL " + "; ".join(problems))
        return 1
    print("supply_candidate_face: check OK (%s)" % want)
    return 0


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--check" in argv:
        return check_published()
    if "run" in argv or len(argv) <= 1:
        face = build()
        face["generated"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z")
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        write_md(face, os.path.join(ROOT, "results", "supply_candidates.md"))
        print("supply_candidate_face: %s ready=%s startable=%s shortfall=%s"
              % (face["verdict"], face["pool_ready"], face["startable_now"],
                 face["shortfall"]))
        return 0
    print(__doc__.strip().splitlines()[0])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))