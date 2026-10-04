# -*- coding: utf-8 -*-
# r667 bm-b merge resolver (14 UU push-race closeout, bm-a r673 window)
# Recipes per bigmoney-conflict-resolve SKILL.md + classifier output:
#   rolling-ledger (compute_audit/regime_state): (ts,canon) union zero-loss + take-new scalars
#   token_usage: per-key machines union by entry ts (r456 side-pick>0 law) + scalars take-new
#   snapshots: take-new whole-face by embedded ts (tie -> HEAD per r140)
#   docs pairs (.json+.md twins): same side as json verdict, exact blob bytes
# Laws: r657(2) HEAD:/MERGE_HEAD: direct blob take; r461 ts_norm before compare;
#       r185 reparse before add; r664 marker check content-based.
import json, subprocess, io, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def blob(ref, path):
    p = subprocess.run(["git", "show", ref + ":" + path], capture_output=True)
    assert p.returncode == 0, ("blob fail", ref, path)
    return p.stdout

def ts_norm(v):
    return str(v).replace("T", " ")[:19]

def canon(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)

def take_side(path, side):
    ref = "HEAD" if side == "ours" else "MERGE_HEAD"
    data = blob(ref, path)
    with io.open(path, "wb") as f:
        f.write(data)
    return data

report = {"probe": "r667bmb_merge_resolve", "faces": {}, "verify": {}}

# --- sanity: UU set exactly the expected 14 ---
p = subprocess.run(["git", "status", "--porcelain"], capture_output=True)
uu = sorted(l[3:].strip() for l in p.stdout.decode("utf-8", "replace").splitlines()
           if l[:2] in ("UU", "AA"))
expect = sorted([
    "docs/daily_report/REPORT-2026-10-04.json", "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json", "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json", "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/lhb_update_status.json", "results/regime_state.json",
    "results/token_usage.json", "results/update_status.json"])
assert uu == expect, "UU set drifted: %s" % (uu,)

# --- snapshot faces: ts-probed verdicts (probe evidence _r667bmb_uu_probe.py) ---
SNAP = {
    "results/_attrition_guard_scan.json": "theirs",        # 11:27:29 > 11:26:42
    "results/fundamental_b_layer_filter.json": "theirs",   # 11:26:06 > 11:26:04
    "results/futures_update_status.json": "ours",          # 11:25:59 > 11:25:41
    "results/lhb_update_status.json": "ours",              # 11:25:58 > 11:25:40
    "results/update_status.json": "ours",                  # 11:25:14 > 11:24:58
    "docs/daily_report/REPORT-2026-10-04.json": "theirs",   # gen 11:26:25 > 11:26:24
    "docs/daily_report/REPORT-2026-10-04.md": "theirs",
    "docs/live_usage/LIVE-2026-10-04.json": "theirs",      # gen 11:26:26 > 11:26:25
    "docs/live_usage/LIVE-2026-10-04.md": "theirs",
    "docs/live_usage/LIVE-latest.json": "theirs",
    "docs/live_usage/LIVE-latest.md": "theirs",
}
# guard: re-derive each verdict from live blobs (no hard-trust of probe)
for path, side in SNAP.items():
    if path.endswith(".json"):
        o = json.loads(blob("HEAD", path).decode("utf-8", "replace"))
        t = json.loads(blob("MERGE_HEAD", path).decode("utf-8", "replace"))
        ko = next((k for k in ("updated", "generated", "generated_at", "ts", "now")
                   if k in o), None)
        kt = ko
        no = ts_norm(o.get(ko, ""))
        nt = ts_norm(t.get(kt, ""))
        derived = "ours" if no >= nt else "theirs"
        assert derived == side, ("snapshot verdict drift", path, no, nt, derived, side)
    take_side(path, side)
    report["faces"][path] = "take-" + side

# --- compute_audit: history (ts,canon) union zero-loss + latest take-new ---
o = json.loads(blob("HEAD", "results/compute_audit.json").decode("utf-8", "replace"))
t = json.loads(blob("MERGE_HEAD", "results/compute_audit.json").decode("utf-8", "replace"))
seen, union = set(), []
for row in sorted(o["history"] + t["history"], key=lambda x: str(x.get("ts", ""))):
    k = (str(row.get("ts", "")), canon(row))
    if k in seen:
        continue
    seen.add(k)
    union.append(row)
o_set = {(str(r.get("ts", "")), canon(r)) for r in o["history"]}
t_set = {(str(r.get("ts", "")), canon(r)) for r in t["history"]}
u_set = {(str(r.get("ts", "")), canon(r)) for r in union}
lost_o, lost_t = len(o_set - u_set), len(t_set - u_set)
assert lost_o == 0 and lost_t == 0, ("audit zero-loss violated", lost_o, lost_t)
base = o if ts_norm(o["latest"].get("ts", "")) >= ts_norm(t["latest"].get("ts", "")) else t
doc = {"history": union[-400:], "latest": base["latest"]}
with io.open("results/compute_audit.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
report["faces"]["results/compute_audit.json"] = (
    "union history %d+%d->%d lost=0, latest from %s"
    % (len(o["history"]), len(t["history"]), len(union),
       "ours" if base is o else "theirs"))

# --- regime_state: history union + scalars take-new by updated ---
o = json.loads(blob("HEAD", "results/regime_state.json").decode("utf-8", "replace"))
t = json.loads(blob("MERGE_HEAD", "results/regime_state.json").decode("utf-8", "replace"))
seen, union = set(), []
for row in sorted((o.get("history") or []) + (t.get("history") or []),
                  key=lambda x: str(x.get("ts", x.get("updated", "")))):
    k = canon(row)
    if k in seen:
        continue
    seen.add(k)
    union.append(row)
o_set = {canon(r) for r in (o.get("history") or [])}
t_set = {canon(r) for r in (t.get("history") or [])}
lost_o, lost_t = len(o_set - seen), len(t_set - seen)
assert lost_o == 0 and lost_t == 0, ("regime history zero-loss", lost_o, lost_t)
sc = o if ts_norm(o.get("updated", "")) >= ts_norm(t.get("updated", "")) else t
sc["history"] = union
with io.open("results/regime_state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(sc, f, ensure_ascii=False, indent=1)
report["faces"]["results/regime_state.json"] = (
    "history union %d lost=0, scalars from %s (updated %s)"
    % (len(union), "ours" if sc is o else "theirs", sc.get("updated")))

# --- token_usage: per-key machines union by entry ts (r456 law) + scalars take-new ---
o = json.loads(blob("HEAD", "results/token_usage.json").decode("utf-8", "replace"))
t = json.loads(blob("MERGE_HEAD", "results/token_usage.json").decode("utf-8", "replace"))
assert sorted(o["machines"].keys()) == sorted(t["machines"].keys()), "token keyset diverged"
side_pick = {"ours": 0, "theirs": 0}
machines = {}
def entry_ts(e):
    return ts_norm(e.get("updated", e.get("ts", e.get("generated", ""))))
for k in o["machines"]:
    oe, te = o["machines"][k], t["machines"][k]
    if entry_ts(oe) >= entry_ts(te):
        machines[k] = oe
        side_pick["ours"] += 1
    else:
        machines[k] = te
        side_pick["theirs"] += 1
assert side_pick["ours"] > 0, "r456 side-pick zero on ours leg -- whole-face fallback needed"
sc = o if ts_norm(o.get("generated", "")) >= ts_norm(t.get("generated", "")) else t
sc["machines"] = machines
with io.open("results/token_usage.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(sc, f, ensure_ascii=False, indent=1)
report["faces"]["results/token_usage.json"] = (
    "per-key union side_pick=%s, scalars from %s (gen %s)"
    % (side_pick, "ours" if sc is o else "theirs", sc.get("generated")))

# --- reparse gate (r185) on all resolved json faces ---
for path in [f for f in expect if f.endswith(".json")]:
    json.loads(io.open(path, encoding="utf-8").read())
report["verify"]["reparse"] = "PASS %d json faces" % len([f for f in expect if f.endswith(".json")])

# --- marker residue check (content-based, r664/r657) across all 14 ---
bad = []
for f in expect:
    for i, line in enumerate(io.open(f, "rb").read().split(b"\n")):
        if line.startswith(b"<<<<<<<") or line.startswith(b">>>>>>>") or line.startswith(b"======="):
            bad.append((f, i + 1))
assert not bad, ("marker residue", bad[:3])
report["verify"]["markers"] = "none"

# --- auto-merged append-only faces: zero-loss containment (HEAD + MERGE_HEAD lines in wt) ---
for f in ("results/fund_value_p1/nulls.jsonl", "results/fund_quality_p1/nulls.jsonl",
          "results/fund_divlowvol_p1/nulls.jsonl"):
    wt = set(io.open(f, "rb").read().split(b"\n"))
    ho = set(blob("HEAD", f).split(b"\n"))
    th = blob("MERGE_HEAD", f).split(b"\n")
    th_lines = set(th) - set(blob("HEAD", "results/fund_value_p1/nulls.jsonl")[:0])  # keep raw
    lost_h = len(ho - wt)
    lost_t = len(set(th) - wt)
    assert lost_h == 0, ("HEAD line loss", f, lost_h)
    # theirs-side new lines beyond merge-base must also be present
    assert lost_t == 0, ("MERGE_HEAD line loss", f, lost_t)
    report["verify"][f] = "wt=%d HEAD-lost=0 MERGE_HEAD-lost=0" % len(wt)

# --- state/heartbeat survived auto-merge intact ---
st = json.loads(io.open("state.json", encoding="utf-8").read())
assert st["round_no"] == 667 and isinstance(st["round_no"], int)
hb = json.loads(io.open("fleet/machines/bm-b.json", encoding="utf-8").read())
assert isinstance(hb["heartbeat_epoch_utc"], int) and hb["round_no"] == 667
rr = io.open("logs/iteration-loop/round_reports.md", "rb").read()
cnt = rr.decode("utf-8", "replace").count("round 667 | bm-b")
assert cnt == 1, ("round report r667 entry count", cnt)
report["verify"]["state-heartbeat-rr"] = "PASS (round 667, epoch int, rr count 1)"

with io.open("results/_r667bmb_merge_resolve.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("RESOLVE_DONE faces=%d verify=%s" % (len(report["faces"]), sorted(report["verify"].keys())))
