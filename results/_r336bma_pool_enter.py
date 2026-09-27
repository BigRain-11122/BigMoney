import io, json, time

TS = time.strftime('%Y-%m-%d %H:%M:%S')

# 1) pool entry append
p = 'results/runnable_pool.json'
d = json.load(io.open(p, encoding='utf-8'))
assert not any(e.get('id') == 'SINA-CONSTRUCT-P1' for e in d['entries']), 'duplicate entry'
entry = {
    "id": "SINA-CONSTRUCT-P1",
    "ticket_ref": "T-2026-09-25-46-P1 sina-construct leg (sibling of parked EM face MF_IC_P1; lane pick (a) data-host local burn MSG-20260927-1615 bm-a; both two-conditions met r333 bm-b: runner commit 6c9fb92f + prereg FROZEN commit f5acd8fa; F-04 MSG-20260927-1642 burn-unblock receipt to bm-a)",
    "prereg_ref": "research/SINA_CONSTRUCT_P1.md FROZEN v1.0 commit f5acd8fa (R99 independent freeze, zero cells burned, sec.7/sec.8 empty placeholders); seeds sina_construct_p1=58_550 band 58_550..58_649 registered inside freeze commit (rg full-repo scan clean r333); N_eff=5 constructs + per-construct K=100 same-mask within-day permutation nulls; IC 3-gate V1/V2/V3 h10 sole gating horizon (h5/h20 report-only), IS>=100/OOS>=30 positional 2/3 split, cross-section n>=1000 per signal day",
    "runner": "scripts/sina_construct_ic.py",
    "runner_args": ["run"],
    "lane_owner": "bm-a",
    "priority": 1,
    "status": "ready",
    "entered_at": TS,
    "workers_plan": {
        "workers": 1,
        "priority": "BelowNormal",
        "note": "single-process L1 per runner CLI (run|selftest only, no worker fan-out); prereg sec.0 cap worker<=12 informational; est 10-20min; C8 semantics preemption->whole-run restart, no intra-run state face (prereg sec.6 engineering note); selftest 9/9 PASS cross-verified on bm-a box r336 (bm-b hermetic 9/9 r333); products results/shortline/sina_construct_p1.json (top-level evidence_cutoff=C2 legal key) + research/shortline/sina_construct_p1_results.csv row-level IC face"
    },
    "data_gates": "in-runner fail-closed exit 2 (prereg sec.2 completeness gate): sina_mf_accept verdict PASS + panel complete + n_symbols>=5000 + eligible signal days>=150; current box face verified r336: accept PASS ts=2026-09-27T15:06:09 + panel cutoff 2026-09-24 complete=true n_symbols=5228 (rows_total 1,294,199); latent_repull_defect_note echoed in audit block (collector face only, first monthly re-pull window ~2026-10-27); D6 real cross-family verdicts compute on bm-a (ths+lhb+EM panels in-place; EM overlap thin 53/5222 -> honest weak_check_insufficient_coverage if overlap<30d per MSG-1642 sec.5)",
    "shards": [{
        "key": "sinac-0of1",
        "status": "ready",
        "owner": None,
        "owner_since": None,
        "checkpoint": None,
        "note": "single shard whole-batch; no intra-run checkpoint by design (C8 whole-run restart semantics prereg sec.6); finalize -> results/shortline/sina_construct_p1.json + research/shortline/sina_construct_p1_results.csv; pool flip to done = round work per r312 law"
    }]
}
d['entries'].append(entry)
d['updated_at'] = TS
d['_stamp_note'] = str(d.get('_stamp_note', '')) + "; SINA-CONSTRUCT-P1 entered r336 bm-a post-unblock (prereg FROZEN f5acd8fa + runner 6c9fb92f both r333 bm-b; F-04 MSG-20260927-1642 burn-unblock received by bm-a before entry)"
io.open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
# round-trip proof
d2 = json.load(io.open(p, encoding='utf-8'))
assert any(e.get('id') == 'SINA-CONSTRUCT-P1' and e['status'] == 'ready' for e in d2['entries'])
print('pool entry appended at', TS, '| total entries:', len(d2['entries']))

# 2) T-46 progress_r336 claim note
tp = 'fleet/tasks/T-2026-09-25-46-P1.json'
t = json.load(io.open(tp, encoding='utf-8'))
t['progress_r336'] = (TS + " sina-construct leg census burn CLAIMED by bm-a (data-host lane pick (a) per MSG-1615; both two-conditions met: runner 6c9fb92f + prereg FROZEN f5acd8fa r333 bm-b; MSG-1642 burn-unblock receipt processed r336): "
    "bm-a box gates verified = sina_mf_accept PASS ts=15:06:09 + panel cutoff 2026-09-24 complete=true 5228 + runner selftest 9/9 PASS cross-verified on bm-a; "
    "pool entry SINA-CONSTRUCT-P1 submitted results/runnable_pool.json status=ready lane_owner=bm-a shard sinac-0of1 single-process L1 est 10-20min (C8 whole-run restart semantics, no intra-run state); "
    "burn executes via autofill C8 pool supervision (O-2100 long-batch law, no inline round-run); EM-face MF_IC_P1 leg stays parked (panel source-blocked, rank-lane self-heal spawned r336)")
t['note_updated_at'] = TS
io.open(tp, 'w', encoding='utf-8').write(json.dumps(t, ensure_ascii=False, indent=1))
t2 = json.load(io.open(tp, encoding='utf-8'))
assert 'progress_r336' in t2
print('T-46 progress_r336 note landed')
