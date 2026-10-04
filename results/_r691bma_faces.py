"""r691 bm-a: key S6 face readings -> single facts JSON."""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
out = {}

# dualrun evidence tail
try:
    lines = [l for l in open("results/pool_dualrun.bm-a.jsonl", encoding="utf-8",
                             errors="replace").read().splitlines() if l.strip()]
    tail = [json.loads(l) for l in lines[-3:]]
    out["dualrun_tail"] = [{k: r.get(k) for k in ("evidence_cutoff", "consecutive_green",
                                                  "ts", "drift", "verdict")} for r in tail]
except Exception as e:
    out["dualrun_err"] = repr(e)[:120]

# watermark red + verdict
try:
    out["watermark_red"] = json.load(open("results/watermark_red.json", encoding="utf-8"))
except Exception as e:
    out["wr_err"] = repr(e)[:120]

# py watermark last lines
try:
    wl = [l for l in open("results/watermark.jsonl", encoding="utf-8",
                         errors="replace").read().splitlines() if l.strip()]
    last = json.loads(wl[-1])
    out["py_watermark_last"] = {k: last.get(k) for k in ("verdict", "ts", "py_cpu_pct",
                                                         "runnable_facts")}
except Exception as e:
    out["pw_err"] = repr(e)[:120]

# token usage delta
try:
    tu = json.load(open("results/token_usage.json", encoding="utf-8"))
    machines = tu.get("machines", {})
    bma = machines.get("bm-a", {})
    out["token_bm_a"] = {k: bma.get(k) for k in ("total_tokens_est", "last_ts", "ts")}
except Exception as e:
    out["tu_err"] = repr(e)[:120]

# saturation engine face
try:
    se = json.load(open("results/saturation_engine/state_bm-a.json", encoding="utf-8"))
    out["satengine"] = {k: se.get(k) for k in ("last_verdict", "queue_depth",
                                              "shards_done_total", "heartbeat_ts")}
except Exception as e:
    out["se_err"] = repr(e)[:120]

json.dump(out, open("results/_r691bma_faces.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("OK")
