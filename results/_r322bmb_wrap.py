# -*- coding: utf-8 -*-
"""r322 bm-b S7 wrap: state round_no++, round report append, heartbeat update (inbox empty -> no move)."""
import json, time, subprocess, os
from datetime import datetime, timezone, timedelta

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# 1) state.json round_no++ (logs/iteration-loop/state.json)
sp = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 322
st["did"] = ("r322: 周日诚实维护轮 -- S0 显式 stash 三步舞 pull --rebase FF ecb2de58->ddc8e84c（p1d_gates 第三写手面轮首脏=定向 add 律生效·stash pop 零冲突·保持 unstaged 设计态）；"
             "orders 双扫 96/96 零未回执（Compare-Object 机械 diff）；smoke 25/25；S2 双板 0 open+池 77=76 done+1 ready（T19 lane-gated bm-c 12:30 已认领在磨）；"
             "post_review 49 行 0 NO 零复审债；S6 全链 32 legs rc=0（compute_audit CLEAN flags=0·watermark py_low_board_clear 合法 idle·周日 collectors 全景诚实 no-op）；"
             "迁移窗只读实探（v2.2 armed·precheck 编辑器门·旧根在=开工面正确·零干预）")
st["verdict"] = "green"
st["next"] = ("sina 深面板 complete+N>=250 后 sina-construct prereg 起草（12:31 探针 27.7%·ETA ~15:02 bm-a 判定窗）；GM 审 M-20260927-01；"
              "周一 09-28 09:15 T-91 s3 首队列入场+开市新 bar 全链+T-87 astock 15:30 首拉；10-01 月度三件套+REGIME_GUARD v3 日期门；R325 5x 核对")
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json round_no ->", st["round_no"])

# 2) round report append (utf-8; preserve trailing-newline convention)
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    f"- {ts} | r322 bm-b | dept:舰队+工程 | 水位=绿（red=false@12:30:14 lane healthy·probe 12:32:34 py_low_board_clear 合法 idle 白名单=板 0 open+bandit 0+池内唯一 T19-PHANTOM-P1 lane_owner=bm-c R31 本机禁碰（bm-c 12:30:07 已认领在磨）+主线全门控）"
    "| did: (1) S0 pull --rebase FF ecb2de58→ddc8e84c（bm-a autofill tick 窗 4 件：autofill_state/compute_audit/regime_state/runnable_pool）；轮首 p1d_gates.json 第三写手面（12:30 derive 噪声面）=轮首脏→定向 add 律生效：显式 stash 三步舞（push→pull→pop 零冲突）·p1d_gates 保持 unstaged 设计态不入本轮 commit（r317 正典）"
    "(2) S0.5 双扫 orders 96/96 零未回执（轮首 Compare-Object 机械 diff+轮尾复扫一致·零新令）；集团 ..\\..\\docs\\decisions.md 路不存在=零动作；firm/DECISIONS.md 无 09-27 新行（尾=09-26 r239 面）"
    "(3) smoke 25/25"
    "(4) S2 双板清点：job_list 0+fleet tasks 0 open（93 票全 done/claimed·T-83 票 ConvertFrom-Json 解析噪声=done 态无疑）·池 77 条 76 done+1 ready（T19 bm-c 车道）·post_review 49 行 0 NO 零复审债·反重复核实=r321 已清点全队列（town/J12/J13/J10/J18b 已交付或他人拥有·Optuna gated-P1 GM 面不擅启）"
    "(5) S6 全链 32 legs rc=0（r321 链脚本逐字复用 _r322bmb_s6_chain.ps1·直呼 python 无 splat·rc 数字断言）：compute_audit CLEAN（flags=0·GPU 无越权·无僵尸）·watermark probe 12:32:34 py_low_board_clear（py_cpu 0.6%·open 0·bandit 0·bars present+daily panel 在位）·regime ORANGE shadow（breadth 0.77 触发·asof 09-24）·clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 幂等·周日 collectors 全景诚实 no-op（lhb 30min 节流/heat 周末/futures 本地覆盖零网络/options·moneyflow·sina_mf·ths·ah·fund_premium·system_v1=车道护栏 stdout-only/astock 面板新鲜/rev_osc SIG+BARS 幂等/aggr·alloc·grid 幂等/promotion 0/22 诚实/t35v PASS 0/0/0 六员零 pending/export 09-24 面再生/scorecard 6+28+7 卡/daily_report faces=4 token=1/fundamental 14.2h 新鲜 skip/b_layer 5222 全过）"
    "(6) 迁移窗只读实探（O-20260926-2000-bm-c 续·零干预勿双 arm 遵守）：journal 尾 12:31:22 precheck waiting（Tuanjie 编辑器三进程+cmd-holder 拦）·E:\\Fluxgroup 空骨架·旧根 E:\\Minigame 在=本机 Bigmoney 仓开工面正确·车道照跑零影响"
    "(7) S7：schtasks 三任务在役实探（IterationLoop 正在运行·Autofill 就绪 12:40·Watchdog 就绪 13:00）·state.json round_no→322"
    f"| evidence: results/_r322bmb_s6_chain.ps1+_r322bmb_s6_chain.log（32/32 rc=0 板）+smoke 25/25+watermark.jsonl 尾行 verdict=py_low_board_clear+orders 双扫 diff=NONE+post_review 0 NO+state/heartbeat json.loads 自证 epoch={epoch} int"
    "| next: sina 深面板 complete+N≥250（12:31 探针 1450/5228=27.7%·pace 21.9/min·ETA ~15:02 bm-a 三件套判定窗）→sina-construct prereg 起草；GM 审 M-20260927-01（wave-1 三新 prereg 签发/驳回归 GM 面）；周一 09-28 09:15 T-91 s3 首队列入场+开市新 bar 全链（daily→live.paper REGIME_GUARD v3 enforce 首跑→t35v→t24×2→aggr→grid 首拍→alloc→export→scorecard→daily_report）+T-87 astock 15:30 后首拉；10-01 月度三件套+REGIME_GUARD v3 日期门；R325 5x 核对；迁移重试窗至 09-29 12:00（v2.2 armed 编辑器门·勿双 arm）\n"
)
raw = open(rp, "rb").read()
needs_nl = raw and not raw.endswith(b"\n")
with open(rp, "ab") as f:
    if needs_nl:
        f.write(b"\n")
    f.write(line.encode("utf-8"))
print("round_reports.md appended, bytes:", len(line.encode("utf-8")))

# 3) heartbeat fleet/machines/bm-b.json
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch  # int by construction
hb["clock_read"] = ts  # T-separated ISO 8601 with offset
hb["round_no"] = 322
hb["current_task"] = ("r322: Sunday honest-maintenance round (S6 32/32 rc=0, py_low_board_clear legit idle, board fully gated, post_review 0 NO); "
                      "next = sina-construct prereg after sina deep panel complete+N>=250 (27.7% @12:31, ETA ~15:02 bm-a verdict window) + GM adjudication M-20260927-01 "
                      "+ Monday 09-28 T-91 s3 auto-fire 09:15 + new-bar full chain + T-87 astock first pull after 15:30")
hb["verdict"] = ("green; r322: honest maintenance round -- S0 explicit-stash dance pull FF ecb2de58->ddc8e84c (p1d_gates third-writer kept unstaged per r317 canon), "
                 "orders double-scan 96/96 zero unacked (mechanical diff), smoke 25/25, S6 32 lanes rc=0 (compute_audit CLEAN flags=0 + watermark py_low_board_clear legit idle + Sunday collectors honest no-ops), "
                 "post_review 49 rows 0 NO, pool 76 done + 1 ready T19 lane-gated bm-c (claimed 12:30 in grind), schtasks three tasks alive; board fully gated (sina panel 27.7% in-flight, GM unsigned, Optuna gated-P1, Monday chains); "
                 "migration window probed read-only (v2.2 armed, editor-gated, old root alive, zero interference)")
# fresh machine snapshot
try:
    import psutil
    hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=1), 1)
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / 1e9, 1)
    hb["total_ram_gb"] = round(vm.total / 1e9, 1)
except Exception as e:
    print("psutil snapshot fallback:", e)
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10)
    free_mb = int(out.stdout.strip().splitlines()[0])
    hb["gpu_free_vram_gb"] = round(free_mb / 1024, 2)
    hb["gpu_free_vram_mb"] = free_mb
except Exception as e:
    print("gpu snapshot fallback:", e)
with open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat ok: epoch int =", chk["heartbeat_epoch_utc"], "clock =", chk["clock_read"])
print("WRAP DONE")
