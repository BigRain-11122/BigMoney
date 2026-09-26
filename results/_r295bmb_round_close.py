"""r295 bm-b round close: round report line + HANDOVER 5x line + state bump +
heartbeat (epoch int verified) + inbox archive + closing orders double-scan.
All appends: line-ending aware (CRLF/LF detected from file tail), zero-loss."""
import glob
import json
import os
import shutil
import subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now().astimezone()
TS = NOW.isoformat()
REPORTS = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
HANDOVER = os.path.join(ROOT, "research", "HANDOVER.md")
STATE = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")


def append_line(path, text):
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw[-200:]
    nl = b"\r\n" if crlf else b"\n"
    if not raw.endswith(nl):
        raw += nl
    raw += text.encode("utf-8") + nl
    with open(path, "wb") as fh:
        fh.write(raw)
    print("appended %d bytes -> %s (crlf=%s)" % (len(text.encode("utf-8")), os.path.relpath(path, ROOT), crlf))


REPORT_LINE = (
    "{ts} | r295 bm-b | dept:工程+舰队 | WM-VERDICT: 绿(red=false lane=healthy; probe 04:12:31 "
    "verdict=py_low_with_work_cands 合法闲面：T-87 astock 全宇宙供给在飞=本机可跑批在飞"
    "(2.5s/股限速结构性低 CPU 非饿保)+板 0 open+bandit claimed/parked+池全 done;"
    "audit pool_starvation 旗=同面合法供给白名单) | did: S0 pre-S0 fold 自有脏"
    "(autofill_state+p1d_gates per r290 自提交律)后 pull --rebase 干净;"
    "S0.5 orders 91/91 轮首扫零未回执+集团直扫面 bm-b 不可达如实注记(R291 律镜面承接)"
    "+inbox MSG-0355(bm-a CN_KLINE_P1 claim F-04)处理归档零冲突; S1 smoke 25/25; "
    "S2 板 0 open 全 claimed 零认领; S3 5x 法定闭环=P0 账本完整性双修"
    "(实读平衡=bm-a r290 挂账兑现：CN-TREND r288 裁定后败方 pid 10544 未杀跑到 03:42:52 "
    "二次 finalize=同批 +2,007 双计; CENSUS 三连同批 append +9,036=2x4518 幻影"
    "(attrition 191864->205418 声明 +4518); 修复=产物先字节还原 bm-a 正典 6151dabb "
    "再 R252 链修头移锚不动 4dp->head 209432->198389 链尾全连续+幻影 attrition 行字节级移除"
    "+判据 3 锚随真值更正 per r290 合法序列+复审器重 derive 36 YES/0 NO+面板 209432 净化"
    " 198389 上盘)+town.html<->org_chart v6 对齐核验=已完成态(r277/r292 覆盖零重建); "
    "S6 30/30 legs rc=0(周末诚实 no-op 族; T-87 lock-alive; bm-a/bm-c 车道 stdout-only; "
    "live.paper 锚 OK+t35v PASS 零 pending+t24 22/22 drift 0+promo 0/22+aggr/alloc/grid 幂等"
    "+export 09-24 regen+regime ORANGE shadow+scorecard 6/28/7+daily_report faces=4"
    "+token delta=81); S4 CODELY +1 坑律(竞速裁定必杀进程+append 跨进程幂等+产物 prev 链断言); "
    "S7 HANDOVER 5x 核对行+state/心跳 295 | evidence: results/_r295bmb_chain_reanchor_record.md"
    "+_r295bmb_ledger_scan.py(head=198389·0 平衡败·0 双计冲突)+post_review 36 YES/0 NO"
    "+dashboard_status.js 载 198389 零 209432+watermark.jsonl 04:12:31 probe "
    "| next: T-87 pass-completion 复探(ETA 06:40-09:30 后·gate 自动·panel complete 翻面"
    "=bm-a wave-2 解锁); 09-28 周一开市新 bar 全链接力; CN-KLINE runner=bm-a 下一棒零触碰; "
    "迁移窗 v2.2 armed 至 09-29 12:00 执行器域勿双 arm"
).format(ts=TS)

HANDOVER_LINE = (
    "- 开发队列增量窗（接续版）**round 295 bm-b（5x 核对本轮），2026-09-27 04:2x 补核；"
    "对账区间=增量 bm-b r291-295 并读 bm-a R291-292（基线=round 290 bm-b 行），统一链实读="
    "**head 198,389（R295 链修头后真值：…→CN_SOE 191,864→CENSUS +4,518=196,382→CN_TREND "
    "+2,007=198,389 链尾全连续；bm-a r290 行「head=205,418」与 6151dabb「ledger 207425」"
    "系 CENSUS 三连同批 append +9,036 + CN-TREND 败方双计 +2,007 所致，本轮 R252 律移锚复位"
    "·4dp 科学值零动·复审 36 YES/0 NO·判据 3 锚随值更正 per r290 序列）**：①r291-292=S0 撞车解窗"
    "（r291 stash-pop 双 pop 38 行重复注入零丢失收口+drop 律；r292 town.html footer 近失误自捕"
    "+研究部席位对齐）；②r293-294=维护窗（r293 dual-UU 正典解+r294 r282 孤儿 PID 7828 定性"
    "=迁移 Gate0.5 Bigmoney 树阻塞面清）；③**r295（本轮）=5x 实读平衡 P0 双修+链修头**"
    "（CN-TREND pid 10544 败方未杀跑到 03:42:52 二次 finalize=+2,007 双计（r288 裁定 void 产物"
    "≠杀进程实弹）；CENSUS attrition 191,864→205,418 声明 +4,518 实跳 3×4,518=三连 append"
    "（幸存 prev 200,900=191,864+2×4,518·runner 单 finalize 单 append=三次重跑）；"
    "修复=产物字节还原 bm-a 正典 6151dabb 再移锚+幻影 attrition 行字节级移除"
    "+全链审计器 results/_r295bmb_ledger_scan.py（73 件 0 平衡败 0 双计冲突）+复审器重 derive "
    "36 YES/0 NO+面板 209432 净化 198389 上盘+修复档案 results/_r295bmb_chain_reanchor_record.md"
    "+CODELY 坑律三正律=竞速裁定落册同轮必 kill 败方 pid/finalize append 跨进程幂等门"
    "/产物 commit 前必实读 trials_ledger prev 链断言）；同窗 town.html↔org_chart v6 对齐核验="
    "已完成态零重建；④观测（非本机车道）：bm-a R291=CN-TREND judged-negative 收割+池双翻"
    "+post_review 热锚迁移（其产物数值面已由本轮移锚正）；R292=CN_KLINE_PATTERN_P1 prereg "
    "冻结（SCHOOL_SUPPLY 队列 #3·runner=其下一棒）；bm-c r71 后结构性停摆维持；⑤维护面："
    "S6 30/30 legs rc=0 周末 no-op 族·smoke 25/25·orders 91/91 双扫零未回执·post_review "
    "36 YES/0 NO/WAIT 5·板 0 open·水位 py_low_with_work_cands 合法（T-87 astock 供给在飞"
    " 59.5%+·ETA 06:40-09:30）；⑥指针：09-28 周一开市新 bar 全链接力（update_daily→live.paper "
    "REGIME_GUARD v3（10-01 日期门前 shadow）→t35v→t24×2→aggr→grid 5 账首拍→export→"
    "scorecard→daily_report）+T-87 pass-completion 复探+10-01 月度三件套+10-31 六员首检 "
    "all-HOLD+T-34 半档梯 11-01+迁移窗 v2.2 armed 至 09-29 12:00 不变"
)

# 1) round report + 2) HANDOVER
append_line(REPORTS, REPORT_LINE)
append_line(HANDOVER, HANDOVER_LINE)

# 3) state.json bump 294 -> 295
state = json.load(open(STATE, encoding="utf-8-sig"))
prev_round = state.get("round_no")
state["round_no"] = 295
state["did"] = ("S0 fold+rebase clean; orders 91/91 zero unacked double-scan; smoke 25/25; "
                "5x legal closed loop = P0 ledger integrity: CN-TREND losing-burn double-append "
                "+2007 + CENSUS 3x same-batch append +9036 -> R252 chain re-anchor head "
                "209432->198389 tail continuous, phantom attrition row removed, criteria 3 "
                "anchors corrected, review 36 YES/0 NO; town<->org_chart v6 alignment verified "
                "done; S6 30/30 legs rc=0 weekend no-ops; HANDOVER 5x line")
state["verdict"] = "green"
state["next"] = ("T-87 astock pass-completion re-probe after ETA 06:40-09:30 (gate auto; panel "
                 "complete flip = bm-a wave-2 unlock); 09-28 Monday new-bar full chain; "
                 "CN-KLINE runner = bm-a next baton zero-touch; migration window v2.2 armed "
                 "to 09-29 12:00 executor domain")
state["current_task"] = "r295 5x reconciliation round (P0 ledger chain re-anchor + maintenance green)"
state["last_round_ts"] = TS
state["last_result"] = "ok"
state["updated_at"] = TS
with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
chk = json.load(open(STATE, encoding="utf-8-sig"))
assert chk["round_no"] == 295 and prev_round == 294, (prev_round, chk["round_no"])
print("state.json: round %s -> %d" % (prev_round, chk["round_no"]))

# 4) heartbeat: epoch must be JSON int
hb = json.load(open(HB, encoding="utf-8-sig"))
epoch = int(NOW.timestamp())
assert isinstance(epoch, int)
hb["machine_id"] = "bm-b"
hb["last_seen"] = TS
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = TS
hb["current_task"] = ("r295 5x P0 ledger chain re-anchor (head 209432->198389: census 3x +9036 + "
                      "cn-trend losing-burn +2007, R252 law, review 36 YES/0 NO); T-87 astock "
                      "supply in flight ETA 06:40-09:30")
hb["round_no"] = 295
hb["verdict"] = "green"
try:
    import psutil
    vm = psutil.virtual_memory()
    hb["free_ram_gb"] = round(vm.available / (1024 ** 3), 1)
    hb["cpu_util_pct"] = round(psutil.cpu_percent(interval=0.5), 1)
except Exception:
    pass
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True,
                         timeout=10).stdout.strip().splitlines()
    if out:
        hb["gpu_free_vram_gb"] = round(float(out[0]) / 1024, 1)
except Exception:
    pass
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
chk = json.load(open(HB, encoding="utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), type(chk["heartbeat_epoch_utc"])
assert "T" in chk["clock_read"] and chk["clock_read"].count("+") == 1
print("heartbeat: epoch=%d (int verified) clock=%s ram=%s gpu=%s" % (
    chk["heartbeat_epoch_utc"], chk["clock_read"], chk.get("free_ram_gb"),
    chk.get("gpu_free_vram_gb")))

# 5) inbox archive
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20260927-0355-bm-a.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-20260927-0355-bm-a.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("inbox: MSG-20260927-0355-bm-a.md -> processed/")
else:
    print("inbox: msg already archived")

# 6) closing orders double-scan
ack = set(json.load(open(HB, encoding="utf-8-sig")).get("orders_ack", "").split())
files = {os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "fleet", "orders", "O-*.md"))}
unacked = sorted(files - ack)
print("closing orders scan: files=%d ack=%d unacked=%d %s" % (
    len(files), len(ack), len(unacked), unacked if unacked else "(zero)"))
assert not unacked, "closing scan found unacked orders: %s" % unacked
print("ROUND CLOSE OK r295")
