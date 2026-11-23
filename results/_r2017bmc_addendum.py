"""r2017 addendum row: delivery verification + tail double-scan (append-only)."""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "fleet", "round_reports-bm-c.md")

ROW = (
    "| 2026-11-24 01:4x | r2017 **addendum**（送达核验 + 两处口径说明） | "
    "commit **ed2097df4a** 已推 origin/main（0fbcd872dc..ed2097df4a），fetch 后 **AHEAD=0 / BEHIND=0**，"
    "`git ls-tree -r origin/main` 七件 blob 在位（scripts/astock_veto_turnover_layers.py / results/astock_veto_turnover_layers.json / "
    "research/ASTOCK_VETO_TURNOVER_LAYERS.md / 负控 results/_r2017bmc_turnover_layers_negative.py / 收口 _r2017bmc_closeout.py / "
    "_r2017bmc_round_report.py / _r2017bmc_hb_fields.json，`_r[0-9]*` 走 `git add -f` 既有惯例）→ **本地未达 origin commit 数=0**。"
    "**S7 收尾双扫**：`Tools/orders_ack_scan.py` **CLEAN**（116/329，unacked=[]）；集团 decisions 原字节 sha256 仍 **79e3083b85c130b8**（250,586 B）"
    "= 零新决策；fleet/inbox 0 件。**口径说明（读者会追问的三个数）**："
    "①「U 只有 3.64%」不等于「池子很稳」——全池臂自身就是 4.30%/期，本账因为持仓只占池子 80.0%、同一流量落在 1.25 倍小分母上，"
    "再乘上「进池名字只有 67.8% 落在账上」（其余一进来已是 q==4），合成出 3.64%；"
    "②「边界 84.2%」是按**可归因期**（76 期，去掉首期全额入场）算的份额，账面 23.95% 是含首期的父面口径 22.95%+首期 1.0 期，"
    "两者混用会把 84.2% 算成 80.6%——本面两个分母都印在 JSON 里，随口引用请指明哪一个；"
    "③「前 10% 名字只占 16.1% 穿越」是**反直觉的**度量，若穿越集中在少数名字，这个数该接近 60-80%；16.1% 接近均匀，"
    "正是「集中惩罚没用、要压整片分数」的证据。**未验证（承上条）**：全量 smoke 与 S6 链未跑（竞争窗，`smoke_test.py` / "
    "`logs/smoke_legs.json` / `Tools/s6_chain_bmc.py` 为对端写的共享面）；本面尚未接 smoke 两腿与 S6 腿。记账：本行 1 处（轮报告 addendum）。|\n"
)


def main() -> int:
    with open(RP, "rb") as fh:
        raw = fh.read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    with open(RP, "w", encoding="utf-8", newline="") as fh:
        fh.write(text + ROW.replace("\n", "\r\n" if crlf else "\n"))
    print("appended %d chars -> fleet/round_reports-bm-c.md" % len(ROW))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
