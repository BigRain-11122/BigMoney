"""r126 bm-c rebase storm resolver (2026-09-28 02:5x window).

Push-storm: my r126 (5d2474d7) vs origin f3b11d5f (bmb r355 maintenance S6
30/30 + bma r373 lane-migration closeout). 13 UU = three-machine same-window
S6 mirror convergence, 2nd+ instance of the r120/r354/r355 family.

Side-assert (r352 law, rebase window): :2: == HEAD == upstream/origin face,
:3: == my replayed commit face. VERIFIED pre-write:
  update_status :2: updated 02:49:52 (bmb S6) vs :3: 02:48:32 (bmc S6)
  compute_audit :2: latest 02:49:40 hist 11 vs :3: latest 02:48:24 hist 10

Face laws applied (family per LANE_MIGRATION_S1):
  A-family rolling ledger   -> compute_audit: history identity-union by ts
                               (zero-loss assert), latest take-newer (origin).
  A-family asof rolling     -> regime_state: same asof (09-24) both sides ->
                               take-newer updated (origin 02:49:53).
  B-family gate snapshots   -> update_status / futures / lhb: same-semantics
                               faces (cutoff/new_rows agree), take fresher ts
                               (origin 02:49:52/02:50:32/02:50:31).
  B-family metering         -> token_usage: rough-estimate snapshot (byte/3.5
                               proxy), identical machines key-set both sides,
                               take origin fresher generated; my r126 report
                               line delta (+175B) re-measures next round.
  C-family idempotent derive -> daily_report twins (md-coupled, SAME side both)
                               / dashboard js+json / scorecard_v1 /
                               strategy_scorecard / fundamental_b_layer_filter:
                               take origin (S6 re-derives every round).
  autofill_state auto-merged clean (my last_tick 02:50:01 fresher tick slot
                               rotation; origin launches face kept untouched).
"""
import json
import subprocess
import sys

ROOT = "."


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                       capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"blob probe fail {stage} {path}: {r.stderr[:200]}")
    return json.loads(r.stdout.decode("utf-8"))


def take(stage, path):
    side = "--ours" if stage == 2 else "--theirs"
    r = subprocess.run(["git", "checkout", side, "--", path],
                       capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"take fail {stage} {path}: {r.stderr[:200]}")


log = []

# --- A-family: compute_audit identity-union + latest take-newer ---
p = "results/compute_audit.json"
o2, o3 = blob(2, p), blob(3, p)
h2, h3 = o2["history"], o3["history"]
union = {r["ts"]: r for r in h2}
for r in h3:
    union.setdefault(r["ts"], r)
hist = [union[k] for k in sorted(union)]
latest = o2["latest"] if o2["latest"]["ts"] >= o3["latest"]["ts"] else o3["latest"]
merged = dict(o2)
merged["history"] = hist
merged["latest"] = latest
with open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
n2, n3 = len(h2), len(h3)
log.append(f"compute_audit: history identity-union {n2}+{n3}->{len(hist)} "
           f"zero-loss assert (unique-ts {len(union)}) "
           f"latest take-newer {latest['ts']}")
assert len(hist) >= max(n2, n3), "union lost rows"

# --- A-family same-asof: regime_state take-newer ---
p = "results/regime_state.json"
o2, o3 = blob(2, p), blob(3, p)
assert o2["asof"] == o3["asof"], "asof diverged -> manual look"
take(2 if o2["updated"] >= o3["updated"] else 3, p)
log.append(f"regime_state: same-asof {o2['asof']} take-newer updated "
           f"(origin {o2['updated']} vs mine {o3['updated']})")

# --- B-family gate snapshots: take fresher ts (same-semantics) ---
for p, tk in (("results/update_status.json", "updated"),
              ("results/futures_update_status.json", "updated"),
              ("results/lhb_update_status.json", "updated")):
    o2, o3 = blob(2, p), blob(3, p)
    take(2 if o2.get(tk, "") >= o3.get(tk, "") else 3, p)
    log.append(f"{p.split('/')[-1]}: gate-face take-fresher "
                f"(origin {o2.get(tk)} vs mine {o3.get(tk)})")

# --- B-family metering: token_usage take origin (same key-set) ---
p = "results/token_usage.json"
o2, o3 = blob(2, p), blob(3, p)
assert set(o2["machines"]) == set(o3["machines"]), "machines key-set diverged"
take(2, p)
log.append(f"token_usage: rough-estimate snapshot take origin "
            f"(generated {o2['generated']} vs {o3['generated']}, "
            f"machines key-set identical, bmc r126 report-line delta "
            f"re-measures next round)")

# --- C-family derives + twins: take origin (S6 re-derives) ---
for p in ("docs/daily_report/REPORT-2026-09-28.json",
          "docs/daily_report/REPORT-2026-09-28.md",
          "results/dashboard_status.js", "results/dashboard_status.json",
          "results/fundamental_b_layer_filter.json",
          "results/scorecard_v1.json", "results/strategy_scorecard.json"):
    take(2, p)
    log.append(f"{p.split('/')[-1]}: C-family derive take origin")

print("\n".join(log))
with open("results/_r126bmc_resolve_storm.log", "w", encoding="utf-8") as f:
    f.write("\n".join(log) + "\n")
print("RESOLVER DONE")
