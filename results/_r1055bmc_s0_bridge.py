# -*- coding: utf-8 -*-
"""r1055 bm-c S0 bridge: analyze/apply union faces for ff-merge with dirty tree.

Phase A (default): read-only analysis of local-vs-origin delta for the 3 union faces.
Phase B (--apply): after `git stash push <dirty>` + `git merge --ff-only`, restore
keep-local faces from stash@{0}, union the 3 faces (origin base + local-only lines).

Laws: r1031 (verify stash push rc before drop), r966 (line-level union, zero deletion),
r1002 (regenerable intersect faces -> origin wins, S6 rerun regenerates).
"""
import subprocess, sys, io, json

UNION_FACES = [
    "fleet/orders/O-20261016-1745-bm-a.md",
    "results/post_review.jsonl",
    "results/x2_watch_log.jsonl",
]

def git_show_origin(path):
    r = subprocess.run(["git", "show", "origin/main:" + path],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit("git show failed for %s: %s" % (path, r.stderr[:200]))
    return r.stdout.decode("utf-8", "replace")

def read_disk(path):
    with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        return f.read()

def analyze():
    for p in UNION_FACES:
        origin_txt = git_show_origin(p)
        local_txt = read_disk(p)
        o_lines = [l for l in origin_txt.splitlines()]
        l_lines = [l for l in local_txt.splitlines()]
        o_set = set(x.rstrip("\r") for x in o_lines)
        l_set = set(x.rstrip("\r") for x in l_lines)
        only_local = [x for x in l_lines if x.rstrip("\r") not in o_set]
        only_origin = [x for x in o_lines if x.rstrip("\r") not in l_set]
        print("[FACE] %s" % p)
        print("  origin_lines=%d local_lines=%d local_only=%d origin_only=%d" % (
            len(o_lines), len(l_lines), len(only_local), len(only_origin)))
        for x in only_local[:3]:
            print("  L+ %s" % x[:160])
        for x in only_origin[:3]:
            print("  O+ %s" % x[:160])
        if only_local:
            print("  L+_last %s" % only_local[-1][:160])

def apply_union():
    """Called AFTER stash+merge+checkout-from-stash of union faces (disk=local ver)."""
    receipt = {}
    for p in UNION_FACES:
        origin_txt = git_show_origin(p)
        local_txt = read_disk(p)
        o_lines = [l.rstrip("\r") for l in origin_txt.splitlines()]
        l_lines = [l.rstrip("\r") for l in local_txt.splitlines()]
        o_set = set(o_lines)
        l_set = set(l_lines)
        only_local = [x for x in l_lines if x not in o_set]
        # union: origin block, then local-only lines appended (append-only law, zero deletion)
        union_lines = o_lines + only_local
        nl = "\r\n" if "\r\n" in origin_txt else "\n"
        out = nl.join(union_lines) + (nl if origin_txt.endswith(("\n", "\r")) else "")
        with io.open(p, "w", encoding="utf-8", newline="") as f:
            f.write(out)
        receipt[p] = {"origin": len(o_lines), "local": len(l_lines),
                      "local_only_kept": len(only_local), "union_total": len(union_lines)}
        print("[UNION] %s kept_local_only=%d -> total=%d" % (p, len(only_local), len(union_lines)))
    with io.open("results/_r1055bmc_s0_bridge_receipt.json", "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("receipt written")

if __name__ == "__main__":
    if "--apply" in sys.argv:
        apply_union()
    else:
        analyze()
