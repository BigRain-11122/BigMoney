# r612 bm-b closeout writer -- round report line + state.json + heartbeat refresh.
# Fresh epoch int (R170/R178), clock_read T-format (R262), three CEO-visible lines (P-07 #5).
import json, time, datetime, io

now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S') + ('+' if now.utcoffset() >= datetime.timedelta(0) else '-') + now.strftime('%H:%M')
epoch = int(time.time())

row_line_v = 0
row_line_q = 0
for ln in io.open('results/fund_value_p1/nulls.jsonl', encoding='utf-8', errors='replace'):
    if ln.strip(): row_line_v += 1
for ln in io.open('results/fund_quality_p1/nulls.jsonl', encoding='utf-8', errors='replace'):
    if ln.strip(): row_line_q += 1

report = (
    f"{ts} | r612 bm-b (dept:舰队+工程路origin合流手术+数据面S6) | WATERMARK VERDICT: 绿 "
    "(red=false 09:28 probe; py 96.9% loaded_ok 窗均92.8% 三烧合法; satengine alive rc0; "
    "audit FLAG:cap_violation=满算力令 O-1858 下 py 100%/38procs 如实照录非瞎跑) | "
    "当前活: re-burn chain pid 8016 BelowNormal (PE-X2 leg 在飞 09:05:39 起, PB-X1+SENS 排队; AA-replace+provenance) "
    f"+ dual NULLS burns (VALUE {row_line_v}/2000 ETA 10-06, QUALITY {row_line_q}/2000 ETA 10-08) "
    "+ T-156 croc p1c_stock 传输候 bm-a receive (code 有效期 ~11:07) | "
    "最近实物: docs/daily_report/REPORT-2026-10-03.md + docs/live_usage/LIVE-20261003.md 当日面幂等刷新 (09:28) "
    "+ results/_r612bmb_s6_chain.ps1 (33腿链) + D-19 集团决策水位复核=hash 恒等 4167B7 零动作 (网络已恢复, temp partial clone r481 配方复证) | "
    "下个里程碑: harvest re-burn chain 落账 (PE-X2/PB-X1 AA-replace → SENS → settle) ~今日; "
    "DIVLOWVOL runner 构建+4池条目点火 ~10-04 (O-2115 deadline 10-09 开盘窗); VALUE family finalize ~10-06 | "
    "did: S0-1 锚定 bm-b; S0 pull 被烧录活件阻断→origin refs 直读面代偿 (禁 stash-pop 撞活件 r277 律); "
    "S0.5 令扫 150/150 零新 (双扫); D-19 恒等 4167B7 零动作+K: 门面已灭 (C迁后盘符消亡) 实位探查落 temp partial clone 正解 "
    "(pit-git r481 律命中, 集团仓 fa3183b→eacf720 decisions 内容不变); smoke 47/47; S6 33/33 rc0 "
    "(dualrun 连绿保持, token delta 0); S7 attrition CLEAN + claws 2/2 + loop pin=2 no-op (下轮 09:42) + watchdog alive; "
    "**P0 origin 合流手术**: origin 侧 bm-b 心跳 39.5min 陈旧 (epoch 1790988988) + VALUE/QUALITY-NULLS+QUALITY-SENS 池条目 "
    "ready 无主可见 = r611 bm-a 假接管事故诱因全量再现 (kill-advice MSG-0857 已在 origin 在册) → 本轮执行 "
    "r611 滞留 closeout (f81d4cb2b) + r612 单squash rebase 合流: 交集 23 面分类解 (19 共享 derive take-origin per r513 "
    "newer-wins / runnable_pool.bm-b lane 属主 keep-mine / CODELY.md union 双行 / 共享池面 take-origin+settle 补 per MSG-0612) "
    "+ 心跳 epoch 刷新推送 = 假接管诱因根除; 手术前活件备份 %TEMP%\\r612bmb_backup (47件) | "
    "证据: results/_r612bmb_s6_runner.log (33腿 rc0); results/_attrition_guard_scan.json CLEAN; "
    "results/_r612bmb_closeout.py (本收尾器); %TEMP%\\r612bmb_backup | "
    "本地未达 origin commit 数=1 (本轮收尾 commit, push 后 fetch+ls-tree 自证归零; 若拒→pull --rebase 重试一次→再拒 machine/bm-b-r612 分支注记) | "
    "下轮指针: harvest re-burn chain 落账核验 + settle 后池面属主复核 (owner_since 三条目) + DIVLOWVOL runner 构建 (r610 冻结链续作)"
)

with io.open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(report + '\n')

state = json.load(io.open('state.json', encoding='utf-8'))
state['round_no'] = 612
state['round_no_label'] = 'round 612 (bm-b)'
state['last_round_at'] = ts
state['ts'] = ts
state['updated'] = ts
state['updated_at'] = ts
state['last_round_ts'] = ts
state['last_seen'] = ts
state['last_decisions_at'] = ts
state['note'] = ('r612: S6 33/33 rc0; P0 origin合流手术 (origin 心跳39.5min陈旧+池条目无主=假接管诱因→rebase合流+settle+心跳刷新); '
                 'D-19 恒等 4167B7 零动作 (K:门面已灭, temp partial clone r481 正解); burns VALUE/QUALITY NULLS + re-burn chain PE-X2 在飞')
with io.open('state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

hb = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['round_no'] = 612
hb['round_no_label'] = 'round 612 (bm-b)'
hb['ts'] = ts
hb['updated'] = ts
hb['updated_at'] = ts
hb['current_task'] = ('re-burn chain pid 8016 (PE-X2 in fire, PB-X1+SENS queued; AA-replace+provenance) '
                      f'+ dual NULLS burns (VALUE {row_line_v}/2000 ETA 10-06, QUALITY {row_line_q}/2000 ETA 10-08) '
                      '+ T-156 croc transfer awaiting bm-a receive (code to ~11:07)')
hb['verdict'] = ('round 612 done: WM=GREEN loaded_ok (py 96.9% three burns legal, audit FLAG:cap_violation 满算力照录); '
                 'smoke 47/47; S6 33/33 rc0; attrition CLEAN; claws 2/2 + loop pin=2 + watchdog alive; '
                 'orders 150/150 double-scan zero-new; D-19 hash 恒等 4167B7 零动作 (网络恢复复证); '
                 'P0 origin合流手术: r611滞留closeout+池面无主假接管诱因→rebase合流+settle+心跳刷新')
try:
    import psutil
    hb['cpu_util_pct'] = round(psutil.cpu_percent(interval=1.0), 1)
    vm = psutil.virtual_memory()
    hb['free_ram_gb'] = round(vm.available / 1024**3, 2)
    hb['idle_ram_gb'] = hb['free_ram_gb']
    hb['ram_avail_gb'] = hb['free_ram_gb']
except Exception:
    pass
with io.open('fleet/machines/bm-b.json', 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

d = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(d['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178)'
print('REPORT LINE OK; state round_no=612; heartbeat epoch', epoch, 'int-verified; VALUE', row_line_v, 'QUALITY', row_line_q, 'rows')
