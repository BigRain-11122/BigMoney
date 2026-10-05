# -*- coding: utf-8 -*-
"""r728 bm-a close-window merge resolver -- 14-UU per-face directed ts
newer-wins (r709 law: directed fields, normalized parse) + compute_audit
rolling union (r725 canon: base=newer side, union history rows zero-loss).
This window is a genuine two-machine S6 regen race: ours 14:11-14:13 vs
theirs 14:10:55-14:11:53 (origin advanced 2 commits mid-push).
Stage-sourced :2:/:3: blobs per r515 law (python bytes face, never PS
redirect, r706-A law; len>100 assertion r710-B); write-then-reparse +
readback ts equality assertions per r704 law; md twins follow their json
twins same-side per r708/r510 law. Receipt -> results/_r728bma_merge_resolve.json
"""
import subprocess, sys, os, json
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# (path, ts_key, side) -- side decided by directed probe, normalized parse
DECISIONS = [
    ("docs/daily_report/REPORT-2026-10-05.json", "generated_at", "ours"),   # 14:12:30 > 14:11:31
    ("docs/daily_report/REPORT-2026-10-05.md", None, "ours"),               # twin follows json (r708)
    ("docs/live_usage/LIVE-2026-10-05.json", "generated", "ours"),           # 14:12:31 > 14:11:32
    ("docs/live_usage/LIVE-2026-10-05.md", None, "ours"),                   # twin
    ("docs/live_usage/LIVE-latest.json", "generated", "ours"),              # 14:12:31 > 14:11:32
    ("docs/live_usage/LIVE-latest.md", None, "ours"),                      # twin
    ("results/_attrition_guard_scan.json", "ts", "ours"),                    # 14:13:22 > 14:11:53
    ("results/fundamental_b_layer_filter.json", "updated", "ours"),           # 14:12:29 > 14:11:16
    ("results/futures_update_status.json", "ts", "ours"),                     # 14:12:03 > 14:11:11
    ("results/lhb_update_status.json", "updated", "ours"),                   # 14:12:02 > 14:11:11
    ("results/regime_state.json", "updated", "ours"),                         # 14:11:14 > 14:11:04 (history identical)
    ("results/token_usage.json", "generated", "ours"),                       # 14:12:42 > 14:11:33 (machines equal both sides)
    ("results/update_status.json", "updated", "ours"),                        # 14:11:11 > 14:11:03
]
UNION_FACE = "results/compute_audit.json"  # rolling union, r725 canon
receipt = {"window": "r728 bm-a close merge 14-UU per-face newer-wins + compute_audit rolling union",
           "faces": {}, "law": "r709 directed fields / r515 stage-source / r706-A bytes / r704 readback / r708 twins / r725 rolling-union"}


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
        continue  # twin faces (md/js) follow their json twin; not probed here (r727 bloodline guard)
    try:
        ours = json.loads(stage_blob(2, path).decode("utf-8"))
    except Exception as e:
        import sys as _sys
        print("PRE-VERIFY FAIL face:", repr(path), "| exc:", repr(e)[:120], file=_sys.stderr)
        raise
    theirs = json.loads(stage_blob(3, path).decode("utf-8"))
    ov, tv = get_ts(ours, key), get_ts(theirs, key)
    winner = "ours" if norm(ov) >= norm(tv) else "theirs"
    assert winner == side, "probe fork %s: ours=%s theirs=%s -> %s != decided %s" % (
        path, ov, tv, winner, side)

# --- compute_audit rolling union decision (pre-verify) ----------------------
co = json.loads(stage_blob(2, UNION_FACE).decode("utf-8"))
ct = json.loads(stage_blob(3, UNION_FACE).decode("utf-8"))
assert co["latest"]["ts"] == "2026-10-05 14:11:00" and ct["latest"]["ts"] == "2026-10-05 14:10:55", \
    "compute_audit latest ts drift vs probe"
o_ids = {json.dumps(h, sort_keys=True): h for h in co["history"]}
t_ids = {json.dumps(h, sort_keys=True): h for h in ct["history"]}
overlap = len(set(o_ids) & set(t_ids))
assert len(o_ids) == 201 and len(t_ids) == 201 and overlap == 200, \
    "compute_audit row sets drift: %d/%d/%d" % (len(o_ids), len(t_ids), overlap)
merged_rows = list(o_ids.values()) + [h for k, h in t_ids.items() if k not in o_ids]
merged_rows.sort(key=lambda h: h["ts"])
receipt["faces"][UNION_FACE] = {"side": "ROLLING-UNION", "base": "ours (latest 14:11:00 newer)",
                                "rows_ours": 201, "rows_theirs": 201, "overlap": overlap,
                                "union_rows": len(merged_rows), "theirs_only_row": "14:10:55 preserved",
                                "latest_ts": co["latest"]["ts"]}

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
        # twin readback: md must carry the same decided side (byte equality with stage)
        assert open(path, "rb").read() == stage_blob(stage, path), "twin byte drift %s" % path
    receipt["faces"][path] = ent
    resolved += 1

# --- compute_audit union write + readback -----------------------------------
co_out = dict(co)
co_out["history"] = merged_rows
co_out["latest"] = co["latest"]  # base = ours (ts-newer)
open(UNION_FACE, "wb").write(json.dumps(co_out, ensure_ascii=False, indent=1).encode("utf-8"))
rb = json.loads(open(UNION_FACE, "rb").read().decode("utf-8"))
assert len(rb["history"]) == 202, "compute_audit union readback row count drift"
assert rb["latest"]["ts"] == "2026-10-05 14:11:00", "compute_audit latest readback drift"
assert [h["ts"] for h in rb["history"]][-2:] == ["2026-10-05 14:10:55", "2026-10-05 14:11:00"], \
    "compute_audit union tail readback drift"
resolved += 1

# zero conflict markers in resolved faces (r503 head-anchor semantics)
all_faces = [p for p, k, s in DECISIONS] + [UNION_FACE]
for path in all_faces:
    b = open(path, "rb").read()
    for marker in (b"<<<<<<<", b">>>>>>>", b"|||||||"):
        assert marker not in b, "conflict marker residue in %s" % path

receipt["resolved"] = resolved
receipt["verdict"] = ("14/14: 13 per-face ours-newer (directed ts probes re-derived "
                      "from stages pre-resolve, zero fork; md twins byte-equal "
                      "readback) + 1 compute_audit rolling union 201+201->202 rows "
                      "(200 overlap, theirs-only 14:10:55 observation preserved, "
                      "latest=ours 14:11:00)")
json.dump(receipt, open("results/_r728bma_merge_resolve.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("resolver: 14/14 (13 take-ours directed-newer + 1 rolling union) written+readback-verified, receipt written")
