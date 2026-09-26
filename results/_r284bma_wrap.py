# r284 bm-a state + heartbeat write-back (S7). Laws: R271 timestamps all
# from one datetime.now() instance; heartbeat_epoch_utc = JSON int
# (R170/R178); clock_read ISO8601 T-separator (R262); byte-face mirror
# per file (r255/r257: BOM/EOL/indent/trailing-newline/ensure_ascii).
import json, time
from datetime import datetime

now = datetime.now().astimezone()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
ts_iso = now.isoformat()
epoch = int(time.time())


def face(path):
    raw = open(path, "rb").read()
    bom = raw[:3] == b"\xef\xbb\xbf"
    crlf = b"\r\n" in raw
    end_nl = raw.endswith(b"\n")
    non_ascii = any(b > 127 for b in raw)
    src = raw.decode("utf-8-sig" if bom else "utf-8")
    lines = src.split("\r\n" if crlf else "\n")
    indent = len(lines[1]) - len(lines[1].lstrip())
    return json.loads(src), bom, crlf, end_nl, non_ascii, indent


def write(path, d, bom, crlf, end_nl, non_ascii, indent):
    out = json.dumps(d, ensure_ascii=not non_ascii, indent=indent)
    if end_nl and not out.endswith("\n"):
        out += "\n"
    data = out.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    json.loads(data.decode("utf-8-sig" if bom else "utf-8"))
    with open(path, "wb") as fh:
        fh.write(data)


# -- state-bm-a.json (round_no 283 -> 284)
sp = "state-bm-a.json"
s, bom, crlf, end_nl, na, ind = face(sp)
s["round_no"] = 284
s["did"] = ("R284: CN_SOE_ETF_P1 runner built + pooled (T-87 s2 #2): "
            "scripts/cn_soe_etf_p1.py selftest 34/34 + real-data probe "
            "PASS (T=2445 N=8==frozen roster; REPAIR 3 episodes in s5 "
            "band) + pool entry ready cnsoe-0of1 + S0 rebase UU "
            "autofill_state union resolve + S6 22 legs rc=0")
s["verdict"] = "ok"
s["next"] = ("harvest CN_SOE after 02:00-tick burn -> prereg s7/s8 "
            "backfill (D6 cross legs vs DIV dated / TREND after it "
            "lands on bm-b); queue #3 next per SCHOOL_SUPPLY_S1 order")
s["ts"] = ts_iso
s["last_round_ts"] = ts
s["updated_at"] = ts
s["current_task"] = ("R284 done: CN_SOE runner + pool entry; awaiting "
                     "tick burn + harvest")
s["last_run"] = ts
s["last_round_at"] = ts
s["last_round"] = 283
s["updated"] = ts
s["last_seen"] = ts_iso
write(sp, s, bom, crlf, end_nl, na, ind)
print("state-bm-a.json: round_no=%d ts=%s (face: crlf=%s indent=%d)"
      % (s["round_no"], ts_iso, crlf, ind))

# -- fleet/machines/bm-a.json heartbeat
hp = "fleet/machines/bm-a.json"
h, bom, crlf, end_nl, na, ind = face(hp)
h["last_seen"] = ts_iso
h["current_task"] = s["current_task"]
h["cpu_cores"] = 32
h["cpu_pct"] = 6.0
h["free_ram_gb"] = 52.7
h["gpu_free_vram_gb"] = 5.1
h["verdict"] = "py_low_board_clear"
h["heartbeat_epoch_utc"] = epoch          # JSON int (R170/R178 law)
h["clock_read"] = ts_iso                  # T-separator (R262 law)
h["round_no"] = 284
h["task"] = s["current_task"]
h["last_seen"] = ts_iso
assert isinstance(h["heartbeat_epoch_utc"], int)
write(hp, h, bom, crlf, end_nl, na, ind)
print("heartbeat: epoch=%d (int verified) clock=%s"
      % (h["heartbeat_epoch_utc"], h["clock_read"]))
