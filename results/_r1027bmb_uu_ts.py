import re, subprocess, sys

FACES = [
    "results/regime_state.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "docs/daily_report/REPORT-2026-10-19.json",
    "results/d19_watermark.json",
    "results/_r686bmb_d19_check.json",
    "results/_r686bmb_orders_fresh.md",
]

def ts_of(blob_text):
    # first timestamp-ish field anywhere
    m = re.search(r'"(?:asof|ts|updated|updated_at|generated|generated_at|scanned_at|sampled_at|checked_at|last_check)"\s*:\s*"?([0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9:.]+)', blob_text)
    if m:
        return m.group(1)
    m = re.search(r'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})', blob_text[:4000])
    return m.group(1) if m else "n/a"

def side(rev, path):
    b = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if b.returncode != 0:
        return "MISSING"
    return ts_of(b.stdout.decode("utf-8", "replace"))

for p in FACES:
    o = side("origin/main", p)
    m = side("5bf56f231c", p)
    print(f"{p}\n  origin: {o}\n  ours(r1026): {m}")
