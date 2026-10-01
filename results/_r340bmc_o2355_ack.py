"""r340 bm-c: O-20261001-2355 CEO direct order FAST ACK (<=15min window).

Receipt = heartbeat orders_ack + round-report receipt line + CODELY execution-record line.
Execution follows immediately in-round (wave freeze W33 + ignition = order sec.2 core demand).
"""
import json
import time
import datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
ORDER = "O-20261001-2355-bm-c.md"

# 1) heartbeat orders_ack
hp = f"{ROOT}\\fleet\\machines\\bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
ack = hb.setdefault("orders_ack", [])
if ORDER not in ack:
    ack.append(ORDER)
hb["updated_at"] = NOW
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = NOW
hb["activity_now"] = (
    "r340 addendum: O-20261001-2355 CEO direct order ACKED (排好单子开工令) -- executing in-round: "
    "(1) seat-system dethrottle -> bm-c own continuous series W33 freeze+ignite NOW (order sec.2); "
    "(2) T-131 backfill in flight post-hang-cure (queue board item); (3) T-134 s2 pick9 landed -> conversion next round; "
    "audit load_state py%-face upgrade + Law A exit-census gate = follow-up faces this window"
)
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)

# 2) round report receipt line
rr = f"{ROOT}\\round_reports-bm-c.md"
with open(rr, "a", encoding="utf-8") as f:
    f.write(
        f"{NOW}｜r340-addendum｜O-20261001-2355-bm-c 回执：CEO 直令「排好单子！开工！」23:55 轮中落盘（S7 双扫面命中）·ack ≤15min 内送达。"
        f"本机执行面=§二 去节流即刻生效：座位制观察窗终结·本机自持连续系列即刻冻结 W33（r339 已投影 A 109_004..111_003/B 41_601..41_800 CLEAN·本窗机闸复扫+法典表尾 fetch 锁防撞）+引擎重启点火（r330 三动作律）·核闲 5min 红旗线即刻生效；"
        f"§三 队列板：T-131 在飞（挂死已治愈·增长面恢复）·T-134 s2 pick9 已定谳（p1e_synth）转换下轮接续；"
        f"§一 T-142 裁决三项=bm-a lane（P2 void/P3 起草开烧/律 A 升格）+审计 load_state py% 面升级=本窗后续面；"
        f"§四 验收：明晨战报三机 py 均值 ≥50% 目标本机以连续烧承接｜证据: 本回执 commit+push 送达核验（O-1108 律）\n"
    )

# 3) CODELY execution-record line (one line, orders protocol)
cl = f"{ROOT}\\CODELY.md"
ENTRY = (
    f"\n- [2026-10-01 23:5x r340 bm-c] O-20261001-2355-bm-c 执行记录：CEO 直令「排好单子！开工！」23:55 轮中落盘·ack ≤15min 送达；"
    f"§二 引擎去节流即刻生效=座位制/观察窗终结·每机自持连续系列·核闲>5min 红旗·pool=0 不再当 starvation 证据（py% 才是）；"
    f"bm-c 本窗=W33 冻结+点火（r330 三动作律+法典表尾 fetch 锁）+T-131 续跑+T-134 pick9 接续；§一 T-142 三项=bm-a lane；"
    f"§四 明晨验收=三机 py 均值≥50%。\n"
)
with open(cl, "ab") as f:
    f.write(ENTRY.encode("utf-8"))

# verify
for p in (hp, rr.replace("\\round_reports-bm-c.md", "") + "\\state-bm-c.json"):
    json.load(open(p, encoding="utf-8"))
assert ORDER in json.load(open(hp, encoding="utf-8"))["orders_ack"]
assert isinstance(json.load(open(hp, encoding="utf-8"))["heartbeat_epoch_utc"], int)
print("ACK OK", NOW)
