# -*- coding: utf-8 -*-
"""r768 bm-c addendum: mark silence-duo CAS receipts landed (79ba710228)."""
import json

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
ADD = ("r768 addendum: group silence-duo receipts CAS-landed SAME round (commit 79ba710228, "
       "2 rows 2110B, landed=true, parent 1f57caf); next-round zero-hop on own-receipt-only "
       "ORD delta expected. || ")
st_path = ROOT + r"\state-bm-c.json"
st = json.load(open(st_path, encoding="utf-8"))
for k in ("did", "note", "verdict", "last_round_summary", "last_action"):
    if k in st and isinstance(st[k], str):
        st[k] = ADD + st[k]
st["next"] = st.get("next", "").replace(
    "②组仓静默两令 bm-C 回执行 CAS 直投（b4eb539 quark Access-Denied 物理域+21b45d7 部署实弹——本轮时间墙未及·最高优先）",
    "②组仓静默两令回执已本轮 CAS 落地（79ba710228·2 行）——下轮 ORD 面=own-receipt-only delta 零跳预期")
st["next_pointer"] = st["next"]
st["next_milestone"] = st.get("next_milestone", "").replace(
    "group silence-duo receipts CAS next round;", "group silence-duo receipts LANDED 79ba710228 same round;")
json.dump(st, open(st_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

f_path = ROOT + r"\results\_r768bmc_s05_facts.json"
fx = json.load(open(f_path, encoding="utf-8"))
fx["group_receipts_pending"] = "RESOLVED same round: silence-duo rows CAS-landed 79ba710228 (landed=true)"
json.dump(fx, open(f_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ADDENDUM_OK")
