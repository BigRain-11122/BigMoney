# -*- coding: utf-8 -*-
# r237 bm-b rebase step-1 resolver driver (run from repo root; TEMP copy per r231 law)
import subprocess, json, io, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r237b_replay_resolver import resolve_autofill, resolve_ledger, resolve_jsonl_union, probe, load

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"

def stage(path, n):
    b = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True, cwd=REPO).stdout
    assert b, f"stage {n} empty for {path}"
    return b

def write_bytes(path, b):
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(b)

def write_temp(path, n):
    b = stage(path, n)
    p = os.path.join(os.environ["TEMP"], f"r237_stage_{n}_" + path.replace("/", "_").replace("\\", "_"))
    with open(p, "wb") as f:
        f.write(b)
    return p

results = []

# --- 1) ticket add/add: keep bm-a's 73 (ours=origin), renumber mine to 76 ---
t73 = "fleet/tasks/T-2026-09-26-73-P1.json"
ours73 = stage(t73, 2)   # bm-a CN-schools ticket (origin side)
theirs73 = stage(t73, 3) # my wave-10 ticket (replay side)
o = json.loads(ours73.decode("utf-8")); m = json.loads(theirs73.decode("utf-8"))
assert "wave10" in m["type"], "theirs must be my wave-10 ticket"
assert o["id"] == "T-2026-09-26-73" and "wave10" not in str(o.get("type", "")), "ours must be bm-a ticket"
write_bytes(t73, ours73)  # keep bm-a's ticket at 73
# renumber mine -> T-76 with yield note
m["id"] = "T-2026-09-26-76"
m["note"] = m["note"] + " RENUMBER DISCLOSURE (r237 bm-b): locally created as T-2026-09-26-73 same-window as bm-a CEO-order ticket T-73 (CN schools panorama, commit-time priority per fleet/README s4) -> yielded number, renumbered to 76 at rebase replay; zero content change otherwise."
nl, ind = probe(theirs73)
raw = json.dumps(m, indent=ind, ensure_ascii=False)
if nl == "\r\n":
    raw = raw.replace("\n", "\r\n")
write_bytes("fleet/tasks/T-2026-09-26-76-P1.json", raw.encode("utf-8"))
results.append(("ticket", "73=ours(bm-a) kept; mine renumbered -> T-2026-09-26-76"))

# --- 2) autofill_state.json: launches union cap50 + last_tick take-new dict ---
p = "results/autofill_state.json"
r = resolve_autofill(write_temp(p, 2), write_temp(p, 3), os.path.join(REPO, p))
results.append(("autofill", r))

# --- 3) compute_audit.json: latest take-new by ts + history union zero-loss ---
p = "results/compute_audit.json"
a = load(write_temp(p, 2)); b = load(write_temp(p, 3))
out = dict(b)
ta = str(a.get("latest", {}).get("ts", "")); tb = str(b.get("latest", {}).get("ts", ""))
out["latest"] = b["latest"] if tb >= ta else a["latest"]
la = a.get("history", []); lb = b.get("history", [])
seen = {}
for row in la + lb:
    k = str(row.get("ts", "")) + "|" + str(row.get("machine", ""))[:24]
    if k not in seen:
        seen[k] = row
out["history"] = sorted(seen.values(), key=lambda r: str(r.get("ts", "")))
# write with base-blob indent probe (base=origin side bytes, producer indent=2)
base = stage(p, 2)
nl, ind = probe(base)
raw = json.dumps(out, indent=ind, ensure_ascii=False)
if nl == "\r\n":
    raw = raw.replace("\n", "\r\n")
write_bytes(p, raw.encode("utf-8"))
results.append(("compute_audit", f"latest {ta}->{tb} pick {'theirs' if tb>=ta else 'ours'}; history {len(la)}|{len(lb)}->{len(out['history'])}"))

# --- 4) dashboard twins: decide by .json meta.generated_at, take WHOLE BYTES both files ---
pj = "results/dashboard_status.json"
ga = json.loads(stage(pj, 2).decode("utf-8")).get("meta", {}).get("generated_at", "")
gb = json.loads(stage(pj, 3).decode("utf-8")).get("meta", {}).get("generated_at", "")
side = 3 if gb > ga else 2
write_bytes(pj, stage(pj, side))
write_bytes("results/dashboard_status.js", stage("results/dashboard_status.js", side))
results.append(("dashboard_twins", f"gen {ga} vs {gb} -> side {side}; js wrapper whole-bytes preserved"))

# --- 5) regime_state.json: state face take-new by updated + history/transitions union ---
p = "results/regime_state.json"
a = load(write_temp(p, 2)); b = load(write_temp(p, 3))
ua = str(a.get("updated", a.get("ts", ""))); ub = str(b.get("updated", b.get("ts", "")))
out = dict(b if ub >= ua else a)
for key in ("history", "transitions"):
    seen = {}
    for row in a.get(key, []) + b.get(key, []):
        k = str(row.get("ts", row.get("date", ""))) + "|" + str(row.get("state", row.get("trigger", "")))[:40]
        if k not in seen:
            seen[k] = row
    out[key] = sorted(seen.values(), key=lambda r: str(r.get("ts", r.get("date", ""))))
base = stage(p, 2); nl, ind = probe(base)
raw = json.dumps(out, indent=ind, ensure_ascii=False)
if nl == "\r\n":
    raw = raw.replace("\n", "\r\n")
write_bytes(p, raw.encode("utf-8"))
results.append(("regime", f"updated {ua} vs {ub} -> {'theirs' if ub>=ua else 'ours'}; history {len(a.get('history',[]))}|{len(b.get('history',[]))}->{len(out['history'])}; transitions ->{len(out['transitions'])}"))

# --- 6) simple snapshots: take-new by best ts-ish key ---
for p, keys in [
    ("results/fundamental_b_layer_filter.json", ["ts", "updated", "generated_at"]),
    ("results/futures_update_status.json", ["ts", "updated"]),
    ("results/heat_update_status.json", ["updated", "ts"]),
    ("results/lhb_update_status.json", ["updated", "ts"]),
    ("results/update_status.json", ["ts", "updated"]),
    ("results/token_usage.json", ["ts", "updated"]),
]:
    a = load(write_temp(p, 2)); b = load(write_temp(p, 3))
    def best(d):
        for k in keys:
            if isinstance(d, dict) and k in d:
                return str(d[k])
        return ""
    ba_, bb_ = best(a), best(b)
    pick = b if bb_ > ba_ else a
    base = stage(p, 2); nl, ind = probe(base)
    raw = json.dumps(pick, indent=ind, ensure_ascii=False)
    if nl == "\r\n":
        raw = raw.replace("\n", "\r\n")
    write_bytes(p, raw.encode("utf-8"))
    results.append((p.split("/")[-1], f"{ba_} vs {bb_} -> {'theirs' if bb_>ba_ else 'ours'}"))

# --- verify: all resolved files parse ---
for f in ["results/autofill_state.json", "results/compute_audit.json", "results/dashboard_status.json",
          "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
          "results/heat_update_status.json", "results/lhb_update_status.json", "results/regime_state.json",
          "results/token_usage.json", "results/update_status.json",
          "fleet/tasks/T-2026-09-26-73-P1.json", "fleet/tasks/T-2026-09-26-76-P1.json"]:
    json.load(io.open(os.path.join(REPO, f), encoding="utf-8-sig"))
js = open(os.path.join(REPO, "results/dashboard_status.js"), "rb").read()
assert js.count(b"window.DASH_DATA") >= 1 and b"<<<<<<<" not in js, "js wrapper broken"
for f in ["results/autofill_state.json", "results/compute_audit.json", "results/regime_state.json",
          "results/dashboard_status.js", "results/dashboard_status.json", "fleet/tasks/T-2026-09-26-73-P1.json",
          "fleet/tasks/T-2026-09-26-76-P1.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/update_status.json", "results/token_usage.json"]:
    b = open(os.path.join(REPO, f), "rb").read()
    assert b"<<<<<<<" not in b and b">>>>>>>" not in b and b"=======" not in b.split(b"\n")[0], f"markers left in {f}"
for name, r in results:
    print(name, "::", r)
print("STEP1 RESOLVED+VERIFIED")
