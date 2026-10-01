"""r533 bm-b LA-EDGE legacy_base conflict-soup repair (r498 deterministic AA face).

Origin carries cells_LA-EDGE_legacy_base.jsonl as a 43-block marker soup
(introduced by bm-a r549 rebase against rebased-away 9f6ea8b2d; both sides =
concurrent deterministic burns, line-order-only conflict). Repair:
- collect all valid JSON rows from both sides
- assert per-key payload identity across ALL copies (determinism)
- rewrite clean file (one row per key, key-sorted, peer EOL preserved)
Expected unique keys 1029 (225 missing -> runner checkpoint resume burns them).
"""
import json
import sys

F = r"results\lowamp_p3\cells_LA-EDGE_legacy_base.jsonl"
PEER = r"results\lowamp_p3\cells_LA-EQ_legacy_base.jsonl"
MARKS = ("<<<<<<<", "=======", ">>>>>>>", "|||||||")


def main():
    raw = open(PEER, "rb").read()
    eol = "\r\n" if b"\r\n" in raw[:400] else "\n"
    rows_by_key = {}
    bad = 0
    for ln in open(F, encoding="utf-8").read().splitlines():
        if not ln.strip() or any(ln.startswith(m) for m in MARKS):
            continue
        try:
            row = json.loads(ln)
        except Exception:
            bad += 1
            continue
        k = row["key"]
        canon = json.dumps(row, sort_keys=True)
        if k in rows_by_key:
            if rows_by_key[k][1] != canon:
                print(f"ASSERT FAIL: key {k} has divergent payloads across copies")
                sys.exit(1)
        else:
            rows_by_key[k] = (row, canon)
    keys = sorted(rows_by_key, key=lambda k: int(k.rsplit("|", 1)[1]))
    out = eol.join(rows_by_key[k][0] and json.dumps(rows_by_key[k][0]) for k in keys)
    with open(F, "wb") as fh:
        fh.write((out + eol).encode("utf-8"))
    print(f"eol={eol!r} unique_keys={len(keys)} bad_lines={bad}")
    pos = [int(k.rsplit('|', 1)[1]) for k in keys]
    print(f"pos range {min(pos)}..{max(pos)} contiguous={pos == list(range(min(pos), max(pos)+1))}")
    print(f"missing_vs_1254 = {1254 - len(keys)}")


if __name__ == "__main__":
    main()
