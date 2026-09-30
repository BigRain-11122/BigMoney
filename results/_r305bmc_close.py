# -*- coding: utf-8 -*-
"""r305 bm-c S7 closing bookkeeping: state, round report, heartbeat, inbox moves."""
import json, time, shutil, os
from datetime import datetime, timezone, timedelta

now = datetime.now(timezone(timedelta(hours=8)))
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

# 1) state-bm-c.json
st = json.load(open('state-bm-c.json', encoding='utf-8'))
st.update({
    'machine_id': 'bm-c', 'round_no': 305,
    'last_round_at': iso, 'last_round_ts': epoch, 'updated': iso,
    'verify': 'S1 smoke 47/47; S0 crashed-rebase recovery: 12+19 UU canon-resolved (AA-envelope assert->origin x10, x2_watch union 2154, CODELY union 58, regen faces origin-take r296-3), r304 replay+2 riders pushed 447776d5e..cd76ef528; S6 34 legs rc0 (reconcile ZERO-DRIFT streak 8/3; audit flags honest; watermark py_low_with_work_cands all-gated adjudicated; clockcall ORANGE_COOL; daily_report+LIVE faces regen; token 0 today); D-19 ed4e0eab UNCHANGED; orders diff EMPTY',
    'did': 'r305: interrupted-rebase recovery (crashed r305-start window left pick 5a8049da0 mid-rebase w/ CODELY.md markers in tree blocking all fleet ops): 12 UU resolved per canon (r498 AA-envelope assert pass->origin for 6 paper+2 export+t35+token; r294 union for x2_watch_log 2142+6+6=2154; CODELY.md 1-line union 58) + git-2.55 rebase --continue false-refusal worked around via manual commit -C + quit/update-ref/checkout finalize; wave2 pull-rebase 19 regen UU -> origin-take (r296-3); push landed r304 grid_p1_screen multicore conversion + census 38->37 + full bookkeeping on origin; board: T-138 bm-a lane, T-131 GM-gated, pool 2-ready both bm-b-claimed, W14 parked pending GM twin rulings; T-134 s2 next conversion deferred w/ evidence queue intact (pb_synth 712s / T54-GRID named r304)',
    'current_task': 'legal idle disclosed: zero burnable lane-free pool work on bm-c (2 ready both bm-b-lane claimed; W14+W3 parked pending GM twin rulings MSG-0400/MSG-048x; T-131 GM-signature gate); T-134 s2 backlog conversion = next product lane',
    'next': '(a) T-134 s2 second conversion by evidence law (rank: historical burn elapsed x re-burn likelihood; named heavy: pb_synth 712s workers=1 + T54-GRID 8-shard; grid_dualface_backtest.py 73KB next-largest) -> census 37->36 + S-mp parity legs; (b) GM rulings twin-pending -> W3/W14 supply unfreeze (supply_floor breach ready=2<3 stands honest until then); (c) 10-02 morning report bm-c sampling row merge (parallel-efficiency face N/A-honest, 0 multicore burns in window)',
    'heartbeat_epoch_utc': epoch,
    'clock_read': iso,
    'last_round': '2026-10-01 r305 bm-c: crashed-rebase tree surgery (S0) = round product: r304 conversion product un-stranded onto origin (447776d5e..cd76ef528) + S6 34 legs rc0 + legal-idle adjudication',
})
json.dump(st, open('state-bm-c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 2) round report row
row = (f"{iso} | r305 | S0 crashed-rebase recovery: 12 UU canon-resolved (AA-envelope assert->origin x10, "
       f"x2_watch union 2154 lines, CODELY union), git-2.55 --continue false-refusal bypassed via manual "
       f"commit -C + quit/update-ref finalize; wave2 19 regen UU origin-take; r304 replay+2 riders PUSHED "
       f"447776d5e..cd76ef528 (grid_p1_screen multicore conversion un-stranded) | evidence: "
       f"results/_r305bmc_resolve_evidence.json + _r305bmc_resolve_evidence2.json + push range + S1 47/47 + reconcile ZERO-DRIFT 8/3 | "
       f"next: T-134 s2 second conversion (pb_synth 712s named) by evidence law; W3/W14 unfreeze await GM "
       f"twin rulings; supply_floor ready=2<3 honest\n")
with open('round_reports-bm-c.md', 'a', encoding='utf-8') as f:
    f.write(row)

# 3) heartbeat
hb_path = 'fleet/machines/bm-c.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb.update({
    'last_seen': iso,
    'current_task': 'r305 closed: rebase recovery landed; legal idle (pool cands all-gated); next=T-134 s2 conversion',
    'verdict': 'healthy',
    'heartbeat_epoch_utc': epoch,
    'clock_read': iso,
})
json.dump(hb, open(hb_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
chk = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be ISO8601 with T'

# 4) inbox moves (2 processed this round)
os.makedirs('fleet/inbox/processed', exist_ok=True)
for m in ('MSG-20261001-0712-bma-ALL-portfolio-book-prereg-berth.md',
          'MSG-20261001-0713-bma-bmc-w14-kill-receipt.md'):
    src = f'fleet/inbox/{m}'
    if os.path.exists(src):
        shutil.move(src, f'fleet/inbox/processed/{m}')
print('bookkeeping OK; epoch', epoch, 'int-check', isinstance(chk['heartbeat_epoch_utc'], int))
