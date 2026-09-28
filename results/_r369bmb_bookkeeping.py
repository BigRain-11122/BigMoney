# r369 bm-b S5/S7 bookkeeping: round report + state.json + heartbeat (fresh probes)
import io, json, time, subprocess, datetime

NOW = datetime.datetime.now().astimezone()
clock_read = NOW.strftime('%Y-%m-%dT%H:%M:%S') + ('+%02d:00' % (NOW.utcoffset().total_seconds() // 3600) if NOW.utcoffset() else '+00:00')
epoch = int(time.time())
assert isinstance(epoch, int)

# probes
import psutil
idle_gb = round(psutil.virtual_memory().available / 1e9, 2)
cpu_pct = psutil.cpu_percent(interval=2)
cores = psutil.cpu_count(logical=True)
gpu_free_gb = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    gpu_free_gb = round(int(r.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    pass

# 1) round report line
rr = ("2026-09-28T08:55:00+08:00 | round 369 bm-b | dept:舰队/算力 (S0 泄洪+maintenance+witness) | "
      "WM-VERDICT: py_low_with_work_cands=合法 (probe 08:42:35: census W2B 4-worker 在飞 local_batch_running=True 结构性 py 27.9% "
      "+ 板 0 open + bandit 0 open + 池候选全 RAM 物理门 r354 三采样律 free 0.24GB=合法让路; red=false@08:20:23 lane healthy) | "
      "did: (1) S0-1 bm-b 锚定 + S0 泄洪: r368 escape 2-commit rebase onto origin/main 双波 26-UU 全解 "
      "(wave1 25面=_r369bmb_resolve.py r368-resolver 复用 + paper_export 2新face take-new 08:23:05>08:17:20 + daily_report twins 同侧强化 "
      "+ compute_audit union 68+66->69 + regime_state union 0+0 两侧行恒等零丢失 + x2_watch_log line-union 1158+1158->1164 CRCR=0; "
      "wave2=CODELY memory-union r149 bm-c+r368 bm-b 双坑律条全保) + push LANDED 1d793199..c2a24df0 + escape machine/bm-b-r368 冗余 "
      "+ tick-stash 三连舞步 + stash-vs-活进程撞车判=活面 i=2599 新者胜 2200/2200 逐行解析+i单调 PASS=零孔洞 stash 冗余弃 6793b0e0; "
      "(2) S0.5 令 99/99 全回执零未执行(全扫) + decisions.md 五候选路径缺位=零动作 + S7 双扫同判; "
      "(3) S1 smoke 25/25 PASS; (4) S2 板 0 open/63 done/34 claimed; "
      "(5) S3 常设线: W3-SCREEN slice-2=bm-c MSG-0839 单写者认领(runner 三联+results/trial_labor_w3/+池条目), "
      "bm-b 零相交证明+零异议回执 MSG-0852 已发+MSG-0839 归 processed; W4 不起草=漏斗瓶颈在 JUDGE 算力 RAM 门非候选供给面 "
      "(W1/MASS x4/W2 judge+DECISION-CHAIN-V2-P1 池等待, census W2B i=2599/5620 在飞); "
      "(6) S6 33/33 legs rc=0 (pre-15:30 no-op 族 + lane guards 诚实 skip; market_clock ORANGE_COOL@cutoff 09-24; "
      "post_review 15 历史NO 最新判定全翻YES=零P0); (7) S4 pitlaw r369 stash-vs-活进程面入正典 + CODELY 三十九批当窗整编 "
      "9953->9337B 行级零丢失校验 | 验证: git push LANDED c2a24df0 + smoke 25/25 + S6 33rc0 + resolver 25面 parse-verified marker-free "
      "+ w2b checkpoint 2200/2200 完整性 | 下轮: RAM 首稳窗≥4GB=W2-JUDGE/W1/MASS x4 flips (autofill 续批合法) + "
      "census W2B finalize 后 DECISION-CHAIN-V2-P1 un-defer (清 defer_note r378 律) + W3 screen 收割 witness")
with io.open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + rr + '\n')

# 2) state.json round_no 368 -> 369
st = json.load(io.open('state.json', encoding='utf-8'))
assert st.get('machine_id') == 'bm-b', st.get('machine_id')
st['round_no'] = st.get('round_no', 0) + 1
st['note'] = 'r369: S0 discharge (r368 escape rebased+pushed), maintenance+witness round, W3 screen slice-2 bm-c single-writer, all heavy lanes RAM-gated lawful'
io.open('state.json', 'w', encoding='utf-8', newline='').write(json.dumps(st, ensure_ascii=False, indent=2) + '\n')

# 3) heartbeat
hb = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = clock_read
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock_read
hb['current_task'] = ('r369: S0 discharge landed (r368 escape -> origin/main, push LANDED); maintenance+witness round; '
                      'W3 screen slice-2 = bm-c single-writer (bm-b frozen, zero-objection MSG-0852); next = census W2B finalize watch '
                      '(i=2599/5620) -> RAM stable >=4GB window -> W1-JUDGE/MASS x4/W2-JUDGE flips (bm-b = flip executor, autofill-fed) '
                      '-> W2 judge-finalize -> intake live fire; V2-P1 un-defer after W2B finalize+RAM (clear defer_note r378 law)')
hb['cpu_cores'] = cores
hb['cores'] = cores
hb['free_ram_gb'] = idle_gb
hb['idle_ram_gb'] = idle_gb
hb['idle_ram_mb'] = int(idle_gb * 1024)
hb['free_ram_mb'] = int(idle_gb * 1024)
hb['total_ram_gb'] = round(psutil.virtual_memory().total / 1e9, 1)
hb['cpu_util_pct'] = cpu_pct
hb['cpu_pct'] = cpu_pct
if gpu_free_gb is not None:
    hb['gpu_free_vram_gb'] = gpu_free_gb
    hb['gpu_idle_vram_gb'] = gpu_free_gb
    hb['gpu_idle_vram_mb'] = int(gpu_free_gb * 1024)
hb['round_no'] = 369
hb['round'] = 369
hb['loop_round'] = 369
hb['verdict'] = ('healthy: smoke 25/25, S6 33 legs rc=0 (pre-15:30 no-op family + lane guards honest skip), '
                 'S0 r368-escape discharge LANDED c2a24df0, census W2B in-flight 4-worker i=2599/5620 (py ~28-37% structural), '
                 'free RAM 0.24GB window (judge flips RAM-gated lawful r354), W3 screen slice-2 bm-c single-writer bm-b zero-collision')
io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8', newline='').write(json.dumps(hb, ensure_ascii=False, indent=1) + '\n')

# self-verify: epoch int + clock T-format + orders_ack intact
hb2 = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178)'
assert 'T' in hb2['clock_read'] and ' ' not in hb2['clock_read'], 'clock_read must be T-separated (R262)'
assert len(hb2['orders_ack']) == 99, len(hb2['orders_ack'])
st2 = json.load(io.open('state.json', encoding='utf-8'))
assert st2['round_no'] == 369, st2['round_no']
print('bookkeeping OK: state round_no=369, epoch int=%d, clock=%s, ack=99, idle_ram=%.2fGB, cpu=%.1f%%, gpu_free=%s' % (
    hb2['heartbeat_epoch_utc'], hb2['clock_read'], idle_gb, cpu_pct, gpu_free_gb))
