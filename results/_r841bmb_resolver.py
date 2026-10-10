"""r841 rebase resolver: 18 UU regen faces -> embedded-ts newer-wins (r838
push-race law). During rebase stage2 = new base (origin/bm-a side), stage3 =
replayed commit (bm-b r841 side). For each UU file: parse embedded
timestamps from both stages; newer wins; equal/unparseable -> stage3 (the
replayed change is the later logical write). Zero conflict markers left."""
import json
import re
import subprocess as sp
import sys

TS_KEYS = ("ts", "generated_at", "generated", "updated_at", "updated", "asof",
           "written_at", "now")
ISO_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")


def stage_bytes(path, stage):
    return sp.run(["git", "show", f":{stage}:{path}"], capture_output=True
                  ).stdout


def ts_of(data: bytes):
    try:
        d = json.loads(data.decode("utf-8"))
    except Exception:
        hits = ISO_RE.findall(data.decode("utf-8", "replace"))
        return max((h[0] if isinstance(h, tuple) else h for h in hits),
                   default="")
    best = ""
    stack = [d]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, str) and k in TS_KEYS and len(v) >= 10:
                    if v > best:
                        best = v
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(x, list):
            stack.extend(x)
    return best


def main():
    out = sp.run(["git", "diff", "--name-only", "--diff-filter=U"],
                 capture_output=True, text=True).stdout.split()
    resolved = {"stage2_newer": [], "stage3_newer": [], "fallback3": []}
    for path in out:
        b2, b3 = stage_bytes(path, 2), stage_bytes(path, 3)
        if b2 == b3:
            open(path, "wb").write(b3)
            resolved["stage3_newer"].append(path)
            continue
        t2, t3 = ts_of(b2), ts_of(b3)
        if t2 and t3:
            winner = b2 if t2 > t3 else b3
            key = "stage2_newer" if t2 > t3 else "stage3_newer"
        else:
            winner, key = b3, "fallback3"
        open(path, "wb").write(winner)
        resolved[key].append(path)
        sp.run(["git", "add", "--", path], check=True)
    for k, v in resolved.items():
        print(k, len(v))
        for p in v:
            print("  ", p)
    # verify no conflict markers remain in worktree copies
    bad = []
    for path in out:
        if b"<<<<<<< " in open(path, "rb").read()[:200000]:
            bad.append(path)
    if bad:
        print("CONFLICT MARKERS REMAIN:", bad)
        return 1
    print("resolver done: all UU resolved, zero markers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
