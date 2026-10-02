import json, time, datetime

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

# --- 1. state.json ---
s = json.load(open('state.json', encoding='utf-8'))
s['round_no'] = 601
s['round_no_label'] = 'round 601 (bm-b)'
s['note'] = ("r601: (1) S0 r589 revoke-FF-reland: 2 stranded appender keepalive commits dropped, "
             "42 overlap shared-derive faces origin-verbatim, FF 0210dfff6->7c67c1e79 (bm-c r397+bm-a r606 N4-B2 frozen integrated); "
             "(2) FUND-VALUE-P1-SENS duplicate burn killed (pid 54016+3 workers, 02:44 start) + yielded to bm-a origin-canonical "
             "claim 04:18:04 (my keepalive refreshes 04:14/04:16 stranded unpushed >20min stale on origin, takeover legal r489; "
             "partial moved aside results/_r603bmb_sens_partial_killed.jsonl); (3) PRODUCT: quality-family unblock package "
             "delivered b1a99c1b3 -- T-152 transfer ticket + T-153 work ticket + MSG-0350 + FUND-QUALITY-P1 prereg DRAFT + "
             "probe (selftest 25/0) + runner (selftest 22 ALL PASS) + receipts, was stranded untracked after dead r600 closeout; "
             "T-152 now visible to bm-c = FUND-QUALITY-P1 critical path unblocked (O-2115 holiday window, due 10-09 open). "
             "S6 34 legs rc0 (dualrun ZERO-DRIFT streak 5, audit CLEAN); autofill self-healed: VALUEPB-X2 launched 04:26:02 "
             "(py 60.3%), NULLS ready fleet-claimable. SENS lessons -> CODELY (diverged-window invisible keepalive face).")
for k in ('last_round_at', 'last_round_ts', 'ts', 'updated', 'updated_at', 'last_seen'):
    s[k] = iso
with open('state.json', 'w', encoding='utf-8') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)

# --- 2. heartbeat fleet/machines/bm-b.json ---
h = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=1.0), 1)
    ram = round(psutil.virtual_memory().available / 1024**3, 2)
except Exception:
    cpu, ram = h.get('cpu_util_pct', 0), h.get('free_ram_gb', 0)
h['last_seen'] = iso
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = iso
h['round_no'] = 601
h['round_no_label'] = 'round 601 (bm-b)'
h['current_task'] = ("FUND-QUALITY-P1 waiting T-152 transfer (bm-c quality_faces.parquet, prereg freeze+ignition after probe green, "
                     "due 10-09 open per O-2115); FUND-VALUE-P1 VALUEPB-X2 burn in-flight (autofill 04:26:02 pid 56444); NULLS ready fleet-claimable")
h['verdict'] = ("healthy: S6 34/34 rc0, dualrun ZERO-DRIFT streak 5, audit CLEAN, smoke 47/47, SENS dup-burn killed+yielded to bm-a "
                "canonical, quality unblock package delivered b1a99c1b3")
h['cpu_util_pct'] = cpu
h['free_ram_gb'] = ram
h['idle_ram_gb'] = ram
h['ram_avail_gb'] = ram
h['ram_free_gb'] = ram
h['ts'] = iso
h['updated'] = iso
h['updated_at'] = iso
assert isinstance(h['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178)'
assert 'T' in h['clock_read'], 'clock_read must be T-separated (R262)'
with open('fleet/machines/bm-b.json', 'w', encoding='utf-8') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
print('state+heartbeat written; epoch int ok; cpu=', cpu, 'ram=', ram)

# --- 3. round report line ---
line = (f"\n| {iso} | round 601 (bm-b) | WM verdict: GREEN (red=false healthy; 04:26:12 sample red=transient kill/launch handoff window, "
        "self-resolved by autofill VALUEPB-X2 launch 04:26:02 py 60.3%; SatEngine alive queue 0; dualrun ZERO-DRIFT streak 5/3; audit CLEAN) | "
        "当前活: VALUEPB-X2 烧录在飞（autofill pid56444+11 workers·04:26:02 起）+ 质量族候 T-152 数据送达（bm-c） | "
        f"最近实物: b1a99c1b3 质量族解锁包 14 件（T-152 transfer 票+T-153 工单+MSG-0350+FUND-QUALITY-P1 prereg DRAFT+probe selftest 25/0+runner selftest 22 全绿+必要性回执，{iso[:16]}） | "
        "下个里程碑: FUND-QUALITY-P1 冻结+点火（T-152 送达→probe 绿→D6→SEED→冻结→池注册点火，10-09 开市前·O-2115 假期窗，≤48h） | "
        "S0: r589 撤-FF-重落环——2 笔滞留 appender keepalive commit 撤（r382 可撤面）+42 重叠共享派生面取 origin verbatim+FF 0210dfff6→7c67c1e79（bm-c r397+bm-a r606 N4-B2 冻结全集成）；"
        "同窗 FUND-VALUE-P1-SENS 双烧定谳+处置：我方 keepalive 刷新 04:14/04:16 分叉窗内未推→origin 末次可见刷新 03:56 超龄>20min→bm-a 04:18 stale-claim 合法接管（r489 判据）→"
        "本地 4 工人（02:44 起 --sensitivity·~100min CPU/工人）=重复烧录，04:25 击杀+partial 移旁 results/_r603bmb_sens_partial_killed.jsonl+池面让路 origin 正主；教训入 CODELY | "
        "S0.5: orders 双扫零未回执（150/150）；D-19 honest skip（K: 门面缺席 S4U r597 律·水位 sha 937A373D 不动）；MSG-0410（bmc→bma W14-GENERATE 双层滞留观察）非本机件零动作 | "
        "S1: smoke 47/47 | S2: job_list 空；T-151 bm-a N4-B1 已闭不碰；T-152 open=bm-c 数据面（本机消费门已就位）；T-153 本机 claimed（前会话 r601/r602 已建 probe+runner，本轮补送 origin） | "
        "S6: 34 腿全 rc0（黄金周无新 bar 数据腿诚实 no-op；daily_report+LIVE-2026-10-03 同日幂等再生；dashboard_status/scorecard 宿主守卫跳过诚实 stdout；token delta 照记） | "
        "S7: attrition guard CLEAN 4 台账（bm-a shrink healed 注记照录）；自愈 4/4（loop pin=2 no-op·watchdog 在跑·pre-commit/pre-push 爪双 MATCH）；"
        "inbox 2 件均非本机收件（0350=我方发 bm-c 已随包送达·0410=bmc→bma） | 本地未达 origin commit 数=0（b1a99c1b3 fetch+ls-tree 自证；收口 commit 同窗随推） | "
        "下轮指针: T-152 送达则 probe 重跑转绿进冻结窗（D6→SEED→banned gate→冻结 commit→池注册+点火）；VALUEPB-X2 烧完看 autofill 续 NULLS；value 族 finalize 判决面 bm-a 窗口 | [via bm-b r601]\n")
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(line)
print('round report appended')

# --- 4. CODELY.md lesson ---
lesson = ("\n- [2026-10-03 04:4x r601 bm-b] 分叉窗 keepalive 自投 commit 滞留本地=origin claim 超龄被合法接管→本地在飞烧录成双烧坑"
          "（FUND-VALUE-P1-SENS 实弹·r489 族新触发面）：autofill keepalive commit（04:14/04:16）在 behind 分叉窗内 push 恒拒→"
          "claim 刷新对 origin 不可见（末次可见刷新 03:56）→bm-a 04:18 按 stale-claim（龄>20min）合法接管+launch-claim→"
          "本地 4 工人（02:44 起 --sensitivity）照烧成双烧（~40min×4 核浪费·04:25 击杀）。处置=杀本地烧录+partial 移旁径防碰撞+"
          "池面取 origin verbatim 让路（接管合法勿写 kill-advice）；预防=轮首 ahead>0 且尾笔为 appender keepalive commit 时"
          "优先速通 r589 撤-FF-重落（phantom claim 只活在分叉窗内·窗越短双烧窗越短）。")
with open('CODELY.md', 'a', encoding='utf-8') as f:
    f.write(lesson)
print('CODELY lesson appended')
