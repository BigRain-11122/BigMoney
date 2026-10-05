# -*- coding: utf-8 -*-
"""r726 bm-a close-window merge resolver -- 14-UU take-ours (ALL OURS-NEW by
directed ts probe: our S6 regeneration 13:21-13:24 vs bm-c r543 S6 13:19-13:20,
verified per-face incl. the compute_audit nested /latest/ts deep probe).
Stage-sourced :2: blobs per r515 law (python bytes face, never PS redirect,
r706-A law; len>100 assertion r710-B); write-then-reparse + readback ts
equality assertions per r704 law; md twins follow their json twins same-side
per r708/r510 law. Receipt -> results/_r726bma_merge_resolve.json
"""
import subprocess, sys, os, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

FACES = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/daily_report/REPORT-2026-10-05.md",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
# directed ts probes (ours, theirs) verified pre-resolve; ours newer on all 14
PROBES = {
    "docs/daily_report/REPORT-2026-10-05.json": ("generated_at", "2026-10-05 13:23:34", "2026-10-05 13:20:28"),
    "docs/live_usage/LIVE-2026-10-05.json": ("generated", "2026-10-05T13:23:35", "2026-10-05T13:20:29"),
    "docs/live_usage/LIVE-latest.json": ("generated", "2026-10-05T13:23:35", "2026-10-05T13:20:29"),
    "results/_attrition_guard_scan.json": ("ts", "2026-10-05T13:24:41+08:00", "2026-10-05T13:20:54+08:00"),
    "results/compute_audit.json": ("latest/ts", "2026-10-05 13:21:30", "2026-10-05 13:19:29"),
    "results/fundamental_b_layer_filter.json": ("updated", "2026-10-05 13:23:33", "2026-10-05 13:20:13"),
    "results/futures_update_status.json": ("ts", "2026-10-05T13:23:06", "2026-10-05T13:20:09"),
    "results/lhb_update_status.json": ("updated", "2026-10-05 13:23:05", "2026-10-05 13:20:08"),
    "results/regime_state.json": ("updated", "2026-10-05 13:21:40", "2026-10-05 13:19:38"),
    "results/token_usage.json": ("generated", "2026-10-05 13:23:45", "2026-10-05 13:20:29"),
    "results/update_status.json": ("updated", "2026-10-05 13:21:39", "2026-10-05 13:19:37"),
}
receipt = {"window": "r726 bm-a close merge 14-UU take-ours", "faces": {}, "probes": PROBES}


def stage_blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    assert r.returncode == 0, "stage read fail %s" % path
    b = r.stdout
    assert len(b) > 100, "stage blob suspiciously empty %s (%d bytes)" % (path, len(b))
    return b


def get_ts(j, keypath):
    cur = j
    for k in keypath.split("/"):
        cur = cur[k]
    return cur


resolved = 0
for f in FACES:
    ours = stage_blob(2, f)
    theirs = stage_blob(3, f)  # fetched for the receipt byte counts only
    open(f, "wb").write(ours)  # python bytes write (r706-A)
    if f.endswith(".json"):
        j = json.loads(open(f, "rb").read().decode("utf-8"))
        if f in PROBES:
            key, ov, tv = PROBES[f]
            got = get_ts(j, key)
            assert got == ov, "readback ts drift %s: %r != %r (r704 law)" % (f, got, ov)
            receipt["faces"][f] = {"side": "ours", "ts_key": key, "ts": got,
                                   "bytes_ours": len(ours), "bytes_theirs": len(theirs)}
        else:
            receipt["faces"][f] = {"side": "ours", "bytes_ours": len(ours),
                                   "bytes_theirs": len(theirs), "reparse": "ok"}
    else:
        # md twin: reparse-free text face; same-side lock with its json twin (r708)
        twin = f[:-3] + ".json"
        assert twin in PROBES or twin in FACES, "twin missing %s" % twin
        receipt["faces"][f] = {"side": "ours (md twin follows json r708)",
                               "bytes_ours": len(ours), "bytes_theirs": len(theirs)}
    resolved += 1

# zero conflict markers in resolved faces (r503 head-anchor semantics)
for f in FACES:
    b = open(f, "rb").read()
    for marker in (b"<<<<<<<", b">>>>>>>", b"|||||||"):
        assert marker not in b, "conflict marker residue in %s" % f

receipt["resolved"] = resolved
receipt["verdict"] = "14/14 take-ours OURS-NEW (directed ts probes verified pre-resolve; stage-sourced r515; python-bytes r706-A; readback r704)"
json.dump(receipt, open("results/_r726bma_merge_resolve.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("resolver: 14/14 take-ours written+readback-verified, receipt written")
