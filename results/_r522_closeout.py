import json, time, subprocess, os, datetime

NOW = datetime.datetime.now()

# ---------- state-bm-a.json ----------
sp = 'state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
st['did'] = ("r522: (1) CRASH RECOVERY: r521 closeout session died mid-rebase on final pick "
             "(de3ec842a onto 9135d6cf1) at 15:22:43 -> two-hop surgery: R1 resolve 13 UU "
             "(12 snapshot take-new all-local + x2_watch union 2202) + commit -C + finalize; "
             "R2 rebase onto bm-c 3996c464f, resolve 31 UU (3 twin pairs md-coupled, js wrapper "
             "same-side, 16 snapshot probes, ALL_FACES x6 via merge_lane_views, union 2208) -> "
             "r521 closeout DELIVERED to origin 2d28710cf (fetch-verified) incl. REV-P2 + "
             "REFINE-BENCH-REV-P2 judged finalizes + state r522 + MSG-1535; (2) SATURATION "
             "ENGINE P0: bm-a instance never ticked -> manual tick ignition (verdict=idle "
             "honest) + task registration fixed (S4U principal 0x80070005 false-success -> "
             "default principal + -ErrorAction Stop gate; name kept Bigmoney-SatEngine-bm-b "
             "fleet-shared to avoid double-engine on bm-b); (3) T-140 E1 FOUR-LEG (r492 "
             "before-consume gate, evidence results/lowamp_p2/e1_three_leg.json): P2 verdict "
             "integrity FAIL -- exit neutralization did NOT hold (params bridge reads only 6 "
             "kwargs; loss_time_days/global_hard_limit = dead letters -> default stack 8d/25d "
             "ejected 174/181 = 96% churn); engine+ExitPatch corrected face +15.88%/sharpe "
             "+1.158 (7 signal exits only) ~ independent arithmetic +15.95%/+1.163 = declared "
             "sec.0.6 face POSITIVE (T-136 B/C reproduction); watchlist row-1 annotated UNDER "
             "REVIEW + append-only exit-log entry (consumption BLOCKED before watchlist exit "
             "= zero pollution); T-140 progress appended; T-2026-10-01-142-P0 adjudication "
             "request ticket opened+claimed; MSG-20261001-1615 to fleet/GM; (4) S6 chain "
             "37/37 rc0 (National Day holiday = all bar pulls legitimate no-op, export stays "
             "09-30) + live_paper leg rerun after cmd/env escape bug -> 38/38 green; monthly "
             "trio (science_audit 15:00 / self_review + briefing 15:08) already run by fleet "
             "today = skipped (idempotent, anti-waste); smoke 47/47; attrition guard CLEAN.")
st['verify'] = ("push 2d28710cf == origin fetch-verified; E1 Leg A bp-match + 9 summary fields "
                "= instrument innocent; Leg A2 census 108 loss_time + 66 hard_limit vs 7 "
                "signal = neutralization failed; Leg B' vs C max diff 5.05bp/day; SatEngine "
                "task Ready 60s cadence (schtasks-verified); smoke 47/47; attrition CLEAN x4 "
                "files; orders double-scan 139/139 acked 0 unacked; D-19 watermark pending "
                "refresh next probe")
st['next'] = ("r523: (1) T-142 GM adjudication consumption -> P2 verdict disposition (void-"
              "with-face-note pattern) + P3 runner ExitPatch fix prereg (two non-bridged keys "
              "via ExitPatch channel; sec.0.6 criteria zero-change); (2) N1 W11 supply "
              "generation trigger-face check (engine queue empty, perpetual_faces never-dry "
              "gate vs parked W14 ghost entries); (3) holiday maintenance rounds till 10-08 "
              "reopen (bar pulls no-op by design)")
st['last_round_at'] = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00')
st['current_task'] = ("r523 queue: T-142 adjudication consumption > N1 W11 supply trigger-face "
                      "> holiday maintenance")
st['updated'] = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00')
st['round_no'] = 523
json.dump(st, open(sp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)

# ---------- heartbeat ----------
hp = 'fleet/machines/bm-a.json'
hb = json.load(open(hp, encoding='utf-8'))
epoch = int(time.time())
hb['last_seen'] = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00')
hb['clock_read'] = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00')
hb['heartbeat_epoch_utc'] = epoch
hb['current_task'] = ("r523: T-142 GM adjudication consumption > N1 W11 supply trigger-face "
                      "> holiday maintenance (market closed till 10-08)")
hb['verdict'] = ("r522 OK: crash-recovery two-hop rebase delivered r521 closeout to origin; "
                 "SatEngine P0 fixed (tick + task Ready); T-140 E1 four-leg caught P2 "
                 "neutralization failure BEFORE consumption (verdict numbers blocked, GM "
                 "adjudication requested via T-142 + MSG-1615); S6 38/38 rc0 (holiday no-op); "
                 "smoke 47/47")
hb['last_round'] = 522
hb['round_no'] = 522
try:
    import psutil
    hb['cpu_pct'] = round(psutil.cpu_percent(interval=0.5), 1)
    hb['free_ram_gb'] = round(psutil.virtual_memory().available / 2**30, 1)
except Exception:
    pass
json.dump(hb, open(hp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=2)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat epoch int-verified:', chk['heartbeat_epoch_utc'])

# ---------- round report ----------
rp = 'round_reports-bm-a.md'
ts = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00')
line = (f"{ts} | r522 | WM=RED runnable-work-idle-low-cpu（W14 治理 park+RETAIL 五件事全✅+N1 队空=供给真空如实）"
        "｜当前活=崩溃轮恢复+引擎 P0+E1 消费前闸拦截｜最近实物=results/lowamp_p2/e1_three_leg.json 16:1x"
        "+fleet/tasks/T-2026-10-01-142-P0.json+watchlist 注记｜下里程碑=GM 裁决 P2 verdict→P3 ExitPatch 修 prereg（≤48h）"
        " | did: (1) r521 猝死恢复两跳手术（R1 13 UU 12 snapshot take-new+x2 union；R2 onto bm-c 3996c464f 31 UU "
        "twin×3 对+js 同侧+snapshot 16+ALL_FACES×6 merge_lane_views）→ r521 closeout 落 origin 2d28710cf（含 REV-P2/"
        "REFINE-BENCH-REV-P2 双判负+MSG-1535）；(2) 饱和引擎 P0=tick 点火+任务注册净修（S4U 0x80070005 假成功→默认 "
        "principal+错误闸·名保 bm-b 共享防他机双引擎）；(3) T-140 E1 四腿=P2 中和未生效实锤（params 桥 6 键面·"
        "loss_time_days/global_hard_limit 死信→缺省栈 174/181=96% 踢出；引擎+ExitPatch +15.88%/+1.158≈独立算术 "
        "+15.95%/+1.163=声明面为正）→watchlist ① UNDER REVIEW+进出记录+T-142-P0+MSG-1615（消费闸拦于出名单前零污染）；"
        "(4) S6 37/37 rc0+live_paper 补腿=38/38 全绿（国庆休市 bar 面全 no-op 合法·导出留 09-30）；月度三件他机今日已跑齐"
        "跳过；smoke 47/47 | evidence: E1 LegA bp-match+9 字段=仪器无罪·A2 174/181·B'/C 5.05bp/day；attrition CLEAN×4；"
        "orders 双扫 139/139=0 未回执；SatEngine schtasks Ready | next: r523 (1) T-142 GM 裁决消费→P3 prereg；"
        "(2) N1 W11 供给触发面；(3) 国庆休市至 10-08 维护态\n")
with open(rp, 'a', encoding='utf-8', newline='\n') as fh:
    fh.write(line)
print('round report appended, r522')

# ---------- CODELY.md one-line pit law (四问门过关: P0 lesson, pointer-only) ----------
cm = 'CODELY.md'
cl = ("- [2026-10-01 r522 bm-a] 出场中和 params 死信坑（LOWAMP-P2 E1 四腿实弹·r301 族复发根因钉死）："
      "engine/backtester.py ExitConfig 桥只读 6 个 params kwargs（take_profit_levels/trailing_stop_activate/"
      "trailing_lock/initial_stop/time_decay_period/time_decay_threshold）——loss_time_days/global_hard_limit "
      "两键为非桥接字段，prereg 出场轴声明把这两键写进 params=死信→缺省栈 8d/25d 照常踢出（P2 烧录面 174/181=96% 换手）。"
      "正解=live.paper ExitPatch 通道（T-136 fixture 先例·copy-adapt 时补丁丢失=本坑入口）。How to apply：一切"
      "「禁用引擎缺省出场栈」类 prereg/runner，中和必须走 ExitPatch（或先核对桥键集只声明桥内键）；judged verdict "
      "消费前 E1 出场普查腿必跑（r492 律本例拦于 watchlist 出名单前=零污染）。正典=T-2026-10-01-142 票+"
      "results/lowamp_p2/e1_three_leg.json。\n")
with open(cm, 'a', encoding='utf-8', newline='\n') as fh:
    fh.write(cl)
print('CODELY.md pit-law appended; size =', os.path.getsize(cm), 'bytes')
