"""Rebase conflict resolution helper (one-shot): union-merge compute_audit
ts-key history + token_usage machine-key latest; mirrors take remote."""
import json
import subprocess


def blob(rev: str, path: str):
    out = subprocess.run(["git", "show", f"{rev}:{path}"],
                         capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"git show {rev}:{path} failed: {out.stderr[:200]}")
    return json.loads(out.stdout.decode("utf-8"))


# --- compute_audit: union by ts key (r104/r80 recipe) ---
p = "results/compute_audit.json"
ours = blob(":2", p)      # rebase: ours = remote side
theirs = blob(":3", p)    # theirs = my replayed commit
hist_ours = {h["ts"]: h for h in ours.get("history", [])}
hist_theirs = {h["ts"]: h for h in theirs.get("history", [])}
union = {**hist_ours, **hist_theirs}
merged_hist = sorted(union.values(), key=lambda h: h["ts"])
base = dict(ours)                     # remote head frame
base["history"] = merged_hist
newest = merged_hist[-1] if merged_hist else {}
for k, v in newest.items():
    if k != "ts":
        base[k] = v                  # mirror fields from the newest sample
with open(p, "w", encoding="utf-8") as fh:
    json.dump(base, fh, indent=1, ensure_ascii=False)
print(f"compute_audit merged: history {len(hist_ours)}+{len(hist_theirs)}"
      f" -> {len(merged_hist)} ts-unique rows")

# --- token_usage: machine-key union, latest per machine (r113 recipe) ---
p = "results/token_usage.json"
ours = blob(":2", p)
theirs = blob(":3", p)
mo = ours.get("machines", {})
mt = theirs.get("machines", {})
machines = {**mo, **mt}              # same-machine: later writer wins
base = dict(ours)
base["machines"] = machines
# keep newest top-level state frame
if str(theirs.get("updated_at", "")) > str(ours.get("updated_at", "")):
    for k, v in theirs.items():
        if k != "machines":
            base[k] = v
with open(p, "w", encoding="utf-8") as fh:
    json.dump(base, fh, indent=1, ensure_ascii=False)
print(f"token_usage merged: machines {sorted(machines.keys())}")
