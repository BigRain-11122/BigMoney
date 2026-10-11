# -*- coding: utf-8 -*-
# r914 fact-gather for W216 freeze-prep (machine-read, zero transcription)
import json, re, subprocess, sys, os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

d = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w215_results.json"), encoding="utf-8"))
kl = d["skill_line_v2_k_lift"]
print("kl:", json.dumps(kl, ensure_ascii=False))
s = json.dumps(d, ensure_ascii=False)
print("se_mu mentions:", re.findall(r'"se_mu[^,}]*', s)[:6])
led = d["science_gates"]["ledger"]
print("ledger:", {k: led.get(k) for k in ("total", "prev_total", "batch_trials")})
m = d["null_pool_cumulative"]["merged"]
print("merged:", {k: m.get(k) for k in ("n_values", "mu", "sigma")})
print("w215_only:", json.dumps(d["null_pool_cumulative"]["w215_only"], ensure_ascii=False))
print("p95:", d["families"]["A_random_engine_exit"]["full_sharpe_p95"])
print("cutoff:", d.get("evidence_cutoff"))
print("audit:", json.dumps(d.get("science_gates", {}).get("audit", d.get("audit", {})), ensure_ascii=False)[:400])

# W215 prereg freeze-time add commit
r = subprocess.run(["git", "-C", REPO, "log", "--diff-filter=A", "--format=%H",
                    "--", "research/PERPETUAL_N1_W215_PREREG.md"], capture_output=True)
print("w215_prereg_add_commit:", r.stdout.decode().strip())

# W215 freeze splice commit (five-face) -- pickaxe on the band row
r = subprocess.run(["git", "-C", REPO, "log", "--format=%H", "-S", '215: {"a"',
                    "--", "scripts/perpetual_faces.py"], capture_output=True)
print("w215_freeze_sha:", r.stdout.decode().strip().splitlines()[:1])

# seat MSG filename + origin commit
r = subprocess.run(["git", "-C", REPO, "show", "--stat", "--format=%H %s", "f8b38fa1e"], capture_output=True)
print("f8b38fa1e stat:", r.stdout.decode(encoding="utf-8", errors="replace")[:600])

# engine live state (queue/burns)
for p in ("results/saturation_engine_state.bm-c.json",):
    try:
        e = json.load(open(os.path.join(REPO, p), encoding="utf-8"))
        print(p, "->", json.dumps({k: e.get(k) for k in ("queue_next", "burns_active", "activity_now") if k in e}, ensure_ascii=False)[:400])
    except Exception as ex:
        print(p, "ERR", ex)
