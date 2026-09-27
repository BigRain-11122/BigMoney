# r94 bm-c S5/S7 batch append (r93 lineage, S4 zero-pitlaw this round; python append per r303 PS CJK law)
import json, time, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')

def probe_write(path, obj):
    """json write replicating original writer format: indent + tail-newline byte-exact."""
    raw = Path(path).read_bytes()
    indent = 1
    for line in raw.decode('utf-8').splitlines():
        stripped = line.lstrip(' ')
        if stripped.startswith('"'):
            indent = len(line) - len(stripped)
            if '"' in stripped[:12]:
                break
    txt = json.dumps(obj, indent=indent, ensure_ascii=False)
    if raw.endswith(b'\n'):
        txt += '\n'
    Path(path).write_bytes(txt.encode('utf-8'))

# ---------- S5: state + round report ----------
now = datetime.now().astimezone()
stamp = now.isoformat(timespec='seconds')
state = json.loads((ROOT / 'state-bm-c.json').read_text(encoding='utf-8'))
state['round_no'] = 94
state['updated'] = stamp[:16]
state['note'] = ('r94: green maintenance round (board clear, all lanes claimed/future-dated): S0 fetch-verify origin zero-delta at open '
                 '(pull blocked by unstaged autofill_state.json, HEAD==origin proven, no stash dance needed) + mid-round origin+2 bm-a r341 pair '
                 '(CODELY folded 5057B) -> rebase+push at S7; smoke 25/25; S6 33/33 rc=0 Sunday no-op; decisions D-06..10 no-new-action '
                 '(D-09 BigMoney-face closed-by-r84 re-verified); next: (1) Mon 09-28 09:15 T-91 s3 watch (2) Mon 15:30 fund_premium bm-c lane '
                 '(3) r95 5x HANDOVER check (4) C-01 09-29 12:00 (5) 10-01 month trio')
state['last_round_ts'] = stamp
probe_write(ROOT / 'state-bm-c.json', state)

report_line = (
    stamp + '｜R94｜bm-c (dept:engineering+fleet)｜WM verdict: green (red=false 17:10 bma write; probe 18:09:58 py 0.0% py_low_board_clear '
    'legal-idle: board 0 open 96 tickets all done/claimed + job_list 0 + bandit_open 0 + no local batch; audit v2.3 CLEAN flags=[])｜'
    'S0: pull --rebase blocked by unstaged autofill_state.json -> fetch-verify path: HEAD==origin zero-delta at round open (skip rebase, '
    'zero stash-pop needed, autofill delta left to its own tick lane) + mid-round origin +2 (bma r341 pair, CODELY folded 5057B) -> '
    'rebase at S7 close｜S0.5 orders 96/96 double-scan zero-unacked (round-start + S7 rescan) + decisions tail D-06..D-10 audited: '
    'D-09 BigMoney-face closed-by-r84 in-tree verified, rest not-our-face zero-action｜S1 smoke 25/25｜S2 board 0 open 96 tickets '
    '(93 claimed by others + done), job_list 0｜S3 full dev-gap sweep zero-claimable: town v7 aligned (调研部 seat r292 landed), '
    'J10/J18b delivered, post_review 3045 rows ✗0, Optuna still gated (6 validated < 8), PLAN §7 rest future-dated (10-31 paper / '
    '10-01 trio) -> green maintenance round per protocol (勿只堆新功能)｜S6 33/33 rc=0 (_r94bmc_s6_chain.ps1 r91-lineage): Sunday '
    'statutory no-op family + live legs green (regime ORANGE breadth-0.77 shadow trigger / clock CALL-2026-09-24 ORANGE idempotent / '
    'live_paper OK / t35v PASS zero-pending 6 / t24 22/22 drift=0 / promo 0/22 honest NOT-ELIGIBLE / aggr+grid idempotent at cutoff '
    '09-24 / t35 export 09-24 / scorecard 6+28+7 / daily_report faces=4 token=1 / build_status 432combos 0pass 6 traders 5/7 / token '
    'L2 1 leg) + lane guards honest (repo/options/moneyflow/sina_mf/ths/ah=bma; astock/sigexp/alloc/system_v1=bmb; fund_premium '
    'weekend no-op bmc lane)｜S7: claw identical+installed / schtasks Loop Running(this session)+Watchdog Ready / inbox 0 pending / '
    'orders rescan 96/96 zero-unacked｜next: (1) Mon 09-28 09:15 T-91 s3 first-marks watch (bma) + 15:30 fund_premium bmc lane '
    '(2) r95 5x HANDOVER check (3) C-01 window 09-29 12:00 (4) 10-01 month trio standing (5) bma r341 escape-valve fold-landing=its '
    'next-round duty noted｜evidence: results/_r94bmc_s6_chain.ps1 + results/_r94bmc_s7_wrap.py + smoke 25/25 + S6 33/33 rc=0 [via bm-c]'
)
rp = ROOT / 'logs/iteration-loop/round_reports-bm-c.md'
rp_txt = rp.read_text(encoding='utf-8')
if not rp_txt.endswith('\n'):
    rp_txt += '\n'
rp.write_text(rp_txt + report_line + '\n', encoding='utf-8')

# ---------- S7: heartbeat ----------
hb_path = ROOT / 'fleet/machines/bm-c.json'
hb = json.loads(hb_path.read_text(encoding='utf-8'))
try:
    import psutil
    cpu_util = round(psutil.cpu_percent(interval=1), 1)
    vm = psutil.virtual_memory()
    free_gb, total_gb = round(vm.available / 1e9, 1), round(vm.total / 1e9, 1)
except Exception:
    cpu_util, free_gb, total_gb = 0.0, hb.get('free_ram_gb', 0), hb.get('total_ram_gb', 0)
try:
    q = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    gpu_free = int(q.stdout.strip().splitlines()[0]) if q.returncode == 0 else hb.get('gpu_free_vram_mb', 0)
except Exception:
    gpu_free = hb.get('gpu_free_vram_mb', 0)
epoch = int(time.time())
hb['last_seen'] = stamp
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = stamp
hb['current_task'] = ('R94 green maintenance round done: S0 fetch-verify + S6 33/33 Sunday no-op + board-clear sweep; '
                      'next=Mon 09-28 T-91 s3 watch 09:15 (bma) + fund_premium 15:30 bmc lane + r95 HANDOVER + C-01 09-29')
hb['cpu_cores'] = 32
hb['cpu_util_pct'] = cpu_util
hb['free_ram_gb'] = free_gb
hb['total_ram_gb'] = total_gb
hb['gpu_free_vram_mb'] = gpu_free
hb['verdict'] = ('legal idle: board 0 open, wm green red=false py_low_board_clear, audit CLEAN flags=[]; '
                 'r94=green-maintenance-round S6 33/33 all green')
probe_write(hb_path, hb)
chk = json.loads(hb_path.read_text(encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
print('heartbeat ok: epoch=%d clock=%s cpu=%s ram_free=%s gpu_free=%s' % (chk['heartbeat_epoch_utc'], chk['clock_read'], cpu_util, free_gb, gpu_free))
print('S5/S7 appends done')
