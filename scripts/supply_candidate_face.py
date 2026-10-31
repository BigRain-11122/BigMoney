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
          queue_paths=None, floor=None):
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
    return {
        "tool": "supply_candidate_face",
        "floor": floor,
        "pool_ready": pool_ready,
        "pool_ready_ids": pool_ids,
        "tickets_unclaimed": tickets,
        # startable = what can be ignited today without a new freeze
        "startable_now": startable,
        "shortfall": (None if pool_ready is None
                      else max(0, floor - pool_ready)),
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
        "reading": {
            "SUPPLY_OK": "pool holds floor-many ready batches",
            "SUPPLY_BROKEN": "startable work exists and is not in the pool: "
                             "enqueue it, this is a mechanism fault",
            "AGENDA_DEBT": "nothing to enqueue: the red names topic "
                           "generation, not the pool",
            "UNKNOWN": "pool unreadable -- unknown is not empty (r98)",
        }[verdict],
    }


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

    # (4) end to end on fixtures, then the same call twice must be identical
    f1 = build(pool_ready=0, pool_ids=[], tickets=0, backlog_path=bl,
               queue_paths=[q], floor=3)
    f2 = build(pool_ready=0, pool_ids=[], tickets=0, backlog_path=bl,
               queue_paths=[q], floor=3)
    check("fixture verdict", f1["verdict"], "AGENDA_DEBT")
    check("deterministic", json.dumps(f1, sort_keys=True),
          json.dumps(f2, sort_keys=True))
    check("startable excludes queue drafts", f1["startable_now"], 0)
    check("shortfall named", f1["shortfall"], 3)

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