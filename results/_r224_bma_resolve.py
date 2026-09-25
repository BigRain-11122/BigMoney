# -*- coding: utf-8 -*-
"""R224 bm-a push-collision resolver (bm-b r227 same-window S6 mirror, 9th演).

Classifier: 11 UU, 0 UNKNOWN. Recipes per skill SKILL.md:
  - 9 snapshots / js-wrapper / regime(history identical) -> take-mine whole bytes
    (mine newer on every ts face: 06:15:xx vs 06:11-06:12:xx; js twin .json
    meta.generated_at governs per bm-b r226 addendum law)
  - compute_audit.json (rolling-ledger): history union 201+201 -> 202 zero-loss
    (dedupe by full-entry identity), latest take-new (mine ts 06:14:51)
  - autofill_state.json (mixed-dict+ledger): launches union 50+50 -> 50 (identical
    sets), last_tick SAME-SECOND tie 06:10:01 -> HEAD (bm-b, r140 law, whole dict),
    isinstance(last_tick, dict) assert, CRLF producer mirror (indent=1)
  - byte style: both rebuild targets CRLF / no BOM (mirrored from stage-2 blobs)
Parse-verify before add (r185). Zero-loss anchors printed.
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show :{stage}:{path} failed")
    return r.stdout


TAKE_MINE = [
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/regime_state.json",   # histories identical (2==2), state take-new by updated ts
]
anchors = {}

# ---- 1) take-mine whole bytes (producer format preserved verbatim) ----
for p in TAKE_MINE:
    b = blob(3, p)
    with open(p, "wb") as f:
        f.write(b)
    json.loads(b.decode("utf-8-sig")) if p.endswith(".json") else None
    # parse-verify (js wrapper: strip wrapper prefix for parse)
    if p.endswith(".js"):
        body = b.decode("utf-8", errors="replace")
        assert body.lstrip().startswith("window.DASH_DATA"), f"wrapper lost in {p}"
        payload = body.split("=", 1)[1].rsplit(";", 1)[0].strip()
        json.loads(payload)
    anchors[p] = f"take-mine bytes={len(b)}"

# ---- 2) compute_audit.json: rolling-ledger union + latest take-new ----
p = "results/compute_audit.json"
a = json.loads(blob(2, p).decode("utf-8-sig"))
b = json.loads(blob(3, p).decode("utf-8-sig"))
ha, hb = a["history"], b["history"]
seen, union = set(), []
for e in ha + hb:
    k = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        union.append(e)
union.sort(key=lambda e: e.get("ts", ""))
n_union = len(union)
assert n_union == 202, f"ca union expected 202 got {n_union}"
latest = a["latest"] if a["latest"].get("ts", "") >= b["latest"].get("ts", "") else b["latest"]
assert latest.get("ts") == "2026-09-26 06:14:51", "latest take-new face"
merged = {"latest": latest, "history": union}
txt = json.dumps(merged, ensure_ascii=False, indent=2).replace("\n", "\r\n")
with open(p, "wb") as f:
    f.write(txt.encode("utf-8"))
json.loads(open(p, encoding="utf-8").read())          # parse-verify
anchors[p] = f"union {len(ha)}+{len(hb)}->{n_union} zero-loss; latest.ts={latest['ts']} take-new"

# ---- 3) autofill_state.json: launches union + last_tick tie->HEAD ----
p = "results/autofill_state.json"
a = json.loads(blob(2, p).decode("utf-8-sig"))   # HEAD/origin (bm-b)
b = json.loads(blob(3, p).decode("utf-8-sig"))   # mine (bm-a replay)
la, lb = a["launches"], b["launches"]
seen, union = set(), []
for e in la + lb:
    k = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        union.append(e)
union.sort(key=lambda e: e.get("ts", ""))
union = union[-50:]                                     # cap50 rolling window (R215)
lt_h, lt_m = a.get("last_tick"), b.get("last_tick")
if (lt_h or {}).get("ts", "") >= (lt_m or {}).get("ts", ""):
    last_tick = lt_h                                    # same-second tie -> HEAD (r140)
else:
    last_tick = lt_m
assert isinstance(last_tick, dict), "last_tick not dict (r203 law)"
assert last_tick.get("machine") == "bm-b", f"tie->HEAD face broken: {last_tick}"
note = ("r224 union (bm-b r227 same-window push collision, 9th演): launches "
        f"{len(la)}+{len(lb)}->{len(union)} identical-set dedupe zero-loss; "
        "last_tick same-second 06:10:01 tie -> HEAD/bm-b whole-dict (r140); "
        "CRLF indent=1 producer mirror (bm-b r223 law)")
merged = {"last_tick": last_tick, "launches": union, "rebase_union_note": note}
txt = json.dumps(merged, ensure_ascii=False, indent=1).replace("\n", "\r\n")
with open(p, "wb") as f:
    f.write(txt.encode("utf-8"))
chk = json.loads(open(p, encoding="utf-8").read())
assert isinstance(chk["last_tick"], dict) and len(chk["launches"]) == len(union)
anchors[p] = (f"launches {len(la)}+{len(lb)}->{len(union)}; last_tick ts="
              f"{chk['last_tick']['ts']} machine={chk['last_tick']['machine']} tie->HEAD")

# ---- 4) stage all resolved files ----
all_files = TAKE_MINE + ["results/compute_audit.json", "results/autofill_state.json"]
r = subprocess.run(["git", "add"] + all_files, capture_output=True, text=True)
assert r.returncode == 0, r.stderr
print("staged", len(all_files), "files")
for k, v in anchors.items():
    print("ANCHOR", k.split("/")[-1], "|", v)
print("RESOLVE OK -- run: git rebase --continue")
