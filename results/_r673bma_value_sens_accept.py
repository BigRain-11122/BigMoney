# r673 bm-a: FUND-VALUE-P1-SENS burn acceptance receipt (the 1/3 missing leg of the
# trio finalize-readiness evidence chain; siblings r629 QUALITY / r630 DIVLOWVOL).
# Live-computes every leg from primary evidence, writes sens_acceptance.json, reparse-verifies.
import json, hashlib, os, subprocess, datetime

FAM = 'fund_value_p1'
ROWS = f'results/{FAM}/sens.jsonl'

# --- A: rows unique contiguous + schema ret numeric
lines = [json.loads(l) for l in open(ROWS, encoding='utf-8') if l.strip()]
ks = sorted(r['k'] for r in lines)
A_rows = len(lines) == 500 and ks == list(range(500))
A_schema = all(isinstance(r.get('ret'), (int, float)) and not isinstance(r.get('ret'), bool) for r in lines)
# --- A2: provenance uniformity (re-burn rows)
A2_machine = set(str(r.get('burn_machine')) for r in lines) == {'bm-b'}
A2_reason = set(str(r.get('redo_reason')) for r in lines) == {'off-caliber-reburn-2026-10-03'}
A2_digest_single = set(str(r.get('cache_digest')) for r in lines) == {'6c586d0872ca81e3'}

# --- B: claim closures (superseded first burn + final redo burn)
ca = json.load(open('results/pool_claims/FUND-VALUE-P1-SENS/fund-value-p1-sens-0of1.bm-a.json', encoding='utf-8'))
cb = json.load(open('results/pool_claims/FUND-VALUE-P1-SENS/fund-value-p1-sens-0of1.bm-b.json', encoding='utf-8'))
B_first = f"bm-a {ca['started']} -> {ca['closed_at']} exit={ca['exit_code']} (OFF-CALIBER first burn, rows discarded per containment r615/r617)"
B_final = f"bm-b redo {cb['started']} -> {cb['closed_at']} exit={cb['exit_code']} outcome={cb['outcome']}"

# --- C: pool entry truth
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
entry = next(e for e in pool['entries'] if e['id'] == 'FUND-VALUE-P1-SENS')
sh = entry['shards'][0]
C = {'status': entry['status'], 'shard_status': sh['status'], 'shard_owner': sh['owner'],
     'shard_owner_since': sh['owner_since'], 'shard_done_at': sh.get('done_at'),
     'harvest_claim': sh.get('harvest_claim')}

# --- D: origin blob present + EOL-normalized byte-equal (r660 law: LF-canon sha)
ob = subprocess.run(['git', 'show', 'origin/main:results/fund_value_p1/sens.jsonl'], capture_output=True).stdout
lb = open(ROWS, 'rb').read()
D_present = len(ob) > 0
D_equal = lb.replace(b'\r\n', b'\n') == ob
D_sha = hashlib.sha256(ob).hexdigest()

# --- E: T-156 four-point receipt (shared verified-cache face, r627 bm-a)
fp = json.load(open('results/_r627bma_t156_fourpoint.json', encoding='utf-8'))
E_keys = sorted(fp.keys())
E_pass = fp.get('pass', False)

# --- F: byte-identity caliber proof -- local T-156-verified cache digest == row digest
import sys
sys.path.insert(0, 'scripts')
import fund_value_p1 as fv
h = hashlib.sha256()
for name in ('volume.npy', 'amount.npy'):
    with open(os.path.join(fv.P1C.CACHE_DIR, name), 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b''):
            h.update(chunk)
F_digest = h.hexdigest()[:16]
F_match = F_digest == '6c586d0872ca81e3'

receipt = {
 "acceptance": "FUND-VALUE-P1-SENS burn acceptance (r673 bm-a)",
 "ts": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
 "machine": "bm-a",
 "legs": {
  "A_rows_500_unique_contiguous": A_rows,
  "A_row_schema_ret_numeric": A_schema,
  "A2_rows_all_burn_machine_bm_b": A2_machine,
  "A2_rows_all_redo_reason_offcaliber": A2_reason,
  "A2_cache_digest_single_valued": A2_digest_single,
  "B_superseded_first_burn": B_first,
  "B_final_redo_burn": B_final,
  "C_entry_status": C['status'], "C_shard_status": C['shard_status'],
  "C_shard_owner": C['shard_owner'], "C_shard_owner_since": C['shard_owner_since'],
  "C_shard_done_at": C['shard_done_at'], "C_harvest_claim": C['harvest_claim'],
  "D_origin_blob_present": D_present,
  "D_eol_normalized_byte_equal": D_equal,
  "D_lf_canon_sha256": D_sha,
  "E_t156_fourpoint_keys": E_keys,
  "E_pass": E_pass,
  "E_fourpoint_ts": fp.get('ts'),
  "F_local_verified_cache_digest": F_digest,
  "F_row_digest_byte_identity": F_match
 },
 "all_pass": all([A_rows, A_schema, A2_machine, A2_reason, A2_digest_single,
                  C['status'] == 'done', C['shard_status'] == 'done',
                  D_present, D_equal, E_pass, F_match]),
 "note": ("Re-burn face (r611 AA-replace): first bm-a burn 04:18-04:48 on off-caliber local cache "
          "discarded per containment r615/r617; final rows all burn_machine=bm-b redo_reason=off-caliber-reburn "
          "with row-level cache_digest 6c586d0872ca81e3 == local T-156 four-point-verified cache content digest "
          "(byte-identity caliber proof, computed live this receipt). Descriptive face no verdict; prereg "
          "research/FUND-VALUE-P1.md FROZEN (sens 500 rng([20500500,k])). G-SEG governance adjudicated "
          "O-20261004-0808 item-2: insufficient-sample frozen path, window 10-06..09 closed by that ruling; "
          "finalize waits bm-b nulls 2000-draw (ETA 10-06/07 per rate 0.39/min).")
}
out = json.dumps(receipt, ensure_ascii=False, indent=1) + '\n'
open(f'results/{FAM}/sens_acceptance.json', 'wb').write(out.encode('utf-8'))
# reparse self-check
json.loads(open(f'results/{FAM}/sens_acceptance.json', encoding='utf-8').read())
print('RECEIPT WRITTEN, all_pass =', receipt['all_pass'])
for k, v in receipt['legs'].items():
    print(' ', k, '=', v)
