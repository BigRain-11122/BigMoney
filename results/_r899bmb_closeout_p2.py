# -*- coding: utf-8 -*-
"""r899 bm-b closeout part-2 (fix): heartbeat orders_ack is a LIST (not dict) -
append two acked order filenames with dedup guard; round report append.
state.json part already landed by _r899bmb_closeout.py (round_no=900), do NOT touch it."""
import json, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

hb_path = ROOT + r"\fleet\machines\bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = "r899 closeout: two CEO orders bm-b legs closed (O-2147 inspector -KRoot re-register + machine-state flag patch + BigHouse board verified / O-2215 maintain leg)"
hb["verdict"] = "GREEN: CEO order closeout + i2v night batch 1/53 healthy + S6 41/41; watch faces = night-net pushes deferred to morning window + tight RAM"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
ack = hb.get("orders_ack")
assert isinstance(ack, list), "orders_ack expected list, got %s" % type(ack).__name__
for name, note in [
    ("O-20261011-2147-bm-c.md", "r899 bm-b: all three legs closed -- (1) inspector deploy = r898 pre-kill heritage (task registered 22:55 + first run 22:56:30 Result=0 flags=0), this round verified + re-registered with -KRoot C:\\Fluxgroup (readback hidden-chain green, backup results/_r899bmb_oversight_task_backup.xml) + canonical three scripts git-show extracted (Tools/fleet-oversight.ps1+task-register.ps1+InvisibleRunner.vbs, zero tree checkout); (2) machine-state.ps1 flag patch = r898 killed mid-leg, completed this round (Write-StateFlag fn L46 + pause L85 + resume L95, Parser 0 errors, flag beside script = KRoot-symmetric single source); (3) BigHouse board = T-1 done@21:2x (first-cut workorder + R1 research piece r896) + TASKS.md 4 open >= 3 satisfied (T-2 due 10-15 carried to next windows)"),
    ("O-20261011-2215-bm-c.md", "r899 bm-b: S-at-bm-b leg = maintain O-2147 all legs (closed this round, see 2147 row); BigLife kokoro soundscape = non-mandatory face, honest not-started, week-surplus window evaluation"),
]:
    if name not in ack:
        ack.append(name)
    hb.setdefault("orders_ack_notes", {})[name] = note
hb["orders_ack"] = ack
json.dump(hb, open(hb_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert isinstance(chk["orders_ack"], list) and len(chk["orders_ack"]) >= 200

line = ("| r899 | 2026-10-11T23:2x | two CEO orders bm-b legs closed: O-2147 inspector (r898 heritage verified + -KRoot re-register readback green + flag patch parse-0 + BigHouse T-1 done/4 open>=3) + O-2215 maintain leg | O-2126 i2v 1/53 + 2 in-burn zero err; smoke 49/49; S6 41/41 rc0; G-soft/r895 night-net flipped again deferred to morning window (supervisor 4/4 STALL exited, payloads intact); watermark ADVANCED ord 0513e9e7 | r900: i2v watch + pushes morning retry + T-184 receive due 10-12 |")
with open(ROOT + r"\logs\iteration-loop\round_reports.md", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("part-2 done: heartbeat ack=%d (epoch=%d int ok), round report appended" % (len(chk["orders_ack"]), chk["heartbeat_epoch_utc"]))
