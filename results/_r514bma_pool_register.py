"""r514 bm-a: register LOWAMP-P2 judged-batch entries in runnable_pool.json
(T-140 next_steps (c)). Raw-text anchored insertion per r509 pool law
(indent-0 flat keys + CRLF + trailing line); NEVER json re-serialize the
pool. 18 entries: 16 cell-shards + NULLS + SENS."""
import json
import re
import subprocess
import sys
import time

POOL = "results/runnable_pool.json"
raw = open(POOL, "rb").read().decode("utf-8")
assert "\r\n" in raw and '"{\n"' not in raw[:200], "pool must stay CRLF"
assert raw.count('"version": 1,') == 1

# --- reference: a fresh (ready) entry's shard shape --------------------
ref = None
for m in re.finditer(r'\{\r\n"id": "([^\"]+)",', raw):
    eid = m.group(1)
    depth, i = 0, m.start()
    while i < len(raw):
        if raw[i] == "{":
            depth += 1
        elif raw[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    b = raw[m.start():i + 1]
    if '"status": "ready"' in b[:800]:
        ref = (eid, b)
        break
if ref:
    print("### READY-REF", ref[0])
    print(repr(ref[1][:900]))
else:
    print("### no ready entry found (all done/in-flight?)")

# --- guard: P2 entries must not already exist --------------------------
assert "LOWAMP-P2-" not in raw, "LOWAMP-P2 entries already registered"

NOW = time.strftime("%Y-%m-%d %H:%M:%S")
TICKET_REF = ("T-2026-10-01-140-P1 (GM immediate O-20261001-1108 sec.3 "
              "VOID ruling; action-4 prereg frozen c3c825c2a bm-a r514 "
              "adoption; banned_direction_gate ADMIT rc0 re-verified)")
PREREG_REF = ("research/LOWAMP-P2.md (exit-axis explicit gate FIRST "
              "application: sec.0.6 hold-through + engine default exit "
              "stack disabled key-by-key in runner params; cutoff "
              "2026-09-22 D2; evidence_cutoff 2026-09-22)")
GATES = ("in-runner FAIL-CLOSED: probe.json PASS required before ignition "
         "(G-CENSUS 1254/1506 + adj 19/19 + cutoff end-row==2026-09-22 + "
         "cost x1 rt 26.082bp single-source + D6 max|corr| fresh probe "
         "0.1738 vs 0.7 + closed_family open); per-start JSONL checkpoint "
         "resume (t22 pattern); idempotent no-op when shard complete; "
         "engine canon T+1, exit priority frozen, engine/ zero-mod; "
         "sec.0.6 HOLD-THROUGH exit-axis (default stack disabled in "
         "runner params, six keys, prereg verbatim)")


def q(s):
    return json.dumps(s, ensure_ascii=False)


def entry(eid, args, shard_key, note=None):
    sh = [f'{{\r\n"key": {q(shard_key)},\r\n"status": "ready",\r\n'
          f'"checkpoint": "results/lowamp_p2/ JSONL per-start append, '
          f'done-key skip"']
    if note:
        sh.append(f',\r\n"note": {q(note)}')
    sh.append("\r\n}")
    shard_txt = "".join(sh)
    runner_args = ",\r\n".join("        " + q(a) for a in args)
    runner_args = ",\r\n".join(q(a) for a in args)
    return (f'{{\r\n"id": {q(eid)},\r\n'
            f'"ticket_ref": {q(TICKET_REF)},\r\n'
            f'"prereg_ref": {q(PREREG_REF)},\r\n'
            f'"runner": "scripts/lowamp_p2.py",\r\n'
            f'"runner_args": [\r\n{runner_args}\r\n],\r\n'
            f'"lane_owner": "ANY",\r\n'
            f'"priority": 0,\r\n'
            f'"status": "ready",\r\n'
            f'"entered_at": {q(NOW)},\r\n'
            f'"entered_by": "bm-a (OS iteration loop r514)",\r\n'
            f'"data_gates": {q(GATES)},\r\n'
            f'"workers_plan": {{\r\n"workers": 12,\r\n'
            f'"priority": "BelowNormal"\r\n}},\r\n'
            f'"shards": [\r\n{shard_txt}\r\n]\r\n}}')


blocks = []
for cell in ("LA-REP", "LA-EQ", "LA-T3", "LA-EDGE"):
    for axis in ("legacy", "deep"):
        for face in ("base", "x2"):
            # r494 key-drift law: _entry_of computes
            # cell.replace("-", "").upper() -- pool id MUST mirror it
            eid = ("LOWAMP-P2-CELL-" + cell.replace("-", "").upper()
                   + "-" + axis.upper() + "-" + face.upper())
            key = eid.lower() + "-0of1"
            blocks.append(entry(
                eid, ["run", "--cell", cell, "--axis", axis, "--face", face],
                key))
blocks.append(entry(
    "LOWAMP-P2-NULLS", ["run", "--nulls"], "lowamp-p2-nulls-0of1",
    "K=2000 same-mask random selection nulls, legacy full panel, "
    "rng([20334500,k]) per prereg sec.3 verbatim; feeds skill_line_v2 "
    "null_pool; N_eff face: net ledger head + 2008"))
blocks.append(entry(
    "LOWAMP-P2-SENS", ["run", "--sensitivity"], "lowamp-p2-sens-0of1",
    "N=500 space-filling draws over W77-104/N{2,3}/{invvol,eq}, legacy "
    "full panel, rng([20333500,k]); descriptive face only; exit-axis "
    "hold-through same face per prereg sec.3"))
assert len(blocks) == 18, len(blocks)

# --- raw-text anchored insertion: before the final ']' ----------------
tail_re = re.compile(r"\](\r\n)\}(\r\n)?$")
m = tail_re.search(raw)
assert m, "pool tail shape unexpected"
insert = "".join(",\r\n" + b for b in blocks)
new = raw[:m.start()] + insert + raw[m.start():]
pool = json.loads(new)          # parse-verify BEFORE write
assert len(pool["entries"]) == 273 + 18, len(pool["entries"])
p2 = [e for e in pool["entries"] if e["id"].startswith("LOWAMP-P2-")]
assert len(p2) == 18 and all(e["status"] == "ready" for e in p2)
open(POOL, "wb").write(new.encode("utf-8"))
print(f"\nwrote {POOL}: +18 entries (total {len(pool['entries'])})")
print("first new block preview:")
print(repr(blocks[0][:400]))
