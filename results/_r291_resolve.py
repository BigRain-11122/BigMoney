# r291 bm-b S0 pull --rebase conflict resolver (skill: bigmoney-conflict-resolve)
# Context: r290 addendum scheduled "main-face incorporation next round S0" (r290 push
# double-rejected, fallback branch machine/bm-b-r290 pushed). This rebase replays
# local dc70b83a + 32dd7a9d onto origin/main 1150732c (bm-a tick claim 2b9926cf +
# bm-a r288/289 S6 regen 02:52 face). 15 UU = S6-mirror family.
# Recipes (classifier + manual adjudication of 5 UNKNOWN per SKILL.md):
#   snapshots (12) -> take-new whole blob by internal ts: origin side wins all
#     (bm-a 02:52:xx regen > my r290 02:46-47 regen); byte-exact copy, no re-serialize.
#   runnable_pool.json (pool ledger) -> only diverged id CENSUS-FUS-S2-W1
#     (shards owner face); origin side = newer claim state (bm-a) -> take origin blob
#     whole = zero-loss union (54/54 ids, claim preserved).
#   compute_audit.json (rolling-ledger) -> history union by ts (|A u B| = 203),
#     latest = take-new (origin 02:52:03); write LF + 2-space indent + ASCII
#     mirroring upstream blob producer face.
#   regime_state.json (rolling-ledger) -> history rows verified equal both sides;
#     only 'updated' ts differs -> take origin blob whole (zero-loss by equality).
# Law: r188/R208 union zero-loss, R209 js-wrapper no-restrip, r185 parse-before-write.
import json
import subprocess

def blob(idx, path):
    b = subprocess.run(["git", "show", f":{idx}:{path}"], capture_output=True).stdout
    if not b:
        raise SystemExit(f"empty blob stage {idx} for {path}")
    return b

TAKE_OURS = [
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "docs/daily_report/REPORT-2026-09-27.json",
    "docs/daily_report/REPORT-2026-09-27.md",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/runnable_pool.json",
]

# --- sanity: the snapshot ts ordering claimed above (fail-closed, not blind) ---
TS_FIELD = {
    "results/fundamental_b_layer_filter.json": "updated",
    "results/futures_update_status.json": "ts",
    "results/heat_update_status.json": "updated",
    "results/lhb_update_status.json": "updated",
    "results/token_usage.json": "generated",
    "results/update_status.json": "updated",
    "docs/daily_report/REPORT-2026-09-27.json": "generated_at",
    "results/scorecard_v1.json": "generated",
    "results/strategy_scorecard.json": "generated",
}
for p, k in TS_FIELD.items():
    o = json.loads(blob(2, p)); t = json.loads(blob(3, p))
    assert o[k] >= t[k], f"{p}: origin side not newer ({o[k]} vs {t[k]}) - STOP manual look"
dm_o = blob(2, "docs/daily_report/REPORT-2026-09-27.md").decode("utf-8")
dm_t = blob(3, "docs/daily_report/REPORT-2026-09-27.md").decode("utf-8")
import re
go = next(l for l in dm_o.splitlines() if "生成" in l and "2026-" in l)
gt = next(l for l in dm_t.splitlines() if "生成" in l and "2026-" in l)
assert re.search(r"2026-\d\d-\d\d \d\d:\d\d:\d\d", go).group(0) >= re.search(r"2026-\d\d-\d\d \d\d:\d\d:\d\d", gt).group(0), \
    f"daily report md origin not newer: {go!r} vs {gt!r}"
# pool: verify only census id diverges and origin side carries the newer claim face
po = json.loads(blob(2, "results/runnable_pool.json")); pt = json.loads(blob(3, "results/runnable_pool.json"))
oe = {e["id"]: e for e in po["entries"]}; te = {e["id"]: e for e in pt["entries"]}
assert set(oe) == set(te) and len(oe) == 54, "pool id sets diverged - STOP"
diverged = [i for i in oe if oe[i] != te[i]]
assert diverged == ["CENSUS-FUS-S2-W1"], f"unexpected pool divergence {diverged}"
sh_o = oe["CENSUS-FUS-S2-W1"]["shards"]; sh_t = te["CENSUS-FUS-S2-W1"]["shards"]
assert all(s.get("owner") == "bm-a" for s in sh_o + sh_t), "census claim face lost - STOP"
assert po["updated_at"] >= pt["updated_at"], "pool origin not newer"

# --- regime_state: verify history identical -> take origin whole ---
ro = json.loads(blob(2, "results/regime_state.json")); rt = json.loads(blob(3, "results/regime_state.json"))
assert ro["history"] == rt["history"] and ro.get("transitions", []) == rt.get("transitions", []), \
    "regime history diverged - STOP manual union"
assert ro["state"] == rt["state"] and ro["asof"] == rt["asof"]
assert ro["updated"] >= rt["updated"]
TAKE_OURS.append("results/regime_state.json")

# --- write byte-exact origin blobs for take-ours set ---
for p in TAKE_OURS:
    data = blob(2, p)
    with open(p, "wb") as f:
        f.write(data)
    if p.endswith(".json"):
        json.loads(open(p, "rb").read().decode("utf-8"))
    elif p.endswith(".js"):
        text = open(p, "rb").read().decode("utf-8")
        assert text.startswith("window.DASH_DATA = ") and text.rstrip().endswith(";"), f"js wrapper broken {p}"
    else:
        assert len(open(p, "rb").read()) > 100, f"md truncated {p}"

# --- compute_audit: history union by ts, latest take-new ---
co = json.loads(blob(2, "results/compute_audit.json")); ct = json.loads(blob(3, "results/compute_audit.json"))
merged = {r["ts"]: r for r in co["history"]}
for r in ct["history"]:
    merged.setdefault(r["ts"], r)
union_rows = sorted(merged.values(), key=lambda r: r["ts"])
n_union = len(union_rows)
n_expect = len(co["history"]) + len({r["ts"] for r in ct["history"]} - {r["ts"] for r in co["history"]})
assert n_union == n_expect == 203, f"union count {n_union} != expected 203"
assert co["latest"]["ts"] >= ct["latest"]["ts"], "latest not newer on origin"
out = {"latest": co["latest"], "history": union_rows}
text = json.dumps(out, indent=2, ensure_ascii=True) + "\n"
assert "\r" not in text
with open("results/compute_audit.json", "wb") as f:
    f.write(text.encode("utf-8"))
chk = json.loads(open("results/compute_audit.json", "rb").read().decode("utf-8"))
assert len(chk["history"]) == 203
assert {r["ts"] for r in chk["history"]} == {r["ts"] for r in union_rows}

print("RESOLVED: 14 take-origin byte-exact + compute_audit union 203 rows zero-loss")
print("  census claim face preserved (owner=bm-a), regime history equal, daily_report md newer",
      go[:40])
