# -*- coding: utf-8 -*-
"""r991 addendum: O-20261014-0925-bm-b CEO order mid-window consumption (receipt
flipped same-window, <=1 loop cycle law) + push-saga disclosure + ack bookkeeping."""
import json, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")

now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
ORD = "O-20261014-0925-bm-b.md"

hb = json.load(open(HB, encoding="utf-8"))
ack = hb.get("orders_ack")
if isinstance(ack, list):
    if ORD not in ack:
        ack.append(ORD)
else:
    ack = [ORD]
hb["orders_ack"] = ack
hb["orders_ack_count"] = len(ack)
hb["orders_ack_last"] = ORD
hb["orders_ack_ts"] = now_iso
hb["orders_ack_receipt"] = ("r991 addendum: O-20261014-0925-bm-b CEO fleet-idleness "
                            "accountability order consumed SAME-WINDOW (mid-window arrival 281f5b562 "
                            "post-S7-tail-scan): receipt flipped in-order-file sec.4 (bm-c line, "
                            "<=1 loop cycle met): CPU backfill pool ACCEPTED with RAM-light "
                            "constraint disclosed (0.2G free, MV V3 GPU burn window protected "
                            "O-20261014-0312 sec.2; heavy-RAM items deferred to post-MV window) + "
                            "one-line occupancy + window product (W239 seat). Prior r991 opening+tail "
                            "dual-delta FALSE unacked=0 stands.")
hb["now_active"] = f"2026-10-14 {time.strftime('%H:%M')} | r991 addendum | bm-c: CEO O-0925 consumed+receipt | counter stays 992"
hb["activity_now"] = hb["now_active"]
hb["current_task"] = ("r991 closeout + addendum complete (W239 seat + CEO O-0925 receipt + push saga "
                      "healed); next: r992 wait-window faces (bars 15:30 / MF panel recheck / W238 "
                      "finalize watch -> W239 freeze-prep)")
hb["current_task_at"] = now_iso
with open(HB, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

st = json.load(open(STATE, encoding="utf-8"))
st["orders_ack"] = hb["orders_ack"]
st["orders_ack_count"] = hb["orders_ack_count"]
st["orders_ack_last"] = ORD
st["orders_ack_ts"] = now_iso
st["orders_ack_receipt"] = hb["orders_ack_receipt"]
st["now_active"] = hb["now_active"]
st["activity_now"] = hb["now_active"]
st["current_task"] = hb["current_task"]
st["current_task_at"] = now_iso
st["r991_addendum_note"] = ("r991 addendum: (1) O-20261014-0925-bm-b CEO fleet-idleness order "
                            "landed MID-WINDOW (origin 281f5b562, after S7 tail scan) -> consumed "
                            "same-window per CEO immediate law: receipt flipped in-order-file (sec.4 "
                            "bm-c line: CPU backfill ACCEPTED, RAM-light <=1G/items constraint honest "
                            "[0.2G free, MV V3 burn window protected], one-line occupancy, window "
                            "product = W239 seat) + heartbeat ack appended (209->210); (2) push saga: "
                            "bm-a 51fb88b87 + bm-b 281f5b562 advanced mid-push -> stash->pull --rebase "
                            "-> single conflict results/token_usage.json (resolved theirs=newer "
                            "09:16:48 face) -> rebase --continue PHANTOM-REJECT x2 with ZERO unmerged "
                            "(r863 family 4th+5th instances) -> per r990 pit mandate sequencer files "
                            "CAPTURED FIRST (results/_r991bmc_rebase_sequencer_capture/, 9 files, "
                            "committed as evidence for root-cause analysis) -> manual commit -C + "
                            "rebase --skip clean heal (603ff65d9) -> stash superseded snapshot "
                            "dropped live-wins (r986 precedent); counter stays 992 (same window)")
with open(STATE, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

add_line = (f"{now_iso} | r991 附产 | bm-c | O-20261014-0925-bm-b CEO 机队闲置问责令 MID-WINDOW 落链 "
            f"（281f5b562·09:25·S7 尾扫后到达）→ 同窗消费+回执节翻✅（§4 bm-c 线 ≤1 轮循环达成：CPU 填窗"
            f"承接=接受委员会后备件池排产·RAM-light ≤1G/件档约束如实[RAM 空闲 0.2G·MV V3 GPU 烧窗保护 "
            f"O-20261014-0312 §2]·重 RAM 件候 MV 窗收尾·供应链等待律不破+占用一行+本窗产出=W239 席位）"
            f"+ heartbeat ack 209→210 | push saga 披露：bm-a 51fb88b87+bm-b 281f5b562 撞窗推进 → "
            f"stash→rebase→token_usage.json 单冲突（theirs=newer 09:16:48 快照解）→ rebase --continue "
            f"PHANTOM-REJECT ×2 零 unmerged（r863 家族第 4/5 例）→ sequencer 状态件 9 件先捕入库"
            f"（results/_r991bmc_rebase_sequencer_capture/·r990 坑令执行·根治分析=下窗）→ manual "
            f"commit -C + --skip 收官（603ff65d9）→ 陈旧 stash 快照 live-wins 弃（r986 先例）| "
            f"counter 维持 992（r992=下窗）")
with open(CANON, "a", encoding="utf-8", newline="") as f:
    f.write(add_line + "\n")
print(f"ADDENDUM OK: ack {hb['orders_ack_count']}, state+report updated, order receipt disclosed")
