"""r266 (bm-a, live instance) resolver: stash-pop 3-UU (dead-round r266 residue vs bm-b r269 incoming).

Stash-pop face: ours(:2)=origin/bm-b r269, theirs(:3)=stash=r266 residue.
Probed shapes:
- post_review.jsonl: append-log -> line-union zero-loss (ours 1100 = base 1067
  + 33 bm-b 19:25:45 run rows; theirs 1096 = same base + 29 r266 19:30:34
  run rows; union = 1129, zero row overlap expected).
- post_review_criteria.json: registry items row union (ours adds 4 T-81 rows,
  theirs adds 1 T-83-S4-QUARTERLY-WIRING row; _reconciled/_law byte-identical
  both sides). Face: LF, no BOM, indent=1, ensure_ascii=False, no trailing
  newline (roundtrip-asserted before write).
- REPORT-20260926.md: NOT hand-resolved; Tools/post_review.py run re-derives
  it after the union (deterministic view, canonical re-derive path, no hand
  ledger edit) -- run separately after this resolver.
Fail-closed: any assert red = exit 2, nothing written (r185/r188 discipline).
"""
import difflib
import json
import subprocess
import sys


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"blob fail {spec}: {r.stderr[:200]!r}")
    return r.stdout


def main():
    # ---- 1. post_review.jsonl: line-union zero-loss ----
    p1 = "results/post_review.jsonl"
    o = blob(f":2:{p1}").splitlines(keepends=True)
    t = blob(f":3:{p1}").splitlines(keepends=True)
    c = 0
    while c < min(len(o), len(t)) and o[c] == t[c]:
        c += 1
    add_o, add_t = len(o) - c, len(t) - c
    if not (add_o == 33 and add_t == 29 and c >= 1000):
        raise SystemExit(
            f"FAIL prefix face: common={c} ours-added={add_o} theirs-added={add_t} (expected 33/29)"
        )
    o_set = set(o)
    dup = [ln for ln in t[c:] if ln in o_set]
    if dup:
        raise SystemExit(f"FAIL unexpected row overlap between run sets: {len(dup)}")
    union = o + t[c:]
    for ln in union:
        json.loads(ln.decode("utf-8"))
    if len(union) != 1129:
        raise SystemExit(f"FAIL union count {len(union)} != 1129")
    with open(p1, "wb") as fh:
        fh.write(b"".join(union))
    print(f"[1/2] jsonl union OK: {c} common + {add_o} bm-b + {add_t} r266 = {len(union)} rows")

    # ---- 2. post_review_criteria.json: items row union, byte-face mirrored ----
    p2 = "results/post_review_criteria.json"
    o_b = blob(f":2:{p2}")
    t_b = blob(f":3:{p2}")
    o_obj = json.loads(o_b.decode("utf-8"))
    t_obj = json.loads(t_b.decode("utf-8"))
    if json.dumps(o_obj, indent=1, ensure_ascii=False).encode("utf-8") != o_b:
        raise SystemExit("FAIL ours roundtrip face mismatch (indent/ascii/EOL probe wrong)")
    if o_obj.get("_reconciled") != t_obj.get("_reconciled") or o_obj.get("_law") != t_obj.get("_law"):
        raise SystemExit("FAIL _reconciled/_law diverged -- manual adjudication required")
    o_ids = [e["id"] for e in o_obj["items"]]
    t_ids = [e["id"] for e in t_obj["items"]]
    if len(set(o_ids)) != len(o_ids) or len(set(t_ids)) != len(t_ids):
        raise SystemExit("FAIL duplicate ids within a side")
    added = [e for e in t_obj["items"] if e["id"] not in set(o_ids)]
    if [e["id"] for e in added] != ["T-83-S4-QUARTERLY-WIRING"]:
        raise SystemExit(f"FAIL theirs-added ids: {[e['id'] for e in added]}")
    merged = dict(o_obj)
    merged["items"] = o_obj["items"] + added
    out = json.dumps(merged, indent=1, ensure_ascii=False).encode("utf-8")
    ops = [op for op in difflib.SequenceMatcher(None, o_b, out, autojunk=False).get_opcodes()
           if op[0] != "equal"]
    if not (len(ops) == 1 and ops[0][0] == "insert"):
        raise SystemExit(f"FAIL byte-diff not single insert: {ops}")
    if json.loads(out) != merged:
        raise SystemExit("FAIL post-merge roundtrip")
    with open(p2, "wb") as fh:
        fh.write(out)
    print(f"[2/2] criteria union OK: items {len(o_ids)} + {len(added)} = {len(merged['items'])} (single-insert verified)")

    print("RESOLVED both files; REPORT left for Tools/post_review.py run re-derive")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        msg = str(e)
        if msg.startswith("FAIL"):
            print(msg)
            sys.exit(2)
        raise
