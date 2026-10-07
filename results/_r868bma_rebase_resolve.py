# _r868bma_rebase_resolve.py -- 6-face rebase conflict resolver (r835/r794 canon).
# Stage semantics in rebase (r609/r782 family): stage2 = onto/origin side (bm-c),
# stage3 = replayed side (bm-a ours). Rolling regen/metering faces -> whole-file
# ts-newer-wins (tie -> stage3 ours per r140); REPORT regen faces -> stage3 ours
# (deterministic same-day regen, next S6 re-derives anyway).
# Blob reads via git cat-file with sha from ls-files -u (r648 law: :N: can empty-read).
import json, re, subprocess, sys

CONFLICTED = [
    "docs/daily_report/REPORT-2026-10-08.json",
    "docs/daily_report/REPORT-2026-10-08.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/futures_update_status.json",
    "results/token_usage.json",
]
# REPORT faces: deterministic same-day regen; ours (stage3) per r782 host-ref law.
TAKE_OURS_REGEN = {"docs/daily_report/REPORT-2026-10-08.json", "docs/daily_report/REPORT-2026-10-08.md"}
TS_KEYS = ["generated", "ts", "generated_at", "scanned_at", "updated", "now", "clock"]

def git(*args):
    r = subprocess.run(["git", *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}: {r.stderr[:300]}")
    return r.stdout

def stages():
    out = git("ls-files", "-u").decode("utf-8", "replace")
    m = {}
    for line in out.splitlines():
        parts = line.split("\t")
        meta, path = parts[0], parts[1]
        sha, stage = meta.split(" ")[1], meta.split(" ")[2]
        m.setdefault(path, {})[int(stage)] = sha
    return m

def blob(sha):
    return git("cat-file", "-p", sha)

def find_ts(data):
    # first matching ts-ish top-level or shallow-nested key
    try:
        j = json.loads(data)
    except Exception:
        m = re.search(rb'"(generated|ts|generated_at)"\s*:\s*"([^"]+)"', data)
        return (m.group(2).decode() if m else None)
    def walk(o, depth=0):
        if depth > 3 or not isinstance(o, dict):
            return None
        for k in TS_KEYS:
            if k in o and isinstance(o[k], str):
                return o[k]
        for v in o.values():
            r = walk(v, depth + 1)
            if r:
                return r
        return None
    return walk(j)

def main():
    st = stages()
    report = []
    for path in CONFLICTED:
        s2, s3 = st[path][2], st[path][3]
        b2, b3 = blob(s2), blob(s3)
        if path in TAKE_OURS_REGEN:
            winner, side = b3, "ours-regen"
        else:
            t2, t3 = find_ts(b2), find_ts(b3)
            if t2 is None and t3 is None:
                winner, side = b3, "ours-nots-tie"
            elif t3 is None:
                winner, side = b2, "theirs-nots"
            elif t2 is None:
                winner, side = b3, "ours-nots"
            else:
                winner, side = (b3, "ours-newer") if t3 >= t2 else (b2, "theirs-newer")
        # conflict-marker hard gate before write (r648/r804 law)
        if re.search(rb"^(<{7}|={7}|>{7})", winner, re.M):
            print(f"MARKER-POLLUTION {path} side={side} -- refusing")
            sys.exit(3)
        with open(path, "wb") as f:
            f.write(winner)
        t2s, t3s = (find_ts(b2) or "?"), (find_ts(b3) or "?")
        report.append({"path": path, "side": side, "ts_stage2_origin": t2s, "ts_stage3_ours": t3s,
                       "bytes": len(winner), "sha2": s2, "sha3": s3})
    print(json.dumps(report, indent=1))
    with open("results/_r868bma_rebase_resolve.json", "w") as f:
        json.dump(report, f, indent=1)

if __name__ == "__main__":
    main()
