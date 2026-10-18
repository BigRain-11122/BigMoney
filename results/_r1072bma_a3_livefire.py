"""r1072 bm-a A3 live-fire intercept probe (plan sec.III A3, <=10-24).

Exercises the REAL Tools/autofill.py runtime gates end-to-end against
hermetic fixtures (r117 law: zero production-surface writes) and lands
the intercept evidence JSON for V3/V4 acceptance:
  * G1 closed-family ignite refusal (tick verdict + gate-event ledger)
  * G2 budget_cap runtime auto-DISABLE (pool faces + gate-event ledger)

Pure offline: zero network, zero git, zero engine. Exit 0 = evidence
captured (faces reported honestly whatever they are).
"""
import importlib.util
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "af_livefire", os.path.join(ROOT, "Tools", "autofill.py"))
af = importlib.util.module_from_spec(spec)
spec.loader.exec_module(af)

tmp = tempfile.mkdtemp(prefix="a3_livefire_")
af.POOL = os.path.join(tmp, "runnable_pool.json")
af.STATE = os.path.join(tmp, "autofill_state.json")
af.FUSE = os.path.join(tmp, "crash_fuse.json")
af.LOG = os.path.join(tmp, "autofill.log")
af.LOGS_DIR = os.path.join(tmp, "logs")
os.makedirs(af.LOGS_DIR, exist_ok=True)
af.MACHINES = os.path.join(tmp, "machines")
os.makedirs(af.MACHINES, exist_ok=True)
af.CLAIMS = os.path.join(tmp, "pool_claims")
af.CORE_SAMPLES = os.path.join(tmp, "pool_core_samples.jsonl")
af.RED_FLAGS = os.path.join(tmp, "pool_red_flags.jsonl")
af.STRAND = os.path.join(tmp, "claim_strand.json")
af.GATE_EVENTS = os.path.join(tmp, "pool_gate_events.jsonl")
af._runner_core_verdict = lambda r: ("multiproc", "fixture-passthrough")
af._py_cpu_pct = lambda w=2.0: 5.0

BASE = {"runner": "scripts/fake_runner.py", "runner_args": ["run"],
        "lane_owner": None, "priority": 1, "status": "ready",
        "entered_at": "2026-10-19 04:00:00",
        "workers_plan": {"workers": 12, "priority": "BelowNormal"},
        "shards": [{"key": "s0", "status": "ready", "owner": None}]}

out = {"probe": "r1072bma_a3_livefire", "tmp": tmp}


def _events():
    if not os.path.exists(af.GATE_EVENTS):
        return []
    return [json.loads(l) for l in
            open(af.GATE_EVENTS, encoding="utf-8").read().splitlines()
            if l.strip()]


def _pool_face():
    lane = af._lane_path_for(af.POOL)
    faces = {"shared": json.load(open(af.POOL, encoding="utf-8"))
             ["entries"] if os.path.exists(af.POOL) else None}
    if lane and os.path.exists(lane):
        faces["lane"] = json.load(open(lane, encoding="utf-8"))["entries"]
    return faces


# --- G1: closed-family head + clean later entry (anti-starvation) ---
with open(af.POOL, "w", encoding="utf-8") as fh:
    json.dump({"entries": [
        dict(BASE, id="LIVEFIRE-G1-微盘因子reburn", priority=1),
        dict(BASE, id="LIVEFIRE-G1-clean", priority=2)]}, fh)
_lp = af._lane_path_for(af.POOL)
if _lp and os.path.exists(_lp):
    os.remove(_lp)
with open(af.FUSE, "w", encoding="utf-8") as fh:
    json.dump({"sigs": {}}, fh)
rc_g1 = af.tick(dry=True)
st_g1 = af._load_state()["last_tick"]
out["g1"] = {
    "rc": rc_g1,
    "verdict": st_g1.get("verdict"),
    "launched_entry": st_g1.get("entry"),
    "refused": st_g1.get("closed_family_refused"),
    "gate_events": [e for e in _events()
                    if e.get("gate") == "closed_family"],
}

# --- G2: budget_cap reached -> runtime auto-DISABLE + exposure ---
with open(af.POOL, "w", encoding="utf-8") as fh:
    json.dump({"entries": [dict(
        BASE, id="LIVEFIRE-G2-cap", budget_cap=5,
        shards=[{"key": "s0", "status": "done", "owner": "bm-z"},
                {"key": "s1", "status": "ready", "owner": "bm-b"},
                {"key": "s2", "status": "ready", "owner": None}])]}, fh)
if _lp and os.path.exists(_lp):
    os.remove(_lp)
with open(af.FUSE, "w", encoding="utf-8") as fh:
    json.dump({"sigs": {"scripts/fake_runner.py|run": {"count": 3}}}, fh)
rc_g2 = af.tick(dry=True)
st_g2 = af._load_state()["last_tick"]
faces = _pool_face()
out["g2"] = {
    "rc": rc_g2,
    "verdict": st_g2.get("verdict"),
    "budget_disabled_rec": st_g2.get("budget_disabled"),
    "shared_entry": faces.get("shared"),
    "lane_entry": faces.get("lane"),
    "gate_events": [e for e in _events()
                    if e.get("gate") == "budget_cap"],
    "consumed_unit": af._budget_consumed(
        dict(BASE, id="x", budget_cap=5,
             shards=[{"key": "a", "status": "done", "owner": "z"},
                     {"key": "b", "status": "ready", "owner": "y"},
                     {"key": "c", "status": "ready", "owner": None}]),
        {"sigs": {"scripts/fake_runner.py|run": {"count": 3}}}),
}

outp = os.path.join(ROOT, "results", "_r1072bma_a3_livefire.json")
with open(outp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
print(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True)[:4000])
print("evidence:", outp)
sys.exit(0)
