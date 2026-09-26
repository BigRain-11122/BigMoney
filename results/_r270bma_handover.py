# -*- coding: utf-8 -*-
"""R270 bm-a 5x HANDOVER reconciliation update (anchor-insert per r260/R265 precedent).

Edits (fail-closed anchored, byte-face mirrored CRLF + trailing nl):
  1. L4 最近核对 chain: prepend bm-a round 270, demote bm-b round 270 to 上一次核对,
     drop demoted bm-a round 265 tail (two-level window per R265 precedent).
  2. File end: append round 270 bm-a increment-window row.
Facts re-derived this round: chain head 187,845 census-run (zero finalize window);
pool 49/49 done; orders 84/84; post_review 31 YES/0 NO/5 WAIT (1470 rows); smoke 25/25.
"""
import io, sys

PATH = "research/HANDOVER.md"
b = io.open(PATH, "rb").read()
assert b.endswith(b"\n") and b"\r\n" in b[:500], "byte face drifted"
s = b.decode("utf-8")

# --- surgery 1: L4 chain prepend ---
OLD_HEAD = "最近核对=bm-b round 270（2026-09-26 19:5x·对账增量=文末 round 270 bm-b 行〔"
NEW_HEAD = (
    "最近核对=bm-a round 270（2026-09-26 22:1x·对账增量=文末 round 270 bm-a 行〔bm-a R266-270 窗+bm-b r268-274 并读："
    "**T-83 s3 GM 七件套全落地**（R269 slice1 件①②④+R270 slice2 件③DOC_HIERARCHY 层级序正典/件⑤ORDERS_INDEX 84 令+取代裁定面"
    "/件⑥12 裁定+活文档指针修复 8 件/件⑦STRATEGY_LIBRARY §〇 线状态单源表+zoo 升格）"
    "+O-2000 迁移 v2.1 armed 待 CEO 编辑器（precheck 零突变）；统一链 187,845 平持=本窗零批 finalize"
    "（治理面+迁移面零批·MF_IC_P1 待 moneyflow 面板源恢复）〕）；"
    "上一次核对=bm-b round 270（2026-09-26 19:5x·对账增量=文末 round 270 bm-b 行〔"
)
assert s.count(OLD_HEAD) == 1, "L4 head anchor not unique"
s = s.replace(OLD_HEAD, NEW_HEAD)

# drop demoted bm-a round 265 tail from L4 (two-level window); keep line boundary + CRLF face
CUT = "〕）；上次=bm-a round 265（"
i = s.find(CUT)
assert i > 0, "L4 cut anchor missing"
j = s.find("\n", i)
assert j > i and s[j - 1] == "\r", "L4 CRLF boundary missing"
s = s[:i] + "〕）。\r\n" + s[j + 1:]

# --- surgery 2: append increment-window row ---
ROW = (
    "- 开发队列增量窗（接续版）**round 270 bm-a（5x 核对本轮），2026-09-26 22:1x 补核；"
    "对账区间=bm-a R266-270 增量+bm-b r268-274 并读（基线=round 265 bm-a 行·round 270 bm-b 行已收讫窗），"
    "统一链 187,845 平持实读（census 复跑核证=本窗零批 finalize：T-83 s2/s3 治理面零批·O-2000 迁移面零批·MF_IC_P1 待源）**："
    "①**bm-a R266-270=T-83 s3 GM 七件套收口+O-2000 迁移窗**——R266 post_review CRLF 正典面修+T-83 s4 季度接线；"
    "R267 维护窗+O-2000 收令 ack 盘点快照；R268 迁移执行器 v1 三败收尸+stash 三仓回救+v2（precheck-first 零冻结）"
    "+R269 s3 slice1（JUDGMENT_MATRIX 9 判据面/ACCOUNT_LIFECYCLE 五环/org_chart v6 KPI 刷新）；"
    "**R270 s3 slice2=件③ firm/DOC_HIERARCHY.md v1.0（L2 21 件层级序 H0-H6+裁决规则 5 条+集团层指针标注律）"
    "+件⑤ research/ORDERS_INDEX.md v1.0（84 令全量索引；GM 原文精读裁定=1 条款级取代边 O-1136→O-1738「保留20%」"
    "+3 机制修正 O-2205/O-1730/O-2012+5 关键词假面；生成器幂等）"
    "+件⑥ research/AUDIT-20260926-S2-ADJUDICATION.md（12 裁定：t22 双链=车道本地大文件面假阳〔.gitignore:65〕"
    "/集团仓指针 3 面合法/SYSTEM_LOGIC+FACTOR_BLEND_V2 头注记归档不删/local-coding 01-10 不晋升消费驱动晋升律"
    "+任务 11/12 未实现/活文档指针修复 8 件字节级幂等 fixer〔CASH_LEG 子串假面自捕〕/BACKTEST_PLAN 引 O-1738 合法零改）"
    "+件⑦ STRATEGY_LIBRARY §〇 线状态单源表（12 线×状态×判据面×载体+判负库存 6 面 zoo 升格"
    "·WILD-S1 首判 negative 0/1569 g2 注册空·MATRIX/MAP 单源指针行接线）**——s3 七件全落地、票四片全齐（owner bm-b 可翻 done 收口）；"
    "②**bm-b r268-274 并读**（T-83 s2 检测面/T-81 闭票/post_review sha 锚 LF git-blob 正典面根修/T-76 五面闭"
    "/迁移执行器 20:48 收尸 CwdProbe 捐赠 bm-a v2.1 吸收）；"
    "板 0 open/池 49/49 done/orders 84/84 双扫零未回执/post_review 31 YES/0 NO/5 WAIT（1,470 行零 ✗）/smoke 25/25；"
    "S6 25 腿 rc=0（周末 no-op 族·moneyflow rank-spawn+AH panel spawn 自愈·fund_premium/alloc 车道护栏诚实 no-op·周六无新 bar 条件腿合法跳过）；"
    "**陈产物指针现行实位对照（件⑥裁定⑤一次性注记，HANDOVER 历史行按 r252 律零改写）**："
    "results/g2_folk.json→results/shortline_g2_folk.json、results/p4_folk_screen.json→results/shortline_p4_folk.json、"
    "research/{P5_RANDOM_ENTRY,XLIB_SYNTH}.md→research/shortline/ 同名、screening/gtja191_ops.py→research/shortline/screening/——此后新行用实位；"
    "最近窗=09-28 周一新 bar 全链接力+10-01 月度三件套+REGIME_GUARD v3 日期门生效+R275 5x 核对。\n"
)
assert "增量窗（接续版）**round 270 bm-a" not in s, "duplicate end-row"
if not s.endswith("\n"):
    s += "\r\n"
s += ROW.replace("\n", "\r\n")

raw = s.encode("utf-8")   # decoded str already carries CRLF; NO re-normalize (r270 EOL-poison self-catch)
io.open(PATH, "wb").write(raw)
print("HANDOVER updated: L4 chain prepended (bm-a R270 <- bm-b r270), end row appended")
