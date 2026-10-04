# -*- coding: utf-8 -*-
"""r679 bm-a S7 bookkeeping: surgical state+heartbeat updates, orders rescan.
Pattern = r678 _r678bma_s7.py (roundtrip-unsafe faces -> line surgery, strict
key-hit-once, post-verify, epoch int + clock T proof)."""
import json, time, os
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_EPOCH = int(time.time())
o = []

def surgical_json_update(path, updates):
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    nl = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    lines = text.split(nl)
    hits = {}
    for k, v in updates.items():
        needle = '"%s"' % k
        idxs = [i for i, ln in enumerate(lines)
                if ln.lstrip().startswith(needle + ":")]
        assert len(idxs) == 1, "key %s hits=%d" % (k, len(idxs))
        i = idxs[0]
        ln = lines[i]
        indent = ln[: len(ln) - len(ln.lstrip())]
        comma = "," if ln.rstrip().endswith(",") else ""
        if isinstance(v, str):
            newln = '%s%s: %s%s' % (indent, needle, json.dumps(v, ensure_ascii=False), comma)
        else:
            newln = '%s%s: %s%s' % (indent, needle, json.dumps(v), comma)
        lines[i] = newln
        hits[k] = (i, ln, newln)
    open(path, "wb").write(nl.join(lines).encode("utf-8"))
    d = json.loads(open(path, "rb").read().decode("utf-8"))
    for k, v in updates.items():
        assert d[k] == v, "post-verify key %s: %r != %r" % (k, d[k], v)
    return hits

# ---------- 1) heartbeat ----------
HP = os.path.join(B, "fleet", "machines", "bm-a.json")
hb_updates = {
    "clock_read": NOW_ISO,
    "heartbeat_epoch_utc": NOW_EPOCH,
    "cpu_pct": 2,
    "cpu_util_pct": 2,
    "free_ram_gb": 60.3,
    "gpu0_free_vram_gb": 5.63,
    "gpu_free_vram_mb": 5634,
    "current": ("r679 DONE: FUND piece-4 prereq slice CLOSED -- CFO panel completeness probe "
                "on r663-delivered statement panel (cashflow 292,537 rows x 86 periods "
                "2005Q1..2026H1, CFO nonnull 100%, CFO+NI+TA triple-join 282,289 pairs -> "
                "invested-capital caliber buildable TODAY; mktcap leg GAP confirmed = GM P1 "
                "signature face). digest sec.6 addendum + facts file. D-19 dual MATCH, "
                "orders 153/153 double-scan, S6 37/37 rc0 104.2s, smoke 48/48"),
    "current_task": ("r679 done; next: 10-05..09 fund-trio finalize watch (bm-b) + piece-4 "
                     "prereg draft AFTER trio finalize (D6 corr measured) + 10-06+ next "
                     "trial-labor candidate wave draft (TRIAL_LABOR_LAW standing)"),
    "last_action": ("r679: CFO panel completeness probe PASS (cfo_leg PASS, mktcap "
                    "GAP_CONFIRMED) + digest addendum + S6 37/37 rc0 + smoke 48/48"),
    "last_round": "r679",
    "last_run": NOW_ISO,
    "last_seen": NOW_ISO,
    "health": "ok",
}
h = surgical_json_update(HP, hb_updates)
o.append("hb surgical-updated %d keys" % len(h))
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert chk["clock_read"][10] == "T"
o.append("hb epoch=%d clock=%s acked=%d" % (chk["heartbeat_epoch_utc"], chk["clock_read"], len(chk.get("orders_ack", []))))

# ---------- 2) state ----------
SP = os.path.join(B, "state-bm-a.json")
st_updates = {
    "round_no": 679,
    "round": "r679",
    "last_round": "r679",
    "last_round_at": NOW_ISO,
    "last_round_ts": NOW_EPOCH,
    "next": ("r679: fund trio NULLS finalize window 10-05..09 (bm-b canonical in flight); "
             "piece-4 excess-CFO prereg draft gate = trio finalize -> D6 corr measured -> "
             "invested-capital caliber first candidate (mktcap leg = GM P1 signature, "
             "facts file results/_r679bma_cfo_panel_facts.json as evidence); 10-06+ next "
             "trial-labor candidate wave draft (theme family closed, TRIAL_LABOR_LAW "
             "standing); 10-08 market-open external run-11/run-7 dual legs + governance day"),
}
s = surgical_json_update(SP, st_updates)
o.append("state surgical-updated %d keys" % len(s))

# ---------- 3) S7 orders rescan ----------
orders_dir = os.path.join(B, "fleet", "orders")
order_files = sorted([f for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md")])
hb2 = json.load(open(HP, encoding="utf-8"))
unacked = [f for f in order_files if f not in hb2.get("orders_ack", [])]
o.append("orders_rescan total=%d unacked=%s" % (len(order_files), unacked if unacked else "NONE"))
assert not unacked, "NEW ORDERS mid-round: %s" % unacked

open(os.path.join(B, "results", "_r679bma_s7_receipt.json"), "w", encoding="utf-8").write("\n".join(o))
print("\n".join(o))
print("S7_BOOKKEEP_OK now=%s epoch=%d" % (NOW_ISO, NOW_EPOCH))
