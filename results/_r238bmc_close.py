"""_r238bmc_close.py -- bm-c r238 close: inbox archive + state/heartbeat/round-report writes."""
import json, os, shutil, time
from datetime import datetime

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
now = datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")          # T-separated, +08:00
hmx = f"{now.strftime('%Y-%m-%dT%H:%M')}x+08:00"
epoch = int(time.time())
CPU, RAM, GPU = 2.3, 10.1, 9730

# 1) inbox -> processed
for f in ["MSG-20260929-2016-bm-a-ALL-t101-v4-a12-predcond-claim.md",
          "MSG-20260929-2015-bm-c-ALL-w11-candidate-berth-declaration.md"]:
    src = os.path.join("fleet", "inbox", f)
    if os.path.exists(src):
        shutil.move(src, os.path.join("fleet", "inbox", "processed", f))

# 2) state-bm-c.json
sp = "state-bm-c.json"
s = json.load(open(sp, encoding="utf-8"))
s["machine_id"] = "bm-c"
s["round_no"] = 239
s["updated"] = iso
s["last_round_ts"] = iso
s["note"] = ("r238: S6 37-leg chain resumed (36 rc0 + update_lhb rc3 source-restatement "
             "quarantine r229, local zero-write); W10-JUDGE ignition watch (bm-b T-122); "
             "W11 berth parked on trigger-1; state 238->239")
s["did"] = ("r238 closed: S0 absorb+pull (bm-a r445 A12-PREDCOND freeze absorbed, v4 lane no-collision); "
            "orders 122/122 diff 0; decisions tail zero new BigMoney rows; smoke 26/26; boards 0 open; "
            "S6 chain resumed 37 legs: 36 rc0 + update_lhb rc3 (EM LHB source-restatement flag, r229 "
            "precedent quarantine, local zero-write, reported as-is); dualrun ZERO-DRIFT streak 46/3; "
            "09-29 bar klc2 pending honest cutoff 09-28 (~21:00 natural publication, later round lands "
            "bar + paper chain); REPORT/LIVE-0929 idempotent regen; WM red=false (probe "
            "insufficient_history single-sample window = normal); inbox 2 MSG processed (bm-a A12 claim "
            "ack + own W11 berth leg2); W10-JUDGE ignition watch continues (bm-b lane T-122); W11 berth "
            "parked awaiting trigger-1 (W10 verdict + zero in-flight judge faces)")
s["verify"] = ("smoke 26/26; S6 evidence results/_r238bmc_s6_chain.json (non_green=update_lhb rc3 only, "
               "quarantine legal); dualrun streak 46/3; loop pin=5 no-op, watchdog Ready, claw identical; "
               "orders 122/122")
s["next"] = ("(a) 09-29 bar ~21:00 klc2 publication -> same-night S6 auto-land + live.paper marks + "
             "REPORT/LIVE regen (b) W10-JUDGE landing watch (bm-b lane T-122) -> W11 freeze trigger-1 "
             "(adopting machine freeze step: 10-item checklist + seeds three-step law + ticket+claim) "
             "(c) 10-01 month-first trio (science_audit + monthly_briefing + self_review) + REGIME_GUARD "
             "v3 date-gate hands-off (d) r240 next 5x HANDOVER")
s["last_round_at"] = "r238"
s["current_task"] = ("r238 closed: S6 chain resumed green (lhb rc3 quarantine); W11 berth parked on "
                     "W10-JUDGE; next: 21:00 bar landing watch + W10 landing watch")
s["updated_at"] = iso
s["cpu_pct"] = CPU
s["idle_ram_gb"] = RAM
s["gpu_free_vram_mib"] = GPU
json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 3) heartbeat fleet/machines/bm-c.json
hp = os.path.join("fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["current_task"] = ("r238 closed: S6 37-leg chain resumed green (update_lhb rc3 source-restatement "
                     "quarantine); W10-JUDGE ignition pending bm-b (T-122); W11 berth parked on trigger-1")
h["cpu_cores"] = 32
h["cpu_util_pct"] = CPU
h["free_ram_gb"] = RAM
h["total_ram_gb"] = 25.7
h["gpu_free_vram_mb"] = GPU
h["verdict"] = ("S6 chain resumed 36 rc0 + lhb rc3 quarantine (r229); WM red=false; W10-JUDGE ignition "
                "pending bm-b (T-122); W11 berth parked on trigger-1; 09-29 bar ~21:00 landing -> later "
                "rounds run paper chain")
h["round_no"] = 238
h["updated_at"] = iso
for k, v in [("cpu_pct", CPU), ("idle_ram_gb", RAM), ("gpu_free_vram_mib", GPU),
             ("ram_free_gb", RAM), ("gpu_vram_free_mb", GPU)]:
    h[k] = v
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 4) round report line
line = (
    f"{hmx} | r238 bm-c (dept:舰队+数据·维护链复跑轮) | "
    "WM-VERDICT: 绿 (red=false@watermark_red.json 20:10 lane=healthy; probe 20:30:05 py_procs 8/cpu 2.3% "
    "板 0 open+bandit claimed-parked+池 ready=W10-JUDGE bm-b 车道 T-122 认领点火在即〔heartbeat 19:58: "
    "ignition=closing manual tick〕=漏斗纪律合法等待·probe verdict insufficient_history 单采样窗正常非红) | "
    "CEO 可见面: 当前活=S6 维护链 37 腿复跑（r237 legit-skip 后恢复·r237 verdict 指定）; "
    "最近实物=results/_r238bmc_s6_chain.json（20:3x·逐腿 rc 证据·36 绿+1 rc3 隔离）+REPORT/LIVE-2026-09-29 "
    "幂等再生; 下个里程碑=09-29 bar klc2 ~21:00 自然发布→当晚自动落 bar+纸盘链记账（<1h）+W10-JUDGE 落地→"
    "W11 收编冻结步（今晚-明日·窗 ≤48h）| did: S0-1 锚 bm-c→轮首脏 2 件吸收+pull --rebase 同步 bm-a r445"
    "（A12-PREDCOND 冻结·v4 残余预测器/条件化面·bm-a 车道无撞）→S0.5 令差集 122/122 程序化 0+decisions 尾核"
    "零涉本仓新行（委员会件=HQ 收取面）→S1 smoke 26/26→S2 双板 0 open+job_list 空+水位绿（next_pick=claimed "
    "moneyflow IC 停泊源阻断 advisory 照旧）→S3 常设线裁定: W10-JUDGE bm-b 车道在飞（T-122 认领·点火在即）→"
    "让路看护零双烧;W11 泊位已立（r237）·冻结触发器①未满足（W10 verdict 未落+判官池 ready 1）=泊位停泊合法;"
    "A12=bm-a 车道;klc2 09-29 bar 未发布（~21:00·r235 源分层定谳合法等源）→S6 37 腿复跑: 36 rc=0+update_lhb "
    "rc=3（EM LHB 源改史旗标·r229 判例·本地零改写隔离·原样上报）;dualrun ZERO-DRIFT streak 46/3;fund_premium "
    "09-28 NAV 已盖 no-op;CALL-2026-09-28 ORANGE_COOL;REPORT/LIVE-0929 当日幂等再生;lane 守卫腿诚实 no-op;"
    "token ~0→S7 自愈三件（Loop pin=5 no-op 首发保 20:35/Watchdog Ready/claw identical）+inbox 2 MSG 处理"
    "归档（bm-a A12 开工声明 ack+本机 W11 泊位 leg2 自认）+state 239+心跳 epoch int 自证 | verify: smoke 26/26; "
    "S6 证据 results/_r238bmc_s6_chain.json non_green={update_lhb rc3 隔离合法}; orders 122/122 差集 0; "
    "心跳 epoch int 自证 | next: (a) 09-29 bar ~21:00 落地→S6 自动落 bar+live.paper 纸盘记账+REPORT/LIVE 再生 "
    "(b) W10-JUDGE 落地观察（bm-b）→W11 收编机冻结步（泊位开放·触发器①=全链消费落地+判官零在飞） (c) 10-01 "
    "月首轮三件套 science_audit/monthly_briefing/self_review+REGIME_GUARD v3 日期门 hands-off (d) r240 5x "
    "HANDOVER 核对 [via bm-c]\n"
)
with open(os.path.join("logs", "iteration-loop", "round_reports-bm-c.md"), "a", encoding="utf-8") as f:
    f.write(line)

# 5) self-verify
s2 = json.load(open(sp, encoding="utf-8"))
h2 = json.load(open(hp, encoding="utf-8"))
assert s2["round_no"] == 239, "state round_no"
assert isinstance(h2["heartbeat_epoch_utc"], int) and h2["heartbeat_epoch_utc"] == epoch, "epoch int"
assert "T" in h2["clock_read"], "clock_read T-separator"
print("close ok: state 239, epoch", epoch, "clock", h2["clock_read"],
      "| inbox left:", os.listdir(os.path.join("fleet", "inbox")))
