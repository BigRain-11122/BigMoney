# r588 bm-b books update: state round_no, heartbeat (dynamic fields only, r583 law), round report line
import json, time, datetime, psutil

# 1) state.json round_no 587 -> 588
sp = 'state.json'
d = json.load(open(sp, encoding='utf-8'))
assert d.get('machine_id') == 'bm-b', 'identity anchor fail'
d['round_no'] = 588
now = time.strftime('%Y-%m-%d %H:%M:%S')
iso = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
d['last_round_at'] = now
d['last_round_ts'] = iso
d['ts'] = now
d['updated'] = now
d['updated_at'] = iso
json.dump(d, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state round_no ->', d['round_no'])

# 2) heartbeat: load existing, update dynamic fields only (orders_ack carried per r583 law)
hp = 'fleet/machines/bm-b.json'
h = json.load(open(hp, encoding='utf-8'))
epoch = int(time.time())
clock = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
vm = psutil.virtual_memory()
h['last_seen'] = now
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = clock
h['current_task'] = 'W106 finalize landed (chain head 597,748, K=231,120, S5 4/4); W109 12/12 products delivered to origin; next own finalize seat waits W107(bm-a)/W108(bm-c) chain order'
h['cpu_cores'] = psutil.cpu_count(logical=True)
h['free_ram_gb'] = round(vm.available / 1024**3, 1)
h['round_no'] = 588
h['round_no_label'] = 'r588'
h['verdict'] = 'W106 finalize one-pass landed + S5 4/4 PASS (dmu 0.0012, sigma +1.64%, A-p95 diff +0.0285, K-lift +0.0002); W109 products delivered; S6 33/33 rc0 ZERO-DRIFT 32/3; Golden Week no-new-bar honest face'
json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
h2 = json.load(open(hp, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be JSON int (F7 law)'
assert 'T' in h2['clock_read'], 'clock_read must be T-separated (F7 law)'
assert len(h2.get('orders_ack', [])) >= 143, 'orders_ack list must be carried not rebuilt'
print('heartbeat ok: epoch int', h2['heartbeat_epoch_utc'], 'clock', h2['clock_read'], 'orders_ack', len(h2['orders_ack']))

# 3) round report line
rp = 'logs/iteration-loop/round_reports.md'
line = (f"{now} | r588 | W106 FINALIZE one-pass landed (bm-b own wave, chain head 595,548(W105 bm-c r379)+2,200=597,748, K=231,120, "
        f"skill_line 1.1698->1.17 K-lift +0.0002, se_mu 0.000509; S5 four gates ALL PASS on W100 frozen anchors: |dmu|0.0012<0.02 / sigma +1.6352%<10% / A-p95 diff +0.0285<0.05 / K-lift +0.0002>=-0.02) "
        f"+ prereg SS7/SS8 mechanical backfill (r307 same-round law) + n1 default-wave selftest PASS + pf 9/9 + W109 12/12 shard products delivered to origin (bm-b 37th owned wave, burn completed 18:36 engine tick) "
        f"+ S6 33/33 rc0 (dualrun ZERO-DRIFT 32/3 cutoff 2026-10-01; Golden Week honest no-new-bar LAST_BAR=2026-09-30, paper block skipped; lane guards honest no-op; ORANGE_COOL) "
        f"+ S7 self-heal 4/4 (loop pin=2 no-op, watchdog, pre-commit/pre-push claws) + attrition CLEAN + smoke 47/47 + orders 143/143 double-scan + D-19 honest skip (no group tree on bm-b) "
        f"| verification: n1_w106_results.json ledger block prev=595548 batch=2200 total=597748 audit.machine=bm-b; _r588bmb_w106_gates.py 4/4 PASS; selftests green "
        f"| next: W109 finalize waits W107 bm-a -> W108 bm-c chain order (never-dry supply continues); watermark next_pick=moneyflow IC reference batch (panel parked source-blocked 30-min self-heal) | behind-origin-commits=0 (this push)\n")
with open(rp, 'a', encoding='utf-8') as f:
    f.write(line)
print('round report line appended')
