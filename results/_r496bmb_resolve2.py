# r496 bm-b rebase resolver (2nd collision window: bm-a r504 same-window S6)
# Recipes per bigmoney-conflict-resolve skill + r496 AA law:
#  - host=bm-a single-writer faces + bm-a lane-owned status + rolling snapshots -> origin whole bytes
#  - same-day idempotent regen products -> assert envelope-only diff then take origin
#  - token_usage.json -> per-machine key union (bm-a entry from origin, bm-b from mine)
import json, subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def stage(n, p):
    r = subprocess.run(["git", "-C", REPO, "show", ":%d:%s" % (n, p)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def take_origin(p):
    r = subprocess.run(["git", "-C", REPO, "checkout", "--ours", "--", p], capture_output=True)
    if r.returncode != 0:
        print("CHECKOUT_FAIL", p, r.stderr.decode(errors="replace")[:200]); sys.exit(2)
    print("take-origin:", p)

# --- 1. host=bm-a single-writer + lane-owner status + snapshot faces: origin whole bytes ---
ORIGIN_SIDE = [
    "results/dashboard_status.js", "results/dashboard_status.json",
    "results/scorecard_v1.json", "results/strategy_scorecard.json",
    "results/daily_scorecard.json", "results/compute_audit.json",
    "results/futures_update_status.json", "results/lhb_update_status.json",
    "results/regime_state.json", "results/update_status.json",
    "results/_attrition_guard_scan.json",
]
for p in ORIGIN_SIDE:
    if os.path.exists(p) and p in subprocess.run(["git","-C",REPO,"diff","--name-only","--diff-filter=U"],capture_output=True).stdout.decode():
        take_origin(p)
    else:
        # force origin even on auto-merged full-rewrite snapshot faces (anti-Frankenstein)
        b = stage(2, p)  # during rebase stage2 = origin side
        if b is not None:
            with open(os.path.join(REPO, p), "wb") as fh:
                fh.write(b)
            print("force-origin(snapshot face):", p)

# --- 2. same-day idempotent regen products: assert envelope-only diff, then origin ---
def strip_envelope(obj):
    if isinstance(obj, dict):
        return {k: strip_envelope(v) for k, v in obj.items()
                if k not in ("generated", "ts", "generated_at", "machine",
                             "elapsed_sec", "generated_by", "updated_at", "asof")}
    if isinstance(obj, list):
        return [strip_envelope(x) for x in obj]
    return obj

ASSERT_ORIGIN = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-latest.json",
    "results/fundamental_b_layer_filter.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]
for p in ASSERT_ORIGIN:
    ob, mb = stage(2, p), stage(3, p)
    if ob is None or mb is None:
        print("stage-missing:", p); continue
    try:
        jo, jm = json.loads(ob.decode("utf-8")), json.loads(mb.decode("utf-8"))
        same = strip_envelope(jo) == strip_envelope(jm)
    except Exception as ex:
        same = None
        print("  parse-note:", p, ex)
    print("assert %s: %s" % (p, "envelope-only PASS" if same else "DIFF-BEYOND-ENVELOPE (flagged; origin taken, next cycle regenerates)"))
    take_origin(p)
# md twins: textual, take origin (idempotent same-day regen; diff = generator stamp faces)
for p in ["docs/daily_report/REPORT-2026-10-01.md",
          "docs/live_usage/LIVE-2026-10-01.md",
          "docs/live_usage/LIVE-latest.md"]:
    take_origin(p)

# --- 3. token_usage.json: per-machine union ---
p = "results/token_usage.json"
ob, mb = stage(2, p), stage(3, p)
jo, jm = json.loads(ob.decode("utf-8")), json.loads(mb.decode("utf-8"))
merged = dict(jm)  # mine newer (generated ts)
merged["machines"] = {}
for k in sorted(set(jo.get("machines", {})) | set(jm.get("machines", {}))):
    # per-machine key: prefer the side that OWNS the machine key update (dict-merge, mine wins only for -bm- keys)
    vo, vm = jo.get("machines", {}).get(k), jm.get("machines", {}).get(k)
    if vo is None: merged["machines"][k] = vm
    elif vm is None: merged["machines"][k] = vo
    else: merged["machines"][k] = vm if k.endswith("-bm-b") else vo
for tot_key, sub_key in (("total_state_tokens_est", "state_tokens_est"),
                         ("total_report_tokens_est", "report_tokens_est")):
    if all(sub_key in v for v in merged["machines"].values()):
        merged[tot_key] = sum(v[sub_key] for v in merged["machines"].values())
        print("recomputed %s = %s (union of %d machines)" % (tot_key, merged[tot_key], len(merged["machines"])))
crlf = b"\r\n" in ob
out = json.dumps(merged, ensure_ascii=False, indent=1)
if crlf: out = out.replace("\n", "\r\n")
with open(os.path.join(REPO, p), "w", encoding="utf-8", newline="") as fh:
    fh.write(out)
json.load(open(os.path.join(REPO, p), encoding="utf-8"))
print("token_usage union: machines =", sorted(merged["machines"].keys()))

print("RESOLVER_DONE")
