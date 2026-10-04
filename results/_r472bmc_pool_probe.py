# r472 bm-c probe: pool face summary (tolerant utf-8 read per pit-encoding) + satengine verdict
import json, subprocess, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
out = {}

# pool face
raw = open(ROOT + r"\results\runnable_pool.json", "rb").read().decode("utf-8", errors="replace")
d = json.loads(raw)
shards = d.get("shards", d)
items = []
def _iter_shards(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, dict) and "status" in v:
                yield k, v
            elif isinstance(v, dict):
                yield from _iter_shards(v)
for k, v in _iter_shards(d):
    items.append((k, v.get("status"), v.get("owner")))
from collections import Counter
out["pool_by_status"] = dict(Counter(s for _, s, _ in items))
out["ready_or_burning"] = [(k, s, o) for k, s, o in items if s in ("ready", "burning")][:8]

# satengine status (Tools copy = bm-c registered face per r467)
p = subprocess.run([sys.executable, ROOT + r"\Tools\saturation_engine.py", "status"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
out["satengine_rc"] = p.returncode
try:
    st = json.loads(p.stdout)
    out["satengine_alive"] = st.get("alive")
    out["satengine_verdict"] = st.get("verdict")
    out["satengine_burns_active"] = st.get("burns_active")
    out["satengine_keys"] = list(st.keys())[:12]
except Exception as e:
    out["satengine_parse_err"] = str(e)
    out["satengine_stdout_tail"] = (p.stdout or "")[-400:]
    out["satengine_stderr_tail"] = (p.stderr or "")[-200:]

open(ROOT + r"\results\_r472bmc_pool_satengine.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("WROTE _r472bmc_pool_satengine.json rc_probe_done")
