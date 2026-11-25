"""r2083 closeout: round ledger line + state + heartbeat (indent-preserving)."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUND = 2083
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S%z")
ISO_T = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())


def indent_of(path):
    with open(path, encoding="utf-8") as f:
        f.readline()
        second = f.readline()
    return len(second) - len(second.lstrip(" "))


def update(path, patch):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    d.update(patch)
    ind = indent_of(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=ind)
        f.write("\n")
    return ind


STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

state_patch = {
    "round_no": ROUND,
    "本轮": (
        "r2083 · PRODUCT（全量冒烟 767 腿实测 734 PASS / 33 FAIL，wall 1030s；水位绿 red=false lane=healthy "
        "next_pick 他机 claimed；孤儿面=0；竞争探针 rc=0 CLEAN 单宿主 → 本轮可动共享面）：33 红里有 4 条同一个病——"
        "读者把 k 对到了另一个 bar 上。票面有两个日子：base_bar=2026-11-24（这张票按哪个 bar 定价）与 "
        "book_decided_at=2026-11-11（名册哪天定的），k 只在排程步上跳，两日子隔着一整步"
        "（11-11→2026-10-23 步 k=0.460253，11-24→2026-11-20 步 k=0.458463）。r1886 的读者用 book_decided_at "
        "复算 k_rule，拿 0.460253 对一个写着 0.458463 的票面判「恒等式破裂」，把三个消费面一起染红——"
        "而 etf_book_k_identity_bar 早判过 IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP（r1852 读者别再判一遍）。"
        "修法=按该面已发布的 PATCH 改 bar（base_bar → as_of → book_decided_at），容差保持 6dp 不动。"
        "四条红转绿：size_rulers_decision 7/7、decision_line CHECK_OK（CONFLICT_BETWEEN_RECEIPTS→NO_CUT_OWED）、"
        "permission_persistence 6/6（上一轮连 run 都起不来）、rebal_adoption CHECK_OK PHASE_DEPENDENT。"
        "下游随刷新同步：rebalance_permission 6/6 KEEP_SUPPORTED_BY_INDEPENDENT_PATH、cut_order_gap 9/9 "
        "ORDER_WITHIN_PERMISSION、do_or_wait 13/13 NOTHING_OWED_TODAY，CEO 一页纸重生（无 CONFLICT）。"
    ),
    "当前任务": (
        "r2083 · 修红：33 条冒烟红里 4 条同根（bar 选错：base_bar vs book_decided_at），按专门面已发布的 "
        "PATCH 落地并自证 4/4 转绿；同窗自捕=FATAL 文案打印 k_schedule_last 却比较 k_schedule_at_base_bar，"
        "于是 2026-11-25 打出「0.458463 != 0.458463」——看着像浮点 bug，其实是 bar bug"
    ),
    "当前活": "把「两张面互相矛盾」的 4 条红查出共同根因（读错了 bar），改 bar 不改容差，4 条转绿、CEO 页无 CONFLICT",
    "最新判词": "SIZE_IS_A_RULER_CHOICE / NO_CUT_OWED / NOTHING_OWED_TODAY",
    "最新实物": "qa/smoke-red-r2083.md + scripts/etf_book_size_rulers_decision.py @%s" % ISO_T,
    "最近实物": "四条红转绿（size_rulers 7/7 · decision_line CHECK_OK · permission_persistence 6/6 · rebal_adoption CHECK_OK）",
    "最近实物_update": "results/etf_book_size_rulers_decision.json + results/etf_book_permission_persistence.json @%s" % ISO_T,
    "未验证_r2083": (
        "①全量 767 腿仍有 29 条红（修前 33），本轮只收 4 条，剩余清单见 logs/smoke_legs.json 的 failed 数组；"
        "②本轮未重跑整条 S6 链，只逐面跑了受影响族；③k_identity_bar 的 PATCH 文本保留原样，现在描述的是已落地状态；"
        "④心跳面 GPU 键由 Tools/gpu_face.py apply 重写，其余文本字段本窗手写"
    ),
    "下轮指针": (
        "(a) 剩下 29 条红按族分批收（先看 logs/smoke_legs.json 的 failed 数组，按「面代差 vs 真分歧」分类："
        "代差走 refresh，真分歧才动代码）；(b) 给本轮 4 条转绿腿在 smoke 里补负控（改 bar 应红、改容差不应被当成修复）；"
        "(c) S6 全链分批补跑（连续第 23 轮未跑）"
    ),
    "通过_r2083": (
        "orders 117 件 / fleet/inbox 空；集团 origin/main:docs/decisions.md 原生字节 250,586B "
        "sha256 79e3083b85c130b8… == 自持水位 → 零新决策零动作；attrition_ledger_guard CLEAN（4 账本，"
        "三处历史缩行 healed 照录）；Bigmoney-IterationLoop 重注册 no-op（pin=0）；watchdog S4U 翻转被拒"
        "（管理员提权面，LogonType 回归注记保留）；pre-commit / pre-push 爪未触发新装"
    ),
    "竞争_r2083": (
        "repo_write_contention rc=0 CLEAN：fewer than two codely hosts alive（对端 pid 79608 已退）；"
        "本宿主 pid=84212 自 09:20:03 起；排除 9 次 scheduler/self 写入（saturation_engine/watermark_red/"
        "idle_trigger/orders_ack_scan/orphan_face_probe/repo_write_contention/host_contention）"
    ),
    "孤儿面": "0",
    "孤儿面_note": "round-zero orphan_face_probe: orphans 0 (py_faces 4, resident_servers 2)",
    "记账_r2083": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把「日期判据要对到产出那个数的那张面」再落一处属证据与载体，方法卡已在库 E685）",
}

hb_patch = {
    "last_seen": ISO_T,
    "ts": ISO_T,
    "clock_read": ISO_T,
    "heartbeat_epoch_utc": EPOCH,
    "当前任务": "r2083 修红：33 条冒烟红里 4 条同根（base_bar vs book_decided_at 选错 bar），改 bar 不改容差，4 条转绿",
    "activity": "product",
    "activity_now_round": str(ROUND),
    "activity_now": (
        "r2083 · 水位绿 red=false lane=healthy · 竞争探针 CLEAN 单宿主（对端已退）· 全量冒烟 767 腿实测 "
        "734 PASS / 33 FAIL（wall 1030s）→ 收 4 条同根红：票面有两个日子 base_bar=2026-11-24 与 "
        "book_decided_at=2026-11-11，k 只在排程步上跳，两者隔一整步（0.460253 vs 0.458463），r1886 的读者用错日子"
        "复算 k_rule 就判「恒等式破裂」，三个消费面一起红；按 etf_book_k_identity_bar 已发布的 PATCH 改 bar 后 "
        "size_rulers 7/7、decision_line CHECK_OK、permission_persistence 6/6、rebal_adoption CHECK_OK 全绿"
    ),
    "artifacts": (
        "scripts/etf_book_size_rulers_decision.py, scripts/etf_book_permission_persistence.py (selftest 19/19), "
        "qa/smoke-red-r2083.md, results/etf_book_{size_rulers_decision,permission_persistence,rebalance_permission,"
        "decision_line,rebal_adoption,cut_order_gap}.json, docs/live_usage/LIVE-2026-11-25.md"
    ),
    "verdict": "healthy",
    "idle_rounds": 0,
    "agenda_starved": False,
    "ahead_origin": "0",
    "behind_origin": "0",
    "batch": "none (red-triage round, no compute batch)",
    "carrier_debt_r2083": (
        "29 条冒烟红仍在（本轮收 4 条）；S6 全链连续第 23 轮未跑（本轮只逐面跑受影响族）；"
        "四条转绿腿尚未在 smoke 里配负控（改 bar 应红）"
    ),
}

si = update(STATE, state_patch)
hi = update(HB, hb_patch)

with open(HB, encoding="utf-8") as f:
    hb = json.load(f)
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int (smoke F7)"
assert "T" in hb["clock_read"] and hb["clock_read"] == hb["ts"], "clock_read/ts must be ISO-T and equal"

LINE = (
    "%s | r%d | bm-c | **PRODUCT（全量冒烟 767 腿 734 PASS / 33 FAIL·wall 1030s；水位绿 red=false·lane=healthy·"
    "next_pick 他机 claimed；孤儿面=0 py_faces=4/resident_servers=2；竞争探针 rc=0 CLEAN 单宿主）**：33 红里 4 条同一个病——"
    "**读者把 k 对到了另一个 bar 上**。票面有两个日子：`base_bar=2026-11-24`（这张票按哪个 bar 定价）与 "
    "`book_decided_at=2026-11-11`（名册哪天定的）；k 只在排程步上跳，两日子隔着一整步（11-11 读 2026-10-23 步 "
    "k=0.460253，11-24 读 2026-11-20 步 k=0.458463）。r1886 的读者用 `book_decided_at` 复算 `k_rule`，拿 0.460253 "
    "对一个写着 0.458463 的票面判「恒等式破裂」，把三个消费面一起染红——而专门面 `etf_book_k_identity_bar` 早判过 "
    "`IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP`（r1852：生产者已声明的事读者别再判一遍）。修法=按该面**已发布的 PATCH** "
    "改 bar（`base_bar → as_of → book_decided_at`），容差保持 6dp 存储精度不动（放宽到一整步会把相邻两行的真断裂一起盖掉）。"
    "四条红转绿：`size_rulers_decision` `--check` 7 field(s) 0 mismatch（`identity_broken=[]`、判词 SIZE_IS_A_RULER_CHOICE）、"
    "`decision_line` CHECK_OK（CONFLICT_BETWEEN_RECEIPTS→NO_CUT_OWED）、`permission_persistence` 6/6（**上一轮它连 run 都起不来**）、"
    "`rebal_adoption` CHECK_OK PHASE_DEPENDENT（cells=20/phases=5）。下游随刷新同步转绿：`rebalance_permission` 6/6 "
    "KEEP_SUPPORTED_BY_INDEPENDENT_PATH（permitted_k=0.435003）、`cut_order_gap` 9/9 ORDER_WITHIN_PERMISSION、"
    "`do_or_wait` 13/13 NOTHING_OWED_TODAY，CEO 一页纸重生且无 CONFLICT 字样。**同窗自捕**：FATAL 文案打印 "
    "`k_schedule_last` 却比较 `k_schedule_at_base_bar`，于是 2026-11-25 打出「0.458463 != 0.458463」——看着像浮点 bug，"
    "其实是 bar bug；改为 `_identity_fatal()` 点名被比较的算子+bar+bar 来源。自检腿 17→19（L18 base_bar 优先/as_of 兜底/"
    "旧票面仍受检、L19 拒绝文案必须点名被比较那一对）。｜证据：`python -m smoke_test`（734/767·记录 logs/smoke_legs.json "
    "failed=33）+ 上述六面逐条 check/selftest + `qa/smoke-red-r2083.md`｜未做（如实）：全量仍有 **29 条红**；S6 全链连续第 23 轮"
    "未跑（只跑受影响族）；四条转绿腿尚未配负控。｜S0.5 双扫：fleet/orders 117 件、fleet/inbox 空；集团 "
    "origin/main:docs/decisions.md 原生字节 250,586B sha256 79e3083b85c130b8… == 自持水位 → 零新决策零动作。｜S7："
    "orphan_face_probe（py_faces=4/orphans=0/resident_servers=2）；attrition_ledger_guard CLEAN（4 账本·三处历史缩行 healed "
    "照录）；Bigmoney-IterationLoop 重注册 no-op（pin=0）；watchdog S4U 翻转被拒（提权面·LogonType 回归注记保留）。｜"
    "**本地未达 origin commit 数**：本轮 commit 前实测 origin/main…HEAD = 0/0。｜下轮指针：(a) 剩余 29 条红按「面代差 vs "
    "真分歧」分类分批收；(b) 给四条转绿腿补负控；(c) S6 全链分批补跑。｜**CEO 三行**：当前活＝把「两张面互相矛盾」的 4 条红"
    "查出共同根因（读错 bar 不是算术错）并修绿，CEO 页从「无法判定」回到「今天不欠你什么」｜最近实物="
    "`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\qa\\smoke-red-r2083.md`（2026-11-25T09:4x·4/4 转绿）+ "
    "`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\docs\\live_usage\\LIVE-2026-11-25.md`（重生·NOTHING_OWED_TODAY）｜"
    "下个里程碑＝剩余 29 条红按族收口 + S6 全链分批补跑（≤48h）| 记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3"
) % (ISO, ROUND)

with open(os.path.join(ROOT, "round_reports-bm-c.md"), "a", encoding="utf-8", newline="\n") as f:
    f.write(LINE + "\n")

print("state indent=%d heartbeat indent=%d" % (si, hi))
print("round report appended: %d chars" % len(LINE))
print("state round_no=%s" % json.load(open(STATE, encoding="utf-8"))["round_no"])
