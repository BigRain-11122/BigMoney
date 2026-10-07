# _r855bma_closeout.py -- r855 closeout: round report append (repo ROOT, UTF-8+CRLF), state 854->855, heartbeat full-field update.
import json, time, datetime, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec='seconds')
epoch = int(time.time())

# --- machine vitals (CPU cores, free RAM, GPU VRAM) ---
cores = os.cpu_count()
try:
    import psutil
    ram_free_pct = round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total, 1)
except Exception:
    ram_free_pct = -1
vram_free = 5.45  # from idle_trigger.bm-a.json r855 round-zero face (01:31:58 read)
try:
    it = json.load(open('results/idle_trigger.bm-a.json', encoding='utf-8'))
    vram_free = it.get('vram_free_gb', vram_free)
except Exception:
    pass

# --- round report (repo ROOT canonical, UTF-8 append; legacy head is GBK, appends UTF-8 per r843/r846 law) ---
RR = 'round_reports-bm-a.md'
line = (f"{ts} | r855 | S0: churn absorb x2 + E42 writer-pause rebase (1 UU shared probe face ts-newer --theirs; "
        f"rebase-continue false-refusal 4th-state cured in-round = unrelated unstaged daemon churn absorbed into continue commit, pit->pit-git-resolver.md 30,089B line held; "
        f"main CODELY 30,606B line held no append) | S1: smoke 48/48 | S2: jobs 0, orders 51/51 acked (md-ext diff), DEC/ORD hash identical zero-action (ee659451/2bb2ee75) | "
        f"S3 main product: OSS S5-01 vibe-astock admission probe GO (probe scripts/_r855bma_vibe_probe.py rc0; evidence results/oss_eng_scan/vibe-probe-20261008.json; "
        f"emotion_metrics.py 19.9KB pure-compute ref archived; cycle_position 3-axis score formula extracted=(limit_up+max_consec+(1-broken_rate))/3 minmax 10d; "
        f"channels akshare zt_pool_em/zbgc/dtgc all present local 1.18.96; zero-dup PASS theme_event_library L261 deferred gap; ledger section-7 appended +13/-0; "
        f"next=update_zt_pool.py collector gate leg -> prereg admission replay) | watermark: green py_low_board_clear | saturation engine alive (hb 27s, queue 0, burns 0) | "
        f"idle: green_idle=false (VRAM 5.45<6), idle_rounds=0 | orphan face=1 read-only (BigDomain 41108 cross-company) | "
        f"S6: 38/38 rc0 (dualrun streak 51 zero-drift; compute_audit FLAG pool_starvation+supply_floor=trial-labor line in motion via OSS admission; py_watermark py_low_board_clear; "
        f"all collector gates honest no-op pre-open; reports daily_report 10-08 + ceo_live + scorecard + build_status + token L2 0 today) | "
        f"S7: attrition CLEAN; loop pin=8 no-op; watchdog re-registered; claws 4/4; "
        f"verify: smoke 48/48, S6 38/38 rc0, probe rc0, ledger +13/-0, not-at-origin=N post-push | "
        f"next r856: update_zt_pool.py zt-pool forward collector gate (bm-a lane, wiring skill paradigm) + 15:30 reopen chain re-arm + W181 seat watch\n")
with open(RR, 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report appended')

# --- state file 854 -> 855 ---
ST = 'state-bm-a.json'
st = json.load(open(ST, encoding='utf-8'))
st.update({
    'round': 855, 'round_no': 855, 'loop_round': 'r855', 'last_round': 'r855',
    'last_round_at': ts, 'last_round_ts': ts, 'last_run': ts, 'last_seen': ts, 'updated': ts, 'ts': ts,
    'clock_read': ts,
    'current_task': 'r855 closed: OSS S5-01 vibe-astock admission probe GO + S6 38/38 + S7 quartet; next=update_zt_pool.py collector gate leg',
    'did': ('r855: S0 churn absorb x2 + E42 rebase (probe-face UU ts-newer --theirs; rebase-continue 4th-state false-refusal cured = '
            'unrelated daemon churn absorbed into continue commit, pit appended pit-git-resolver.md) + OSS S5-01 vibe-astock admission probe GO '
            '(evidence vibe-probe-20261008.json rc0; emotion_metrics pure-compute ref archived; cycle_position 3-axis formula extracted; '
            'akshare zt_pool 3-endpoint local-ready; zero-dup theme_event_library L261; ledger section-7) + smoke 48/48 + orders 51/51 + '
            'DEC/ORD identical + S6 38/38 rc0 + attrition CLEAN + orphan face=1 read-only'),
    'last_action': 'OSS S5-01 vibe-astock admission probe GO landed (ledger section-7 + evidence + ref archive)',
    'heartbeat_epoch_utc': epoch, 'last_heartbeat_epoch_utc': st.get('heartbeat_epoch_utc', epoch),
    'next': ('r856: update_zt_pool.py zt-pool forward collector gate leg (O-20261001-2103 R2 data face, bm-a lane, wiring-skill paradigm: '
             '15:30 no-op + checkpoint + conn-fuse + lane guard) -> then OSS admission replay prereg (exit-axis 3-choice gate + corr gate + big-sample 3-iron) '
             '+ 10-08 15:30 market-reopen data chain re-arm (all gates + REGIME_GUARD v3 enforce) + W181 seat watch'),
    'verify': ('smoke 48/48; S6 38/38 rc0 dualrun streak 51 zero-drift; attrition CLEAN; orders 51/51; quartet 4/4; probe rc0; '
               'ledger +13/-0; pit-git-resolver 30,089B line held; CODELY main 30,606B line held; not-at-origin=0 post-push'),
    'latest_artifact': 'results/oss_eng_scan/vibe-probe-20261008.json + research/OSS_HARVEST_LEDGER.md section-7 @' + ts,
    'last_artifact': 'results/oss_eng_scan/vibe-probe-20261008.json + research/OSS_HARVEST_LEDGER.md section-7 @' + ts,
    'now_active': 'r855 closed (OSS S5-01 admission probe GO); r856 = update_zt_pool.py collector gate leg + 15:30 reopen re-arm',
    'notes': st.get('notes', ''),
})
json.dump(st, open(ST, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state 854->855')

# --- heartbeat (own file only) ---
HB = 'fleet/machines/bm-a.json'
hb = json.load(open(HB, encoding='utf-8'))
hb.update({
    'last_seen': ts, 'ts': ts, 'clock_read': ts,
    'current_task': 'OSS S5-01 vibe-astock admission probe GO -> next update_zt_pool.py collector gate leg',
    'cpu_cores': cores, 'ram_free_pct': ram_free_pct, 'gpu_vram_free_gb': vram_free,
    'verdict': 'py_low_board_clear (board clear, OSS admission lane active per O-2245)',
    'idle_rounds': 0, 'agenda_starved': False,
    'heartbeat_epoch_utc': epoch,
})
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
json.dump(hb, open(HB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check = json.load(open(HB, encoding='utf-8'))
assert isinstance(check['heartbeat_epoch_utc'], int), 'epoch int self-check'
print('heartbeat updated epoch=', epoch, 'ram_free=', ram_free_pct, 'vram=', vram_free)
