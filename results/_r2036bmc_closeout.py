"""r2036 closeout: state round_no, heartbeat fields, round-report row.

The face itself is already published by scripts/astock_veto_hedge_funding.py. This script only
writes the bookkeeping the round law requires, and it re-reads every file it touches so a
concurrent host's line is never dropped.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB_FIELDS = os.path.join(ROOT, "results", "_r2036bmc_hb_fields.json")
REPORT = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")
TZ = timezone(timedelta(hours=8))


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def mem_gb():
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "$o=Get-CimInstance Win32_OperatingSystem;"
             "[math]::Round($o.FreePhysicalMemory/1MB,1);"
             "[math]::Round($o.TotalVisibleMemorySize/1MB,1)"],
            capture_output=True, text=True, timeout=25).stdout.split()
        return float(out[0]), float(out[1])
    except Exception:
        return None, None


def gpu():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
        free, total = [float(x.strip()) for x in out.split(",")]
        return free / 1024.0, total / 1024.0
    except Exception:
        return None, None


def main() -> int:
    ts = now_iso()
    epoch = int(time.time())
    free_ram, total_ram = mem_gb()
    vram_free, vram_total = gpu()

    # --- state round_no (read-modify-write, every other key preserved)
    with io.open(STATE, encoding="utf-8") as fh:
        state = json.load(fh)
    prev = state.get("round_no")
    state["round_no"] = 2036
    state["round_no_prev"] = prev
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    # --- heartbeat fields for Tools/heartbeat_write.py apply (merge-only writer)
    fields = {
        "round": 2036,
        "round_no": 2036,
        "last_seen": ts,
        "clock_read": ts,
        "ts": ts,
        "heartbeat_epoch_utc": epoch,
        "verdict": "healthy",
        "vcpu": 32,
        "idle_rounds": 0,
        "agenda_starved": False,
        "latest_work": "r2036 astock_veto_hedge_funding (selftest 32/32, negative 11/11)",
        "当前任务": ("r2036: 把「两腿打平」放上付费尺——借券费与抵押现金一收，"
                     "ETF 腿从领先 0.08pp 变成落后 1.91pp（最便宜租金），"
                     "计入全额抵押后 2.87pp；IM 全额资金口径 12.31% → 9.39%"),
        "当前活": ("把 r2033 的「打平」读数改成付费读数：同一 52 期、同一本书、同一 k，"
                   "分别报毛/净借券/计入抵押三条尺"),
        "最近实物": ("research/ASTOCK_VETO_HEDGE_FUNDING.md + results/astock_veto_hedge_funding.json + "
                     "scripts/astock_veto_hedge_funding.py（selftest 32/32·check rc0·负控 11/11）"
                     "（2026-11-24 08:1x）"),
        "下个里程碑": ("(a) 竞争窗关后把 r2022–r2036 十四面接 S6 链腿与冒烟两腿（≤48h）；"
                       "(b) 把「全额资金口径 9.39% / 抵押吃 2.92pp」写进 CEO 一页纸与票据仓位节（≤48h）"),
    }
    if free_ram is not None:
        fields["空闲RAM"] = "%.1f GB free / %.1f GB" % (free_ram, total_ram)
    if vram_free is not None:
        fields["vram_free_gb"] = round(vram_free, 1)
        fields["vram_total_gb"] = round(vram_total, 1)
    with io.open(HB_FIELDS, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fields, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    # --- round report row (append with a fresh read: a concurrent host's line is not dropped)
    row = (
        "| %s | r2036 **新增文件面**（竞争窗 rc=3·不动共享面） | "
        "**watermark：red=false / lane=healthy · 孤儿面=0**（py_faces=3 / resident_servers=1）。"
        "**产品（产品优先律）**：r2033 把两腿放在同一把尺上得出「打平 0.354pp、IM 赢在占款」，"
        "但那把尺是**毛的**——没扣借券费、也没扣抵押现金的机会成本。本面把两笔都收上："
        "同一 52 期、同一本书、同一 k。"
        "**读数一（毛面锚）**：arm 差 **(IM−ETF) −0.08pp**（12.31% vs 12.39%），"
        "r2033 印的 −0.35pp 是两腿自身复合差，长腿把它稀释了——两个数都印出来。"
        "**读数二（借券费不是零头）**：同一名义按 2%/5%/8% 收租，ETF 腿落到 **10.40% / 7.47% / 4.62%**，"
        "arm 差翻成 **+1.91 / +4.84 / +7.70pp** —— 最便宜的租金就已经把一个打平带甩在后面（线 1pp），"
        "`THE_TIE_WAS_GROSS_OF_THE_LENDER`。"
        "**读数三（全额资金口径）**：IM 要压 r2035 走出来的 **403,938 元**，1,403,938 元承诺资本上年化 **9.39%**"
        "（账面 12.31%，让掉 **2.92pp**＝41,650 元/年）；ETF 腿按 100% 抵押＋2% 租金是 **1,901,331 元/ 6.52%**"
        "（让掉 3.88pp＝75,694 元/年，另付 18,027 元租金）→ 抵押这条腿上 ETF 比 IM 多让 **34,044 元/年**，"
        "比那笔租金还大，`THE_COLLATERAL_COSTS_MORE_THAN_THE_LENDER`（全额抵押口径；半额抵押时反过来，页面两档都印）。"
        "**读数四（排序翻面）**：毛面 ETF 领先，付费面 IM 领先 **2.87pp**（全额抵押、最便宜租金），"
        "`THE_RANKING_FLIPS_WHEN_YOU_PAY_FOR_IT` —— 变的不是差距大小，是谁在前面。"
        "**读数五（尺寸不翻）**：k 网格 0/0.5/1，两条腿的 funded 年化都随 k 单调下降（IM 11.03→10.97→9.39），"
        "抵押随 k 线性增长把大的档位越拉越贵——尺寸决定要按 funded 尺重看，不是照毛尺加码。"
        "**读数六（划走利润的代价）**：按常规扫走超额保证金，IM 抵押升到 **834,029 元**、funded 掉到 **7.68%**，"
        "`SWEEPING_THE_ACCOUNT_COSTS_TWICE_THE_BLOCK`。"
        "**验证**：selftest **32/32** PASS（含 L5 活面：两条腿逐位复刻 carrier 面、k=0 无租恒等、租金随名义单调）；"
        "`check` rc0（三父面 sha + 全字段逐值重推 + 页面三 token 在场）；"
        "负控 `results/_r2036bmc_funding_negative.py` **11/11** PASS（租金归零→打平旗灭；抵押变薄→抵押旗灭；"
        "funded 差为负→翻面旗灭；父面动→STALE 不带 FAILED；改一个 funded 回报→FAILED 不带 STALE；"
        "页面丢判词→FAILED；缺面→STALE 不崩；跑完四件逐字节未动）。"
        "文件：`scripts/astock_veto_hedge_funding.py` / `results/astock_veto_hedge_funding.json` / "
        "`research/ASTOCK_VETO_HEDGE_FUNDING.md`"
    )
    with io.open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row + "\n")

    print("state round_no %s -> 2036" % prev)
    print("heartbeat fields -> %s" % os.path.relpath(HB_FIELDS, ROOT))
    print("round report appended (%.0f bytes)" % len(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
