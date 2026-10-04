"""r704 bm-b merge-closeout probe: extract UU stage blobs (bytes, r209 law),
deep-probe ts fields per side, pool per-entry audit. Read-only."""
import subprocess, json, os, re

UU = [
    "docs/daily_report/REPORT-2026-10-05.json",
    "docs/daily_report/REPORT-2026-10-05.md",
    "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/runnable_pool.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
STAGE_DIR = r"results\_r704bmb_stage"
os.makedirs(STAGE_DIR, exist_ok=True)
TS_KEYS = ("ts", "generated", "generated_at", "updated", "updated_at",
           "asof", "as_of", "cutoff", "scanned_at", "run_ts", "when",
           "scorecard_generated", "last_tick", "probe_ts")
LEDGER_KEYS = ("history", "transitions", "launches", "entries", "items",
               "rows", "records")


def git_show(ref):
    r = subprocess.run(["git", "show", ref], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def walk_ts(obj, path, out, depth=0):
    if depth > 4:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) <= 40 and (
                    k in TS_KEYS or k.endswith("_ts") or k.endswith("_at")
                    or k in ("date", "time")):
                out.append((path + "/" + k, v))
            elif isinstance(v, (dict, list)):
                walk_ts(v, path + "/" + k, out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):
            if isinstance(v, (dict, list)):
                walk_ts(v, path + f"[{i}]", out, depth + 1)


report = {"merge_base": None, "files": {}, "pool_audit": None,
          "untracked_sizes": {}}

mb = git_show("MERGE_HEAD")  # placeholder to warm
r = subprocess.run(["git", "merge-base", "HEAD", "MERGE_HEAD"],
                   capture_output=True, text=True)
report["merge_base"] = r.stdout.strip()
mr = subprocess.run(["git", "log", "-1", "--format=%h %ci %s",
                     report["merge_base"]], capture_output=True, text=True)
report["merge_base_head"] = mr.stdout.strip()

for i, p in enumerate(UU):
    ent = {}
    sides = {}
    for s, tag in ((1, "base"), (2, "ours"), (3, "theirs")):
        b = git_show(f":{s}:{p}")
        if b is not None:
            fn = os.path.join(STAGE_DIR, f"{i:02d}_{tag}.blob")
            open(fn, "wb").write(b)
            ent[tag + "_bytes"] = len(b)
            sides[tag] = b
    # deep ts probe for json sides
    for tag in ("ours", "theirs"):
        b = sides.get(tag)
        if not b:
            continue
        txt = None
        if p.endswith(".json"):
            try:
                data = json.loads(b.decode("utf-8"))
                tsf = []
                walk_ts(data, "", tsf)
                ent[tag + "_ts"] = tsf[:14]
                for lk in LEDGER_KEYS:
                    if isinstance(data, dict) and lk in data and isinstance(data[lk], list):
                        ent[tag + "_" + lk + "_len"] = len(data[lk])
                if isinstance(data, dict):
                    ent[tag + "_topkeys"] = sorted(data.keys())[:18]
            except Exception as e:
                ent[tag + "_json_err"] = repr(e)[:120]
        elif p.endswith(".js"):
            m = re.findall(rb"20\d\d-\d\d-\d\d[T ][\d:]{8}", b)
            ent[tag + "_ts_re"] = [x.decode() for x in m[:6]]
        else:  # md
            m = re.findall(r"20\d\d-\d\d-\d\d[T ][\d:]{8}", b.decode("utf-8", "replace"))
            ent[tag + "_ts_re"] = m[:6]
    report["files"][p] = ent

# pool per-entry audit
pool = {}
for tag in ("base", "ours", "theirs"):
    b = open(os.path.join(STAGE_DIR, "14_" + tag + ".blob"), "rb").read()
    d = json.loads(b.decode("utf-8"))
    entries = d.get("entries", d if isinstance(d, list) else [])
    pool[tag] = {e.get("id"): e for e in entries}
    pool[tag + "_meta"] = {k: v for k, v in d.items() if k != "entries"}
ids = {t: set(pool[t]) for t in ("base", "ours", "theirs")}
pa = {
    "counts": {t: len(ids[t]) for t in ("base", "ours", "theirs")},
    "only_ours": sorted(ids["ours"] - ids["theirs"]),
    "only_theirs": sorted(ids["theirs"] - ids["ours"]),
    "shared": len(ids["ours"] & ids["theirs"]),
    "meta_ours": pool.get("ours_meta"),
    "meta_theirs": pool.get("theirs_meta"),
    "shared_ts_diff": [],
    "nulls_in_theirs": 0,
    "nulls_in_ours": 0,
}
for k in sorted(ids["ours"] & ids["theirs"]):
    o, t = pool["ours"][k], pool["theirs"][k]
    for f in ("owner_since", "cleared_ts", "status", "owner"):
        ov, tv = o.get(f), t.get(f)
        if ov != tv:
            pa["shared_ts_diff"].append([k, f, str(ov)[:28], str(tv)[:28]])
    pa["nulls_in_theirs"] += sum(1 for f in ("owner_since", "cleared_ts")
                                 if t.get(f) is None)
    pa["nulls_in_ours"] += sum(1 for f in ("owner_since", "cleared_ts")
                               if o.get(f) is None)
report["pool_audit"] = pa

# untracked backlog sizes
for fn in os.listdir("results"):
    if fn.startswith(("_r686", "_r699", "_r701", "_r702", "_r703")):
        report["untracked_sizes"][fn] = os.path.getsize(os.path.join("results", fn))

open(r"results\_r704bmb_uu_report.json", "w", encoding="utf-8").write(
    json.dumps(report, ensure_ascii=False, indent=1))
print("merge_base:", report["merge_base_head"])
print("pool counts:", pa["counts"], "| only_ours:", pa["only_ours"],
      "| only_theirs:", pa["only_theirs"][:14])
print("pool shared:", pa["shared"], "| ts_diff rows:", len(pa["shared_ts_diff"]),
      "| nulls ours/theirs:", pa["nulls_in_ours"], pa["nulls_in_theirs"])
for d in pa["shared_ts_diff"][:22]:
    print("  POOLDIFF", d)
for p, ent in report["files"].items():
    print("==", p)
    for tag in ("ours", "theirs"):
        line = f"  {tag}: bytes={ent.get(tag + '_bytes')}"
        if tag + "_ts" in ent:
            line += " ts=" + json.dumps(ent[tag + "_ts"][:6], ensure_ascii=False)
        for lk in LEDGER_KEYS:
            if tag + "_" + lk + "_len" in ent:
                line += f" {lk}={ent[tag + '_' + lk + '_len']}"
        if tag + "_ts_re" in ent:
            line += " ts_re=" + json.dumps(ent[tag + "_ts_re"][:3])
        print(line)
print("untracked sizes:", json.dumps(report["untracked_sizes"]))
