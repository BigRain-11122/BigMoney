import io

line = (
    "\n[2026-09-26 09:0x-09:2x | r236 | bm-b OS loop] 水位判定：绿——red=false@09:00:13 lane healthy；"
    "probe 09:06:53 py_low_board_clear=合法 idle 白名单（票 0 open+bandit 0+bars 在位+池 0 ready 供给面）；"
    "audit 09:06:47 flags=[pool_starvation]=同供给面旗（r234/r235 口径非饿）。"
    "S0：轮首赃=4 件背景自动化写入三源定位闭环（autofill tick 09:00:02+watchdog C4 gates 09:00:13+watchdog C9 sweep 09:00:14——"
    "无死轮无并发会话，唯一 Bigmoney codely 会话=本机 r236）→stash→pull already up to date→pop 零冲突。"
    "S0.5：orders 全扫差集=0 未回执（全 76 件 O-*.md 逐令枚举对照 ack 集，README 非令件不计）；"
    "decisions.md 本机不可达（..\\..\\docs 缺位）=零动作如实记。S1 smoke 25/25。"
    "S2：板 0 open（全 claimed）+job_list 空+池 42/42 done+bandit next_pick null+zoo 队列观察态无 actionable"
    "（corr-watch=月更 10-01 到期、FL=2026-12、mf-IC=bm-a 认领 parked、P-B sector heat=blocked-source 风险接受案）。"
    "S3 小闭环（dept:总经办·O-2115 registry 对账 reconcile）：R92 陈旧 claim「d2 跨机复核/战报复审列/C9 腿接线未动工」"
    "实际掩蔽 3/4 已交付子件——C9 腿 bm-c r70 落地（watchdog.log 实跑 C9 post-review sweep exit=0 今日实证）"
    "+T-29 战报复审列（daily_scorecard.py 宣称→复验面）+轮 mandate ✗=P0 句（全机 prompt+bm-a 先例+C9 30min 自动扫）；"
    "真残项=跨机 LLM 复核协议（✗/存疑行→轮值机非执行机裁决入台账·机制四件#3）未接线休眠（0 ✗ 行至今）；"
    "文本级最小 diff 3+/3-（r230 律·LF 保真）+post_review selftest ALL PASS+status 维持 in_flight/WAIT 诚实零自造判据"
    "+_reconciled 留痕（r71 bm-c/r223 bm-a 先例）。复审纪律：post_review ✗ 行＝下一轮 P0——本轮 ✗0/🟡5，无 P0 修复单。"
    "S6 全链绿：14 gate（周末/车道护栏诚实 no-op+fundamental fresh 12h+b_layer all_pass）"
    "+regime ORANGE shadow day2（hs300<MA200·breadth 0.77·只记录零干预）+无新 bar（cutoff 09-24 周六）"
    "=新 bar 纸面链合法跳过+scorecard 6 员/build_status/token_meter 绿（delta=-45）。S4 记忆 1 条（registry 行龄坑律·CODELY.md）。"
    "下轮指针：12:00-13:40 南向重探日照窗（后续轮自然命中）；09-28 周一新 bar 全链接力（READY 6/6 backed by r234）；"
    "10-01 每月首轮三件套（science_audit/monthly_briefing/self_review）+corr-watch 月更。"
)
with io.open(r"logs/iteration-loop/round_reports.md", "a", encoding="utf-8", newline="") as fh:
    fh.write(line)
print("appended", len(line), "chars")

import json
p = r"logs/iteration-loop/state.json"
s = json.load(open(p, encoding="utf-8"))
s["round_no"] = 236
s["did"] = (
    "r236: board-clear maintenance round + O-2115 registry row reconciled to d2 truth "
    "(3/4 sub-items delivered unmasked: C9 leg live bm-c r70 + T-29 review column + round-mandate in practice; "
    "genuine remaining gap = cross-machine LLM re-review protocol, dormant 0 x-rows; status stays WAIT honest; "
    "selftest ALL PASS, minimal diff 3+/3-)"
)
s["next"] = (
    "12:00-13:40 southbound re-probe daylight window (later rounds hit naturally); "
    "09-28 Monday new-bar full-chain relay (READY 6/6 backed by r234); "
    "10-01 monthly first-round three-suite (science_audit/monthly_briefing/self_review) + corr-watch monthly cadence; "
    "O-2115 true remaining d2 item = cross-machine LLM re-review protocol (T-37 owner bm-a, dormant until first x-row)"
)
raw = open(p, "rb").read()
crlf = b"\r\n" in raw
with io.open(p, "w", encoding="utf-8", newline="") as fh:
    txt = json.dumps(s, ensure_ascii=False, indent=1)
    if crlf:
        txt = txt.replace("\n", "\r\n")
    fh.write(txt)
print("state.json round_no ->", s["round_no"], "| CRLF style preserved:", crlf)
