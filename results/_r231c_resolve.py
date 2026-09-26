# r231c (bm-b round 231): stash-pop UU batch resolver (11 files), recipes per
# bigmoney-conflict-resolve classifier output (0 UNKNOWN). Stage 2 = HEAD side
# (origin lineage, bm-a R232 S6 outputs ~07:50-07:51), stage 3 = stash side
# (bm-b working tree, predecessor S6 outputs ~07:24 + 07:50:02 tick).
#   ledgers (compute_audit history / regime_state history+transitions /
#   autofill launches): union dedupe by canonical json, sort by ts ascending
#   (producer append-at-end order), keep producer cap (200 / 50), take-new
#   scalar state by inner ts; EOL = CRLF mirror of bm-b producer (r223).
#   snapshots + dashboard_status.js: take-side WHOLE BYTES of the newer side
#   (r209/R213: byte fidelity, no resolver re-serialization); .js side follows
#   the .json twin meta.generated_at (r226 law, top-level ts absent).
# Parse-verify before write-back (r185). Blob reads via subprocess bytes (r209).
import json
import subprocess

def raw_stage(path, stage):
    out = subprocess.run(["git", "ls-files", "-u", path],
                         capture_output=True, text=True).stdout.split()
    for i in range(0, len(out) - 3, 4):
        if out[i + 2] == str(stage):
            return subprocess.run(["git", "cat-file", "blob", out[i + 1]],
                                  capture_output=True).stdout
    raise SystemExit(f"stage {stage} missing: {path}")

def canon(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)

def union_sorted(a, b, cap):
    seen, union = set(), []
    for e in list(a) + list(b):
        k = canon(e)
        if k not in seen:
            seen.add(k)
            union.append(e)
    union.sort(key=lambda e: str(e.get("ts", e.get("updated", ""))))
    return union, union[-cap:] if cap else union

def write_json(path, obj, crlf):
    body = json.dumps(obj, ensure_ascii=False, indent=1)
    with open(path, "w", encoding="utf-8",
              newline="\r\n" if crlf else "\n") as fh:
        fh.write(body + "\n")
    json.loads(open(path, encoding="utf-8").read())  # parse-verify (r185)

report = []

# ---- rolling ledgers -------------------------------------------------------
for path, ledger_keys, cap, state_cmp in [
    ("results/compute_audit.json", ["history"], 200, "latest"),
    ("results/regime_state.json", ["history", "transitions"], None, None),
]:
    o_raw, t_raw = raw_stage(path, 2), raw_stage(path, 3)
    o, t = json.loads(o_raw), json.loads(t_raw)
    merged = dict(o)
    for key in ledger_keys:
        a, b = o.get(key, []), t.get(key, [])
        union, kept = union_sorted(a, b, cap)
        merged[key] = kept
        report.append(f"{path}::{key}: |A|={len(a)} |B|={len(b)} "
                      f"|AuB|={len(union)} kept={len(kept)}")
    if state_cmp:
        oa, ta = str(o[state_cmp].get("ts", "")), str(t[state_cmp].get("ts", ""))
        pick = "ours" if oa >= ta else "theirs"  # tie -> ours/HEAD (r140)
        merged[state_cmp] = (o if oa >= ta else t)[state_cmp]
        report.append(f"{path}::{state_cmp}: ours={oa} theirs={ta} -> {pick}")
    crlf = t_raw.count(b"\r\n") > 0  # bm-b producer mirror (r223)
    write_json(path, merged, crlf)
    report.append(f"{path}: eol={'CRLF' if crlf else 'LF'}")

# ---- mixed-dict+ledger: autofill_state (same recipe as _r231b) --------------
path = "results/autofill_state.json"
o_raw, t_raw = raw_stage(path, 2), raw_stage(path, 3)
o, t = json.loads(o_raw), json.loads(t_raw)
union, kept = union_sorted(o["launches"], t["launches"], 50)
oa, ta = str(o["last_tick"].get("ts", "")), str(t["last_tick"].get("ts", ""))
last_tick = o["last_tick"] if oa >= ta else t["last_tick"]  # tie -> ours (r140)
merged = {"launches": kept, "last_tick": last_tick}
assert isinstance(last_tick, dict), "last_tick must stay dict (r203)"
crlf = t_raw.count(b"\r\n") > 0
write_json(path, merged, crlf)
report.append(f"{path}: union {len(o['launches'])}+{len(t['launches'])} -> "
              f"{len(union)} kept {len(kept)}; last_tick ours={oa} "
              f"theirs={ta} -> {'ours' if oa >= ta else 'theirs'}; "
              f"pid17616={'yes' if any(e.get('pid')==17616 for e in kept) else 'NO'}; "
              f"eol={'CRLF' if crlf else 'LF'}")

# ---- snapshots: take-side whole bytes (newest wins) -------------------------
SNAP_TS_KEY = {
    "results/dashboard_status.json": ("meta", "generated_at"),
    "results/fundamental_b_layer_filter.json": ("updated",),
    "results/futures_update_status.json": ("ts",),
    "results/heat_update_status.json": ("updated",),
    "results/lhb_update_status.json": ("updated",),
    "results/token_usage.json": ("generated",),
    "results/update_status.json": ("updated",),
}
for path, keypath in SNAP_TS_KEY.items():
    o_raw, t_raw = raw_stage(path, 2), raw_stage(path, 3)
    def ts_of(raw):
        d = json.loads(raw)
        for k in keypath[:-1]:
            d = d[k]
        return str(d[keypath[-1]])
    oa, ta = ts_of(o_raw), ts_of(t_raw)
    winner = o_raw if oa >= ta else t_raw  # tie -> ours/HEAD (r140)
    with open(path, "wb") as fh:
        fh.write(winner)
    json.loads(winner.decode("utf-8"))  # parse-verify (r185)
    report.append(f"{path}: take-{'ours' if oa >= ta else 'theirs'} "
                  f"({oa} vs {ta}) whole bytes")

# ---- dashboard_status.js: side follows .json twin (r226) -------------------
path = "results/dashboard_status.js"
o_raw, t_raw = raw_stage(path, 2), raw_stage(path, 3)
twin = json.loads(raw_stage("results/dashboard_status.json", 2))
oa = str(twin["meta"]["generated_at"])
twin_t = json.loads(raw_stage("results/dashboard_status.json", 3))
ta = str(twin_t["meta"]["generated_at"])
winner = o_raw if oa >= ta else t_raw
with open(path, "wb") as fh:
    fh.write(winner)
report.append(f"{path}: take-{'ours' if oa >= ta else 'theirs'} via twin "
              f"meta.generated_at ({oa} vs {ta}) whole bytes, wrapper intact: "
              f"{winner.lstrip().startswith(b'window.DASH_DATA')}")

print("\n".join(report))
