import json, time, datetime

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

# --- 1. state.json ---
s = json.load(open('state.json', encoding='utf-8'))
s['round_no'] = 602
s['round_no_label'] = 'round 602 (bm-b)'
s['note'] = ("r602: (1) PRODUCT: FUND-VALUE-P1 VALUE-PB x2 judged-cell products delivered to origin (commit ac8519fd2, push verified "
             "157561f8d..ac8519fd2 + ls-tree self-proof blobs 5d30bab7/14068f0b) -- r586/r598 pool-done-but-products-stranded heal: "
             "cells_VALUE-PB_x2.jsonl (401 virtual-start cells) + cont_VALUE-PB_x2.json (7874d, 2296 entries, 2275 trades, nav 1.0M->4.87M, "
             "ret_full 3.866, max_dd -0.820); 4/4 judged-cell product set now complete on origin (PE x1 bm-c / PE x2+PB x1 bm-a / PB x2 bm-b) = "
             "batch finalize no longer product-blocked on my face. (2) NULLS burn in flight (autofill 04:38:02 pid 34396, nulls.jsonl "
             "live-write face NOT committed per r532); SENS owner=bm-a 04:18:04. (3) T-152 quality_faces.parquet still absent = FUND-QUALITY-P1 "
             "freeze window still blocked on bm-c transfer lane (10-09 open deadline unaffected). S6 34/34 rc0 (r601 runner reused verbatim; "
             "dualrun ZERO-DRIFT streak 6/3; audit CLEAN; golden-week no-new-bar honest no-ops; C-family stale-takeover legal bm-a hb 03:47 "
             "~80min). SatEngine alive rc0. attrition CLEAN 4 ledgers. orders 150/150 double-scan zero unacked. D-19 honest skip (K: absent, "
             "r597, watermark sha 937A373D unchanged). smoke 47/47. Self-heal 4/4 (loop pin=2 no-op, watchdog re-registered, claws reinstalled).")
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
h['round_no'] = 602
h['round_no_label'] = 'round 602 (bm-b)'
h['current_task'] = ("FUND-VALUE-P1 NULLS burn in flight (autofill 04:38:02 pid 34396, K=2000, nulls.jsonl live-write); "
                     "judged-cell products 4/4 on origin (PB x2 delivered ac8519fd2 this round); FUND-QUALITY-P1 waiting T-152 transfer "
                     "(bm-c quality_faces.parquet, freeze+ignition after probe green, due 10-09 open per O-2115)")
h['verdict'] = ("healthy: smoke 47/47, S6 34/34 rc0 (dualrun streak 6/3, audit CLEAN), SatEngine alive, attrition CLEAN, "
                "orders 150/150 zero unacked, VALUE-PB x2 product gap healed (r586 law applied), NULLS burn healthy in flight")
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
line = (f"\n| {iso} | round 602 (bm-b) | WM verdict: GREEN (red=false healthy; SatEngine alive rc0 queue 0; dualrun ZERO-DRIFT streak 6/3; "
        "audit CLEAN) | 当前活: FUND-VALUE-P1 NULLS 烧录在飞（本机 autofill 04:38:02 pid 34396·K=2000·nulls.jsonl 活写面）+ "
        "质量族候 T-152 数据送达（bm-c） | 最近实物: ac8519fd2 FUND-VALUE-P1 VALUE-PB x2 判决格产物上 origin（cells_VALUE-PB_x2.jsonl 401 虚拟起点格"
        "+cont_VALUE-PB_x2.json 7874d/2275 笔/ret_full 3.866/max_dd -0.820·r586 池翻面≠产物交付缺口治愈·送达 ls-tree 双 blob 自证）| "
        "下个里程碑: FUND-VALUE-P1 批 finalize 判决面（NULLS 烧完+bm-a SENS 送达→§7/§8 批级判决，窗 ≤48h）+ FUND-QUALITY-P1 冻结+点火"
        "（T-152 送达→probe 绿→D6→SEED→banned gate→冻结 commit→池注册点火，10-09 开市前·O-2115 假期窗） | "
        "S0: 0 ahead/0 behind 全同步零整合（脏面=车道活写面 r532 不碰：autofill_state/p1d_gates/pool_core_samples/satengine） | "
        "S0.5: orders 轮首+S7 双扫 150/150 零未回执；D-19 honest skip（K: 门面本会话缺席 r597 律·水位 sha 937A373D 不动·回执 _r602bmb_d19_check.py）；"
        "inbox 2 件均非本机收件（0350=我方发 bm-c·0410=bmc→bma）零动作 | S1: smoke 47/47 | S2: job_list 空；T-151 bm-a 已闭不碰；"
        "T-152 open=bm-c 数据面（quality_faces.parquet 仍缺席=质量族冻结窗仍 blocked·消费门已就位）；T-153 本机 claimed（slice1/2 已交，候 T-152）| "
        "S3: SatEngine status rc0 活；水位绿 next_pick=moneyflow IC（claimed advisory）；修红无红项；试用常设线=FUND-VALUE-P1 在飞判决批满足 | "
        "S6: 34/34 rc0（r601 跑批器 verbatim 复用 _r602bmb_s6_runner.ps1；黄金周无新 bar 数据腿诚实 no-op；daily_report REPORT-2026-10-03+LIVE-2026-10-03 "
        "同日幂等再生；dashboard_status/scorecard/daily_scorecard C 族单写面 stale-takeover 合法〔bm-a 心跳 03:47≈80min>20min·r378 L3〕；"
        "token delta 照记） | S7: attrition guard CLEAN 4 台账（healed 注记照录）；自愈 4/4（loop pin=2 no-op·watchdog 重注册·双爪字节级重装）；"
        "CODELY 零新条（记忆四问门：无新坑·r586 治愈=既有律在役·r559/r593 编码面属已知族） | "
        "本地未达 origin commit 数=0（ac8519fd2 push+fetch+ls-tree 送达自证；簿记四件随收口 commit 同窗随推） | "
        "下轮指针: NULLS 烧完→harvest→nulls.jsonl 定向交付（活写面禁提前 commit）→FUND-VALUE-P1 finalize 判决面（候 bm-a SENS）；"
        "T-152 送达则 probe 重跑转绿进冻结窗；SENS partial（_r603bmb_sens_partial_killed.jsonl）留置候 bm-a 正主 | [via bm-b r602]\n")
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8') as f:
    f.write(line)
print('round report appended')
