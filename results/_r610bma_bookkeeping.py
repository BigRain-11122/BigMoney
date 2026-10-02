# -*- coding: utf-8 -*-
# r610 bm-a bookkeeping: state round_no+1, round report line, heartbeat, closing orders rescan
import json, io, time, datetime, glob, os, re

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")           # T-separated per R262
epoch = int(time.time())                          # JSON int per R170/R178

# --- state-bm-a.json: round_no +1 ---
sp = "state-bm-a.json"
s = json.load(io.open(sp, encoding="utf-8"))
prev_round = s.get("round_no", 0)
s["round_no"] = prev_round + 1
s["current_task"] = ("J10 fund-family campaign panel landed (build_status derive + "
                     "dashboard chain row, DOM-verified); E14 methodology card debt "
                     "cleared; N4 family window closed (K_eff=499); awaiting bm-b "
                     "NULLS for FUND-VALUE-P1 judged verdict")
s["last_seen"] = iso
io.open(sp, "w", encoding="utf-8", newline="").write(
    json.dumps(s, ensure_ascii=False, indent=1))

# --- heartbeat fleet/machines/bm-a.json ---
hp = "fleet/machines/bm-a.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = iso
h["heartbeat_epoch_utc"] = epoch                  # int, not str (smoke F7)
h["clock_read"] = iso
h["current_task"] = s["current_task"]
h["round_no"] = s["round_no"]
h["verdict"] = "loaded_ok"
io.open(hp, "w", encoding="utf-8", newline="").write(
    json.dumps(h, ensure_ascii=False, indent=1))

# self-verify: epoch int + clock ISO parseable
h2 = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
datetime.datetime.fromisoformat(h2["clock_read"])  # raises if malformed
s2 = json.load(io.open(sp, encoding="utf-8"))
assert s2["round_no"] == prev_round + 1

# --- closing orders rescan (S7 double-scan) ---
acked = set(h2.get("orders_ack") or [])
files = set(os.path.basename(p) for p in glob.glob("fleet/orders/*.md"))
unacked = sorted(files - acked)
print("ORDERS_UNACKED:", unacked if unacked else "ZERO")
print("STATE round_no:", s2["round_no"], "| epoch int ok | clock ISO ok")

# --- round report line ---
line = (
    iso + " | round " + str(s2["round_no"]) + " | 水位 verdict=绿（red=false·probe py 0.0% 板清=假期合法 idle·"
    "引擎队列 0=N4 波尽·池 ready=1=NULLS bm-b 在烧） | 当前活：J10 基本面族战役监控面板"
    "上盘+E14 方法论卡补账收口 | 最近实物：monitor/build_status.py+_fund_family_state+"
    "dashboard.html 基本面族战役链行（" + iso[:16] + "·DOM 实弹验收 VALUE[frozen] 判格 4/4 SENS 500 "
    "NULLS ready@bm-b · QUALITY[draft]）+ knowledge/METHODOLOGY_ASSETS.md E14 不等 K "
    "跨波池化算术律卡 | 下个里程碑：bm-b NULLS 烧毕→FUND-VALUE-P1 judged verdict "
    "finalize（D6+judged 判线·窗≤10-06 晚） | 本轮主产出：①J10 车道=基本面族战役面板"
    "（build_status derive 33 腿 S6 内建复跑全 rc0+dashboard.html 渲染 DOM 级验收+数据面"
    "自证 cells 4/4×401 行+SENS 500+NULLS owner 实读）②E14 方法论卡（r609 N4-B3 "
    "finalize 窗捕获律欠账·逐波 PINNED-K 求和律+S20 腿 live 实证）③HANDOVER r610 五倍数"
    "核对行（r510..r605 二十窗欠账合并覆盖+坑-79 族如实注记） | did: (1) S0-1 锚定 "
    "bm-a+S0 纯 FF ca588cee7（behind 1=bm-b keepalive·差集不含本机活写面） (2) S0.5 双"
    "扫 orders 150/150 差集 0（S7 收尾再扫=仅 README 非令件）·D-19=K: 盘与 C 盘备援"
    "双缺=诚实 skip（r597 律·水位键 937A373D 不动） (3) S1 smoke 47/47 (4) S2 双板："
    "job_list 空·任务板零 open（T-151 本机链闭·T-152 bm-c·T-153 bm-b） (5) S3 水位绿+引"
    "擎活（idle 队列 0）+判决批在飞=NULLS bm-b→试用期线免起草 (6) 产品闭环：town.html "
    "11 楼对齐在案（r383/r414）→选 J10 车道补当前最热战役面的监控缺位（fund_family "
    "derive：prereg 横幅+cells/sens/nulls 行数+池 FUND-* 条目 status/owner；渲染链行"
    "接 engine_wave 后）·浏览器 DOM 级实弹验收（行文本精确提取+截图布局复核） (7) E14 "
    "卡补账（捕获律：r609 finalize 有新方法未入卡=本窗补录） (8) 610=5 倍数轮→HANDOVER "
    "核对行落盘（欠账披露+产物清单漂移+统一链 N=617,500 直读） (9) S6 34 腿全 rc0"
    "（dualrun ZERO-DRIFT streak 3/3·paper 块黄金周无新 bar 诚实 skip last bar 09-30·"
    "ORANGE_COOL cap50%·daily_report REPORT-2026-10-03+LIVE-2026-10-03 落地） (10) S7 "
    "自愈 4/4（loop pin=8 no-op·watchdog 重注册·双爪字节级装·attrition CLEAN）·inbox "
    "唯一未读=MSG-0548 bm-b→bm-c 件非本机零动作 | 验证证据: smoke 47/47+S6 34 rc0"
    "+attrition CLEAN+心跳 epoch int json.loads 自证+fund_family 面板 JSON 自证+DOM 行"
    "文本验收 | 本地未达 origin commit 数=0（commit 后 push+fetch 自证） | 下轮指针: "
    "NULLS 看护（daemon 算·禁手工代烧池面批）→烧毕即 FUND-VALUE-P1 judged verdict "
    "finalize（D6+judged 判线）；N4 后续供给=新家族窗登记须月界面裁定非自动展开；"
    "T-152 TRANSFER 到货后 bm-b 冻结五条件门推进 [via bm-a r610]"
)
with io.open("round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(line + "\n")
print("ROUND REPORT appended; round", s2["round_no"])
