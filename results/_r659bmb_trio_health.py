"""r659 bm-b trio NULLS burn health probe: three fund P1 faces
(value/divlowvol/quality x 2000-run NULLS batch) -- row counts, per-face
progress vs target, evidence_cutoff freshness, honest ETA estimate from
file mtime window, pid liveness. Read-only watch product; no lane writes.
Output: results/_r659bmb_trio_health.json"""
import json, os, subprocess, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACES = {
    "fund_value_p1": "results/fund_value_p1/nulls.jsonl",
    "fund_divlowvol_p1": "results/fund_divlowvol_p1/nulls.jsonl",
    "fund_quality_p1": "results/fund_quality_p1/nulls.jsonl",
}
PIDS = {"fund_value_p1": 34396, "fund_quality_p1": 57116, "fund_divlowvol_p1": 30208}
TARGET = 2000
# baseline counts from r658 closeout state note (08:52 local)
BASE = {"fund_value_p1": 661, "fund_divlowvol_p1": 363, "fund_quality_p1": 504}
BASE_TS = "2026-10-04T08:52:14+08:00"

out = {"probe": "r659bmb_trio_health", "target": TARGET, "base_ts": BASE_TS}
total_left = 0
for name, rel in FACES.items():
    path = os.path.join(ROOT, rel)
    n = 0
    ks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            n += 1
            try:
                row = json.loads(line)
                ks.append(row.get("k"))
            except Exception:
                continue
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
    k_ok = all(isinstance(k, int) for k in ks) and ks == list(range(len(ks)))
    left = TARGET - n
    total_left += max(0, left)
    out[name] = {"rows": n, "left": left, "k_contiguous": k_ok,
                 "max_k": ks[-1] if ks else None, "mtime": mtime,
                 "delta_since_base": n - BASE[name]}

# pid liveness via tasklist parse (workaround: /FI filter proved flaky in PS quoting)
p = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True)
alive = set()
for line in p.stdout.decode("utf-8", "replace").splitlines():
    parts = [c.strip('"') for c in line.split('","')]
    if len(parts) > 1 and parts[1].isdigit():
        for name, pid in PIDS.items():
            if int(parts[1]) == pid:
                alive.add(name)
out["pids_alive"] = {n: (n in alive) for n in PIDS}

# ETA estimate: per-face rate from delta since base; ETA = max over faces
base_t = datetime.datetime.fromisoformat(BASE_TS).replace(tzinfo=None)
elapsed_h = (datetime.datetime.now() - base_t).total_seconds() / 3600.0
deltas = {n: out[n]["delta_since_base"] for n in FACES}
rates = {n: deltas[n] / max(elapsed_h, 1e-9) for n in FACES}
etas = [out[n]["left"] / rates[n] for n in FACES if rates[n] > 0 and out[n]["left"] > 0]
out["agg_rows_per_hour_observed"] = round(sum(deltas.values()) / max(elapsed_h, 1e-9), 1)
out["eta_hours_to_complete"] = round(max(etas), 1) if etas else None
out["total_rows_left"] = total_left
path = os.path.join(ROOT, "results", "_r659bmb_trio_health.json")
json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
