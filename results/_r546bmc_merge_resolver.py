# -*- coding: utf-8 -*-
"""r546 bm-c close-window merge resolver -- 4-UU per-face directed ts
newer-wins (r709 law: directed fields, normalized parse; probe derived all
4 = ours newer: ours 13:58:35-14:00:56 vs theirs 13:48:12-13:52:20, genuine
two-machine S6 regen race vs bm-a r727 wave).
Lineage: results/_r727bma_merge_resolver.py (verbatim law set, face set
changed to this window's 4 UU faces). Stage-sourced :2:/:3: blobs per r515
law (python bytes face, never PS redirect, r706-A law; len>100 assertion
r710-B); write-then-reparse + readback ts equality assertions per r704 law.
Receipt -> results/_r546bmc_merge_resolve.json
"""
import subprocess, sys, os, json
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# (path, ts_keypath) -- side derived from stage probe, normalized parse
FACES = [
    ("results/_attrition_guard_scan.json", "ts"),       # ours 14:00:56 > theirs 13:52:20
    ("results/compute_audit.json", "latest/ts"),        # ours 13:58:35 > theirs 13:48:12
    ("results/regime_state.json", "updated"),           # ours 13:58:44 > theirs 13:48:22
    ("results/token_usage.json", "generated"),          # ours 14:00:30 > theirs 13:49:38
]
receipt = {"window": "r546 bm-c close merge 4-UU per-face newer-wins",
           "faces": {}, "law": "r709 directed fields / r515 stage-source / r706-A bytes / r704 readback"}


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
decisions = []
for path, key in FACES:
    ours = json.loads(stage_blob(2, path).decode("utf-8"))
    theirs = json.loads(stage_blob(3, path).decode("utf-8"))
    ov, tv = get_ts(ours, key), get_ts(theirs, key)
    side = "ours" if norm(ov) >= norm(tv) else "theirs"
    decisions.append((path, key, side, ov, tv))

# --- resolve: write decided side bytes, reparse, readback assert ------------
resolved = 0
for path, key, side, ov, tv in decisions:
    stage = 2 if side == "ours" else 3
    blob = stage_blob(stage, path)
    open(path, "wb").write(blob)
    j = json.loads(open(path, "rb").read().decode("utf-8"))
    ent = {"side": side, "bytes": len(blob), "ts_key": key,
           "ts": get_ts(j, key), "ours_ts": ov, "theirs_ts": tv}
    # readback equality: written ts must equal the source stage ts (r704)
    src = json.loads(stage_blob(stage, path).decode("utf-8"))
    assert get_ts(j, key) == get_ts(src, key), "readback ts drift %s (r704)" % path
    receipt["faces"][path] = ent
    resolved += 1

# zero conflict markers in resolved faces (r503 head-anchor semantics)
for path, key, side, ov, tv in decisions:
    b = open(path, "rb").read()
    for marker in (b"<<<<<<<", b">>>>>>>", b"|||||||"):
        assert marker not in b, "conflict marker residue in %s" % path

receipt["resolved"] = resolved
receipt["verdict"] = ("%d/%d per-face newer-wins all-ours (S6 regen race: ours 13:58-14:00 vs "
                      "bm-a r727 wave 13:48-13:52; probes re-derived from stages pre-resolve, "
                      "zero fork)" % (resolved, len(FACES)))
json.dump(receipt, open("results/_r546bmc_merge_resolve.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("resolver: %d/%d per-face newer-wins written+readback-verified, receipt written"
      % (resolved, len(FACES)))
for path, key, side, ov, tv in decisions:
    print("  %s -> %s (ours=%s theirs=%s)" % (path, side, ov, tv))
