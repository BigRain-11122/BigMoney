"""r266 rebase resolver: my round-266 commit replayed onto bm-b r270 (sha-fix yield).

Rebase stages: :2 = ours = origin/bm-b r270 base, :3 = theirs = my commit.
Yield adjudication (anti-dup, fleet/README §4 spirit): the same-window
independent sha-face P0 fix -- bm-b r270 root-fix (LF/git-blob canonical x4
producer sites + criteria 4 anchors re-encoded with fact-proof) is the
origin canon and is MORE complete (covers market_clock_call 4th site);
my CRLF-face producer variant yields (dropped via checkout --ours).
What survives from my commit: dead-round r266 residue adoption faces
(T-83 ticket r266 row line-splice, prompt quarterly leg, 3 archived scripts),
criteria T-83-S4 row (auto-merged, integrity-checked here), jsonl line-union
zero-loss (my r266 29-row run + my 2 fresh re-derive runs preserved).
Fail-closed: any assert red = exit 2, nothing written.
"""
import json
import subprocess
import sys

P = "results/post_review.jsonl"


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"blob fail {spec}: {r.stderr[:200]!r}")
    return r.stdout


def main():
    # ---- 1. take origin for yield files (rebase face: --ours = base) ----
    for f in ["scripts/strategy_scorecard.py", "results/strategy_scorecard.json",
              "results/scorecard_v1.json", "results/autofill_state.json"]:
        subprocess.run(["git", "checkout", "--ours", f], check=True)
        subprocess.run(["git", "add", f], check=True)
    print("[1] yield files taken from origin (bm-b r270 LF-canonical sha fix)")

    # ---- 2. criteria auto-merge integrity check (not hand-edited) ----
    c = json.load(open("results/post_review_criteria.json", encoding="utf-8-sig"))
    ids = [e["id"] for e in c["items"]]
    assert len(ids) == 34 and len(set(ids)) == 34, f"items {len(ids)}"
    assert "T-83-S4-QUARTERLY-WIRING" in ids, "my row lost in auto-merge"
    prof = [e for e in c["items"] if e["id"] == "T-81-PROFILE-CARDS"][0]
    got = json.dumps(prof)
    assert "67c48f8aab9708a0" in got, "origin LF-face anchor missing"
    assert "same frozen fact, canonical face, zero check deleted/weakened" in c["_reconciled"]
    print("[2] criteria auto-merge verified: 34 items, my row + origin re-anchors intact")

    # ---- 3. jsonl line-union: origin base + my unique rows ----
    o = blob(f":2:{P}").splitlines(keepends=True)
    t = blob(f":3:{P}").splitlines(keepends=True)
    c_n = 0
    while c_n < min(len(o), len(t)) and o[c_n] == t[c_n]:
        c_n += 1
    o_set = set(o)
    mine_only = [ln for ln in t[c_n:] if ln not in o_set]
    # expected: common core = r269 union base (1100), mine adds 97 (29 r266 + 34 + 34)
    if not (c_n == 1100 and len(t) - c_n == 97 and len(mine_only) == 97):
        raise SystemExit(
            f"FAIL jsonl face: common={c_n} mine-tail={len(t) - c_n} mine-only={len(mine_only)} (want 1100/97/97)")
    union = o + mine_only
    for ln in union:
        json.loads(ln.decode("utf-8"))
    if len(union) != len(o) + 97:
        raise SystemExit(f"FAIL union count {len(union)} != {len(o) + 97}")
    with open(P, "wb") as fh:
        fh.write(b"".join(union))
    print(f"[3] jsonl union OK: {len(o)} origin + {len(mine_only)} mine = {len(union)} rows")
    print("RESOLVED; REPORT left for Tools/post_review.py run re-derive")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if str(e).startswith("FAIL") or str(e).startswith("blob fail"):
            print(e)
            sys.exit(2)
        raise
