import json, re, subprocess, sys

FILES_JSON = [
    "results/autofill_state.bm-a.json",
    "results/crash_fuse.bm-a.json",
    "results/crash_fuse.json",
    "results/runnable_pool.bm-a.json",
    "results/saturation_engine/face_bm-a.json",
    "results/saturation_engine/state_bm-a.json",
]
FILES_JSONL = [
    "results/saturation_engine/history_bm-a.jsonl",
    "results/x2_watch_log.jsonl",
]
TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

def stage(path, n):
    return subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True).stdout

def max_ts(text):
    tss = TS_RE.findall(text.decode("utf-8", "replace"))
    return max(tss) if tss else ""

for f in FILES_JSON:
    ours, theirs = stage(f, 2), stage(f, 3)
    try:
        json.loads(ours)  # sanity: ours parseable
    except Exception:
        ours_is_json = False
    else:
        ours_is_json = True
    pick = ours
    reason = "ours"
    if ours_is_json:
        try:
            json.loads(theirs)
            to, tt = max_ts(ours), max_ts(theirs)
            if tt > to:
                pick, reason = theirs, f"theirs newer ({tt} > {to})"
        except Exception:
            pass
    else:
        # ours unparseable -> prefer theirs if parseable
        try:
            json.loads(theirs)
            pick, reason = theirs, "ours unparseable"
        except Exception:
            pass
    open(f, "wb").write(pick)
    print(f"JSON  {f}: {reason} ({len(pick)}B)")

for f in FILES_JSONL:
    ours = stage(f, 2).decode("utf-8", "replace").splitlines()
    theirs = stage(f, 3).decode("utf-8", "replace").splitlines()
    seen = set(ours)
    extra = [l for l in theirs if l not in seen and l.strip()]
    merged = [l for l in ours if l.strip()] + extra
    body = "\n".join(merged) + ("\n" if merged else "")
    open(f, "w", encoding="utf-8", newline="\n").write(body)
    print(f"JSONL {f}: ours {len(ours)} + theirs-new {len(extra)} = {len(merged)} lines")
print("DONE")
