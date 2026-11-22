#!/usr/bin/env python
"""bench_queue_truth -- is the bench console honest about its own cells?

Why this face exists
--------------------
`research/BENCH-QUEUE.json` is the operating console of the continuous-testing line: one cell
per question that can change whether we bet, and at what size. Its `status` field is what the
silent tick reads to decide what to run next, and what a reader uses to know what has already
been answered.

On 2026-11-23 the console and the evidence disagreed: `repo_ladder` was still `pending` after
`scripts/bench_repo_ladder.py`, `results/bench_repo_ladder.json` (with a full verdict block) and
`research/BENCH-REPO-LADDER.md` had all been delivered the same night, and `BENCH-STATUS.md`
announced eight cells while the queue carried ten. Two costs follow mechanically: the tick can
re-run a finished question, and a reader cannot tell what is answered without opening three
files. Household law (查重律 / r1787) says a delivered question must not be run twice.

What this face does (and what it refuses to do)
-----------------------------------------------
It checks only what can be checked from the files themselves:

  T1  every delivered cell's declared script, result and page exist (repo-relative paths)
  T2  a `done` cell's result carries a verdict-bearing key (verdict / verdicts / headline)
  T3  a cell whose result AND page exist and whose result carries a verdict is NOT `pending`
      -- that combination is a re-run trap, whatever the tick believes
  T4  BENCH-STATUS.md lists exactly the ids in the queue, and its header count matches
  T5  no declared path is absolute or escapes the repository

It does NOT judge whether a verdict is still true on today's bar (that is the `revalidate`
cell's job), and it does not edit the queue: a contention window forbids shared-face writes,
and a checker that rewrites the thing it checks is not a checker.

Exit codes: 0 = consistent, 3 = drift found (named, never silent), 2 = mechanism failure.
"""
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

QUEUE = os.path.join(bc.RESEARCH, "BENCH-QUEUE.json")
STATUS = os.path.join(bc.RESEARCH, "BENCH-STATUS.md")
OUT_JSON = os.path.join(bc.RESULTS, "bench_queue_truth.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-QUEUE-TRUTH.md")

VERDICT_KEYS = ("verdict", "verdicts", "headline")
DRIFT = ("DELIVERED_BUT_PENDING", "DONE_WITHOUT_EVIDENCE", "DONE_WITHOUT_VERDICT",
         "PATH_MISSING", "PATH_OUTSIDE_REPO", "STATUS_ROW_MISSING", "STATUS_ROW_UNKNOWN",
         "STATUS_COUNT_WRONG", "STATUS_FILE_MISSING")


def _now():
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _resolve(root, rel):
    """Repo-relative declared path -> absolute, with a containment check.

    A path that was never declared (None / empty) is not a promise, so it is not an error --
    the caller records it as undeclared and moves on.
    """
    if not rel:
        return None, None
    if os.path.isabs(rel):
        return None, "PATH_OUTSIDE_REPO"
    abs_path = os.path.normpath(os.path.join(root, rel))
    if os.path.commonpath([os.path.abspath(abs_path), os.path.abspath(root)]) != os.path.abspath(root):
        return None, "PATH_OUTSIDE_REPO"
    return abs_path, None


def _load_result(abs_path):
    try:
        with open(abs_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _status_ids(status_path):
    """Ids listed in the STATUS.md table, in order, with the verdict column text."""
    ids = {}
    if not os.path.exists(status_path):
        return ids, None
    count = None
    with open(status_path, "r", encoding="utf-8") as fh:
        for line in fh:
            m = re.search(r"细胞数\s*(\d+)", line)
            if m:
                count = int(m.group(1))
            if not line.startswith("|"):
                continue
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cols or not cols[0] or cols[0] in ("id",) or set(cols[0]) <= set("-: "):
                continue
            ids[cols[0]] = cols[2] if len(cols) > 2 else ""
    return ids, count


def audit(queue_path=QUEUE, status_path=STATUS, root=None):
    root = root or bc.ROOT
    if not os.path.exists(queue_path):
        return {"schema": "bench_queue_truth/v1", "ts": _now(), "headline": "QUEUE_MISSING",
                "drifts": [{"code": "QUEUE_MISSING", "cell": None}], "cells": []}
    with open(queue_path, "r", encoding="utf-8") as fh:
        queue = json.load(fh)

    status_ids, status_count = _status_ids(status_path)

    rows = []
    for cell in queue.get("cells", []):
        cid = cell.get("id")
        status = (cell.get("status") or "").lower()
        codes = []
        evidence = {}

        readable = {}
        for kind in ("script", "result", "page"):
            abs_path, bad = _resolve(root, cell.get(kind))
            if bad:
                codes.append(bad)
                readable[kind] = False
                continue
            if abs_path is None:
                readable[kind] = None          # never declared (a reuse cell may declare none)
                evidence[kind] = None
                continue
            exists = os.path.exists(abs_path)
            readable[kind] = exists
            evidence[kind] = cell.get(kind)
            if not exists and status == "done":
                # a pending cell that has not been built yet is the honest default, not drift;
                # a done cell that points at a file which is not there is a broken promise.
                codes.append("PATH_MISSING")

        payload = None
        if readable.get("result"):
            payload = _load_result(_resolve(root, cell.get("result"))[0])
        result_verdict = bool(payload) and any(k in payload for k in VERDICT_KEYS)
        # a reader can also meet the verdict in the status table; that counts as evidence
        status_verdict = (status_ids.get(cid) or "").strip()
        status_verdict_ok = bool(status_verdict) and status_verdict not in ("—", "-", "–")
        has_verdict = result_verdict or status_verdict_ok
        evidence["result_verdict_key"] = result_verdict
        evidence["status_verdict"] = status_verdict_ok
        if payload is not None:
            evidence["result_keys"] = [k for k in VERDICT_KEYS if k in payload]

        delivered = bool(readable.get("result")) and bool(readable.get("page") or readable.get("page") is None) \
            and has_verdict
        if status == "done":
            if not readable.get("result"):
                codes.append("DONE_WITHOUT_EVIDENCE")
            if not has_verdict:
                codes.append("DONE_WITHOUT_VERDICT")
        elif delivered:
            # the result block already answers the question but the tick would run it again
            codes.append("DELIVERED_BUT_PENDING")

        codes = [c for c in dict.fromkeys(codes)]
        rows.append({"id": cid, "status": status, "lane": cell.get("lane"),
                     "question": (cell.get("question") or "")[:120],
                     "delivered": bool(delivered), "evidence": evidence,
                     "drift": codes})

    ids_in_queue = [r["id"] for r in rows]
    if not os.path.exists(status_path):
        rows_drift = [{"code": "STATUS_FILE_MISSING", "cell": None}]
    else:
        rows_drift = []
        for cid in ids_in_queue:
            if cid not in status_ids:
                rows_drift.append({"code": "STATUS_ROW_MISSING", "cell": cid})
        for cid in status_ids:
            if cid not in ids_in_queue:
                rows_drift.append({"code": "STATUS_ROW_UNKNOWN", "cell": cid})
        if status_count is not None and status_count != len(ids_in_queue):
            rows_drift.append({"code": "STATUS_COUNT_WRONG", "cell": None,
                               "printed": status_count, "queue": len(ids_in_queue)})

    cell_drifts = [{"code": c, "cell": r["id"]} for r in rows for c in r["drift"]]
    drifts = cell_drifts + rows_drift
    headline = "QUEUE_CONSISTENT" if not drifts else "QUEUE_DRIFT"

    return {
        "schema": "bench_queue_truth/v1",
        "ts": _now(),
        "headline": headline,
        "queue_path": os.path.relpath(queue_path, root).replace("\\", "/"),
        "queue_updated": queue.get("updated"),
        "cells": rows,
        "counts": {
            "cells": len(rows),
            "done": sum(1 for r in rows if r["status"] == "done"),
            "pending": sum(1 for r in rows if r["status"] == "pending"),
            "delivered": sum(1 for r in rows if r["delivered"]),
            "status_rows": len(status_ids),
            "drifts": len(drifts),
        },
        "drifts": drifts,
        "limits": ("This face cannot know whether a published verdict is still true on today's "
                   "bar; that is the revalidate cell's job. It also cannot know whether a cell "
                   "was declared with the right question -- only whether the console agrees with "
                   "the files next to it."),
    }


def write_md(p):
    lines = ["# Is the bench console honest about its own cells?\n",
             "Headline: **%s** (%d cell(s), %d drift(s)). Queue `%s`, updated %s." % (
                 p["headline"], p["counts"]["cells"], p["counts"]["drifts"],
                 p["queue_path"], p.get("queue_updated") or "n/a"),
             "\n| id | status | delivered | script | result | page | verdict in JSON | verdict in status | drift |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in p["cells"]:
        ev = r["evidence"]
        page = "not declared" if ev.get("page") is None else ("ok" if ev.get("page") else "missing")
        res = "not declared" if ev.get("result") is None else ("ok" if ev.get("result") else "missing")
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["id"], r["status"], "yes" if r["delivered"] else "no",
            "not declared" if ev.get("script") is None else ("ok" if ev.get("script") else "missing"),
            res, page,
            "yes" if ev.get("result_verdict_key") else ("no (file exists)" if ev.get("result") else "n/a"),
            "yes" if ev.get("status_verdict") else "no",
            ", ".join(r["drift"]) or "–"))
    lines.append("")
    if p["drifts"]:
        lines.append("Drifts named:")
        for d in p["drifts"]:
            extra = ""
            if d["code"] == "STATUS_COUNT_WRONG":
                extra = " (printed %s, queue %s)" % (d["printed"], d["queue"])
            lines.append("* `%s`%s%s" % (d["code"], (" · " + d["cell"]) if d.get("cell") else "", extra))
    else:
        lines.append("No drift: every delivered cell is marked done, every done cell has a "
                     "result with a verdict and a page, and the status page lists the same ids.")
    lines.append("")
    lines.append("What this face does not claim: " + p["limits"])
    lines.append("")
    lines.append("Generated %s by `scripts/bench_queue_truth.py`." % p["ts"])
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- selftest
def _plant(tmp, cells, status_rows, status_count, verdicts=None):
    root = tmp
    os.makedirs(os.path.join(root, "research"), exist_ok=True)
    os.makedirs(os.path.join(root, "results"), exist_ok=True)
    os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
    q = {"updated": "2026-01-01T00:00:00+08:00", "note": "", "cells": cells}
    qp = os.path.join(root, "research", "BENCH-QUEUE.json")
    with open(qp, "w", encoding="utf-8") as fh:
        json.dump(q, fh)
    verdicts = verdicts or {}
    sp = os.path.join(root, "research", "BENCH-STATUS.md")
    with open(sp, "w", encoding="utf-8") as fh:
        fh.write("# status\n\nupdated x | 细胞数 %d\n\n| id | 状态 | 判决 |\n|---|---|---|\n" % status_count)
        for cid in status_rows:
            fh.write("| %s | done | %s |\n" % (cid, verdicts.get(cid, "ok")))
    return qp, sp


def _cell(cid, status, verdict=True, page=True, script=True, result=True):
    c = {"id": cid, "status": status, "lane": "x", "question": "q",
         "script": "scripts/%s.py" % cid, "result": "results/%s.json" % cid,
         "page": "research/%s.md" % cid}
    return c, {"id": cid, "verdict": True if verdict else None,
               "page": page, "script": script, "result": result}


def _materialize(root, spec):
    for sub in ("scripts", "results", "research"):
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    for c, ev in spec:
        if os.path.isabs(c.get("script") or ""):
            continue  # the absolute-path leg must not touch the disk outside the fixture
        if ev["script"]:
            open(os.path.join(root, c["script"]), "w").write("# stub\n")
        if ev["result"]:
            payload = {"verdict": {"a": "NO_EDGE"}} if ev["verdict"] else {"notes": "no verdict"}
            with open(os.path.join(root, c["result"]), "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
        if ev["page"]:
            open(os.path.join(root, c["page"]), "w").write("# page\n")


def selftest():
    legs = []

    def leg(name, fn):
        try:
            ok, why = fn()
        except Exception as exc:  # a selftest that crashes is not a passing selftest
            ok, why = False, "raised %s: %s" % (type(exc).__name__, exc)
        legs.append((name, bool(ok), why))

    def _run(spec, status_rows=None, status_count=None, verdicts=None):
        tmp = tempfile.mkdtemp(prefix="bqt_")
        try:
            _materialize(tmp, spec)
            qp, sp = _plant(tmp, [c for c, _ in spec],
                            status_rows if status_rows is not None else [c["id"] for c, _ in spec],
                            status_count if status_count is not None else len(spec),
                            verdicts)
            return audit(qp, sp, tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def l1():
        spec = [_cell("a", "done"), _cell("b", "done")]
        p = _run(spec)
        codes = [d["code"] for d in p["drifts"]]
        return p["headline"] == "QUEUE_CONSISTENT" and not codes, "drifts=%s" % codes

    def l2():
        spec = [_cell("a", "done"), _cell("b", "pending")]
        p = _run(spec)
        return [d["code"] for d in p["drifts"]] == ["DELIVERED_BUT_PENDING"], \
            "%s -> %s" % ([d["cell"] for d in p["drifts"]], [d["code"] for d in p["drifts"]])

    def l3():
        spec = [_cell("a", "done", page=False)]
        p = _run(spec)
        codes = [d["code"] for d in p["drifts"]]
        return codes == ["PATH_MISSING"], "codes=%s" % codes

    def l3b():
        spec = [_cell("a", "done", result=False)]
        p = _run(spec)
        codes = sorted(d["code"] for d in p["drifts"])
        return codes == ["DONE_WITHOUT_EVIDENCE", "PATH_MISSING"], \
            "codes=%s" % codes

    def l4():
        spec = [_cell("a", "done", verdict=False)]
        p = _run(spec, verdicts={"a": "—"})
        return [d["code"] for d in p["drifts"]] == ["DONE_WITHOUT_VERDICT"], \
            "codes=%s" % [d["code"] for d in p["drifts"]]

    def l4b():
        # a reuse cell whose JSON has no verdict key is fine if the status table prints one
        spec = [_cell("a", "done", verdict=False)]
        p = _run(spec, verdicts={"a": "verdict=NO_EDGE, ann_pct=7.64"})
        return p["headline"] == "QUEUE_CONSISTENT", "codes=%s" % [d["code"] for d in p["drifts"]]

    def l5():
        spec = [_cell("a", "done"), _cell("b", "done")]
        p = _run(spec, status_rows=["a"], status_count=8)
        codes = sorted(d["code"] for d in p["drifts"])
        return codes == ["STATUS_COUNT_WRONG", "STATUS_ROW_MISSING"], "codes=%s" % codes

    def l6():
        spec = [_cell("a", "done")]
        p = _run(spec, status_rows=["a", "ghost"], status_count=1)
        return [d["code"] for d in p["drifts"]] == ["STATUS_ROW_UNKNOWN"], \
            "codes=%s" % [d["code"] for d in p["drifts"]]

    def l7():
        spec = [_cell("a", "pending", verdict=False, page=False, script=False, result=False)]
        p = _run(spec)
        # a pending cell with nothing built is the honest default, not drift
        return p["headline"] == "QUEUE_CONSISTENT", "codes=%s" % [d["code"] for d in p["drifts"]]

    def l8():
        ok_cell, ok_ev = _cell("a", "done")
        bad_cell = {"id": "b", "status": "done", "lane": "x", "question": "q",
                    "script": "C:/abs.py", "result": "results/b.json", "page": "research/b.md"}
        bad_ev = {"id": "b", "verdict": True, "page": True, "script": True, "result": True}
        p = _run([(ok_cell, ok_ev), (bad_cell, bad_ev)])
        codes = [d["code"] for d in p["drifts"]]
        return "PATH_OUTSIDE_REPO" in codes, "codes=%s" % codes

    def l9():
        # idempotent: same input twice, same drift list
        spec = [_cell("a", "done"), _cell("b", "pending")]
        p1, p2 = _run(spec), _run(spec)
        return ([d["code"] for d in p1["drifts"]] == [d["code"] for d in p2["drifts"]]), "twice"

    def l10():
        p = audit()
        keys = set(p)
        return (p["headline"] in ("QUEUE_CONSISTENT", "QUEUE_DRIFT")
                and {"cells", "counts", "drifts", "limits"} <= keys), "live headline=%s" % p["headline"]

    for name, fn in [("L1 clean queue", l1), ("L2 delivered-but-pending", l2),
                     ("L3 done with a missing page", l3), ("L3b done with no result", l3b),
                     ("L4 done without any verdict", l4), ("L4b verdict in the status row", l4b),
                     ("L5 status count/row drift", l5), ("L6 unknown status row", l6),
                     ("L7 pending and empty is not drift", l7), ("L8 absolute path rejected", l8),
                     ("L9 idempotent", l9), ("L10 live queue readable", l10)]:
        leg(name, fn)
    bad = [x for x in legs if not x[1]]
    for name, ok, why in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " -- " + why))
    print("%d/%d legs PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    payload = audit()
    bc.write_json(OUT_JSON, payload)
    write_md(payload)
    if "--check" in argv:
        # re-audit and compare with what was published: if the queue moved, say STALE rather
        # than reporting a number that no longer describes the console.
        with open(OUT_JSON, "r", encoding="utf-8") as fh:
            published = json.load(fh)
        fresh = audit()
        pub = [(d["code"], d.get("cell")) for d in published["drifts"]]
        now = [(d["code"], d.get("cell")) for d in fresh["drifts"]]
        if pub != now:
            print(json.dumps({"ok": False, "msg": "STALE: the queue moved since the published "
                                                  "face (published %d drifts, now %d)"
                                % (len(pub), len(now)), "published": pub, "now": now},
                             ensure_ascii=False))
            return 3
        print(json.dumps({"ok": True, "headline": fresh["headline"],
                          "drifts": len(now)}, ensure_ascii=False))
        return 0
    print(json.dumps({"headline": payload["headline"], "counts": payload["counts"],
                      "drifts": payload["drifts"][:12]}, ensure_ascii=False))
    return 0 if payload["headline"] == "QUEUE_CONSISTENT" else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
