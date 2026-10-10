# -*- coding: utf-8 -*-
# r855 bm-c rebase-race resolver: 31-UU same-window S6 re-derive face family
# Law: shared regen faces -> take THEIRS (origin/bm-b r864 stands, zero regression,
# next chain re-derives); append-only x2_watch_log.jsonl -> UNION (base + both appends).
import subprocess, io, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

uu = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                    cwd=ROOT, capture_output=True, text=True).stdout.split()
assert len(uu) == 31, ("UU count drift", len(uu))

def stage(n, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)],
                       cwd=ROOT, capture_output=True)
    return r.stdout.decode("utf-8", "replace").splitlines()

union_files = [p for p in uu if p.endswith(".jsonl")]
take_files = [p for p in uu if p not in union_files]
assert len(union_files) == 1 and "x2_watch_log" in union_files[0], union_files

for p in take_files:
    subprocess.run(["git", "checkout", "--theirs", "--", p], cwd=ROOT, check=True)

for p in union_files:
    base = stage(1, p); ours = stage(2, p); theirs = stage(3, p)
    b = len(base)
    assert ours[:b] == base and theirs[:b] == base, ("base prefix drift", p)
    o_new = [l for l in ours[b:] if l not in theirs[b:]]
    merged = base + theirs[b:] + o_new
    body = "\n".join(merged) + "\n"
    io.open(ROOT + "\\" + p.replace("/", "\\"), "w", encoding="utf-8", newline="").write(body)
    print("UNION %s: base=%d theirs+=%d ours-new=%d -> %d" % (p, b, len(theirs) - b, len(o_new), len(merged)))

subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
print("RESOLVED take-theirs=%d union=%d staged" % (len(take_files), len(union_files)))
