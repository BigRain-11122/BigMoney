# r690 bm-b: HANDOVER 5x check (690 = 5-multiple) -- insert newest-first
# blockquote line after the title. Bytes mode + needle count==1 (r657 EOL law).
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "research", "HANDOVER.md")

LINE = (
    "> bm-b round 690 五倍数核对（2026-10-04 19:5x·增量窗 r686-690 五轮）：增量窗 "
    "r686-690=bm-b 面（**金周值守主线+push-race 收口连营+N2-W15 评审/席位双产窗**——"
    "r686 值守〔trio V898/Q707/D541·RAM-floor gate 3.55GB·S7 三波竞速实录：crash_fuse "
    "单 UU 按 r626d-② 属主语义取 theirs（bm-a code_changed 清闸=新正主）+pre-push 爪正"
    "拦删除集→集成后 DELIVERED〕；r687 值守〔trio V902/Q711/D544·S6 38/38·dualrun "
    "ZERO-DRIFT streak 51·post_review ✓45/✗0/🟡5 零活红〕；r688 值守+S7 爪拦陈旧基座假"
    "象收口〔fetch 实核 165b9a3b3→merge 净路 14 UU canon 解=r686 resolver 血统复跑"
    "（r456 side_pick 回退腿在位已核·12 ours+1 theirs+token per-key union ours5）+"
    "marker 行首判定=0（4 子串命中=九月历史轮报告合法叙述）+round_reports 联集自证〕；"
    "r689 值守〔trio V912/Q718/D551·orders 154/154·smoke 48/48·quartet ok〕+closeout "
    "16 UU per-face resolver（15 ours ts-newer+1 theirs compute_audit+token "
    "side_pick ours5-theirs0）+daemon churn absorb；r690=本核对轮 **N2-W15 独立评审 "
    "PASS+supply 物化席位认领**〔评审正主履约 MSG-1845 条款 2：selftest 17/17 直跑+"
    "合同面三面恒等 541_500/542_000/542_500+L4 N1_BANDS 活导出/L8 显式 pop 源码实态+"
    "band gate ADMIT（r250 一步律合规）+generate 一次性门+RAM 门双闸·回执 _r690bmb_"
    "n2_review.json；席位=F-04 先行 MSG-2026-10-04-1940-bmb-ALL+池条目 PERPETUAL-"
    "N2-W15-GENERATE autofill submit 入池（W14 同型·RAM 窗 daemon 自取·12 分片 "
    "screen 条目=candidates 落地后接力）+inbox_guard 发件行判例入 CODELY+CODELY 热冷"
    "窗 r453 纯回执迁 archive 202610.md〕+S0 双 push-race 净路〔absorb+单 UU "
    "crash_fuse per-face newer-wins ours（contest-rc refusal 面 19:32:14>19:27:04）"
    "+bm-c r492 N2-W15 冻结波/bm-a r693 收口波/bm-a contest-rc claim 波吸收+claim "
    "pre-align r626d-② 属主判读〕+S6 38/38 rc0（REPORT/LIVE 再生·update_lhb 11/11 实"
    "拉·ZERO-DRIFT streak 51 @378））产物清单漂移=results/_r690bmb_n2_review.json"
    "〔评审回执〕+results/runnable_pool.json PERPETUAL-N2-W15-GENERATE 条目〔r690 "
    "fc337da55〕+fleet/inbox/MSG-2026-10-04-1940-bmb-ALL.md〔席位声明 pending=活冻"
    "结面〕+CODELY.md 坑律 r690 行+r453 迁移冷指针+research/memory-archive/202610.md"
    "『热冷整编 2026-10-04 r690 bm-b 窗批』节+results/_r686..690bmb_* 工件族+docs/"
    "daily_report/REPORT-2026-10-04.*+docs/live_usage/LIVE-2026-10-04.* 逐轮再生件；"
    "统一链头=646,799（bm-c r484 冻结窗实读·W3 judge finalize 落地后前移）；orders "
    "154/154 双扫零未回执全窗维持；smoke 48/48；D-19 4E5BE321/68947C17 双 MATCH 零消"
    "费；池态=FUND 三族 NULLS bm-b canonical 在飞（V912+/Q718+/D551+ @19:16 读数·ETA "
    "V 10-06T17/Q 10-07/D 10-08·finalize 窗=V 收口后开）+PERPETUAL-N2-W15-GENERATE "
    "ready（RAM 窗 daemon 自取）+CONTEST-YTD-P1-RC bm-a 在烧+W3 judge 4 分片 bm-c 在"
    "飞（~22:1x finalize 观察）；指针：**N2 generate candidates 落地→12 分片 screen "
    "条目接力+screen-prep（窗≤10-08）→trio V 收口 10-06T17→FUND nulls finalize 面"
    "（r668 池双翻同窗律）→W3 judge finalize 观察窗→10-09 开市前数据链完备核验**。\n"
    ).encode("utf-8")

raw = open(P, "rb").read()
NEEDLE_TAIL = LINE[:60]
assert raw.count(NEEDLE_TAIL) == 0, "dup gate: r690 line already present"
TITLE = "# Bigmoney 交接与成果收割指南（HANDOVER）".encode("utf-8")
assert raw.count(TITLE) == 1, "title needle"
i = raw.index(TITLE) + len(TITLE)
# eat the EOL right after the title (LF or CRLF)
if raw[i:i + 2] == b"\r\n":
    eol, i = b"\r\n", i + 2
elif raw[i:i + 1] == b"\n":
    eol, i = b"\n", i + 1
else:
    raise SystemExit("no EOL after title")
out = raw[:i] + LINE + raw[i:]
open(P, "wb").write(out)
chk = open(P, "rb").read()
assert chk.count(NEEDLE_TAIL) == 1 and chk[:i] == raw[:i] and chk[-(len(raw) - i):] == raw[i:]
print("HANDOVER 5x line inserted (bytes=%d, eol-after-title=%r)" % (len(LINE), eol))
