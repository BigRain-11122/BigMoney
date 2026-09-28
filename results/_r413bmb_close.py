import json, time, datetime

NOW = datetime.datetime.now()
ts_iso = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
ts_flat = NOW.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())

# ---- state.json (bm-b face) ----
state = {
    "machine_id": "bm-b",
    "round_no": 413,
    "note": ("r413: W6-SCREEN chain closed (burn 4152/4152 normal exit + in-round "
             "screen-finalize: null p95 0.5196, survivors 293, ledger 333139) + "
             "W6-JUDGE canonical pool submit (judge-prep PASS + RAM r354 3-sample + "
             "pool drained 109/109) + V3 pool-face done-flip (crash-fuse loop cleared) "
             "+ same-window bm-c events: T-116 flip EXECUTED by bm-c (gate 3/3/8 read "
             "pre-dates my 06:58 drift) + judge-0of1 claimed by bm-c (lane_owner=null "
             "fleet-legal, origin-pool taken in rebase per r411 precedent) + dualrun "
             "DRIFT = updated_at format-collision (zero content drift, streak 3->0 "
             "honest, F-04 MSG-0705 disclosed to T-116 owner) + pit-law batch-89 "
             "(pool done-flip = session-only action) + CODELY hot-cold reorg 9149B"),
    "last_round_at": ts_iso,
    "last_round_ts": ts_iso,
    "ts": ts_flat,
}
with open("state.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
with open("state.json", encoding="utf-8") as fh:
    s2 = json.load(fh)
assert s2["round_no"] == 413
print("state.json round 413 written + reload-verified")

# ---- round report line ----
REPORT = "logs/iteration-loop/round_reports.md"
line = (
    f"{ts_iso} | r413 bm-b | dept:策略+工程+舰队 joint（W6 判决链收口+V3 池面清环+T-116 "
    "同窗三事件让路）| WM-VERDICT: 绿牌 red=false @06:40:14 lane=healthy（S6 探针 "
    "06:58:27 py_low_board_clear=合法白名单：板闭环+W6-JUDGE ready 供给响应在飞）| did: "
    "(1) S0-1 bm-b 锚定；S0 坑律八十八批正典序实弹：脏树三件幂等产物（checkpoint 尾行 "
    "JSON 完整验证 4152 行）→定向收割 202abe73→rebase→push 三面解锁；(2) S0.5 双扫 "
    "122/122 零未回执+集团 decisions.md 迁移后缺位诚实 no-op（r400/r402/r408/r411 先例）"
    "+inbox 零未读+firm/DECISIONS.md 零新行；(3) S1 smoke 26/26；(4) S2 双板空（job_list "
    "空+票板 38 claimed 零 open；T-105 余切片=09:15 物理依赖）；(5) S3 主闭环=W6-SCREEN "
    "链收口：burn pid3984 06:40:05 正常收工（worker 日志 'shard 0of1 complete'·4152/4152 "
    "细胞=3952 候选+200 null 全在 checkpoint·screen-finalize=分离子命令设计非崩溃死·"
    "06:42:57 checkpoint 尾写=本会话 rebase checkout 同秒簇非进程行为）→lane owner 轮内 "
    "screen-finalize（W5 bm-a r409 先例）：null p95 0.5196（json 6dp 0.519553）·"
    "survivors 293·ledger 328987+4152=333139 跨线线性·vconf 分段存活 surge 0.0878>none "
    "0.0727>dry 0.0611→双面 done-flip（r407 范式+回执交叉断言全过·p95 断言 4dp/6dp 面 "
    "一次修正确）→judge-prep PASS（manifest 48 员+census L/D 冻结+gate/vol/yang/vconf 全 "
    "meta 锚）→RAM r354 三采样 10.38/10.58/12.71GB@31s PASS→W6-JUDGE canonical submit "
    "（consumer_plan O-1820(3)+契约三件+inbox 卫兵·lane_owner=null 预注册 §9 冻结面·"
    "workers_plan 20=floor(16/0.8)·runner_args 不带 --workers=worker_cap 自锚）→池 "
    "109/109 全 done 首见全清+1 ready；V3-TOURNAMENT 池面 done-flip：判定已落地（前任 "
    "06:01 收割+06:22:42 relaunch 202.1s 确定性重写字节恒等）但池 shard 未翻=autofill "
    "重跑循环+crash-fuse 投毒（06:30:03 CONFIRM count=1）→双面翻面清环（回执断言：6 "
    "面×臂 chain_win 全 False·N=16566·ledger not-counted per audit FLAG supply_gap,"
    "supply_floor 诚实）；T-117 progress_r413 注记；(6) S4 坑律八十九批（池面 done-flip="
    "会话专属动作·deferral 结构性错律）+CODELY 9,874B 触 10KB 硬线→当窗热冷整编（八十八"
    "批+r202 回执 verbatim 迁 archive『坑律归档 2026-09-29 r413 bm-b 窗批』节+指针行→"
    "9,149B·零丢失字节校验 True）；(7) S6 37 腿全 rc=0 nonzero=[]（dualrun DRIFT="
    "updated_at 纯格式碰撞零内容漂移 110/110 全等→streak 3→0 诚实重置·根因=canonical "
    "autofill 空格格式 vs r412 手建 ISO×_flat_winner 字典序同日 'T'(0x54)>' '(0x20) 恒胜"
    "→F-04 MSG-0705 披露 bm-c T-116 认领机（本机未碰其机器·翻门关切后被超越·格式缺陷"
    "诊断对 reconcile 证据面仍有效·日界 09-30 自然恢复面）·audit 三旗 standing-honest"
    "（supply_floor ready1<floor3·ignition_sla·supply_gap·供给响应在飞=W6-JUDGE）·"
    "update_daily 0 新行 cutoff 09-28 盘前诚实+regime ORANGE shadow（breadth 0.83 触发）"
    "+scorecard 6/28/7 derive+clock CALL-0928 ORANGE_COOL sleeves4 act0+采集器车道单 "
    "no-op×10+astock/etf/rev_osc 面板鲜 no-op+minute_feed 09:15 前门+b_layer 全过+"
    "live.paper 6 员 PASS+t35v 0928 PASS 零例+t24a 22/22 drift0+t24b 0/22 诚实+aggr/"
    "alloc/grid 幂等 no-op+system_v1 守卫 no-op+paper_export 0928+REPORT-0929 faces5 "
    "token1+LIVE-0929 ORANGE cap50%+build_status+token L2 0 today）；(8) S7 三查全绿"
    "（schtasks Loop 正在跑=本会话 pin=2 无需纠偏·Watchdog 就绪·claw IN-SYNC 字节等）"
    "+同窗三事件让路收口：bm-c r202-r203 连落=T-116 s3 wave-1 flip 已执行（门读 3/3/8 "
    "MET 先于我 06:58 漂移）+judge-0of1 owner=bm-c 池面认领（lane_owner=null 车队合法）"
    "→rebase 池冲突 stage2/stage3 双探（r411 池先例=取 origin 整面：bm-c 认领在册 110 "
    "条+我 V3/W6-SCREEN 翻面全保+W6-JUDGE entry 在册）→07:10 tick 本机让路自然消费 | "
    "evidence: push 三连落地 45d0f31db+c8b86571e+5b2a7f1c5·w6_screen.json+w6_screen_"
    "cells.csv+judge_state.json 在册·翻面回执断言全过（p95 0.519553·survivors 293·"
    "ledger 333139·V3 6 面×臂 False）·orders 双扫 122/122·CODELY 9,149B 水位安全 | "
    "next: (a) W6-JUDGE bm-c 烧批观测→judge-finalize 落地轮=48h CEO 钟起计+intake 切片"
    "（prereg §6）；(b) MSG-0705 格式缺陷 bm-c 裁量（根修=_flat_winner 时间戳解析或写者"
    "归一）；(c) T-105 v1.4 盘中面 09:15 实弹首验（minute_feed 点亮）；(d) r415=5x "
    "HANDOVER 核对 | marks/账本/SEED 本轮 +0（判决面 finalize 由 runner 冻结代码 append "
    "账本=333139·V3 not-counted 诚实·池面零科学键改写·本会话零判据线触碰） [r413 bm-b]\n"
)
with open(REPORT, "a", encoding="utf-8") as fh:
    fh.write(line)
print("round report r413 appended,", len(line), "chars")

# ---- heartbeat ----
HB = "fleet/machines/bm-b.json"
hb = json.load(open(HB, encoding="utf-8"))
hb["last_seen"] = ts_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = ts_iso
hb["current_task"] = ("round 413 closed: W6-SCREEN chain (burn 4152/4152 + finalize "
                      "survivors 293 ledger 333139) + W6-JUDGE pool entry submitted "
                      "(bm-c claimed judge-0of1 fleet-legal) + V3 pool done-flip (fuse "
                      "cleared) -- next: W6-JUDGE burn observation, 09:15 T-105 intraday "
                      "first-live, MSG-0705 format-collision in bm-c hands")
hb["cpu_cores"] = 16
import psutil
vm = psutil.virtual_memory()
hb["free_ram_gb"] = round(vm.available / 1024 ** 3, 1)
hb["idle_ram_gb"] = hb["free_ram_gb"]
hb["total_ram_gb"] = round(vm.total / 1024 ** 3, 2)
hb["cpu_util_pct"] = psutil.cpu_percent(interval=1)
try:
    import subprocess
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"], capture_output=True)
    hb["gpu_free_vram_gb"] = round(int(r.stdout.decode().strip()) / 1024, 1)
    hb["gpu_idle_vram_gb"] = hb["gpu_free_vram_gb"]
except Exception:
    pass
hb["round_no"] = 413
hb["round"] = 413
hb["loop_round"] = 413
hb["verdict"] = ("healthy: smoke 26/26; r413 W6-SCREEN chain closed (finalize survivors "
                 "293, ledger 333139 linear) + W6-JUDGE submitted canonical (bm-c claimed "
                 "fleet-legal lane_owner=null) + V3 pool done-flip (crash-fuse cleared) + "
                 "dualrun DRIFT format-collision honest streak 3->0 (MSG-0705 disclosed, "
                 "zero content drift) + T-116 flip landed by bm-c same-window + CODELY "
                 "reorg 9149B; orders 122/122 double-scan zero-diff; S6 37 legs rc=0")
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
# self-verify epoch int + clock format
hb2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock must be ISO T-sep"
print(f"heartbeat written: epoch={hb2['heartbeat_epoch_utc']} (int OK) clock={hb2['clock_read']}")
