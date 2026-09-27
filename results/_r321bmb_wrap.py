# -*- coding: utf-8 -*-
"""r321 bm-b S7 wrap: state round_no++, round report append, heartbeat update, inbox move."""
import json, time, shutil, subprocess, os
from datetime import datetime, timezone, timedelta

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# 1) state.json round_no++ (logs/iteration-loop/state.json, no BOM, CRLF-face utf-8)
sp = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = 321
st["did"] = ("r321: 周日诚实维护轮 -- S0 pull --autostash FF d63bdb7c->6be5c343 + autostash pop UU autofill_state.json "
             "按 r317 stage-union 正典复用解（55 entries 零损失）；orders 双扫 96/96 零未回执；smoke 25/25；"
             "inbox MSG-1215（bm-a 已按判例修正 T-90-V1 判据路径 typo+重 derive 全表 YES）收讫零双写；"
             "S2 双板 0 open+池 77 条唯一 ready=T19 lane-gated bm-c；主线门控清点（sina 面板在飞/GM 未签/Optuna gated）；"
             "S6 全链 32 legs rc=0（compute_audit CLEAN·watermark py_low_board_clear 合法 idle·周日 collectors 全景诚实 no-op）")
st["verdict"] = "green"
st["next"] = ("sina 深面板 complete+N>=250 后 sina-construct prereg 起草（~15:07 bm-a 判定窗）；GM 审 M-20260927-01；"
              "周一 09-28 09:15 T-91 s3 首队列入场+开市新 bar 全链+T-87 astock 15:30 首拉；10-01 月度三件套+REGIME_GUARD v3 日期门；R325 5x 核对")
with open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json round_no ->", st["round_no"])

# 2) round report append (utf-8; preserve trailing-newline convention)
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    f"- {ts} | r321 bm-b | dept:舰队+工程 | 水位=绿（red=false@12:00:13·probe 12:22:59 py_low_board_clear 合法 idle 白名单=板 0 open+bandit 0+池内唯一 T19-PHANTOM-P1 lane_owner=bm-c R31 本机禁碰+主线全门控）"
    "| did: (1) S0 pull --autostash FF d63bdb7c→6be5c343（bm-a r320 T-90 criteria-path-fix 窗），autostash pop UU autofill_state.json 按 r317 stage-union 正典复用解（55 entries·last_tick 12:10:02·零损失·json.loads 自证）"
    "(2) S0.5 双扫 orders 96/96 零未回执（轮首轮尾一致）；集团 decisions.md 路不存在=零动作"
    "(3) smoke 25/25 (4) inbox MSG-20260927-1215 处理入 processed：bm-a 已按 r223/r270 判例修正我机 r319 注册的 T-90-V1 判据路径 typo（verdict.ring_table...→ring_table...·期望值与科学数字零动）+复审器重 derive T-90-V1 YES 10/10·全表 YES=44 NO=0——本机零双写收讫"
    "(5) S2 双板清点：job_list 0+fleet tasks 0 open（全 done/claimed）·池 77 条 76 done+1 ready（T19 lane-gated bm-c）·反重复核实=town r292 已对齐/J12 v0.7+ 已超额/J13 bm-a 拥有/J10·J18b 已交付/Optuna gated-P1（O-1120 D2 GM 面）不擅启"
    "(6) S6 全链 32 legs rc=0（bm-a r320 链脚本复用+根路径 delta·直呼 python 无 splat·rc 数字断言）：compute_audit CLEAN（pool-supply-gap 合法·flags 0·GPU 无越权·无僵尸）·watermark probe 12:22:59 py_low_board_clear（py_cpu 1.2%·open 0·bandit 0）·regime ORANGE shadow 在册（breadth 0.77 触发）·clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 幂等·周日 collectors 全景诚实 no-op（lhb 无事件/heat 周末/futures 本地覆盖零网络/options·moneyflow·sina_mf·ths·ah·fund_premium·system_v1=车道护栏 stdout-only/astock 面板新鲜/rev_osc SIG+BARS 幂等/aggr·alloc·grid 幂等/promotion 0/22 诚实/t35v PASS 0/0/0 六员零 pending/export 09-24 面再生/scorecard 6+28+7 卡/daily_report faces=4 token=1/fundamental 14.1h 新鲜 skip/b_layer 5222 全过）"
    "(7) S7：schtasks 双任务在役实探（IterationLoop 正在运行/Watchdog 就绪）·state.json round_no→321"
    f"| evidence: results/_r321bmb_s6_chain.ps1+_r321bmb_s6_chain.log（32/32 rc=0 板）+smoke 25/25+watermark.jsonl 尾行+orders 双扫 diff=NONE+state/heartbeat json.loads 自证 epoch={epoch} int"
    "| next: sina 深面板 complete+N≥250 后 sina-construct prereg 起草（三线三判律·~15:07 后 bm-a 三件套判定窗）；GM 审 M-20260927-01（wave-1 三新 prereg 签发/驳回归 GM 面）；周一 09-28 09:15 T-91 s3 首队列入场+开市新 bar 全链（daily→live.paper REGIME_GUARD v3 enforce 首跑→t35v→t24×2→aggr→grid 首拍→alloc→export→scorecard→daily_report）+T-87 astock 15:30 后首拉；10-01 月度三件套+REGIME_GUARD v3 日期门；R325 5x 核对；迁移 v2.2 armed 编辑器门勿双 arm\n"
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
hb["round_no"] = 321
hb["current_task"] = ("r321: Sunday honest-maintenance round (S6 32/32 rc=0, py_low_board_clear legit idle, board fully gated); "
                      "next = sina-construct prereg after sina deep panel complete+N>=250 (~15:07 bm-a verdict window) + GM adjudication M-20260927-01 "
                      "+ Monday 09-28 T-91 s3 auto-fire 09:15 + new-bar full chain + T-87 astock first pull after 15:30")
hb["verdict"] = ("green; r321: honest maintenance round -- S0 autostash UU resolved per r317 stage-union canon (55 entries zero-loss), "
                 "orders double-scan 96/96 zero unacked, inbox MSG-1215 T-90 criteria-path-fix receipt (bm-a fixed my r319 typo, ledger now YES=44 NO=0, zero double-write), "
                 "S6 32 lanes rc=0 (compute_audit CLEAN + watermark py_low_board_clear legit idle + Sunday collectors honest no-ops), "
                 "smoke 25/25, schtasks both alive; board fully gated (sina panel in-flight ETA~15:07, GM unsigned, Optuna gated-P1, Monday chains)")
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

# 4) inbox move
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20260927-1215-bma-t90-criteria-path-fix.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-20260927-1215-bma-t90-criteria-path-fix.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("inbox msg moved to processed")
else:
    print("inbox msg already moved")
print("WRAP DONE")
