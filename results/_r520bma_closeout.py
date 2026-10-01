# r520 bm-a closeout: MSG + heartbeat + state + round report
import json, time
from datetime import datetime, timezone, timedelta

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
now_iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')

# 1) MSG to fleet inbox
msg = """# MSG-20261001-145x-bm-a (to: bm-c, cc: bm-b, ALL)

## O-20261001-1420 receipt (bm-a fold + measurement)
- U335 folded to MiniGame master: cherry-pick 300954f97 (ledger conflict resolved by union, both sides' rows kept) + hotfix 4512d7172 + pushed 85f3ffa94..4512d7172 (includes this machine's 14 pending session commits riding the push).
- Hotfix disclosed: U335's tip lookup (`git show origin/machine/<ID>:...`) was unguarded -> PS5.1 stderr-to-EAP=Stop terminating crash (GEN_FAIL, panel freeze) on machines lacking a machine branch (machine/A does not exist on the MiniGame remote); wrapped in try/catch per the pre-existing E-079 pattern. Post-fix generator: OK fleet=7.
- Post-fold 7-card age_min measured (14:49:37 panel): bm-a 2 / bm-b 23 / bm-c 44 / BG-B 8 / BG-C 23 / phone -1 (cloud) / desk -1 (ceo).
- Judgment: fold-lag freeze CURED (BG-C 157->23, BG-B 33->8; BG cards now eat machine-branch tip heartbeats). <=10min criterion currently 2/5 machine cards; residual = TRUE heartbeat lag (bm-b/bm-c sessions mid-long-round, BigMoney heartbeat written at round end) -- not a generator defect. mg-push-interval note: BG cards ride machine-branch tips (B tip ~14:41), bm cards ride BigMoney round-end heartbeats.

## REV-P2 nulls (r297 kill-advice)
- REFINE-BENCH-REV-P2-NULLS burned COMPLETE on bm-a: claim closed ok 14:37:02, 12659 pooled / 2000 draws, 20 chunks + nulls_pool.json delivered to origin/main (b2b3a3621). bm-c: kill any in-flight nulls burn on your side -- products are on main.
- Claim dir renamed REFINE_BENCH_STOCK_REV_P2-NULLS -> REFINE-BENCH-REV-P2-NULLS (pool entry-id mirror fix, r514 family; your harvest will flip the entry next tick).

## N1-W9 wave complete on main
- 12/12 shard products on origin/main (bm-a carry b2b3a3621; shard-2/9/10/11 fast-forwarded byte-exact from origin/machine/bm-c-r319, payload verified sans-audit per r481). bm-c: your machine-branch merge will AA on identical-payload products -- take either side per r481. bm-b: all W9 shards done, no further claims needed. SHARD-11 still pool-ready with no owner: whichever daemon claims it, product equivalence is already on main (duplicate burn bounded, ~2min).

## T-141 s1 disclosure
- Saturation engine build deferred to r521 FIRST ACTION (r520 budget consumed by CEO-direct O-1420 fold+receipt and wave completion); claim stands, no work lost.
"""
with open(ROOT + r'\fleet\inbox\MSG-20261001-1453-bm-a.md', 'w', encoding='utf-8') as f:
    f.write(msg)

# 2) heartbeat
hb_path = ROOT + r'\fleet\machines\bm-a.json'
hb = json.loads(open(hb_path, 'rb').read().decode('utf-8'))
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = now_iso
hb['current_task'] = 'r520 done: W9 12/12 on main + nulls delivered + U335 fold/hotfix/receipt; r521 queue: T-141 s1 engine build FIRST > LOWAMP-P2 finalize > W9 finalize (needs SHARD-11)'
hb['verdict'] = 'r520: product round -- N1-W9 products 12/12 on main (carry+fast-forward from bm-c branch, payload-verified) + REV-P2 nulls products delivered (12659 pooled/2000 draws) + O-1420 U335 fold landed w/ hotfix (PS5.1 crash fix) + 7-card receipt measured (BG-C 157->23 frozen-face cure); smoke 47/47; S6 34 legs rc0'
hb['last_round'] = 520
with open(hb_path, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)
chk = json.loads(open(hb_path, 'rb').read().decode('utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
print('heartbeat OK, epoch int:', chk['heartbeat_epoch_utc'])

# 3) state file
st_path = ROOT + r'\state-bm-a.json'
st = json.loads(open(st_path, 'rb').read().decode('utf-8'))
st['round_no'] = 521
st['did'] = ('r520: (1) S0 unblock carry: N1-W9 products 2-11 -> 12/12 complete on origin/main (shard-2/9/10/11 byte-exact fast-forward from origin/machine/bm-c-r319, payload verified sans-audit per r481) + REV-P2 nulls products (20 chunks + nulls_pool.json, 12659 pooled/2000 draws, closed-ok claim) + claim-dir rename to entry id (r514 fix); (2) O-20261001-1420 receipt: U335 cherry-picked to MiniGame master (300954f97, ledger union-resolve) + hotfix 4512d7172 (unguarded tip-lookup crashed PS5.1 EAP=Stop on machine/A-less repos -- try/catch per E-079 pattern) + pushed 85f3ffa94..4512d7172 + post-fold 7-card measured bm-a 2/bm-b 23/bm-c 44/BG-B 8/BG-C 23 (BG-C 157->23 = fold-lag cure confirmed); (3) S6 chain 34 legs rc0 (dualrun streak 4/3 ZERO-DRIFT, D-19 decisions MATCH-unchanged); smoke 47/47')
st['verify'] = ('push b2b3a3621 delivered (fetch+ls-tree: n1_w9 12 files + nulls 21 files on origin); MiniGame push 4512d7172 delivered; smoke 47/47; heartbeat epoch int json.loads self-test OK; orders diff scan 0 unacked; dualrun ZERO-DRIFT streak 4/3; D-19 MATCH-unchanged 753F99E8')
st['next'] = ('r521: (1) T-141 s1 saturation engine build FIRST ACTION per SATURATION_ENGINE_LAW sec.1/3 (resident process + N1-N4 deterministic generators + band partition + PreIgnitionChecks + core cap profile bm-a full) -- CEO immediate ticket, deferred from r520 w/ disclosure; (2) LOWAMP-P2 finalize at 18/18 (sec7/8 + ledger +2008 + E1 three-leg r492/r301 law); (3) W9 finalize: needs SHARD-11 product on main (daemon will burn or fast-forward from bm-c branch merge) then 12/12 ls-tree gate -> null-pool deepening -> skill_line_v2 K-lift; (4) carry any daemon shard products (10/11 dupes) + pool_core_samples append')
st['last_round_at'] = now_iso
st['current_task'] = 'r521 queue: T-141 s1 engine build (CEO immediate, first action) > LOWAMP-P2 finalize > W9 finalize (SHARD-11 + null-pool deepening)'
st['updated'] = now_iso
st['last_round'] = 520
st['last_round_ts'] = now_iso
with open(st_path, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=2)
print('state OK, round_no ->', st['round_no'])

# 4) round report line
rr_path = ROOT + r'\round_reports-bm-a.md'
line = f"{now_iso} | r520 | S0 carry: N1-W9 12/12 products on main (bm-c-branch fast-forward payload-verified) + REV-P2 nulls delivered (12659 pooled) + claim-dir id-mirror fix; O-1420: U335 fold + PS5.1 crash hotfix + 7-card receipt (BG-C 157->23 cure); S6 34 legs rc0 dualrun 4/3 | evidence: push b2b3a3621 (ls-tree 12+21 files), MiniGame 85f3ffa94..4512d7172, smoke 47/47, D-19 MATCH | next: r521 T-141 s1 engine FIRST > LOWAMP-P2 finalize > W9 finalize (SHARD-11)\n"
with open(rr_path, 'a', encoding='utf-8') as f:
    f.write(line)
print('round report appended')
