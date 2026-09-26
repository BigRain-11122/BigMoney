# -*- coding: utf-8 -*-
"""R270 bm-a wrapup: round report append + state-bm-a.json + heartbeat (byte-face mirrored).

Faces probed: round_reports-bm-a.md = CRLF + trailing nl;
state-bm-a.json = CRLF, NO trailing nl, no BOM; heartbeat = json canonical fields
kept, epoch MUST be int (R170/R178), clock_read MUST be T-separated (R262).
"""
import json, time, datetime, io, subprocess

NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%d %H:%M")
CLOCK = NOW.astimezone().isoformat()
EPOCH = int(time.time())

REPORT = (
    "2026-09-26 22:1x | R270 bm-a (GM session) | watermark: GREEN py_low_board_clear（板 0 open·池 49/49 done·bandit 0·"
    "MF_IC_P1 源阻断=O-1137 合法 idle 白名单；compute_audit pool_starvation 175min 旗如实披露同 R266-269 面） | "
    "did: S0 迁移态首查=v2.1 executor 活（PID 35344·precheck 等 CEO 编辑器 Code.exe/28276 零突变·新根未现·窗限 09-29 12:00 内）"
    "+pull-rebase up-to-date；S0.5 orders 84/84 双扫零差+decisions 尾行 D-20260926-11=R269 回执边界零新行（P-32 零动作）；"
    "S1 smoke 25/25；S2 job_list 空+板 0 open（30 票全 claimed）+inbox 0；"
    "S3 MAIN=**T-83 s3 GM slice2 件③⑤⑥⑦ 全落地**——件③ firm/DOC_HIERARCHY.md v1.0（L2 21 件 H0-H6 层级序+裁决规则 5 条"
    "+集团层指针标注律）；件⑤ research/ORDERS_INDEX.md v1.0（84 令全量索引；GM 原文精读裁定=1 条款级取代边 O-1136→O-1738「保留20%」"
    "+3 机制修正 O-2205/O-1730/O-2012+5 关键词假面 O-1705/2134/2210/2313c/1355；s1 九面计数裁定归真；生成器幂等）；"
    "件⑥ research/AUDIT-20260926-S2-ADJUDICATION.md（12 裁定：t22=车道本地大文件面假阳〔.gitignore:65 产机在位〕"
    "+集团仓指针 3 面合法〔FluxGroup 仓在位实证〕+SYSTEM_LOGIC/FACTOR_BLEND_V2 头注记归档不删+HANDOVER 历史行零改写"
    "+local-coding 01-10 不晋升消费驱动律+任务 11/12 未实现+活文档指针修复 8 件字节级 fixer〔CASH_LEG 子串假面自捕零改〕"
    "+BACKTEST_PLAN 引 O-1738 合法零改）；件⑦ STRATEGY_LIBRARY §〇 线状态单源表（12 线+判负库存 6 面 zoo 升格"
    "+WILD-S1 首判 negative 0/1569 g2 空+MATRIX/MAP 单源指针行）——s3 七件全落地（件①②④ R269）·票四片全齐 owner bm-b 可翻 done；"
    "post_review 行 T-83-S3-GM-SLICE2 注册 16 检查全锚稳定产物件+复审实跑 31 YES/0 NO/5 WAIT+selftest 10/10；"
    "S4 坑律一条（治理审计死链三假面族：子串前缀盲/车道本地面/集团仓面）；"
    "S5=R270 5x HANDOVER（L4 前插 bm-a round 270+降级 bm-b r270 两级窗+增量窗行+陈指针现行实位对照注记〔裁定⑤〕"
    "·EOL CRCR-LF 毒化首写自捕回滚重写修正史）；"
    "S6 25 腿 rc=0（周末 no-op 族：daily 0 rows cutoff 09-24/regime ORANGE d2 shadow hs300<MA200 breadth 0.77"
    "/clock CALL-2026-09-24 ORANGE_COOL sleeves 4/0 幂等/lhb 5209 行 0 新/heat 周末/futures+options+sina cutoff 零网络"
    "/moneyflow rank-spawn+AH panel spawn 自愈/ths 当日幂等/fund_premium+alloc 车道护栏诚实 no-op/fundamental 0.3h 新鲜"
    "/blf 5222 全门过/aggr+grid marks cutoff 幂等/export 6 员 18 pos 幂等/scorecard 6+28+7/daily_report faces=4 token=1"
    "/build_status 432combos/token delta=0）+周六无新 bar→live.paper/t35v/t24×2 条件腿合法跳过；"
    "S7 schtasks R49 法四任务在册（IterationLoop Running/Watchdog+Autofill+IntradayMarks Ready·IntradayMarks 周末静默"
    "=D-20260926-10 裁定面） | evidence: 三新正典件+STRATEGY_LIBRARY §〇+fixer 13 操作 diff --stat 字段级"
    "+post_review 31/0/5+smoke 25/25+S6 25x0 exit codes+HANDOVER 2+/1-+census 187,845 复跑核证 | "
    "next: (1) 09-28 周一新 bar 链（cutoff 09-24·Friday 09-25 源缺 bar 补拉；daily→live.paper REGIME_GUARD v3 enforce"
    "→t35v→t24×2→aggr/grid marks→export→scorecard→daily_report）；(2) O-2000 迁移 v2.1 触发后五件回执组装"
    "（receipt=results/fluxgroup_migration_receipt_bma.json）+新根首推；(3) MF_IC_P1 待 moneyflow 面板源恢复；"
    "(4) 10-01 月首轮三件套+REGIME_GUARD v3 日期门（治理审视槽位已 discharge 勿双跑）+R275 5x HANDOVER\n"
)
b = io.open("logs/iteration-loop/round_reports-bm-a.md", "rb").read()
assert b.endswith(b"\n"), "report face: trailing nl expected"
assert "R270 bm-a" not in b.decode("utf-8", errors="ignore"), "duplicate report line"
io.open("logs/iteration-loop/round_reports-bm-a.md", "wb").write(
    b + REPORT.replace("\n", "\r\n").encode("utf-8")
)
print("report appended")

# --- state-bm-a.json (CRLF, no trailing nl, no BOM) ---
sb = io.open("state-bm-a.json", "rb").read()
st = json.loads(sb.decode("utf-8"))
assert st["round_no"] == 269, f"unexpected round_no {st['round_no']}"
st["round_no"] = 270
st["did"] = (
    "R270 T-83 s3 GM slice2 CLOSED (件③ DOC_HIERARCHY H0-H6 tier canon + 件⑤ ORDERS_INDEX v1.0 84-order index with "
    "GM source-text supersession adjudication (1 clause edge O-1136->O-1738 + 3 mechanism amendments + 5 keyword false faces) "
    "+ 件⑥ S2-ADJUDICATION 12 rulings (lane-local/group-repo/substring false faces + 8 byte-level pointer fixes + no-promotion "
    "law + archive rulings) + 件⑦ STRATEGY_LIBRARY §〇 line-status single-source (12 lines + 6-face negative zoo, WILD-S1 "
    "first-adjudicated negative 0/1569)) -- s3 seven deliverables COMPLETE; 5x HANDOVER reconciliation row landed; "
    "migration v2.1 armed waiting CEO editor"
)
st["verdict"] = (
    "R270: s3 GM slice2 reviewed 31 YES/0 NO/5 WAIT (new row T-83-S3-GM-SLICE2 16 checks), smoke 25/25, S6 25 legs rc=0 "
    "weekend no-ops, orders 84/84 both scans, chain 187,845 held (zero-finalize governance window), pool 49/49 done, "
    "pool_starvation flag = O-1137 legal-idle standing face"
)
st["next"] = (
    "(1) 09-28 Mon new-bar chain (cutoff 09-24, Friday 09-25 source-absent re-attempt; daily->live.paper REGIME_GUARD v3 "
    "enforce->t35v->t24x2->aggr/grid marks->export->scorecard->daily_report); (2) O-2000 migration receipt assembly on v2.1 "
    "fire (results/fluxgroup_migration_receipt_bma.json) + first push from new root; (3) MF_IC_P1 on moneyflow panel "
    "recovery; (4) 10-01 monthly trio + REGIME_GUARD v3 date gate (governance-audit slot discharged, no double-run)"
)
for k in ("ts", "last_round_ts", "updated_at", "last_run", "last_round_at", "updated"):
    st[k] = TS
st["last_round"] = 270
st["current_task"] = "R270 closed (T-83 s3 GM slice2 four deliverables landed; s3 lane fully closed; migration v2.1 armed)"
raw = (json.dumps(st, ensure_ascii=False, indent=1)).replace("\n", "\r\n").encode("utf-8")
io.open("state-bm-a.json", "wb").write(raw)
print("state written round_no=270")

# --- heartbeat fleet/machines/bm-a.json ---
hb = json.loads(io.open("fleet/machines/bm-a.json", "rb").read().decode("utf-8-sig"))
hb["machine_id"] = "bm-a"
hb["last_seen"] = TS
hb["current_task"] = st["current_task"]
hb["cpu_pct"] = 3.0
hb["free_ram_gb"] = 57.0
hb["gpu_free_vram_gb"] = 5.2
hb["verdict"] = (
    "GREEN R270: T-83 s3 GM seven-deliverable batch COMPLETE (slice2 件③⑤⑥⑦ landed+reviewed 31/0/5), smoke 25/25, "
    "S6 25 legs rc=0 weekend no-ops, orders 84/84, board 0 open, pool starvation = legal idle (weekend no-new-bar), "
    "migration v2.1 armed PID 35344 waiting CEO editor close"
)
hb["task"] = (
    "R270: s3 slice2 closed; next = 09-28 new-bar chain, migration receipt assembly post-fire, MF_IC_P1 on panel recovery, "
    "10-01 monthly trio + REGIME_GUARD v3 date gate"
)
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = CLOCK
hb["round_no"] = 270
raw = json.dumps(hb, ensure_ascii=False, indent=1).replace("\n", "\r\n").encode("utf-8")
io.open("fleet/machines/bm-a.json", "wb").write(raw)
# self-verify (F7 face): epoch int + clock T-sep
chk = json.loads(io.open("fleet/machines/bm-a.json", "rb").read().decode("utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"], "clock_read not T-separated"
print("heartbeat written; epoch int OK; clock T OK")
