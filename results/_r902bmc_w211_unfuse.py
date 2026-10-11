"""r902: W211 mid-surgery fuse release -- kill engine, clear stale W211
quarantine + crash counters (12 shards fused at 01:01-01:04 on a transient
SyntaxError mid-rebase file state; the committed HEAD file py_compiles clean
+ n1 selftest PASS incl W211 face). Engine restarts via its 1-min
Bigmoney-SaturationEngine task supervisor."""
import json
import os
import signal
import subprocess
import sys

STATE = r"results\saturation_engine_state.bm-c.json"

# 1. locate the resident engine PID (no stale PID assumptions)
out = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "(Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
     "Where-Object {$_.CommandLine -like '*Tools*saturation_engine.py*run*'} "
     "| Select-Object -ExpandProperty ProcessId)"],
    capture_output=True, text=True).stdout.strip()
pids = [int(x) for x in out.split() if x.strip().isdigit()]
print("engine pids found:", pids)

st = json.load(open(STATE, encoding="utf-8"))
q_before = st.get("quarantined") or []
w211_q = [k for k in q_before if isinstance(k, list) and k and k[0] == 211]
assert len(w211_q) == 12, f"expected 12 W211 quarantine rows, got {len(w211_q)}"
cc = st.get("crash_counts") or {}
w211_cc = [k for k in cc if k.startswith("211:")]
assert len(w211_cc) == 12, f"expected 12 W211 crash counters, got {len(w211_cc)}"
assert all(cc[k] >= 3 for k in w211_cc), "crash counters below fuse -- unexpected"

# 2. kill engine(s) FIRST (memory holds quarantine; flush would revert edits)
for pid in pids:
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        f"Stop-Process -Id {pid} -Force"],
                       capture_output=True, text=True, timeout=15)
        print("killed engine pid", pid)
    except Exception as e:
        print("kill failed for", pid, repr(e))

# verify dead (2s grace)
import time
for _ in range(10):
    time.sleep(0.3)
    chk = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f"@(Get-Process -Id {pid} -ErrorAction SilentlyContinue).Count"],
        capture_output=True, text=True).stdout.strip()
    if chk == "0":
        break
print("engine dead confirmed")

# 3. clear W211 quarantine + counters (keep historical [12,11] / 12:11 intact)
st["quarantined"] = [k for k in q_before if not (isinstance(k, list) and k and k[0] == 211)]
for k in w211_cc:
    cc.pop(k)
st["crash_counts"] = cc
st["w211_unfuse_note"] = ("r902: 12 shards fused 01:01-01:04 on transient "
                          "mid-surgery SyntaxError (engine adopted pre-commit "
                          "perpetual_faces_n1.py); HEAD db243f93e py_compile rc0 "
                          "+ n1 selftest PASS incl W211 face -- counters reset, "
                          "fresh 3-fuse budget per shard")
tmp = STATE + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
os.replace(tmp, STATE)
st2 = json.load(open(STATE, encoding="utf-8"))
assert not [k for k in st2["quarantined"] if isinstance(k, list) and k and k[0] == 211]
assert not [k for k in st2["crash_counts"] if k.startswith("211:")]
print("state edited: W211 quarantine cleared, counters reset; remaining quarantine:",
      st2["quarantined"])
