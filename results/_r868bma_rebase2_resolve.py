# -*- coding: utf-8 -*-
"""r868 bm-a generalized rebase resolver: whole-file ts-newer-wins for ALL conflicted
faces (all are shared rolling/deterministic-regen faces; rebase stage2=origin side,
stage3=replayed ours per r609/r782; tie -> stage3 ours r140). Blob reads via
cat-file + ls-files -u shas (r648 law). Conflict-marker hard gate before write."""
import json, re, subprocess, sys

TS_KEYS = ["generated", "ts", "generated_at", "scanned_at", "updated", "now", "clock", "written_at"]

def git(*args):
    r = subprocess.run(["git", *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}: {r.stderr[:200]}")
    return r.stdout

def stages():
    out = git("ls-files", "-u").decode("utf-8", "replace")
    m = {}
    for line in out.splitlines():
        meta, path = line.split("\t")[0], line.split("\t")[1]
        sha, stage = meta.split(" ")[1], meta.split(" ")[2]
        m.setdefault(path, {})[int(stage)] = sha
    return m

def find_ts(data):
    m = re.search(rb'"(generated|ts|generated_at|scanned_at|written_at)"\s*:\s*"?([^"<\n]{4,40})', data)
    return m.group(2).decode("utf-8", "replace") if m else None

def main():
    st = stages()
    report = []
    for path, s in sorted(st.items()):
        b2, b3 = git("cat-file", "-p", s[2]), git("cat-file", "-p", s[3])
        t2, t3 = find_ts(b2), find_ts(b3)
        if t3 is None and t2 is None:
            winner, side = b3, "ours-nots-tie"
        elif t2 is None:
            winner, side = b3, "ours-nots"
        elif t3 is None:
            winner, side = b2, "theirs-nots"
        else:
            winner, side = (b3, "ours-newer") if t3 >= t2 else (b2, "theirs-newer")
        if re.search(rb"^(<{7}|={7}|>{7})", winner, re.M):
            print(f"MARKER-POLLUTION {path} side={side} -- refusing")
            sys.exit(3)
        with open(path, "wb") as f:
            f.write(winner)
        report.append({"path": path, "side": side, "ts2": t2, "ts3": t3, "bytes": len(winner)})
    json.dump(report, open("results/_r868bma_rebase2_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in report:
        print(f"{r['side']:<14} {r['path']}  (origin {r['ts2']} vs ours {r['ts3']})")

if __name__ == "__main__":
    main()
