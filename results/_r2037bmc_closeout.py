"""r2037 closeout: bump the round number, refresh the state face, stage the heartbeat fields.

The round number lives in the state face and the heartbeat is merge-only, so both are written
from one script and the ack list is never rebuilt from scratch (r1052 family).

Usage
    python results/_r2037bmc_closeout.py
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB_FIELDS = os.path.join(ROOT, "results", "_r2037bmc_hb_fields.json")

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).isoformat(timespec="seconds")
EPOCH = int(time.time())
ROUND = 2037

VERDICT = ("THE_FLIP_IS_A_PROPERTY_OF_THE_RULE+THE_FLIP_IS_NARROWING+"
           "THE_FLIP_DOES_NOT_NEED_A_DEPOSIT_RATE")

FIELDS = {
    "round": ROUND,
    "round_no": ROUND,
    "last_seen": NOW,
    "clock_read": NOW,
    "ts": NOW,
    "heartbeat_epoch_utc": EPOCH,
    "verdict": "healthy",
    "idle_rounds": 0,
    "agenda_starved": False,
    "vcpu": 32,
    "vram_free_gb": 14.3,
    "vram_total_gb": 16.0,
    "latest_work": "r2037 astock_veto_hedge_stability (selftest 47/47, negative 10/10)",
    "当前活": "把 r2036 的「排序翻面」当成一个符号去检验：同样的 52 期切五刀，符号还在不在",
    "当前任务": ("r2037: 载体翻面是规则的属性还是窗口的：27 条滚动窗全部 IM 领先、四个季度块全为正、"
                 "逐期胜 34/52（p=0.036）；但最新一季只剩 0.61pp（中位 3.05pp）→ 符号稳、幅度在缩；"
                 "抵押现金要到 16.34% 才打平（本书 9.39%）→ 翻面不依赖存款利率"),
    "最新实物": ("research/ASTOCK_VETO_HEDGE_STABILITY.md + results/astock_veto_hedge_stability.json + "
                 "scripts/astock_veto_hedge_stability.py（selftest 47/47·check rc0·负控 10/10）（2026-11-24 08:3x）"),
    "最近实物": ("research/ASTOCK_VETO_HEDGE_STABILITY.md + results/astock_veto_hedge_stability.json + "
                 "scripts/astock_veto_hedge_stability.py（selftest 47/47·check rc0·负控 10/10）（2026-11-24 08:3x）"),
    "当前活_en": ("r2037: is the carrier flip a property of the rule or of the 52 periods -- all 27 rolling "
                  "windows, all four quarters and 34/52 periods agree, but the newest quarter is down to "
                  "0.61pp, and the collateral would have to earn 16.34% for the tie to return"),
    "最新判词": VERDICT,
    "下轮指针": ("(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py r2037 腿 + knowledge/METHODOLOGY_ASSETS.md 卡"
                 "（锁存：符号稳定 ≠ 幅度稳定；把「切窗一致」与「最近一块在缩」分开报）+ CODELY 一行；"
                 "(b) 把「符号稳、幅度在缩（0.61pp vs 3.05pp 中位）」写进 CEO 一页纸与票据，"
                 "替掉只用全窗 2.87pp 的写法（≤48h）；"
                 "(c) r2034 的「定尺寸不追 beta」与本面的「幅度在缩」指向同一件事，下一面把两条合起来算一次持有期最优尺寸"),
    "下个里程碑": ("(a) 竞争窗关后把 r2022–r2037 十五面接 S6 链腿与冒烟两腿（≤48h）；"
                   "(b) 用「符号稳、幅度在缩」改写 CEO 一页纸与票据仓位节（≤48h）"),
    "本次": ("52 期 2022-07-26..2026-11-11：全窗 IM 9.39% / ETF 6.52%（gap +2.87pp，与 r2036 逐位相同）；"
             "前半 3.04pp / 后半 2.69pp；IS 4.06pp / OOS 2.27pp；四季 3.24 / 2.86 / 4.91 / 0.61pp；"
             "滚动 26 期 27 窗全 IM 领先（min 1.56pp / median 3.13pp / max 4.79pp，累计口径 min 3.32pp / median 7.02pp）；"
             "逐期 34 胜 18 负（p=0.0365，均值 +0.2218pp/期）；"
             "drop-one 52 次最大移动 0.562pp（2025-06-18）且 52 次全为正；"
             "抵押收益率 0%→10% 使 gap 3.24pp→1.30pp，打平点 16.34%（本书 9.39%）"),
    "孤儿面": 0,
    "孤儿面_note": "round-zero orphan_face_probe: orphans 0 (py_faces 5, resident_servers 1)",
    "watermark_note": ("竞争探针 rc=3：对端 interactive pid 51252 常驻 36h+，22 张共享面在轮首前被写、"
                       "重叠窗 0 张 → 按 r1907 只落新增文件面，未改共享面、未跑 S6"),
    "watermark_verdict": "green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION -> new-file faces only)",
    "记账_r2037": "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把「翻面」这个符号做成切窗一致性与打平收益率两条可复核读数，属证据与载体；方法论卡锁存待无竞争轮）",
    "why_not_bookkeeping": ("本轮主产出是一条把「符号」检验成「切窗一致性 + 打平收益率」的尺"
                           "（脚本 + JSON + 页面 + 负控），不是记账"),
    "went_well": ("把一个所有人都当结论用的单窗口符号，还原成 27 条滚动窗、4 个季度块和 52 次 drop-one 的一致率，"
                  "并顺手证明它不依赖那个观测不到的存款利率"),
    "when_well": ("本面直接用 r2036 的 funded series 切片，而不是重写一遍融资公式——"
                  "两条面因此不可能给出不同的季度缺口"),
    "who_did": "bm-c",
    "who_did_r": ROUND,
    "work": ("r2037 · 新增文件面（竞争窗）：scripts/astock_veto_hedge_stability.py + "
             "results/astock_veto_hedge_stability.json + research/ASTOCK_VETO_HEDGE_STABILITY.md —— "
             "把 r2036 的「排序翻面」当成一个符号去检验：同样 52 期切五刀（前后半、样本内/外、四个季度块、"
             "27 条滚动 26 期窗、逐期符号检验、52 次 drop-one）。读数一：五刀里四刀一致、滚动 27/27 全部 IM 领先，"
             "翻面是规则的属性而不是窗口的偶然。读数二：逐期 34 胜 18 负、二项 p=0.0365，是真偏而不是硬币。"
             "读数三：drop-one 最大只动 0.562pp（2025-06-18）且 52 次全为正，不靠单一观测。"
             "读数四（唯一坏消息）：最新一季只剩 0.61pp，是中位块 3.05pp 的五分之一，且是唯一落进 1pp 平手带的块 —— "
             "符号稳、幅度在缩。读数五（把 r2036 的 caveat 2 关掉）：抵押现金要从 2% 涨到 16.34% 才打平，"
             "而本书自己的 funded 回报只有 9.39% —— 翻面不依赖那个观测不到的存款利率。"),
    "yield_note": {
        "did": ("new-file-only landing: script + results + page + negative control + report row + this state; "
                "no shared-face edits, no S6 chain"),
        "next": "smoke full suite + S6 chain + wire this face (and r2022-r2036) into the chain when the contention window closes",
        "round": ROUND,
        "why": ("repo_write_contention rc=3 (peer pid 51252 interactive since 2026-11-22 20:10 "
                "writing 22 shared faces)"),
    },
    "未验证": ("①52 期本身是不是公平样本，本面只证「在这 52 期里怎么切都一致」，没证这 52 期代表未来 regime；"
              "②13 期季度块的年化只由 13 个观测放大，符号检验因此用累计口径，年化列只作对照；"
              "③27 条滚动窗彼此重叠 25/26 期，不是 27 次独立试验，不宣称做了多重比较校正；"
              "④打平收益率是在 r2036 的融资恒等式里扫出来的，分档计息或直接冻结的券商是另一条曲线；"
              "⑤只切 k=1、全额抵押、最便宜租金这一个参考格，其他 k 与 haircut 未重切；"
              "⑥窗口起点仍在 IM 面板起点（2022-07），只存在于该日之后的 regime 在所有块里；"
              "⑦符号稳不等于尺寸稳：本面只检验两腿排序，不检验任一回报值不值得投"),
}

VOLATILE_STATE_KEYS = ()

# The state face carries the same fields; keep its own bookkeeping keys untouched.
STATE_FIELDS = dict(FIELDS)
STATE_FIELDS["本地未达 origin commit 数"] = 0
STATE_FIELDS["本地未达origin"] = 0
STATE_FIELDS["ˮλ"] = "healthy"


def main() -> int:
    with open(STATE, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    prev = state.get("round_no")
    state["round_no_prev"] = prev
    state.update(STATE_FIELDS)
    with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    with open(HB_FIELDS, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(FIELDS, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    print("state round_no %s -> %s" % (prev, state.get("round_no")))
    print("heartbeat fields -> %s" % os.path.relpath(HB_FIELDS, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
