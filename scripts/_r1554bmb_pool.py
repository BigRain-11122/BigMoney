"""r1554 bm-b -- close E525 in the runnable pool and seed its successor (E528).

Same shape as ``scripts/_r1545_pool_update.py``: the pool face's newline style is measured (LF today)
rather than assumed, so the diff is the two real changes and not a whole-file flip.
"""
import datetime
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")

DONE_ID_PREFIX = "E525-"
DONE_RESULT = "results/state_tilt/ONWARDRESIDUE-2026-11-08.json"
DONE_EVIDENCE = ("scripts/e525_onward_residue.py (build rc0, check/verify problems=0, selftest "
                 "clean), S6 leg onward_residue, smoke leg # E525")

NEXT = {
    "deliverable": "results/state_tilt/RECURSIVEREAD-<cutoff>.json",
    "entered_at": None,  # stamped below
    "entered_by": "bm-b r1554 (supply floor refill after E525)",
    "evidence_cutoff": "2026-11-08",
    "id": ("E528-WHICH-OF-THE-SELF-RECURSIVE-FORWARDS-IS-READ-BY-A-TERMINATING-ARM-OF-THE-"
           "SAME-FUNCTION"),
    "lane": "cpu-only",
    "lane_note": "static: read the terminating arms of the same function, no network, no rewrites",
    "priority": "normal",
    "source": ("E525 (r1554 bm-b): of the de-duplicated second-hop parcels behind E524's residue, 6 "
               "return into the same function (a self-recursive forward); E524 had counted them as "
               "unresolved because its hop model cannot follow recursion"),
    "status": "ready",
    "target": "results/state_tilt/recursiveread_latest.json",
    "title": (
        "E525 found 6 second-hop parcels whose value is handed back into the same function it is "
        "already inside (`_resolve` calling `_resolve`, `is_literal_side` calling `is_literal_side`). "
        "A self-recursive forward says the chain does not leave the body, but it does not say "
        "whether the recursion ever terminates on a value the caller can read. For each of those 6 "
        "parcels publish what the same function's non-recursive arms do with the value -- return it, "
        "read it, discard it, or never mention it -- and whether every recursive path is guarded by "
        "a depth or type test that can end the recursion. Keep 'read by a terminating arm' and "
        "'the recursion is unguarded' as separate classes; do not count a recursive call as a read."
    ),
}


def main():
    raw = open(POOL, "rb").read()
    crlf = b"\r\n" in raw
    data = json.loads(raw.decode("utf-8"))
    entries = data["entries"]
    now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M+08:00")

    closed = 0
    for entry in entries:
        if str(entry.get("id", "")).startswith(DONE_ID_PREFIX):
            if entry.get("status") != "done":
                entry["status"] = "done"
                entry["result_ref"] = DONE_RESULT
                entry["evidence"] = DONE_EVIDENCE
                entry["done_at"] = now
                entry["done_by"] = "bm-b r1554"
                closed += 1

    seeded = 0
    if not any(str(e.get("id", "")).startswith("E528-") for e in entries):
        card = dict(NEXT)
        card["entered_at"] = now
        entries.append(card)
        seeded = 1

    data["updated_at"] = now
    text = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True)
    if crlf:
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    with io.open(POOL, "w", encoding="utf-8", newline="") as fh:
        fh.write(text + ("\r\n" if crlf else "\n"))

    ready = sorted(e["id"].split("-")[0] for e in entries if e.get("status") == "ready")
    print("closed=%d seeded=%d crlf=%s updated_at=%s" % (closed, seeded, crlf, now))
    print("ready now: %s" % ", ".join(ready))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())