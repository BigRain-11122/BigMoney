# r358 bm-c: W63 missing-shards (2/5/8) engine-queue diagnosis.
# Why is the engine burning W64 while W63 has 3 holes? Probe queue/
# active_burns/burns history for W63 entries + claim/burn state per shard.
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sp = os.path.join(ROOT, "results", "saturation_engine_state.bm-c.json")
d = json.load(open(sp, "rb"))

print("TOP-KEYS:", sorted(d.keys()))
q = d.get("queue")
print("QUEUE_TYPE=%s" % type(q).__name__)
if isinstance(q, list):
    for it in q[:10]:
        print("  Q:", json.dumps(it, ensure_ascii=False)[:220])
elif isinstance(q, dict):
    print("  Q:", json.dumps(q, ensure_ascii=False)[:600])
ab = d.get("active_burns")
print("ACTIVE_BURNS_TYPE=%s" % type(ab).__name__)
print("  AB:", json.dumps(ab, ensure_ascii=False)[:800])
w = d.get("wave_shards_done", {})
print("WAVE_SHARDS_DONE[63]=%s [64]=%s" % (w.get("63"), w.get("64")))
b = d.get("burns")
if isinstance(b, list):
    w63 = [x for x in b if str(x.get("wave")) == "63"]
    print("BURNS: total=%d w63_entries=%d" % (len(b), len(w63)))
    for it in w63:
        print("  B63:", json.dumps(it, ensure_ascii=False)[:260])
else:
    print("BURNS_TYPE=%s" % type(b).__name__)
hz = d.get("history")
if isinstance(hz, list):
    w63h = [x for x in hz if "63" in json.dumps(x)]
    print("HISTORY: total=%d w63-ish=%d" % (len(hz), len(w63h)))
    for it in w63h[-6:]:
        print("  H:", json.dumps(it, ensure_ascii=False)[:260])
# extra keys possibly holding claim/lock info
for k in ("claims", "inflight", "locks", "pending", "crash_fuse",
          "refusals", "last_tick_epoch", "supply_floor"):
    if k in d:
        print("KEY %s: %s" % (k, json.dumps(d[k], ensure_ascii=False)[:500]))
# W63 local shard face (fresh mtime check)
import time
wdir = os.path.join(ROOT, "results", "p2cal_ext", "n1_w63")
if os.path.isdir(wdir):
    for f in sorted(os.listdir(wdir)):
        st = os.stat(os.path.join(wdir, f))
        print("LOCAL %s mtime=%s" % (f, time.strftime("%H:%M:%S", time.localtime(st.st_mtime))))
w64 = os.path.join(ROOT, "results", "p2cal_ext", "n1_w64")
if os.path.isdir(w64):
    for f in sorted(os.listdir(w64)):
        st = os.stat(os.path.join(w64, f))
        print("LOCAL-W64 %s mtime=%s" % (f, time.strftime("%H:%M:%S", time.localtime(st.st_mtime))))
