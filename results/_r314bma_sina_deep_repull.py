"""R314 bm-a one-off driver: fire the A1 deep-window full-universe re-pull.

Prereg sec-6 A1 (SINA_MF_PREREG.md, freeze commit d1b2d20a) names this exact
mechanism: panel is FRESH (gate staleness face won't fire), so the lane owner
drives the one-shot re-pull via spawn_detached('refresh-repull') directly --
mirror/lock/checkpoint/conn-fuse machinery applies unchanged, gate returns to
canonical staleness drive afterwards. Zero judge faces; collection lane only.
"""
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD = os.path.join(ROOT, "scripts", "update_sina_mf.py")

spec = importlib.util.spec_from_file_location("update_sina_mf", MOD)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

owner = m._lane_owner_id()
assert owner == m.LANE_OWNER, f"lane guard: owner={owner!r} vs {m.LANE_OWNER!r}"
assert m._overlap_tol(1.0, 1.0) >= 1.0, "R226 tol law missing"

m.spawn_detached("refresh-repull")
print("spawned detached refresh-repull (A1 deep window num=250)")

# verify it actually started: lock alive + mirror flipped within retry window
import time
for _ in range(20):
    time.sleep(1.0)
    lock_alive = m._lock_alive()
    try:
        with io.open(m.STATUS, "r", encoding="utf-8") as f:
            st = json.load(f)
    except Exception:
        st = {}
    if lock_alive and "refresh in progress" in str(st.get("mode", "")):
        print(json.dumps({
            "fired": True, "lock_alive": True,
            "mode": st.get("mode"), "panel": st.get("panel"),
            "ts": st.get("ts"),
        }, ensure_ascii=False))
        sys.exit(0)
print(json.dumps({"fired": False, "lock_alive": m._lock_alive(),
                  "mode": st.get("mode")}, ensure_ascii=False))
sys.exit(2)
