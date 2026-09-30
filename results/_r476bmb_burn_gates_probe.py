"""r476 bm-b: pre-pool verification -- burn gates on real data + timing probe.
No burn (pool law: the burn fires via runnable_pool, never inline in-round)."""
import io
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import exclusion_marginal_scan as ex  # noqa: E402

probe_f = json.load(open(ex.PROBE_FILE, encoding="utf-8"))
ok, rep = ex._burn_gates(probe_f)
print("GATES OK =", ok)
print(json.dumps(rep, ensure_ascii=False, indent=1))

# timing probe: load 150 panel files (feature-extraction cost face)
t0 = time.time()
files = sorted(os.listdir(ex.PANEL_DIR))
cal, _ = ex._load_calendar()
cutoff_pos = max(i for i, d in enumerate(cal) if d <= ex.EVIDENCE_CUTOFF)
cal = cal[: cutoff_pos + 1]
cal_pos_of = {d: i for i, d in enumerate(cal)}
n = 0
import pandas as pd
for f in files[:150]:
    df = pd.read_csv(os.path.join(ex.PANEL_DIR, f), usecols=["date", "open", "close", "amount"])
    df = df[df["date"] <= ex.EVIDENCE_CUTOFF]
    a = df["amount"].rolling(20).mean().to_numpy()
    for d in df["date"].astype(str).tolist()[:50]:
        cal_pos_of.get(d)
    n += len(df)
dt = time.time() - t0
print(f"timing: 150 files / {n} rows in {dt:.1f}s -> full 5217 est {dt * 5217 / 150:.0f}s load+extract")
