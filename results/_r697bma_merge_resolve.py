"""r697 bm-a merge resolver: 4 UU faces from bm-c round-496 wave merge.
Per-face canon:
- _attrition_guard_scan.json / daily_scorecard.json / token_usage.json:
  S6 regen/snapshot twins, ours ts newer (21:08:47/21:07:55/21:08:29 vs
  theirs 20:56:46/20:50:12/20:51:58); token_usage machines per-key
  IDENTICAL both sides (r466 side_pick=0 -> explicit whole-face ts
  freshness fallback, ours). -> ours wins all three.
- x2_watch_log.jsonl: append-only -> exact-line union keep-first
  (r656/r456), zero-loss assertion: every distinct line of both sides
  present in product.
Fail-closed: abort without writing on any assertion failure.
"""
import json
import subprocess
import sys

OURS = "HEAD"
THEIRS = "MERGE_HEAD"


def side(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"],
                          capture_output=True).stdout


def resolve_ours(path):
    a = side(OURS, path)
    json.loads(a.decode("utf-8"))          # ours must parse
    with open(path, "wb") as fh:
        fh.write(a)
    json.loads(open(path, "rb").read().decode("utf-8"))   # reparse written
    print(f"[ours-wins] {path}")


def resolve_union_lines(path):
    a = side(OURS, path).decode("utf-8")
    b = side(THEIRS, path).decode("utf-8")
    la = [ln for ln in a.splitlines() if ln.strip()]
    lb = [ln for ln in b.splitlines() if ln.strip()]
    # verify every line parses as json row (x2 watch log rows)
    for ln in la + lb:
        json.loads(ln)
    out = []
    seen = set()
    for ln in la + lb:
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    # zero-loss at the distinct-line canon SET level (r656: intra-side
    # dups exist historically -- theirs 2880 raw/2850 distinct this window;
    # the union contract is on the canon set, not raw counts)
    sa, sb = set(la), set(lb)
    sout = set(out)
    assert sa <= sout and sb <= sout, "zero-loss union failed"
    assert sout == sa | sb and len(out) == len(sout), "union != canon set"
    eol = "\r\n" if "\r\n" in a else "\n"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(eol.join(out) + (eol if out else ""))
    back = [ln for ln in open(path, encoding="utf-8", newline=""
                              ).read().splitlines() if ln.strip()]
    assert set(back) == sout and len(back) == len(out), "write-back verify"
    print(f"[line-union] {path}: ours={len(la)} theirs={len(lb)} "
          f"-> product={len(out)} (shared={len(sa & sb)})")


def main():
    resolve_ours("results/_attrition_guard_scan.json")
    resolve_ours("results/daily_scorecard.json")
    resolve_ours("results/token_usage.json")
    resolve_union_lines("results/x2_watch_log.jsonl")
    print("RESOLVE OK 4/4")


if __name__ == "__main__":
    main()
