"""r578 bm-b: adopt dead-r577 W89 freeze estate; constructive merge vs origin W88 (r531 law).

Subcommands (idempotent, re-runnable against a fresher origin):
  merge  -- three-way union-merge the 3 same-anchor wave files
           (base=merge-base(HEAD, origin/main), theirs=origin/main [bm-c W88
           rows], mine=worktree [dead-r577 W89 rows]); asserts BOTH sides are
           pure insertions vs base; theirs-first ordering at same anchor
           (W88 before W89, r560 last-registered-row law); AST for .py;
           writes merged bytes to the worktree.
  pool   -- rebase-conflict resolver for results/pool_core_samples.jsonl:
           conflict-region union from :1:/:2:/:3: stages (r294 domain law,
           r570 dict type-gate); :2:(origin) verbatim base + local tail lines
           not already present; writes to worktree and git-adds it.
"""
import ast
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAVE_FILES = [
    "research/PERPETUAL_FACES.md",
    "scripts/perpetual_faces.py",
    "scripts/perpetual_faces_n1.py",
]
POOL = "results/pool_core_samples.jsonl"


def gitb(*args, check=True):
    p = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {args} rc={p.returncode}: {p.stderr[:300]!r}")
    return p.stdout


def lines_of(b):
    return b.splitlines(keepends=True)


def ins_at(base_l, other_l, tag):
    """Return {base_index: [lines]} for pure insertions of other vs base."""
    import difflib
    sm = difflib.SequenceMatcher(None, base_l, other_l, autojunk=False)
    ins = {}
    for tag_, i1, i2, j1, j2 in sm.get_opcodes():
        if tag_ == "equal":
            continue
        if tag_ != "insert" or i1 != i2:
            raise RuntimeError(f"{tag}: non-pure-insert opcode {tag_} "
                               f"base[{i1}:{i2}] other[{j1}:{j2}] -- ABORT")
        ins[i1] = other_l[j1:j2]
    return ins


def cmd_merge():
    mb = gitb("merge-base", "HEAD", "origin/main").decode().strip()
    print(f"merge-base(HEAD, origin/main) = {mb}")
    for path in WAVE_FILES:
        base = lines_of(gitb("show", f"{mb}:{path}"))
        theirs = lines_of(gitb("show", f"origin/main:{path}"))
        wt = open(os.path.join(ROOT, path), "rb").read()
        mine = lines_of(wt)
        ins_t = ins_at(base, theirs, f"theirs:{path}")
        ins_m = ins_at(base, mine, f"mine:{path}")
        n_t = sum(len(v) for v in ins_t.values())
        n_m = sum(len(v) for v in ins_m.values())
        merged = []
        for k in range(len(base) + 1):
            merged.extend(ins_t.get(k, []))
            merged.extend(ins_m.get(k, []))
            if k < len(base):
                merged.append(base[k])
        out = b"".join(merged)
        # conservation: base + both insertions, nothing lost, nothing dup
        assert len(merged) == len(base) + n_t + n_m, f"{path}: line count broke"
        for marker, what in ((b"88", "W88"), (b"89", "W89")):
            if path.endswith(".md"):
                assert b"PERPETUAL_N1_W89_PREREG.md" in out and \
                    b"PERPETUAL_N1_W88_PREREG.md" in out, \
                    f"{path}: canon W88/W89 wave bullets missing"
                break
            if path.endswith("perpetual_faces.py"):
                assert b"    88: {" in out and b"    89: {" in out, \
                    f"{path}: N1_BANDS 88/89 entries missing"
                break
            if path.endswith("perpetual_faces_n1.py"):
                assert b'89: {"batch": "PERPETUAL-N1-W89"' in out and \
                    b'88: {"batch": "PERPETUAL-N1-W88"' in out, \
                    f"{path}: WAVE_CONFIGS 88/89 entries missing"
                assert b"W89 materializer face" in out, \
                    f"{path}: W89 selftest leg missing"
                break
        assert b"<<<<<<<" not in out and b">>>>>>>" not in out, f"{path}: markers"
        if path.endswith(".py"):
            ast.parse(out)  # syntax gate on merged bytes
        with open(os.path.join(ROOT, path), "wb") as f:
            f.write(out)
        print(f"MERGED {path}: base={len(base)} +theirs={n_t}@{sorted(ins_t)} "
              f"+mine={n_m}@{sorted(ins_m)} -> {len(merged)} lines")
    print("merge OK (theirs-first at same anchor; AST green)")


def cmd_pool():
    try:
        s1 = gitb("show", f":1:{POOL}")
        s2 = gitb("show", f":2:{POOL}")
        s3 = gitb("show", f":3:{POOL}")
    except RuntimeError as e:
        print(f"no conflict stages for {POOL} ({e}); nothing to do")
        return 0
    b1, b2, b3 = lines_of(s1), lines_of(s2), lines_of(s3)
    assert b2[: len(b1)] == b1, "stage2 not base+append -- ABORT"
    assert b3[: len(b1)] == b1, "stage3 not base+append -- ABORT"
    t_tail, m_tail = b2[len(b1):], b3[len(b1):]
    union_tail = t_tail + [l for l in m_tail if l not in t_tail]
    for l in union_tail:  # r570 dict type-gate
        r = json.loads(l)
        assert isinstance(r, dict), f"non-dict jsonl line: {l[:120]!r}"
    out = b"".join(b1 + union_tail)
    with open(os.path.join(ROOT, POOL), "wb") as f:
        f.write(out)
    gitb("add", POOL)
    print(f"POOL union: base={len(b1)} +theirs_tail={len(t_tail)} "
          f"+mine_tail={len(m_tail)}(dedup->kept {len(union_tail)-len(t_tail)}) "
          f"-> {len(b1)+len(union_tail)} lines, all dict-gated")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "merge"
    if cmd == "merge":
        cmd_merge()
    elif cmd == "pool":
        cmd_pool()
    else:
        raise SystemExit(f"unknown subcommand {cmd}")
