# r764 resolver probe: inspect both stages of tricky UU faces (bytes via subprocess, no PS redirect)
import subprocess, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def stage(path, n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    return r.stdout

for p in ["results/compute_audit.json", "results/token_usage.json",
          "results/_attrition_guard_scan.json", "results/regime_state.json"]:
    for n, side in ((2, "OURS"), (3, "THEIRS")):
        b = stage(p, n)
        try:
            d = json.loads(b.decode("utf-8", "replace"))
            keys = list(d.keys())
            info = {"side": side, "keys": keys[:12], "ts": d.get("ts"), "generated": d.get("generated"), "updated": d.get("updated")}
            if "history" in d and isinstance(d["history"], list):
                info["history_len"] = len(d["history"])
                if d["history"]:
                    h0 = d["history"][0]
                    info["history_key0"] = h0 if isinstance(h0, str) else list(h0.keys())[:8]
                    info["history_sample"] = str(h0)[:150]
            if "machines" in d:
                info["machines_keys"] = list(d["machines"].keys())
            if "bm-a" in d or "bm-b" in d:
                info["per_machine"] = {k: str(d[k])[:120] for k in ("bm-a", "bm-b") if k in d}
            print(p, json.dumps(info, ensure_ascii=False)[:500])
        except Exception as e:
            print(p, side, "parse fail:", e, "bytes=", len(b))
print("---- snapshots ts ----")
for p in ["results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/lhb_update_status.json",
          "results/update_status.json", "results/scorecard_v1.json", "results/strategy_scorecard.json",
          "docs/daily_report/REPORT-2026-10-06.json", "docs/live_usage/LIVE-2026-10-06.json",
          "docs/live_usage/LIVE-latest.json"]:
    row = {}
    for n, side in ((2, "ours"), (3, "theirs")):
        b = stage(p, n)
        try:
            d = json.loads(b.decode("utf-8", "replace"))
            row[side] = {k: d.get(k) for k in ("ts", "generated", "generated_at", "updated", "asof", "cutoff", "last_update") if d.get(k)}
        except Exception as e:
            row[side] = "parse fail " + str(e)[:60]
    print(p, json.dumps(row, ensure_ascii=False)[:400])
