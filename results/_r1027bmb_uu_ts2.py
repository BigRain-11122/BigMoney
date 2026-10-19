import re, subprocess

FACES = [
    "results/_attrition_guard_scan.json",
    "results/_r686bmb_d19_check.json",
    "results/compute_audit.json",
    "results/d19_watermark.json",
    "results/fundamental_b_layer_filter.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def ts_of(t):
    m = re.search(r'"(?:asof|ts|updated|updated_at|generated|generated_at|scanned_at|sampled_at|checked_at)"\s*:\s*"?([0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9:.]+)', t)
    if m:
        return m.group(1)
    m = re.search(r'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})', t[:4000])
    return m.group(1) if m else "n/a"

def side(rev, path):
    b = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if b.returncode != 0:
        return "MISSING"
    return ts_of(b.stdout.decode("utf-8", "replace"))

for p in FACES:
    o = side("d5927d43b1", p)   # bm-a r1080 side (new origin tip)
    m = side("5a7c531b1b", p)   # my r1027 commit
    print(f"{p}: origin(bm-a)={o} | mine(r1027)={m}")
