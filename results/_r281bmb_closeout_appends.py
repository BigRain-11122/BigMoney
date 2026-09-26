"""r281 bm-b final closeout appends: CODELY law line, HQ-FEEDBACK suggestion,
round-report addendum (S7 collision record per skill discipline)."""
import datetime as dt

now = dt.datetime.now().astimezone()
ts_line = now.isoformat(timespec="seconds")

# ---- CODELY.md (tail entries end LF; trailing-newline probe first) ----
p = "CODELY.md"
raw = open(p, "rb").read()
assert raw.endswith(b"\n")
entry = (
    " - [2026-09-27 00:2x] 坑律（bm-b r281·rebase memory-union md 结构坍塌面·r188/R208 家族新参"
    "·E1 复审期自捕零外泄）：**append-only md 记忆件的 union 禁 naive 全文件行去重——"
    "splitlines+seen-set 对含结构重复行（空行/重复头行）的文件会把 61+61 行 union 成 52 行"
    "=结构坍塌（CODELY.md 实弹：base 60 行含 10 结构重复行）；正律=merge-base 字节为锚：两侧"
    "各=base+append 后缀（前缀恒等断言）→union=base+两侧 append 后缀字节直拼（零丢失），"
    "行级 union 只许对各侧新条目段做。指针=results/_r281bmb_resolve2.py 修正史+CODELY.md "
    "40,567B=39,270+597+700 直拼实录\n")
with open(p, "ab") as f:
    f.write(entry.encode("utf-8"))

# ---- HQ-FEEDBACK.md (CRLF file, trailing newline) ----
p = "HQ-FEEDBACK.md"
raw = open(p, "rb").read()
assert raw.endswith(b"\n")
fb = (
    "- F-20260927-01 [bm-b r281 " + ts_line + "·bigmoney-conflict-resolve 技能 memory-union 配方修正建议] "
    "**md 记忆件 union 配方「行级 union 去重相同行」对含结构重复行文件会坍塌结构**——r281 实弹："
    "CODELY.md（base 60 行含 10 结构重复行）按配方字面实现 splitlines 全文件去重=61+61→52 行，"
    "空行/重复头行被吞；正解=merge-base 前缀恒等断言+两侧 append 后缀直拼"
    "（40,567B=39,270+597+700 零丢失实证），或行级去重仅限各侧新条目段——建议 SKILL.md 形态表 "
    "memory-union 行补后缀直拼配方（.codely-cli=机内本地件，跨机同步面=本反馈行+各机 CODELY.md 坑律行）\r\n")
with open(p, "ab") as f:
    f.write(fb.encode("utf-8"))

# ---- round_reports.md addendum ----
p = "logs/iteration-loop/round_reports.md"
raw = open(p, "rb").read()
assert raw.endswith(b"\n")
add = (
    ts_line + " | r281 addendum (bm-b) | dept:工程 | S7 push 撞头实录（两拒两 rebase）"
    "：拒1=2 UU（autofill_state mixed-dict+ledger：launches 双侧各 cap50 union ts 升序重排→50"
    "·last_tick 整 dict 按 ts 取 bm-b 00:00:01 tick 新面·post_review.jsonl 行级 union 1758+72=1830"
    " 全行 json.loads 过）→拒2=16 UU/AA（bm-a r279 收尾同窗再生面）——13 件 take-ours 原始字节"
    "（bm-a 墙钟全面新：daily_report 00:07:51/scorecard_v1 00:06:55/strategy_scorecard 00:07:03"
    "/token 00:07:54/futures 00:07:21/heat·lhb·update_status·fundamental·regime_state·"
    "dashboard_status.json+.js/REPORT-2026-09-27 md+json 双子）、daily_scorecard 取本机侧"
    "（零墙钟同产者配对律：本机消费 post_review 最新尾 00:00:16=union 尾一致性面）、compute_audit "
    "history union 202+latest=ours、CODELY.md=base+双侧 append 后缀直拼（naive 行 union 坍塌"
    "自捕即改·40,567B·F-20260927-01 建议+坑律行已落）| evidence: _r281bmb_resolve.py（69014e67 内）"
    "+_r281bmb_resolve2.py（9af78f10 内）+复跑 smoke 25/25+push b8d82926..9af78f10 落地 | next: "
    "r282 同 r281 主线（pass 复探+周一 09-28 首次日续拉实弹+REV_OSC 消费面 TRANSFER 裁+迁移窗）\n")
with open(p, "ab") as f:
    f.write(add.encode("utf-8"))

print("closeout appends done at", ts_line)
