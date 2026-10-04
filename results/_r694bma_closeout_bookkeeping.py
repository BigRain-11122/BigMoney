"""r694 bm-a closeout bookkeeping: state round_no +1 (programmatic dump +
reparse proof, r645 law) + heartbeat line-surgery (r678 law: file roundtrip
NOT byte-stable -> per-key line surgery, int epoch r170/R178 law)."""
import datetime
import json
import os
import re
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP = os.path.join(ROOT, "state-bm-a.json")
HP = os.path.join(ROOT, "fleet", "machines", "bm-a.json")

now_dt = datetime.datetime.now().astimezone()
now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

CUR_TASK = ("r694: N2-W15 supply materialization -- GENERATE pool entry "
            "enrolled (seat MSG-1943 per MSG-1955 downstream open face); "
            "W3 judge verdict watch ETA ~22:1x")
LAST_ACTION = ("r694: PERPETUAL-N2-W15-GENERATE pool enrollment (377->378, "
               "r481 surgical recipe, bands 541500/542000/542500 live-verified) "
               "+ selftest 17/17 re-run + S6 38/38 rc0 + smoke 48/48")
NEXT = ("r695+: (1) W3 judge product harvest FIRST CHECK (bm-c pid 33768, ETA "
        "~22:1x; probe results/_r693bma_w3_adopt_probe.py --live -> adoption "
        "commit + CEO 48h clock); (2) N2 generate harvest+flip on landing -> "
        "screen-prep -> 12-shard SCREEN enrollment (r481 recipe + r670 tiling); "
        "(3) W117 finalize on bm-b W116 landing (rehearsal r684 armed); "
        "(4) fund trio NULLS finalize watch 10-05..09 (bm-b canonical); "
        "(5) bm-b slice-2 review receipt watch (MSG-1930 window)")
VERDICT = ("green: N2 supply enrolled (pool ready=5, one unowned=claimable); "
           "W3 judge in-flight bm-c; golden-week board-clear legal")

# --- state: programmatic dump + reparse proof (r645 law) ---
with open(SP, encoding="utf-8-sig") as fh:
    st = json.load(fh)
prev_no = int(st["round_no"])
st["round_no"] = str(prev_no + 1)
st["round"] = "r694"
st["last_round"] = "r694"
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["updated"] = now_iso
st["current_task"] = CUR_TASK
st["last_action"] = LAST_ACTION
st["next"] = NEXT
st["heartbeat_epoch_utc"] = str(epoch)
st["did"] = ("r694: orders 154/154 zero-unacked dual-scan + D-19 MATCH 4e5be321 "
             "+ smoke 48/48 + N2 GENERATE enrollment + S6 38/38 rc0")
with open(SP, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
st2 = json.loads(open(SP, encoding="utf-8-sig").read())
assert int(st2["round_no"]) == prev_no + 1, st2["round_no"]
assert st2["heartbeat_epoch_utc"] == str(epoch)
print("state OK: round_no %d->%s, reparse proof pass" % (prev_no, st2["round_no"]))

# --- heartbeat: line surgery per key (r678 law) ---
raw = open(HP, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in raw[:2000] else "\n"


def set_key(raw, key, val_json):
    pat = re.compile(r'^ "%s": .*?(,?)%s' % (re.escape(key), re.escape(eol)),
                     re.M)
    hits = pat.findall(raw)
    assert len(hits) == 1, "key %s line count=%d" % (key, len(hits))
    line_end = hits[0]
    # repl must RE-EMIT the consumed line terminator (pattern match includes
    # eol; forgetting it merges the next line upward -- 5-key chain this window)
    return pat.sub(' "%s": %s%s%s' % (key, val_json, line_end, eol),
                   raw, count=1)


upd = {
    "clock_read": json.dumps(now_iso, ensure_ascii=False),
    "last_seen": json.dumps(now_iso, ensure_ascii=False),
    "heartbeat_epoch_utc": str(epoch),   # JSON int, never string (R170/R178)
    "current_task": json.dumps(CUR_TASK, ensure_ascii=False),
    "task": json.dumps("T-2026-09-30-133 s2 (N2 supply materialization: GENERATE pool entry)", ensure_ascii=False),
    "verdict": json.dumps(VERDICT, ensure_ascii=False),
    "round_no": "694",
    "last_round": json.dumps("r694", ensure_ascii=False),
    "loop_round": "694",
    "free_ram_gb": "58.0",
    "ram_free_gb": "58.0",
}
for k, v in upd.items():
    raw = set_key(raw, k, v)
with open(HP, "w", encoding="utf-8", newline="") as fh:
    fh.write(raw)

hb = json.loads(open(HP, encoding="utf-8-sig").read())
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch not int!"
assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$",
                hb["clock_read"]), hb["clock_read"]
assert hb["round_no"] == 694 and hb["last_round"] == "r694"
assert len(hb["orders_ack"]) == 154
print("heartbeat OK: epoch int %d, clock T-format, round 694, ack 154"
      % hb["heartbeat_epoch_utc"])
