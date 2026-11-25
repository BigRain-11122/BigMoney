# r2090 bm-c closeout: round report line + state fields. Byte-faithful writer
# (state face = indent=1 + CRLF + trailing CRLF; heartbeat = indent=1 + CRLF + no trailing).
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

REPORT_LINE = (
    "2026-11-25T15:0x+08:00 | r2090 | bm-c | "
    "**PRODUCT（水位绿 red=false·孤儿面=0 py_faces=5·竞争探针 rc=0 CLEAN 单宿主 pid=87972）**："
    "上一轮挂出去的自愈任务把 8 臂烧回了一个世界——**19:40 起每 10 分钟一轮，14:23:26 收口："
    "verdict=ONE_WORLD / rebuilt=[cost40, buffer_k05_cost20] / left=[] / audit_check_rc=0 / 654.8s，"
    "任务随即自 DISABLE（Get-ScheduledTask State=Disabled 实证）**。现在 10 臂全部定价在 2026-11-24："
    "`--check` **rc=0**（十臂逐条点名），`--selftest` **144 腿 0 失败**（上一轮同一份代码是 144 腿 7 失败），"
    "floor 拟合的 rung 数回到可解——**这条红线上轮判死、这轮真的修好了，不是又换一句判词**。"
    "顺带把「红名单」这件事做成了常设件：①**全量冒烟终于跑完了**（前两轮都被静默窗守杀在 307 腿）："
    "**767 腿 749 PASS / 18 FAIL @14:36:02**，对照 10:38 那次 738 PASS / 29 FAIL——**红从 29 降到 18**；"
    "②`scripts/smoke_red_recheck.py` 新增 `--check`（selftest **20→23 腿**）：它的身份是「一张烟雾名册的照片」，"
    "所以每轮只需回答「名册动过没有」——名册 `ts` 变了=STALE（rc2，链才付重问的钱），同一名册=绿。"
    "实测 rc2→重问→rc0 三段都真跑过；③**给它和分诊器各接一条链腿**（+`treasury_curve_page`，链 369→372 腿）："
    "三条加起来在一轮没跑冒烟时只花 **0.2 秒**（三名册未动的实证），名册一动就付一次 35 秒重问——"
    "r1282 孤儿面（写了没人重跑）就此有了生产者。④对新名册重问的结果：**18 腿 3 绿 / 1 真红 / 14 内联无可独立命令**，"
    "唯一真红=`etf_book_promotion_provenance`（rows_per_face 与台账不符，下轮处理）；四桶分诊 "
    "CONTRADICTION 12→3、STALE_OR_MISSING 4→2。"
    "｜证据：`python scripts\\etf_book_phase_atlas_arms.py --check` **rc0**（cutoff 2026-11-24，十臂）/"
    "`--selftest` **144/144**；`results/etf_book_atlas_arms_rebuild.json` verdict=ONE_WORLD left=[]；"
    "`python -m smoke_test` **767 腿 749 PASS 18 FAIL**（logs/smoke_legs.json ts=14:36:02）；"
    "`python scripts\\smoke_red_triage.py` 18 红→3/2/13 四桶；`python scripts\\smoke_red_recheck.py --selftest` **23/23** + "
    "`--check` rc0（名册对齐）+ `--triage results/smoke_red_triage.json` 18 腿→3 绿/1 红/14 无命令；"
    "`Tools/s6_chain_bmc.py 2090 --only=...` **4/4**（arms/reader/ceo_page/live_usage，reader 腿自愈付 134.2s）"
    "+ **1/1** treasury_page + **3/3** 新腿；`Tools/chain_writer_audit.py` 重发布 **372 腿 / 159 面 / 155 有写者 / 0 red / 4 disclosed**，`--check` rc0"
    "｜未做（如实）：18 红里 14 条是 suite 内联块（只有整套能重问，本轮无独立命令）；1 条真红未修；"
    "S6 全链仍只跑切片（372 腿未一次性跑完）；`smoke_red_recheck` 在 chain_writer_audit 里仍标 NO_WRITER_MODE（run 形状是 --triage，审计不认）"
    "｜S0.5 双扫：fleet/orders 117 件 / 心跳 orders_ack 331 条 / state 273 条；未回执 44 件全为 2026-10-26 以前的他机 lane 广播（r2066 判例不逐令补 ack）；"
    "集团 `origin/main:docs/decisions.md` 原生字节 **250,586B sha256 79e3083b85c130b8…** == 自持水位 → 零新决策零动作；fleet/inbox 空"
    "｜S7：orphan_face_probe（py_faces=5 / orphans=0 / resident_servers=2）；attrition_ledger_guard **CLEAN**（4 账本·3 处历史缩行 healed）；"
    "Bigmoney-IterationLoop Running / Bigmoney-LoopWatchdog Ready；pre-commit / pre-push **MATCH**；"
    "Bigmoney-AtlasArmsReburn-bm-c **Disabled（自停，按设计）**；saturation_engine rc0（queue 0 / idle）"
    "｜**本地未达 origin commit 数**：commit 前实测 0/0"
    "｜**CEO 三行**：当前活＝把「8 臂停在 20 号世界」这件事真的烧完，并让「红名单」从此有人自动重问｜"
    "最近实物=`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\results\\etf_book_phase_atlas_arms.json`"
    "（2026-11-25T14:23·十臂同一世界·selftest 144/144）｜下个里程碑＝18 条红里 14 条内联腿的可独立化 + 唯一真红修复（≤48h）"
    "| 记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
)


def load(p):
    raw = open(p, "rb").read()
    return json.loads(raw.decode("utf-8")), raw


def dump_state(d):
    return (json.dumps(d, ensure_ascii=False, indent=1).replace("\n", "\r\n")
            + "\r\n").encode("utf-8")


def dump_heart(d):
    return json.dumps(d, ensure_ascii=False, indent=1).replace(
        "\n", "\r\n").encode("utf-8")


st, raw = load(STATE)
assert (json.dumps(st, ensure_ascii=False, indent=1).replace("\n", "\r\n")
        + "\r\n").encode("utf-8") == raw, "state round-trip not byte-identical"

st["round_no"] = 2090
st["last_round_no"] = 2090
st["竞争_r2090"] = (
    "repo_write_contention rc=0 CLEAN：fewer than two codely hosts alive（本宿主 pid=87972 "
    "自 14:20:34 起）；排除 9 次 scheduler/self 写入（saturation_engine/watermark_red/"
    "idle_trigger/orders_ack_scan/orphan_face_probe/repo_write_contention/host_contention）"
)
st["通过_r2090"] = (
    "orders 117 件 / 心跳 orders_ack 331 条 / state 273 条 → 未回执 44 件全为 2026-10-26 以前的"
    "他机 lane 广播（r2066 判例不逐令补 ack）；集团 origin/main:docs/decisions.md 原生字节 "
    "250,586B sha256 79e3083b85c130b8… == 自持水位 → 零新决策零动作；fleet/inbox 空；"
    "attrition_ledger_guard CLEAN（4 账本·3 处历史缩行 healed）；pre-commit / pre-push MATCH；"
    "Bigmoney-AtlasArmsReburn-bm-c 按设计自 DISABLE（Get-ScheduledTask State=Disabled）"
)
st["自捕_r2090"] = (
    "两枚本窗自捕，都由自己的守卫抓到：①**一个不校验 argv 的记账工具会把 `--check` 当成一张待收令**——"
    "`Tools/orders_ack_append.py` 只把 argv[1] 当令号，我按惯例传 `--check` 想「核对」，它却把 `--check` 与随后"
    "的 `--help` 当成两条真令 append 进 state(273→275) 与心跳(331→333) 两面。发现靠计数自己涨了 2；"
    "正法=先核清该工具的 argv 约定（头注写了 `<O-file-name>`，无 flag），再用 python 精确剔除两条伪 ack 并断言回 273/331——"
    "**判据是计数回到 r2069 的实测值，不是「我看它删了」**。②剔除时又踩第二枚：我按 state 的 indent=2 顺手写回心跳，"
    "`git diff --numstat` 立刻给出 953/953（r2043 同族：心跳 indent=1、state indent=1 但**两者都带 CRLF 且 state 结尾多一个 CRLF**）"
    "——整档 diff 会把对端并发字段一起埋掉。正法=先用「load→dump→比对原字节」自证往返恒等再落盘，两面各一次断言。"
    "两枚合起来是一条：**工程动作的对象若不是自己写的，先问它认什么格式/参数，再问字节能不能原样回来**。"
)
st["CEO 三行"] = (
    "当前活＝把「8 臂停在 20 号世界」这件事真的烧完，并让「红名单」从此有人自动重问｜"
    "最近实物=K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\results\\etf_book_phase_atlas_arms.json"
    "（2026-11-25T14:23·十臂同一世界·selftest 144/144）｜"
    "下个里程碑＝18 条红里 14 条内联腿的可独立化 + 唯一真红修复（≤48h）"
)
st["round_r2090_next"] = (
    "(a) 18 红里的 14 条内联腿：把其中可独立化的搬进 smoke_test.py 的声明式腿表，让 recheck 能重问；"
    "(b) 唯一真红 etf_book_promotion_provenance：rows_per_face 与台账不符，先判面代差还是真分歧；"
    "(c) smoke_red_recheck 的 run 形状（--triage ...）在 chain_writer_audit 里仍算 NO_WRITER_MODE；"
    "(d) S6 全链 372 腿仍未一次性跑完"
)
st["记账_r2090"] = "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把「照片型面」的每轮问题收窄成「名册动过没有」属证据与载体）"

with open(STATE, "wb") as fh:
    fh.write(dump_state(st))

with open(REPORT, "ab") as fh:
    fh.write(("\r\n" if raw else "").encode("utf-8"))
    fh.write(REPORT_LINE.encode("utf-8"))

print("state + report written")
