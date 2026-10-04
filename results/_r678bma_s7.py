# -*- coding: utf-8 -*-
import json, time, os
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_EPOCH = int(time.time())
o = []

def surgical_json_update(path, updates, must_exist=True):
    """Line-based surgical JSON field update. updates: {key: new_value}.
    Preserves formatting of untouched lines; replaced lines keep indent+comma.
    Verifies: reparse ok, each key hit exactly once, target count assert."""
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    nl = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    lines = text.split(nl)
    hits = {}
    for k, v in updates.items():
        needle = '"%s"' % k
        idxs = [i for i, ln in enumerate(lines)
                if ln.strip().startswith(needle + ":") or ln.strip() == needle + ","]
        # strict: key line format ` "key": value,` -- match lstrip-startswith key+colon
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
    out = nl.join(lines)
    open(path, "wb").write(out.encode("utf-8"))
    d = json.loads(open(path, "rb").read().decode("utf-8"))
    for k, v in updates.items():
        assert d[k] == v, "post-verify key %s: %r != %r" % (k, d[k], v)
    return hits

# ---------- 1) heartbeat ----------
HP = os.path.join(B, "fleet", "machines", "bm-a.json")
hb_updates = {
    "clock_read": NOW_ISO,
    "heartbeat_epoch_utc": NOW_EPOCH,
    "cpu_pct": 5,
    "cpu_util_pct": 5,
    "free_ram_gb": 59.8,
    "gpu0_free_vram_gb": 5.61,
    "gpu_free_vram_mb": 5611,
    "current": ("r678 DONE: THEME-JUDGE-P2 judged_negative closure (theme family FULL closure "
                "incl 0.75 deep-break face E24-ii; pool entry+shard flip r668; prereg sec7/8 "
                "backfill; T-169 done). r677 dead-window (S6-absorb then crash) outputs "
                "absorbed+closed this window. fund trio NULLS bm-b canonical in flight"),
    "current_task": ("r678 closure done; next: 10-05..09 fund-trio finalize watch + "
                     "next trial-labor candidate wave draft (TRIAL_LABOR_LAW standing)"),
    "last_action": ("r678: TJ2 judged_negative finalize closure (burn 381s/26w, attrition "
                    "8004/641985) + pool double-flip + ticket done + S6 37/37 rc0 + smoke 48/48"),
    "last_round": "r678",
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
    "round_no": 678,
    "round": "r678",
    "last_round": "r678",
    "last_round_at": NOW_ISO,
    "last_round_ts": NOW_EPOCH,
    "next": ("r678: fund trio NULLS finalize window 10-05..09 (bm-b canonical in flight, "
             "V/Q/D rate per r473 ETA face); 10-06+ next trial-labor candidate wave draft "
             "(theme family closed -> next family per TRIAL_LABOR_LAW standing; 万帽候选 "
             "搜索类波次禁大帽 CEO 悬置面维持); 10-08 market-open external run-11/run-7 "
             "dual legs + governance day; W14 GM-parked maintained; moneyflow IC batch "
             "still panel-blocked (source-fuse)"),
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

open(os.path.join(B, "results", "_r678bma_s7_receipt.json"), "w", encoding="utf-8").write("\n".join(o))
print("\n".join(o))
print("S7_BOOKKEEP_OK now=%s epoch=%d" % (NOW_ISO, NOW_EPOCH))
