# r333 bm-c rebase conflict resolver: shared same-day idempotent derive faces ->
# wall-clock-newer side wins (r505 law); no-ts face -> ours (origin host authority).
import re, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def g(args):
    return subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")

unm = [x for x in g(["diff", "--name-only", "--diff-filter=U"]).stdout.splitlines() if x]
print("UNMERGED n =", len(unm))
if not unm:
    print("no conflicts to resolve")
    sys.exit(0)

TS = re.compile(r'"(?:generated|generated_at|ts|updated|updated_at|asof|timestamp)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ][\d:.]+)')

def side_ts(stage, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{stage}:{path}"],
                       capture_output=True)
    txt = r.stdout.decode("utf-8", errors="replace")
    hits = TS.findall(txt)
    return max(hits) if hits else ""

for path in unm:
    o = side_ts(":2:", path)   # ours   = origin (bm-a host side)
    t = side_ts(":3:", path)   # theirs = my replayed commit
    side = "--theirs" if (t and (not o or t > o)) else "--ours"
    g(["checkout", side, "--", path])
    g(["add", path])
    print(f"{path} | ours={o} | theirs={t} -> {side}")
print("resolver done")
