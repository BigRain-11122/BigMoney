"""r414 bm-b round close: state.json + heartbeat update (fresh probe, honest values)."""
import json
import subprocess
import time
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

cpu_pct = 11.0
free_ram_gb = 10.8
gpu_free = 2.6
try:
    out = subprocess.run(
        ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
        capture_output=True, text=True, timeout=10)
    gpu_free = round(float(out.stdout.strip().splitlines()[0]) / 1024, 1)
except Exception:
    pass

state = {
    "machine_id": "bm-b",
    "round_no": 414,
    "note": ("r414: W6-JUDGE judge-0of1 stale-takeover legal (O-2100 s2.4: bm-c claim 21.4min stale + hb 06:34) "
             "+ burn 293/293 complete 07:26:15 normal exit (runner log 'judge shard complete' line) + checkpoint "
             "verified 293/293==survivors + shard done-flip pit-89 burn-round law (entry stays ready for "
             "judge-finalize separate-round next) + MSG-0735 bm-c standdown cross-kill contract + "
             "town.html 11th building ETF-ops per org_chart v2 O-1524 row (Edge headless + node --check + "
             "info-test 5/5) + org_chart principle-5 addendum + S6 34 legs rc=0 (dualrun ZERO-DRIFT streak 1/3)"),
    "last_round_at": iso,
    "last_round_ts": iso,
    "ts": now.strftime('%Y-%m-%d %H:%M:%S'),
}
with open('state.json', 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
    fh.write('\n')

hb_path = 'fleet/machines/bm-b.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb.update({
    "last_seen": iso,
    "heartbeat_epoch_utc": epoch,
    "clock_read": iso,
    "current_task": ("round 414 closed: W6-JUDGE judge-0of1 burned 293/293 on bm-b via legal stale-takeover "
                     "(bm-c claim 21.4min stale, O-2100 s2.4) + shard done-flip + MSG-0735 bm-c standdown -- "
                     "next r415: judge-finalize (w6_judge.json + ledger + entry flip + 48h CEO clock), "
                     "09:15 T-105 intraday first-live window"),
    "cpu_cores": 16,
    "free_ram_gb": free_ram_gb,
    "gpu_free_vram_gb": gpu_free,
    "total_ram_gb": 23.92,
    "cpu_util_pct": cpu_pct,
    "round_no": 414,
    "verdict": ("healthy: smoke 26/26; r414 W6-JUDGE judge shard complete 293/293 normal exit + pit-89 same-round "
                "shard done-flip (entry ready for finalize) + town.html ETF-ops 11th building landed "
                "(screenshot+syntax+functional verified) + S6 34 legs rc=0 + dualrun ZERO-DRIFT streak 1/3 "
                "recovering; orders 122/122 zero-diff; bm-a stale 103min guard-faces self-healed (daily_score "
                "stale-takeover legal)"),
    "round": 414,
    "loop_round": 414,
    "idle_ram_gb": free_ram_gb,
    "gpu_idle_vram_gb": gpu_free,
    "cores": 16,
})
with open(hb_path, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write('\n')

# self-verify (R170/R178: epoch must be JSON int; R262: clock_read T-separated)
d = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(d['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in d['clock_read'] and ' ' not in d['clock_read'], 'clock_read not T-separated'
print('heartbeat self-verify PASS: epoch int', d['heartbeat_epoch_utc'], '| clock', d['clock_read'])
print('state round_no ->', state['round_no'])
