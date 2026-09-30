# r473 bm-b: W14-GENERATE pool park flip per D-20260930-41 sec.1.2 + MSG-20260930-1755-bma-ALL
# vocabulary-legal park: ready -> waiting (waits on RETAIL_QUANT_TRACK sec.4 unfreeze gates)
import json, subprocess, datetime

TS = "2026-09-30T18:4x+08:00"
PARK = {
    "status": "waiting",
    "parked_per": "D-20260930-41 sec.1.2 confirm-type-timing ban (any-confirm-timing family) + MSG-20260930-1755-bma-ALL bm-a r483 adjudication; receipt bm-b r473",
    "parked_at": TS,
    "unfreeze_gate": "research/RETAIL_QUANT_TRACK.md sec.4 gates (trial-budget attribution, <=500/30d) + sec.1.2 compliance self-proof; berth+drafts archived intact (probe facts not invalidated clause)",
}

def load_raw(p):
    return open(p, "rb").read()

def flip_pool(p):
    raw = load_raw(p)
    d = json.loads(raw)
    hit = None
    for e in d["entries"]:
        if e.get("id") == "TRIAL-LABOR-W14-GENERATE":
            hit = e
            break
    assert hit is not None, "W14-GENERATE entry absent in " + p
    before = {"entry_status": hit.get("status"), "shard_status": hit["shards"][0].get("status")}
    if before["entry_status"] == "waiting" and hit.get("parked_per"):
        return {"file": p, "skip": "already parked (idempotent)"}
    assert before["entry_status"] == "ready", before
    hit["status"] = PARK["status"]
    hit["parked_per"] = PARK["parked_per"]
    hit["parked_at"] = PARK["parked_at"]
    hit["unfreeze_gate"] = PARK["unfreeze_gate"]
    sh = hit["shards"][0]
    sh["status"] = "waiting"
    sh["park_note"] = "parked pre-burn: w14_candidates.json absent = zero generate burn, trial-gate consumption N=0 (CEO anti-waste law FB-004 honored)"
    d["updated_at"] = TS
    body = json.dumps(d, indent=2, ensure_ascii=False)
    data = body.replace("\n", "\r\n").encode("utf-8")
    # byte-format mirror check: original must be indent=2 CRLF ensure_ascii=False round-trip
    probe = json.dumps(d, indent=2, ensure_ascii=False).replace("\n", "\r\n").encode("utf-8")
    assert probe == data
    open(p, "wb").write(data)
    json.loads(open(p, "rb").read())
    return {"file": p, "before": before, "after": {"entry_status": hit["status"], "shard_status": sh["status"]}}

rep = [flip_pool("results/runnable_pool.json"), flip_pool("results/runnable_pool.bm-b.json")]

# ---- T-128 progress receipt
tp = "fleet/tasks/T-2026-09-30-128-P1.json"
raw = load_raw(tp)
t = json.loads(raw)
line = ("[2026-09-30 18:4x bm-b r473] PARK RECEIPT: MSG-20260930-1755-bma-ALL consumed -- W14 dual drafts (RESI resi60_hi + CNT cntd5_hi/cntn20_lo) = "
        "confirm-type timing family under ORDER D-20260930-41 sec.1.2 banned face; park upheld, NO objection filed. "
        "TRIAL-LABOR-W14-GENERATE pool entry flipped ready->waiting (both shared+lane pool files, vocabulary-legal) "
        "BEFORE any fleet autofill claim burn: w14_candidates.json absent = generate never burned, trial-gate consumption N=0. "
        "Runner (scripts/trial_labor_w14.py selftest 53/53, grammar sha16 a231bf10940e7878) + probe facts + seeds archived intact "
        "per MSG-1755 'probe facts not invalidated' clause -- ready berth if CEO unfreezes. "
        "Unfreeze path = research/RETAIL_QUANT_TRACK.md sec.4 gates + sec.1.2 compliance self-proof. "
        "Supply energy pivots to RETAIL_QUANT_TRACK five priorities per canon sec.2 (non-stop-work).")
prog = t.get("progress")
if isinstance(prog, list):
    prog.append(line)
elif isinstance(prog, str):
    t["progress"] = (prog + "\n" if prog else "") + line
else:
    t["progress"] = [line]
body = json.dumps(t, indent=2, ensure_ascii=False)
crlf = "\r\n" in raw.decode("utf-8", "replace")[:400]
data = (body.replace("\n", "\r\n") if crlf else body).encode("utf-8")
open(tp, "wb").write(data)
json.loads(open(tp, "rb").read())
rep.append({"file": tp, "progress_appended": True, "status_left_unchanged": t.get("status")})

print(json.dumps(rep, ensure_ascii=False, indent=1))
