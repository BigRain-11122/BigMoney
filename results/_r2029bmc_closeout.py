"""r2029 bm-c closeout: state round bump, heartbeat fields, one round-report row.

Three faces only, all single-writer for this machine:
  state-bm-c.json          round_no 2028 -> 2029, rounds_done 1963 -> 1964
  fleet/machines/bm-c.json via Tools/heartbeat_write.py apply (merge-only)
  fleet/round_reports-bm-c.md one appended row

Nothing here touches a peer-owned face.  The numbers typed into the report row are
the ones the face printed; nothing is recomputed here.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
FIELDS = os.path.join(ROOT, "results", "_r2029bmc_hb_fields.json")

NEW_ROUND = 2029


def now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def bump_state() -> dict:
    with open(STATE, encoding="utf-8") as fh:
        st = json.load(fh)
    prev = st.get("round_no")
    st["round_no_prev"] = prev
    st["round_no"] = NEW_ROUND
    st["rounds_done"] = int(st.get("rounds_done") or 0) + 1
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    return st


def write_hb_fields(iso: str, epoch: int) -> dict:
    fields = {
        "machine_id": "bm-c",
        "round_no": NEW_ROUND,
        "last_seen": iso,
        "ts": iso,
        "clock_read": iso,
        "heartbeat_epoch_utc": int(epoch),
        "verdict": "healthy",
        "task": "r2029: the sizing band beta's own standard error buys (3,919 lots = 3,900 +- 900)",
        "activity": "product",
        "activity_now": (
            "r2029: beta 0.9013 has se 0.0526, so the 1,000,000 ticket is 3,457..4,381 lots "
            "-- a 924-lot band, 1.55x the 595 lots the price date moves (r2028); the worst "
            "end of the band costs only +0.79pp residual vol, so the ticket should print "
            "3,900, not 3,919"),
        "activity_now_round": NEW_ROUND,
        "artifacts": (
            "scripts/astock_veto_hedge_band.py (selftest 37/37); "
            "results/astock_veto_hedge_band.json; research/ASTOCK_VETO_HEDGE_BAND.md; "
            "results/_r2029bmc_band_negative.py (13/13)"),
        "batch": "none this round (contention rc=3: new-file faces only)",
        "chain": "S6 chain NOT run this round (Tools/s6_chain_bmc.py is a peer-written shared face)",
        "chain_verdict": "unchanged this round; r2028's chain state stands",
        "idle_rounds": 0,
        "agenda_starved": False,
        "ahead_origin": 0,
        "behind_origin": 0,
        "carrier_debt_r2029": (
            "the hedge family (r2022-r2029) still has no S6 leg and no smoke leg -- both "
            "files are peer-written shared faces, so the debt waits for a contention-free "
            "window; the r2028 dating face and this one are the two legs to wire"),
    }
    with open(FIELDS, "w", encoding="utf-8") as fh:
        json.dump(fields, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    return fields


ROW = (
    "| {stamp} | r2029 **新增文件面**（竞争窗 rc=3·不动共享面） | "
    "**手数的诚实误差带**：`scripts/astock_veto_hedge_band.py` + "
    "`results/astock_veto_hedge_band.json` + `research/ASTOCK_VETO_HEDGE_BAND.md`。"
    "r2026 定默认档、r2027 印 3,919 手、r2028 印日期错位 595 手——三轮都印三到四位数，"
    "没人说这些位数里有多少是真的。本面只做一件事：beta 自己的标准误换成手数是多少。"
    "**读数一**：beta **0.9013**，se **0.0526**（t=17.13·dof=41），95% 带 **0.7950..1.0076**"
    "（宽 0.2126）。**读数二**：1,000,000 账面的 3,918.83 手，95% 带 **3,457..4,381 —— 宽 924 手**，"
    "是 r2028 日期错位（595 手）的 **1.55 倍**。**读数三（三方对照同价同资本）**：哪天的价 **595 手** /"
    " beta 的不确定度 **924 手** / 换成样本外 beta（1.0263）**543 手** —— 三个同量级，"
    "日期错位是最小的那个。**读数四（但风险不在乎）**：beta 取带下端 0.7950，残余年化波动只从 "
    "**10.76% 升到 11.55%（+0.79pp，线 1.0pp）**；取整 1.0 是 10.64%（更低）；取样本外 1.0263 是 "
    "10.71%。**判词**：`BAND_WIDER_THAN_THE_DATING` + `BETA_ERROR_IS_CHEAP_IN_RISK_TERMS` → "
    "票据应印「**约 3,900 手**」：整百取整只让隐含 beta 动 **0.00433**（0.08 个标准误，比自己的带宽小两个数量级）。"
    "**读数五（beta 会动）**：滚动 20 期拟合 **0.885..1.280**（宽 0.395 = **7.5 个 se**）；"
    "in-sample 0.9013 vs 持有回不用的样本外 1.0263 —— 单个数代表不了它，这正是本面把带而非点印出来的原因。"
    "**读数六（期货臂复述 r2027）**：1M 资本下 IM 的整条带（0.78..0.98 手）落在一个合约内——那臂在此资本压根配不出 beta。"
    "｜**验证证据**：`--selftest` **37/37 PASS**（t 临界值三腿 / OLS 斜率与 se 三腿 / 噪声放大 se 与样本窄化 se / "
    "退化输入四腿 / 手数与取整五腿 / 残余波动四腿 / 两判词双向+缺面不崩六腿 / 滚动窗三腿 / "
    "活面五腿：点估计与 r2022 已发布 beta 逐位相等、带宽=高端-低端、日期错位从父面读出非手抄）；"
    "`run` rc0（evidence_cutoff **2026-11-20**）→ 双件落盘；`check` **rc0**（4 组拟合 × 7 字段 + 8 行梯子 × 7 字段 + "
    "5 行风险面 × 3 字段 + 双判词 + 滚动表长逐项重推，页面逐字验两个判词词）。"
    "**负控 `results/_r2029bmc_band_negative.py` 13/13 PASS**（8 条缺陷形：手数/se/带宽/残余波动/双判词/两处页面丢词 → "
    "CHECK FAILED 且**不带** STALE；2 条漂移形：父面动、价格面板动 → STALE 且**不带** CHECK FAILED；"
    "缺面 → STALE 不崩；跑完发布面逐字节未动且仍 rc0）。"
    "｜**S0**：`fleet/machine.json`=bm-c；`orphan_face_probe` py_faces=5 **orphans=0** 零杀；"
    "`repo_write_contention` **rc=3 CONTENTION**（2 宿主：本宿 pid 77720；对端 interactive pid 51252＝11-22 20:10 起常驻，"
    "30 张共享面在轮首前被对端写、重叠窗 0 张）→ 只落新增文件面，未改共享代码/数据面、未跑 S6 链、未跑全量 smoke。"
    "｜**S0.5 双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116 令 / 329 回执 / 124 陈旧注记 / unacked=[]）；"
    "集团 `git cat-file blob origin/main:docs/decisions.md` **原字节** sha256 = **79e3083b85c130b8**（250,586 B）== state 水位 "
    "→ 零新决策零动作；`docs/orders.md` 原字节 sha256 = **99e8e77d093cc13d**（103,567 B）== 水位 → 零新行；fleet/inbox 0 件。"
    "｜**S1（诚实边界）**：全量 smoke **未跑**（`smoke_test.py` 与 `logs/smoke_legs.json` 是对端写的共享面）；"
    "本轮以 37/37 selftest + 13/13 负控 + run/check 双 rc0 背书，**不宣称全绿**。｜**S6**：未跑（共享面）。"
    "｜**S7**：`state round_no 2028→2029`（rounds_done 1963→1964，round_no_prev 留痕 2028）；"
    "心跳经 `Tools/heartbeat_write.py apply` 合并写；`& Tools/register_loop_task.ps1` **phase ok**（pin=0 current=0，"
    "首燃 11/24 06:05 未动）；`attrition_ledger_guard scan` **CLEAN**（4 账本，4 处历史缩行 healed 注记照录）；"
    "`pre-commit`/`pre-push` 与 `Tools/git-hooks/` 逐字节（CR 归一）MATCH。"
    "｜**CEO 过程可见面**：当前活＝把「3,919 手」这个数里到底有多少是真的算出来，并给出该印多少钱；"
    "最近实物＝`K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ASTOCK_VETO_HEDGE_BAND.md`"
    "（2026-11-24 06:0x·**3,919 手的 95% 带是 3,457..4,381**、比日期错位大 1.55 倍；"
    "带下端只多 0.79pp 残余波动 → **票据印「约 3,900 手」**）＋`results\\astock_veto_hedge_band.json`＋"
    "`scripts\\astock_veto_hedge_band.py`（selftest 37/37）＋`results\\_r2029bmc_band_negative.py`（负控 13/13）；"
    "下个里程碑＝（a）竞争窗结束后把 r2022–r2029 七面接 S6 链腿 + 冒烟两腿（≤48h）；"
    "（b）把「约 3,900 手（±900）」这条带接到 CEO 一页纸与票据的仓位节，替代现在的 3,919（≤48h）。"
    "｜**未验证（如实）**：①带宽是经典 OLS 抽样带，**不覆盖关系本身变化**——样本外 1.0263 与滚动 0.885..1.280 是它会变的证据，"
    "但那部分不在 95% 带里；②periods 是 20 根一组、20 根一隔的不重叠窗（假设成立才可用此误差模型）；"
    "③residual vol 用全窗配对、点取 in-sample beta，混合了两种样本口径；"
    "④保证金/券源/成本/基差全部照抄父面未重估；⑤账面未重估，点与带都坐在陈旧资本上（r2028）；"
    "⑥本面是口径/下单检查件，不是可交易策略。｜**本地未达 origin commit 数**＝推送后复核。"
    "记账：轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把「点」写成「带」属证据与载体）。"
)


def append_report(stamp: str) -> None:
    row = ROW.format(stamp=stamp)
    with open(REPORT, "a", encoding="utf-8", newline="") as fh:
        fh.write(row + "\n")


def main() -> int:
    iso = now_iso()
    epoch = int(time.time())
    stamp = iso[:16].replace("T", " ")
    st = bump_state()
    fields = write_hb_fields(iso, epoch)
    append_report(stamp)
    print("state round_no=%s prev=%s rounds_done=%s"
          % (st["round_no"], st.get("round_no_prev"), st.get("rounds_done")))
    print("heartbeat fields -> %s (round_no=%s, epoch_is_int=%s)"
          % (os.path.relpath(FIELDS, ROOT), fields["round_no"],
             isinstance(fields["heartbeat_epoch_utc"], int)))
    print("report row appended at %s" % stamp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
