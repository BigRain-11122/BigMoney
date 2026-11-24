"""r2039 closeout: bump the round number, refresh the state face, stage the heartbeat fields.

The round number lives in the state face and the heartbeat is merge-only, so both are
written from one script and the ack list is never rebuilt from scratch (r1052 family).

Usage
    python results/_r2039bmc_closeout.py
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB_FIELDS = os.path.join(ROOT, "results", "_r2039bmc_hb_fields.json")

TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).isoformat(timespec="seconds")
EPOCH = int(time.time())
ROUND = 2039

VERDICT = ("THE_CEILING_IS_A_RATIO_NOT_A_WAIT+PARTIAL_HEDGING_DOES_NOT_MAKE_THE_WAIT_CHEAP"
           "+THE_POINT_ESTIMATE_IS_THE_WORST_OF_THREE_BETAS"
           "+YOU_MUST_ALREADY_HOLD_MOST_OF_THE_HEDGE")

LATEST = ("research/ASTOCK_VETO_HEDGE_WAIT_LADDER.md + "
          "results/astock_veto_hedge_wait_ladder.json + "
          "scripts/astock_veto_hedge_wait_ladder.py（selftest 49/49·check rc0·负控 29/29）"
          "（2026-11-24 09:2x）")

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
    "vram_free_gb": 12.6,
    "vram_total_gb": 16.0,
    "latest_work": "r2039 astock_veto_hedge_wait_ladder (selftest 49/49, negative 29/29)",
    "当前活": "把「等待」从一张价签拆成一条阶梯：等待期保留多少对冲，每年付多少波动",
    "当前任务": (
        "r2039: r2038 在边界里写「部分对冲的读者付得更少」却没算。本面用 band 面自己印的五条残差行"
        "（它们是一个二次型的五个点，五取三反解出 Var/Cov/Var，多出的两行当检查）把任意对冲比例 k 变成"
        "等待价格：k=0 复现 16.580pp/年；k=0.65（BUDGET 规则 A）仍要 2.724pp/年（27,242 元/百万），"
        "是天花板的 224.5 倍；打平带只有 k∈[0.8986, 1.0427]——对冲要几乎全部上完，"
        "「等带宽变窄」才不比带宽本身更贵"),
    "最新实物": LATEST,
    "最近实物": LATEST,
    "当前活_en": (
        "r2039: turn the wait from one price tag into a ladder -- the wait costs what the hedge "
        "you keep on leaves exposed; fitting the band face's five published residual rows to the "
        "three-parameter identity R(k)^2 = Vb - 2k*Cov + k^2*Vh recovers the book's own volatility "
        "and the full-window beta to the digit, and shows the wait is cheap only above k=0.8986"),
    "最新判词": VERDICT,
    "下轮指针": (
        "(a) 无竞争轮：smoke_test.py 两腿 + Tools/s6_chain_bmc.py r2039 腿 + "
        "knowledge/METHODOLOGY_ASSETS.md 卡（锁存：一张面自己印的几行残差往往是同一个二次型的采样，"
        "反解它比再拟合一遍便宜，而且能当场检查这张面自不自洽）+ CODELY 一行；"
        "(b) 把「等带宽减半 = 对冲要几乎全上完」写进 CEO 一页纸的仓位节（≤48h）；"
        "(c) 台阶假设 k 在等待期恒定——下一面可以给「边等边加仓」的路径定价（换手成本一并算）"),
    "下个里程碑": (
        "(a) 竞争窗关后把 r2022–r2039 十七面接 S6 链腿与冒烟两腿（≤48h）；"
        "(b) 把「打平带 k∈[0.8986,1.0427]」写进 CEO 一页纸仓位节（≤48h）"),
    "本次": (
        "阶梯（每百万镜头，参考臂 k=0.9013 = 3,919 手）：k=0 16.580pp/年、k=0.25 10.746、k=0.5 5.421、"
        "k=0.65 2.724（27,242 元/年，倍率 224.5）、k=0.75 1.296、k=0.85 0.301、k=0.9 0.006、"
        "k=0.95 -0.138、k=1.0 -0.124、k=1.0263 -0.054；打平带 k∈[0.8986, 1.0427]（3,907..4,534 手）；"
        "身份核对：五条残差行反解出的账本波动 27.3433% 与 band 面印的逐位相同，"
        "反解出的残差最小点 0.970652 与 band 面的全窗 beta 差 1.29e-12"),
    "孤儿面": 0,
    "孤儿面_note": "round-zero orphan_face_probe: orphans 0 (py_faces 4, resident_servers 1 = ComfyUI idle)",
    "watermark_note": (
        "竞争探针 rc=3 CONTENTION：对端 interactive pid 51252 常驻 36.6h、20 张共享面在轮首前被写、"
        "重叠窗 0 张 → 按 r1907 只落新增文件面，未改共享代码/数据面、未跑 S6 链、未跑全量 smoke"),
    "watermark_verdict": ("green (red=false; lane healthy; repo_write_contention rc=3 CONTENTION "
                          "-> new-file faces only)"),
    "记账_r2039": ("轮报告 2 处（本轮行 + 送达核验行）+ state 1 处 + 心跳 1 处 = 4"
                   "（无方法论新增：把一个二次型反解当检查面属证据与载体；方法论卡锁存待无竞争轮）"),
    "why_not_bookkeeping": (
        "本轮主产出是一条把「等待」定价成「保留多少对冲就付多少波动」的阶梯"
        "（脚本 + JSON + 页面 + 负控），不是一个数"),
    "went_well": (
        "五条残差行被证明是同一个二次型的采样：反解出的账本波动与全窗 beta 都与 band 面印的逐位相同，"
        "于是「等带宽减半」这句话第一次有了一个可以按比例查的价目表"),
    "when_well": (
        "本面只读父面、不重算 beta、不重拟合策略，所以 k=0 那一级必须复现 r2038 的 16.580pp"
        "（check 里是硬腿：差 >0.02pp 就红）——阶梯若不是同一条阶梯，红在纸上"),
    "未验证": (
        "①台阶假设等待期内 k 恒定，边等边加仓会产生换手成本，本面没算；"
        "②k=1.0 在残差表自己的窗口上最好，换窗口重选比例就是又在窗口上挑数，本面不宣称它「更对」；"
        "③残差行评估窗口是配对全窗（77 期），点估计 beta 是样本内 43 期拟合，两者窗口不同即本面"
        "「点估计最差」的成因，本面只陈述现象不解释来源；"
        "④52/77 期是否代表未来 regime 未证（r2037 沿用）；"
        "⑤打平带的宽度由「四倍期数」这条标准误律决定，若 beta 本身在动，带宽收窄与残差下降不是一回事；"
        "⑥本面只给「等」定价，不选 k、不宣称对冲值得做"),
}

# The state face carries the same fields; keep its own bookkeeping keys untouched.
STATE_FIELDS = dict(FIELDS)
STATE_FIELDS["本地未达 origin commit 数"] = 0
STATE_FIELDS["本地未达origin"] = 0


def main() -> int:
    with open(STATE, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    prev = state.get("round_no")
    state["round_no_prev"] = prev
    state.update(STATE_FIELDS)
    state["next_pick"] = {
        "candidate": ("price the wait along a path: adding hedge while the band narrows, "
                      "turnover cost included"),
        "status": "open",
    }
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
