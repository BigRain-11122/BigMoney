# r93 bm-c S4/S5/S7 batch append (python append per r303 PS CJK ParserError law)
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

# ---------- S4: archive full pitlaw (25th batch) + CODELY pointer ----------
arch = ROOT / 'research/memory-archive/202609.md'
arch_txt = arch.read_text(encoding='utf-8')
if not arch_txt.endswith('\n'):
    arch_txt += '\n'
arch_txt += (
    '\n## 坑律归档 2026-09-27 二十五批（r93 bm-c·水位律当窗整编：新坑律全文 verbatim 外迁+CODELY 指针行）\n'
    '- [2026-09-27 17:5x r93 bm-c] 坑律：**S0 stash-pop 共享滚动台账 union 修正三律——'
    '①launches 并集键=事件身份（ts+machine+entry+shard），全量 canonical-JSON 键会把「他机后补字段（crash_counted 等）的同事件变体」'
    '当新事件并入（r93 实证：48|48 假并 49+，错序+末位丢字段）；身份集相等（old_only=0/head_only=0）时正解=整件取 HEAD 原文（字段更全侧胜）。'
    '②共享 JSON 重写前必探原写者格式逐字节复刻——autofill_state.json=indent=1 无尾换行；indent=2 假设=1258 行整件 churn，'
    '被 r339 --stat 核 churn 律在 git add 前拦截（写后必核）。'
    '③git stash drop 后其 commit 对象不可达（git show <sha>:<path> 空返）——drop 前先完成内容验证，'
    '或以 pre-stash base commit+已知行差重建对照面（r93 以 2665c962+3 行差重建超集验证）。\n'
)
arch.write_text(arch_txt, encoding='utf-8')

codely = ROOT / 'CODELY.md'
c_txt = codely.read_text(encoding='utf-8')
if not c_txt.endswith('\n'):
    c_txt += '\n'
c_txt += (
    '- [2026-09-27 r93 bm-c] 坑律（二十五批·指针）：S0 stash-pop union 身份键/原写者 indent 探针/stash-drop 不可达三律'
    '——全文=archive 202609.md 二十五批节。\n'
)
codely.write_text(c_txt, encoding='utf-8')
size = codely.stat().st_size
print('CODELY_bytes=', size)
assert size < 10000, 'CODELY >10KB hard line breached: %d' % size

# ---------- S5: state + round report ----------
now = datetime.now().astimezone()
stamp = now.isoformat(timespec='seconds')
state = json.loads((ROOT / 'state-bm-c.json').read_text(encoding='utf-8'))
state['round_no'] = 93
state['updated'] = stamp[:16]
state['note'] = ('r93: S0 autofill UU identity-key resolve (full-JSON-key union false-events caught, take-HEAD zero-loss) '
                 '+ r72/r84 dedicated verify truly_lost=0 -> remote GC both deleted (r90-debt cleared) '
                 '+ smoke 25/25 + S6 33/33 Sunday no-op + decisions no-new-past-D-10 '
                 '+ next: (1) Mon 09-28 09:15 T-91 s3 watch; (2) Mon 15:30 fund_premium bm-c lane; (3) C-01 09-29 12:00; (4) 10-01 month trio')
state['last_round_ts'] = stamp
probe_write(ROOT / 'state-bm-c.json', state)

report_line = (
    stamp + '｜R93｜bm-c (dept:engineering+fleet)｜WM verdict: green (red=false; probe 17:53 py 0.0% legal-idle: board 0 open 93 all-claimed '
    '+ job_list 0 + next_pick=claimed; audit v2.3 CLEAN)｜S0 pull ff+1 (bm-a r340) + stash-pop autofill UU two-pass: v1 full-JSON-key union '
    'WRONG (indent=2 assumption=1258-line churn caught by r339 --stat law + field-variant false-events) -> v2 identity-key '
    '(ts+machine+entry+shard) superset verify 46|46 old_only=0 -> take-HEAD-verbatim zero-loss + stash dropped｜S0.5 orders 96/96 '
    'double-scan zero-unacked + decisions no-new-past-D-10 zero-action｜S1 smoke 25/25｜S3 r72/r84 dedicated verify (r90-deferred): '
    'truly_lost=0 both (CODELY 7+10 archive-verbatim + pointer-prefix evolved; MSG-1407 in processed/; _r84bmc scripts in-tree; '
    'fps/rolling superseded) -> remote GC executed both deleted; FINDING: base machine/bm-c (4 unique T-04 F1/F5/F6/F8 commits 09-24) '
    '+ bm-a pair externally deleted mid-round by other actor (prune surfacing) -- base verify mooted at remote, content evidence '
    'indicates absorbed (T-04 fields live in smoke F7/token_meter today)｜S6 33/33 rc=0 Sunday no-op family + lane guards honest '
    '(fund_premium weekend no-op bm-c lane)｜S4 pitlaw 25th-batch in-window archival (identity-key law full verbatim + CODELY pointer '
    '<10KB asserted)｜next: (1) Mon 09-28 09:15 T-91 s3 first-marks watch + 15:30 fund_premium self-heal bm-c lane (2) C-01 window '
    '09-29 12:00 (3) 10-01 month trio standing (4) r95 5x HANDOVER check｜evidence: results/_r93bmc_branch_verify.py + '
    'results/_r93bmc_branch_verify.json + smoke 25/25 + S6 33/33 rc=0 [via bm-c]'
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
hb['current_task'] = ('R93 done: S0 UU identity-key resolve + r72/r84 branch verify+GC (truly_lost=0, both deleted) + S6 33/33; '
                      'next=Mon 09-28 T-91 s3 watch 09:15 + fund_premium 15:30 bm-c lane + C-01 09-29 12:00 + 10-01 trio')
hb['cpu_cores'] = 32
hb['cpu_util_pct'] = cpu_util
hb['free_ram_gb'] = free_gb
hb['total_ram_gb'] = total_gb
hb['gpu_free_vram_mb'] = gpu_free
hb['verdict'] = ('legal idle: board 0 open 93 all-claimed, wm green red=false, audit CLEAN flags=[]; '
                 'r93=UU-identity-key-resolve+r72/r84-GC+S6 33/33 all green')
probe_write(hb_path, hb)
chk = json.loads(hb_path.read_text(encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
print('heartbeat ok: epoch=%d clock=%s cpu=%s ram_free=%s gpu_free=%s' % (chk['heartbeat_epoch_utc'], chk['clock_read'], cpu_util, free_gb, gpu_free))
print('S4/S5/S7 appends done')
