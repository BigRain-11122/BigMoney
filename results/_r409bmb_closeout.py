# -*- coding: utf-8 -*-
"""r409 bm-b closeout: round report append + state.json + heartbeat + inbox archive.
File-face write per pit-law batch-80 (CJK through command channel corrupts bytes)."""
import json, os, time, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now()

REPORT_LINE = (
    "2026-09-29T04:41:00+08:00 | r409 bm-b | dept:工程/舰队 (全车道有主·纯维护轮·S6 37 腿全绿·T-116 证据行连绿 2/3) | "
    "WM-VERDICT: 绿牌 red=false @04:20:12 lane=healthy; probe 04:31:13 py_low_with_work_cands=合法在飞供给白名单注记"
    "(本地批 running=astock repull pid7644 锁活网络型限速·板全闭环 open=0·bandit 0·池 ready=0·V3 runner bm-c 未建=物理依赖合法 waiting·W6 prereg bm-a r410 在飞), "
    "audit v2.4.1 idle-starvation+supply_floor standing(ready 0<floor 3·streak 710min·供给响应在飞=astock repull+V3 runner bm-c 未建+W6 bm-a 在飞) | "
    "did: (1) S0-1 bm-b 锚定; S0 pull --rebase up-to-date 干净(轮首 porcelain 空); "
    "(2) S0.5 双扫 orders 122/122 零未回执差集(README.md 非令牌排除)+集团 decisions.md 两路径缺位=P-32 诚实 no-op(r400/r402/r408 先例; firm/DECISIONS.md 无新行)+inbox 唯一件=本机 r408 自发 MSG-0415(回执已在本机, 移 processed 归档, bm-a/bm-c 经 git/processed 补读); "
    "(3) S1 smoke 26/26 全绿; "
    "(4) S2 双板 job_list 空+票板 0 open 0 failed(python 全量解析零失败; PS ConvertFrom-Json 两件假失败=T-83/T-96 控制台编码面均 done 态)+post_review 3731 行全扫: 两条 status=open(T-90-V1-E2E/T-89-S3-ATTACK)最新扫描 04:03:15 verdict 均 YES=零未决✗无 P0; "
    "(5) S3 全车道有主判定: V3-TOURNAMENT waiting=物理依赖(bm-c runner 未建, V2-P1 done 已满足序列第一条, flip 门等 runner+selftest; bm-c 心跳 04:08 活跃, 本机=烧判决 host 待命不越权)+W6 prereg bm-a r410 DRAFT 在飞不插+wm next_pick moneyflow IC claimed 不碰+本机车道 astock repull 在途自愈(4621→4731/5217 @09-28 尾·~11 股/min·ETA~05:15·rev_osc 等面板诚实等待)=S6 主面; "
    "(6) S6 37 腿全 rc=0: pool_dualrun bm-b 证据行 ZERO-DRIFT 107 entries streak 2/3(先于 compute_audit 接线律保持)+audit 双旗 standing+wm probe 合法白名单+update_daily 0 新行 cutoff 09-28 盘前诚实+regime ORANGE shadow(hs300<MA200 #10+breadth 0.83)+scorecard 6 策略/28 交易员/7 组合卡 derive=stale-takeover 合法(bm-a 心跳 72-75min>20min STALE_MIN)+clock CALL-0928 ORANGE_COOL sleeves4 act0 幂等+采集器车道守卫单 no-op×11(bm-a×9+bm-c×1+fundamental 18.7h skip)+astock repull 锁活 no-op+etf_daily cutoff 覆盖+rev_osc 面板 incomplete(cutoff 09-24)诚实等待+minute_feed 09:15 前门+b_layer 全过五门+live.paper OK 6 员锚定 PASS(无新 bar)+t35v 0928 PASS 零例+t24a 22/22 drift0+t24b 0/22 诚实+aggr/grid marks 幂等 no-op+alloc 字节恒等 no-op+paper_export 0928+daily_scorecard stale-takeover derive+REPORT-20260929 faces4 token1+LIVE-20260929 ORANGE cap50%+build_status derive+token L2 0 today; "
    "(7) S7 自愈三查绿(schtasks Loop 正在运行 pin=2 no-op 下轮 04:42+Watchdog 就绪 04:50+pre-commit claw IN-SYNC byte-equal)+state 409+心跳 epoch int 自证+orders 双扫零差 | "
    "evidence: smoke 26/26+S6 逐腿 rc=0(37/37)+pool_dualrun jsonl bm-b 行 streak 2/3+astock 面板字节实读 4731/5217 @09-28 尾+票板 python 全量解析零失败+epoch int isinstance 自证 | "
    "next: (a) astock repull 收口(剩 ~475+掉队)→rev_osc SIG/BARS 导出解锁(bm-b 双车道 S6 自然消费); (b) V3-TOURNAMENT bm-c runner 落地后 flip 门二条+RAM 三采样→本机烧判决就位; (c) W6 prereg freeze 窗 bm-a T-114 watch 不插; (d) T-116 s3 wave-1 三机连绿观察窗(本机 2/3); (e) r410=5x HANDOVER 核对 | "
    "marks/账本/SEED 本轮全 +0(纯维护轮: 判决面零触碰·池态零改写·注册件零触碰) [r409 bm-b]"
)

# --- 1. append round report (UTF-8, newline-terminated) ---
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + REPORT_LINE + "\n")
back = open(rp, "rb").read().decode("utf-8")
assert "\ufffd" not in REPORT_LINE and REPORT_LINE in back, "report append verify failed"
print("report appended OK")

# --- 2. state.json round 409 ---
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 409
st["note"] = ("r409: pure maintenance round (all lanes owned elsewhere): S6 37 legs rc=0 "
              "(pool_dualrun bm-b evidence row ZERO-DRIFT streak 2/3; audit idle-starvation+supply_floor standing ready0<3; "
              "wm py_low_with_work_cands legal whitelist = astock repull in-flight network-bound + board closed + bandit 0 + V3 runner bm-c not built + W6 bm-a in-flight); "
              "post_review open rows latest scan YES (zero pending-fail, no P0); orders 122/122 double-scan zero diff; "
              "astock repull progress 4621->4731/5217 @09-28 tail (rev_osc waits panel complete); "
              "V3-TOURNAMENT pool waiting on bm-c runner build (V2-P1 done satisfied seq first leg); W6 prereg bm-a r410 DRAFT in-flight")
st["last_round_at"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
st["last_round_ts"] = "2026-09-29T04:4x"
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
json.load(open(sp, encoding="utf-8"))
print("state.json -> round 409 OK")

# --- 3. heartbeat fleet/machines/bm-b.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
epoch = int(time.time())
assert isinstance(epoch, int)
hb["last_seen"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["current_task"] = ("round 409 done: pure maintenance (all lanes owned elsewhere) -- S6 37 legs rc=0 "
                      "(pool_dualrun bm-b streak 2/3; wm py_low_with_work_cands legal whitelist astock repull in-flight); "
                      "astock repull 4731/5217 @09-28 tail progressing, rev_osc waits; V3 waits bm-c runner; W6 bm-a in-flight")
hb["round_no"] = 409
hb["loop_round"] = 409
try:
    import psutil
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1024**3, 2)
    hb["idle_ram_gb"] = round(vm.available / 1024**3, 2)
    hb["cpu_util_pct"] = psutil.cpu_percent(interval=1)
except Exception:
    pass
hb["verdict"] = ("healthy: smoke 26/26; maintenance round r409 (board closed, pool V3 waiting bm-c runner, W6 bm-a in-flight); "
                 "astock repull in-flight ~88% (rev_osc unlock next); orders ack 122/122; "
                 "supply standing (astock repull + V3 runner gap + W6 in-flight)")
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat OK epoch=", chk["heartbeat_epoch_utc"], "clock=", chk["clock_read"])

# --- 4. inbox: archive own r408 MSG to processed (bm-b side processed; git preserves for peers) ---
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20260929-0415-bmb-ALL-W2-5-CEO-report.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed")
if os.path.exists(src):
    shutil.move(src, os.path.join(dst, os.path.basename(src)))
    print("inbox MSG-0415 -> processed OK")
else:
    print("inbox MSG-0415 already absent")

print("closeout done")
