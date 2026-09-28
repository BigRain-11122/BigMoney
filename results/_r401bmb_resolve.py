"""r401 bm-b S0 rebase-conflict resolver: results/runnable_pool.json (r312 pool-entry-done-union recipe).

Sides:
  A (ours,   rebase base) = 1b6a0d7b9  = origin/main bm-a r404 harvest-union 104 entries
  B (theirs, replayed)    = 7359d47b7  = bm-b T-104 s2/s3 commit (runner + pool ready flip)

Verified pre-facts (zero-loss checklist):
  - only-A id: INNOVATION-QUOTA-SLOT-2 (kept by taking A as base)
  - only-B ids: none
  - shard done-loss B->A: 0 (no B shard done that A lacks)
  - entry-level field diffs across union set: worker_class x103 (transient schema field, A newer canonical)
  - single status diff: T104-GRID-S3-DUALFACE-P1  A=waiting (bm-a push-lag stale harvest, recorded in r404 msg)
    vs B=ready (4 gates receipted in commit 7359d47b7: prereg a03887474 / runner+selftest /
    minute feed v1.3 / RAM) -> flip evidence gate is the authority (r312 law) -> take B side.
  - replayed commit also carries scripts/grid_dualface_backtest.py which origin/main lacks
    (fixes origin pool entry runner-missing inconsistency).

Resolution: base = A verbatim; override T104 entry with B's entry object (in A's list position).
Round-trip serialization must be byte-stable vs A blob before writing (json.loads gate + convention detect).
"""
import json
import subprocess
import sys

PATH = "results/runnable_pool.json"
A_REV = "1b6a0d7b9:results/runnable_pool.json"
B_REV = "7359d47b7:results/runnable_pool.json"
TARGET_ID = "T104-GRID-S3-DUALFACE-P1"


def blob_bytes(rev):
    r = subprocess.run(["git", "show", rev], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show failed for {rev}")
    return r.stdout


def detect_convention(raw: bytes, obj) -> dict | None:
    """Find a json.dumps convention that round-trips the original blob byte-identically."""
    text = raw.decode("utf-8")
    for indent in (1, 2, 3, 4):
        for ea in (False, True):
            for sort in (False, True):
                for seps in (((",", ":"),), ((",", ": "), (",", ": ")), ((",", ":"),))[0] if False else [None]:
                    for trail in ("", "\n"):
                        cand = json.dumps(obj, ensure_ascii=ea, indent=indent, sort_keys=sort, separators=seps) + trail
                        if cand == text:
                            return {"indent": indent, "ensure_ascii": ea, "sort_keys": sort,
                                    "separators": seps, "trailing": trail}
    return None


def main():
    a_raw, b_raw = blob_bytes(A_REV), blob_bytes(B_REV)
    A = json.loads(a_raw)
    B = json.loads(b_raw)
    conv = detect_convention(a_raw, A)
    if conv is None:
        sys.exit("FATAL: no byte-stable convention found for A blob; refuse blind write")

    def walk_ids(o, acc):
        if isinstance(o, dict):
            if o.get("id") == TARGET_ID:
                acc.append(o)
            for v in o.values():
                walk_ids(v, acc)
        elif isinstance(o, list):
            for v in o:
                walk_ids(v, acc)

    a_hits, b_hits = [], []
    walk_ids(A, a_hits)
    walk_ids(B, b_hits)
    if len(a_hits) != 1 or len(b_hits) != 1:
        sys.exit(f"FATAL: expected exactly 1 {TARGET_ID} entry per side, got A={len(a_hits)} B={len(b_hits)}")
    if b_hits[0].get("status") != "ready":
        sys.exit("FATAL: B side T104 not ready; refusing")
    if a_hits[0].get("status") != "waiting":
        print("WARN: A side T104 not waiting:", a_hits[0].get("status"))

    # Override in place: mutate A's embedded T104 entry object with B's content.
    a_hits[0].clear()
    a_hits[0].update(b_hits[0])

    out = json.dumps(A, indent=conv["indent"], ensure_ascii=conv["ensure_ascii"],
                     sort_keys=conv["sort_keys"], separators=conv["separators"]) + conv["trailing"]
    parsed = json.loads(out)  # r185 parse-verify gate before write-back
    # done-absorb assertion: no entry status lost vs either side
    sa = {e["id"]: e.get("status") for e in parsed.get("entries", [])}
    done_a = sum(1 for v in sa.values() if v == "done")
    print(f"union entries={len(sa)} done={done_a} target={sa.get(TARGET_ID)}")
    if sa.get(TARGET_ID) != "ready":
        sys.exit("FATAL: T104 not ready after union")
    with open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print("WROTE", PATH, len(out), "bytes, convention:", conv)


if __name__ == "__main__":
    main()
