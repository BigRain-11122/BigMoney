import json, time, datetime, platform

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

# 1) state.json round bump
st = json.load(open('state.json', encoding='utf-8'))
prev = st.get('round_no', 0)
st['round_no'] = prev + 1
st['last_round_at'] = iso.replace(':', ':')
st['last_round_ts'] = iso
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
st['note'] = ('r493: S0 daemon-dirty-tree rider-commit-then-rebase (autofill_state lineage take-local, '
              'futures/lhb shared status take-origin per lane-owner freshness); W14-GENERATE re-armed '
              'ready (entry+shard, r489 law) -> multicore-gate law-1 REFUSE exposed (single_core classifier '
              'verdict, O-20260930-2355) -> conversion = next-round precise continuation; S6 41 legs rc0 '
              '(reconcile ZERO-DRIFT 10/3); monthly trio idempotent regen (r488 had run 01:43); C6 regime-guard '
              'enforce-vs-shadow x6 disclosed not adjudicated')
json.dump(st, open('state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json round_no:', prev, '->', st['round_no'])

# 2) heartbeat fleet/machines/bm-b.json
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = iso
hb['heartbeat_epoch_utc'] = epoch          # MUST be JSON int (R170/R178 law)
hb['clock_read'] = iso                     # T-separated ISO 8601 with offset (R262 law)
hb['current_task'] = ('r493: W14-GENERATE re-armed ready -> multicore-gate law-1 REFUSE (trial_labor_w14.py '
                      'single_core per classifier; conversion per r484 T-134 s2 recipe = next round); '
                      'EXCLUSION/FACEB parked on astock panel data-wait (refresh healthy 4450/5082 @05:12, '
                      'ETA ~06:10, park law r491; daemon 30-min retry cadence live); T-136 closed by bm-c '
                      '(instrument clean, default-exit-stack root cause, intended face +15.9%); T-137 flip '
                      'claimed by bm-a, untouched; T-131 GM-gated unclaimed')
hb['round_no'] = st['round_no']
hb['round'] = st['round_no']
hb['loop_round'] = st['round_no']
hb['verdict'] = ('healthy: S0 rebase x2 clean (daemon-rider pattern, lineage-based per-file resolution, '
                 'push ok), S1 47/47, S0.5 orders 133/133 EMPTY + D-19 ED4E0EAB UNCHANGED, S6 41/41 rc0 '
                 '(reconcile ZERO-DRIFT 10/3, monthly trio idempotent regen), S7 self-heal 3 legs green '
                 '(pin=2/watchdog S4U/claw), attrition CLEAN; watermark RED=data-wait parked (astock '
                 'refresh in flight, not a deadlock); C6 enforce-vs-shadow x6 disclosed')
hb['last_round_at'] = iso
hb['last_round_ts'] = iso
try:
    import psutil
    vm = psutil.virtual_memory()
    hb['free_ram_gb'] = round(vm.available / 1e9, 1)
    hb['cpu_util_pct'] = psutil.cpu_percent(interval=0.5)
except Exception:
    pass
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat ok, epoch int:', chk['heartbeat_epoch_utc'], '| clock:', chk['clock_read'])

# 3) round report line (bm-b file)
line = (
    f"\n{iso} | r493 bm-b | dept:工程/数据 | [watermark verdict: 红·runnable-work-idle-low-cpu P0 上报——池 ready 面 EXCLUSION/FACEB=astock 面板 data-wait 合法停（refresh 健康在飞 4450/5082 @05:12·ETA ~06:10·r491 停放非死锁·daemon 04:02/04:32/05:10 周期重试实证）；W14-GENERATE=multicore-gate law-1 REFUSE（trial_labor_w14.py 分类 single_core·O-20260930-2355）→conversion backlog 设计态]"
    " | 本轮主产出（实物）：W14-GENERATE re-arm 翻面 commit 9c1d97877（entry+shard 双层 r489 律·r472 死会话 pre-burn park 解除·暴露真根因=多核令拒收）+ S6 41 腿全 rc0（reconcile ZERO-DRIFT 10/3 连绿）+ 月度三件幂等再生（r488 01:43 已跑·BRIEF/SELF-REVIEW-202609 再生 rc0·science_audit history 追加）"
    " | 证据：results/_r493bmb_s6_log.txt + logs/autofill.log multicore-gate REFUSE 行（05:20/05:22）+ runnable_pool.json 翻面外科 3 行 diff + docs/live_usage/LIVE-2026-10-01.md（ORANGE）"
    " | 协同：T-136 已 bm-c r301 完成定谳（仪器干净·根因=裸引擎默认退出栈×常开债对·intended face +15.9%·VOID 备忘交治理）本机零动作；T-137 翻面 bm-a 认领不碰；T-131 GM 门未签不认领；science_audit C6 VIOLATION×6 如实披露（六 anchor paper 记 regime_guard enforce≠shadow——10-01=v3 日期门激活日 vs 审计冻结判据 shadow 预期=判据陈旧面疑·不自行裁定归 GM/bm-a 收取面）；orders 133/133 双扫 EMPTY·D-19 UNCHANGED；月度三件 r488 已跑本轮幂等再生如实注记"
    " | 下轮指针：trial_labor_w14.py generate 腿 ProcessPool 转换（r484 T-134 s2 配方·fixed-order 字节恒等+selftest 腿）→转换后 daemon 自领烧 generate→w14_candidates.json；EXCLUSION/FACEB 面板到位后 daemon 自燃（~06:10+）"
    " | 最近实物：docs/live_usage/LIVE-2026-10-01.md + results/self_review/SELF-REVIEW-202609.md（05:2x 再生）·下个里程碑：W14 candidates 产物（转换后·窗 ≤10-02）+ EXCLUSION/FACEB 双面烧录完成（面板后数小时·窗 ≤48h）\n"
)
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(line)
print('round report line appended')
