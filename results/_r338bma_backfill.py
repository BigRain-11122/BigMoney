import json
import time

now = time.strftime('%Y-%m-%d %H:%M:%S')
ok = []

# --- Edit 2: gate_attrition entries append (r248 law: entries list) ---
ga = json.load(open('results/gate_attrition.json', encoding='utf-8'))
assert isinstance(ga['entries'], list) and len(ga['entries']) == 59
ga['entries'].append({
    "batch": "SINA_CONSTRUCT_P1",
    "ts": now,
    "kind": "measurement",
    "retro_fill": False,
    "cells_ledger_delta": 0,
    "ledger_total_after": 286551,
    "gates": {
        "v1_is_ic_floor": {"TIER_r0": False, "TIER_r1": False, "TIER_r2": False, "TIER_r3": False, "MAIN": False},
        "v2_is_ir_030": {"TIER_r0": False, "TIER_r1": False, "TIER_r2": False, "TIER_r3": False, "MAIN": False},
        "v3_oos_retention": {"TIER_r0": False, "TIER_r1": False, "TIER_r2": True, "TIER_r3": False, "MAIN": False},
        "d6_cross_family": {"TIER_r0": "ok", "TIER_r1": "ok", "TIER_r2": "reject", "TIER_r3": "reject", "MAIN": "reject"},
        "period_gate": "PASS 243 eligible signal days >= 150; IS 156 / OOS 81 positional 2/3-1/3",
        "null_band": "K=100 same-mask within-day permutation; per-construct p95|IR| 0.1485-0.1662; v1_thr=0.02 floor held",
        "run_face": "two deterministic L1 runs (16:40:09 pid 41360 target_met=True + 16:50:02 pid 44968 pre-flip blind-window duplicate; r312 keep-last, T19 r80 precedent); trials chain single-counted 286546->286551"
    },
    "eliminated": 5,
    "refs": {
        "results": "results/shortline/sina_construct_p1.json",
        "csv": "research/shortline/sina_construct_p1_results.csv",
        "prereg": "research/SINA_CONSTRUCT_P1.md",
        "ticket": "fleet/tasks/T-2026-09-25-46-P1.json",
        "pool": "results/runnable_pool.json#SINA-CONSTRUCT-P1"
    },
    "note": "sina four-tier moneyflow construct family IC census (factor-reference batch, engine cells ledger +0); ALL 5 constructs REJECT: V1 |IS IC| 0.0033-0.0078 < 0.02 floor, V2 |IS IR| 0.051-0.094 << 0.30, V3 only TIER_r2 retains; D6 cross-family EM mf rejects TIER_r2/TIER_r3/MAIN (max|corr| 0.7016-0.738 >= 0.7); OOS IC negative across family; negative verdict final, zero promotion face"
})
with open('results/gate_attrition.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(ga, f, ensure_ascii=False, indent=1)
    f.write('\n')
ok.append('gate_attrition entries 59->60')

# --- Edit 3: pool flip SINA-CONSTRUCT-P1 -> done (r312 flip-law) ---
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
e = next(x for x in pool['entries'] if x.get('id') == 'SINA-CONSTRUCT-P1')
assert e['status'] == 'ready'
e['status'] = 'done'
e['done_at'] = now
e['note_done'] = ("census burn complete + judgment face closed r338 bm-a: first run 16:40:09 pid 41360 (fill latency 4.5min target_met=True) "
                  "+ 16:50:02 pid 44968 pre-flip blind-window duplicate (r312 keep-last convergence, T19 r80 precedent, deterministic "
                  "identical output, trials chain single-counted 286551); ALL 5 constructs REJECT (V1 |IS IC|<0.02 floor / V2 |IS IR|<0.30 / "
                  "V3 only TIER_r2 / D6 EM-mf cross-family rejects TIER_r2,TIER_r3,MAIN); prereg sec.7/sec.8 backfilled same round; "
                  "result_ref=results/shortline/sina_construct_p1.json + research/shortline/sina_construct_p1_results.csv; "
                  "gate_attrition row appended; T-46 progress_r338")
sh = e['shards'][0]
assert sh['key'] == 'sinac-0of1'
sh['status'] = 'done'
with open('results/runnable_pool.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(pool, f, ensure_ascii=False, indent=1)
    f.write('\n')
ok.append('pool SINA-CONSTRUCT-P1 -> done')

# --- Edit 4: T-46 ticket progress_r338 ---
tp = 'fleet/tasks/T-2026-09-25-46-P1.json'
t = json.load(open(tp, encoding='utf-8'))
t['progress_r338'] = (
    "2026-09-27 17:1x sina-construct leg CLOSED (judgment face r338 bm-a): census burn 2x deterministic runs (16:40:09 pid 41360 "
    "target_met=True + 16:50:02 pid 44968 pre-flip duplicate, r312 keep-last, trials chain single-counted 286551); ALL 5 constructs "
    "REJECT -- V1 |IS IC| 0.0033-0.0078 < max(0.02,null p95), V2 |IS IR| 0.051-0.094 < 0.30, V3 only TIER_r2 (OOS same-sign retention), "
    "D6 EM-mf cross-family rejects TIER_r2 (0.720/0.738) TIER_r3 (0.7016) MAIN (0.7278/0.7055); OOS IC negative family-wide; "
    "prereg sec.7/sec.8 one-shot backfilled (negative verdict final, zero promotion, no-flip law); gate_attrition entries row appended; "
    "pool entry flipped done (result_ref=results/shortline/sina_construct_p1.json); latent_repull_defect_note = SINA_MF_PREREG R222 "
    "amendment already-closed face (effective tol=max(PRIMARY_TOL,1e-8*scale)), zero new amendment due before first monthly re-pull "
    "~2026-10-27; MF_IC_P1 EM-face sibling stays parked per sec.9 unchanged"
)
t['note_updated_at'] = now
with open(tp, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(t, f, ensure_ascii=False, indent=2)
    f.write('\n')
ok.append('T-46 progress_r338')

print('; '.join(ok))
