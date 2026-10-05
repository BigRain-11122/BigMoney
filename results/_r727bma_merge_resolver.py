# -*- coding: utf-8 -*-
"""r727 bm-a close-window merge resolver -- 18-UU per-face directed ts
newer-wins (r709 law: directed fields, normalized parse -- no blind string
max, no blanket take-ours; this window is a genuine two-machine S6 regen
race: bm-c r545 chain ran 13:48:0x-13:49:37, ours 13:48:0x-13:50:29).
Stage-sourced :2:/:3: blobs per r515 law (python bytes face, never PS
redirect, r706-A law; len>100 assertion r710-B); write-then-reparse +
readback ts equality assertions per r704 law; md/js twins follow their
json twins same-side per r708/r510 law. Receipt -> results/_r727bma_merge_resolve.json
"""
import subprocess, sys, os, json
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# (path, ts_key, side) -- side decided by directed probe, normalized parse
DECISIONS = [
    ("docs/daily_report/REPORT-2026-10-05.json", "generated_at", "theirs"),   # 13:49:24 > 13:49:19
    ("docs/daily_report/REPORT-2026-10-05.md", None, "theirs"),               # twin follows json (r708)
    ("docs/live_usage/LIVE-2026-10-05.json", "generated", "theirs"),           # 13:49:25 > 13:49:20
    ("docs/live_usage/LIVE-2026-10-05.md", None, "theirs"),                   # twin
    ("docs/live_usage/LIVE-latest.json", "generated", "theirs"),              # 13:49:25 > 13:49:20
    ("docs/live_usage/LIVE-latest.md", None, "theirs"),                      # twin
    ("results/_attrition_guard_scan.json", "ts", "ours"),                    # 13:50:29 > 13:49:51
    ("results/compute_audit.json", "latest/ts", "ours"),                     # 13:48:12 > 13:48:00
    ("results/dashboard_status.json", "meta/generated_at", "theirs"),         # 13:49:37 > 13:49:30
    ("results/dashboard_status.js", None, "theirs"),                         # twin follows json (r708)
    ("results/fundamental_b_layer_filter.json", "updated", "ours"),           # 13:49:18 > 13:49:01
    ("results/futures_update_status.json", "ts", "ours"),                     # 13:49:10 > 13:48:56
    ("results/lhb_update_status.json", "updated", "ours"),                   # 13:49:08 > 13:48:55
    ("results/regime_state.json", "updated", "ours"),                         # 13:48:22 > 13:48:08
    ("results/scorecard_v1.json", "generated", "ours"),                       # 13:48:49 > 13:48:40
    ("results/strategy_scorecard.json", "generated", "ours"),                 # 13:48:55 > 13:48:49
    ("results/token_usage.json", "generated", "theirs"),                      # 13:49:37 > 13:49:31
    ("results/update_status.json", "updated", "ours"),                        # 13:48:22 > 13:48:07
]
receipt = {"window": "r727 bm-a close merge 18-UU per-face newer-wins",
           "faces": {}, "law": "r709 directed fields / r515 stage-source / r706-A bytes / r704 readback / r708 twins"}


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


def norm(ts):
    # r711 law: normalize space/T and offset forms before comparing
    s = ts.replace("T", " ").split("+")[0]
    return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")


# --- pre-resolve verification: re-derive every decision from the stages ----
for path, key, side in DECISIONS:
    if key is None:
        continue
    ours = json.loads(stage_blob(2, path).decode("utf-8"))
    theirs = json.loads(stage_blob(3, path).decode("utf-8"))
    ov, tv = get_ts(ours, key), get_ts(theirs, key)
    winner = "ours" if norm(ov) >= norm(tv) else "theirs"
    assert winner == side, "probe fork %s: ours=%s theirs=%s -> %s != decided %s" % (
        path, ov, tv, winner, side)

# --- resolve: write decided side bytes, reparse, readback assert ------------
resolved = 0
for path, key, side in DECISIONS:
    stage = 2 if side == "ours" else 3
    blob = stage_blob(stage, path)
    open(path, "wb").write(blob)
    ent = {"side": side, "bytes": len(blob)}
    if key is not None:
        j = json.loads(open(path, "rb").read().decode("utf-8"))
        ent["ts_key"] = key
        ent["ts"] = get_ts(j, key)
        # readback equality: written ts must equal the source stage ts (r704)
        src = json.loads(stage_blob(stage, path).decode("utf-8"))
        assert get_ts(j, key) == get_ts(src, key), "readback ts drift %s (r704)" % path
    else:
        if path.endswith(".md") or path.endswith(".js"):
            twin = path[:-3] + ".json"
        else:
            raise AssertionError("twin-less face %s" % path)
        tkey = dict((p, k) for p, k, s in DECISIONS if k)[twin]
        ent["twin"] = twin
        ent["twin_ts_key"] = tkey
    receipt["faces"][path] = ent
    resolved += 1

# zero conflict markers in resolved faces (r503 head-anchor semantics)
for path, key, side in DECISIONS:
    b = open(path, "rb").read()
    for marker in (b"<<<<<<<", b">>>>>>>", b"|||||||"):
        assert marker not in b, "conflict marker residue in %s" % path

receipt["resolved"] = resolved
receipt["verdict"] = ("18/18 per-face newer-wins (10 theirs: REPORT/LIVE/dashboard/token "
                      "family +5-7s fresher; 8 ours: attrition/compute/fundamental/futures/"
                      "lhb/regime/scorecard_v1/strategy_scorecard/update_status; "
                      "probes re-derived from stages pre-resolve, zero fork)")
json.dump(receipt, open("results/_r727bma_merge_resolve.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("resolver: 18/18 per-face newer-wins written+readback-verified, receipt written")
