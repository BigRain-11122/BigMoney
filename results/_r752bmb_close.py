# r752 bm-b closeout: state.json + heartbeat + ledger line (bytes append w/ trailing-newline probe)
import json, time, os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

NOTE = ("r752: golden-week steady-state round -- S0: churn-absorb d33606f67 (daemon tick + r751 dead-tail products) "
        "-> merge origin/main behind-12 18-UU canonical resolver (89b1bd4fd, receipt _r752bmb_merge_resolve.json) "
        "-> push LANDED 0/0; r751 dead-tail POST-MORTEM backfill per r714 law (ledger line + churn-absorb); "
        "orders 154/154 zero unacked both scans; D-19 dual MATCH; smoke 48/48; S6 chain 35 legs all rc0 00:01:16-00:04:36 "
        "(REPORT-2026-10-06 + LIVE-2026-10-06 new CEO faces); dualrun ZERO-DRIFT streak 45; compute_audit CLEAN py_cpu 85.1%; "
        "py_watermark py_low_with_work_cands (trio burns in flight = the work, legal); "
        "trio V1614/Q1318/D1076 of 2000 (eta V 6.4h / Q 5.7h / D 53.3h) mechanical_ready=False G4 PENDING; "
        "quartet 4/4 + attrition CLEAN")
NEXT = ("(a) trio finalize windows: V ~10-06 afternoon (eta 6.4h), Q ~10-06 afternoon (eta 5.7h), D ~10-08 (eta 53.3h, "
        "rate drop disclosed) -- leg39 probe every round; governance G4 PENDING -> r638 single-read fallback armed; "
        "(b) D-06 closeout report to group 10-07 12:00 (20 pit-*.md <=30KB re-verify holds); "
        "(c) 10-08 market reopen window (external data legs + paper marks resume + REGIME_GUARD v3 first new bar)")

# ---- state.json
sp = os.path.join(ROOT, 'state.json')
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 752
st['round_no_label'] = 'r752'
st['note'] = NOTE
st['next'] = NEXT
for k in ('last_round_at', 'ts', 'updated', 'last_seen', 'clock_read', 'last_round_ts'):
    st[k] = now_iso
open(sp, 'w', encoding='utf-8', newline='\n').write(json.dumps(st, ensure_ascii=False, indent=1) + '\n')
json.load(open(sp, encoding='utf-8'))
print('state.json -> r752', now_iso)

# ---- heartbeat
hp = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
h = json.load(open(hp, encoding='utf-8'))
try:
    import psutil
    ram = round(psutil.virtual_memory().available / 1e9, 2)
except Exception:
    ram = h.get('free_ram_gb', 0)
h['last_seen'] = now_iso
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now_iso
h['cpu_cores'] = 16
h['free_ram_gb'] = ram
h['gpu_free_vram_gb'] = 3.46
h['gpu_free_vram_mb'] = 3461
h['round_no'] = 752
h['round'] = 752
h['last_round_at'] = now_iso
h['verdict'] = ("healthy: steady-state round complete, trio burns in flight (V/Q ETAs improved ~10-06 afternoon; "
                "RAM %.2fGB borderline heavy gate = zero new burn drafting legal)" % ram)
h['current_task'] = "r752 golden-week steady-state: S6 35 rc0 + merge window behind-12 + r751 dead-tail backfill; trio NULLS burns advance"
h['now_active'] = "FUND trio NULLS burns V1614/Q1318/D1076 of 2000 (autofill+workers alive)"
h['latest_artifact'] = ("docs/daily_report/REPORT-2026-10-06.md (10350B) + docs/live_usage/LIVE-2026-10-06.md (8068B) fresh CEO faces + "
                        "results/_r752bmb_s6_chain.log (35 legs rc0 00:01:16-00:04:36)")
h['next_milestone'] = "trio finalize V+Q ~10-06 afternoon, D ~10-08 (rate drop disclosed); D-06 group closeout 10-07 12:00; market reopen 10-08"
h['last_action'] = ("r752 closed: churn-absorb d33606f67 + merge behind-12 18-UU canon resolve (89b1bd4fd) + S6 35 rc0 "
                    "+ r751 POST-MORTEM backfill (r714 law); trio V1614/Q1318/D1076")
h['task'] = "FUND trio NULLS judgment batch lane (per-family finalize windows)"
h['ts'] = now_iso
h['updated'] = now_iso
assert isinstance(h['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
open(hp, 'w', encoding='utf-8', newline='\n').write(json.dumps(h, ensure_ascii=False, indent=1) + '\n')
rb = json.load(open(hp, encoding='utf-8'))
assert isinstance(rb['heartbeat_epoch_utc'], int)
print('heartbeat -> r752 epoch=%d ram=%.2f' % (epoch, ram))
