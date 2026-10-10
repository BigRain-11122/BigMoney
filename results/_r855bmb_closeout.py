# r855 bm-b closeout: report line + state.json + heartbeat (utf-8, epoch int, read-back)
import json, time, datetime, io, os

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

REPORT_LINE = (
    "2026-10-11T02:33:00+08:00 | r855 bm-b | S0: fetch+FF merge origin/main d7a682ee2 zero-overlap "
    "(bm-c r845 close; 8 own live faces dirty untouched, live-wins) | S0.5: s05_probe orders diff zero "
    "(67 orders/192 acks/unacked 0) + D19 dec identical caca0c6e / ord delta 4d33cb4f->f90233c7 = "
    "8b6570c X2348 bm-a MiniGame walkthrough receipt + O-20261011-0003 executed flip, neither touches "
    "this repo -> zero action + d19_watermark update --advance legal write (read-back equality OK) | "
    "S1: smoke 49/49 + orphan face 0 (17 py faces, 0 orphans) | S2: board empty triple check (job 0, "
    "ticket 0 open, watermark green red=false next_pick=claimed moneyflow IC parked) | S3: engine "
    "alive rc0 idle queue 0; O-20261011-0012 item4 maintained (pool 419 all done zero claimable, "
    "local_batch=1 T23 in-flight = bm-b CPU contribution per order item-5 meaning-law); T23 autofire "
    "watcher ALIVE (pid23124 state=watching poll45s/90min to ~03:27, runner t23_random_grammar_census); "
    "astock panel complete=False 5219/5229 (10 persistent failures attempts=2/3 of QUARANTINE_AT=3: "
    "next pass -> quarantine -> complete flip -> watcher fires census burn; 14 settled_no_new; "
    "disk-truth rebuild face per r834-kin guard); W206 MSGs x2 consumed to processed/ (freeze "
    "68ba08347 12/12 shards ignited engine_alive; M9 bm-b W207 upstream gate 1/2 OPEN, gate 2/2 = "
    "W206 finalize = bm-c next-window top task) -> W207 stays waiting, staged _w207bmb_freeze_edits.py "
    "from r852 untouched; W18 drain-gated maintained (bm-a owns w17-judge) | S6: 41 legs 40 rc0 + "
    "alloc rc2 known 510880 P5 slot (verbatim clone _r855bmb_s6chain.ps1; pool_dualrun ZERO-DRIFT "
    "streak 10; update_options [RETIRED] honest no-op per O-20261009-1105) | S7: four tasks ALIVE "
    "(pin no-op=2, dual claws identical), attrition scan CLEAN, idle --worked reset, commit+push "
    "self-verified behind=0 | next r856: T23 census_holds readout (watcher window to ~03:27: "
    "complete flip -> burn ~10-15min -> holds verdict window <=10-11 06:00; if watcher expires "
    "without flip -> check quarantine carryover + re-arm single-flight) -> if holds N2 U3(1) prereg "
    "window / if negative G2 academic-citation fallback; W207 watch W206 finalize (M9 gate 2/2) via "
    "staged script; astock complete flip then moneyflow IC next_pick unlock observation; "
    "O-20261011-0012 CPU-max maintained"
)

DID = (
    "r855: S0 FF merge d7a682ee2 zero-overlap (8 own live faces live-wins) + s05 orders diff zero "
    "(67/192/0) + D19 ord advance 4d33cb4f->f90233c7 (delta=8b6570c X2348 bm-a receipt + 0003 flip, "
    "not this repo, zero action; dec caca0c6e unchanged) via d19_watermark update --advance legal "
    "path + smoke 49/49 + orphan 0 + S2 job0/ticket0/wm green + S3 engine rc0 idle0; O-0012 item4 "
    "pool 419 zero claimable maintained; T23 autofire watcher ALIVE pid23124 watching to ~03:27; "
    "astock complete=False 5219/5229 (10 fails attempts 2/3, next pass quarantines->complete flips-"
    ">census fires; 14 settled_no_new); W206 freeze MSG x2 consumed (freeze 68ba08347, 12/12 "
    "ignited; M9 gate 1/2 open, gate 2/2 = W206 finalize = bm-c next window) -> W207 waits; W18 "
    "drain-gated; S6 41 legs 40 rc0 + alloc rc2 known; S7 four tasks ALIVE, attrition CLEAN, "
    "idle --worked, commit+push behind=0"
)
VERDICT = (
    "GREEN: r855 (zero-overlap FF merge path; orders watermark advanced legally; chain 40/41 with "
    "known alloc rc2; T23 watcher armed on self-healing quarantine path; W207 waiting on "
    "bm-c W206 finalize; tasks ALIVE; attrition CLEAN)"
)
NEXT = (
    "r856 queue: T23 census_holds readout (watcher to ~03:27; complete flip -> burn 10-15min -> "
    "verdict window <=10-11 06:00; watcher expiry without flip -> quarantine carryover check + "
    "re-arm single-flight) -> holds: N2 U3(1) prereg window / negative: G2 academic-citation "
    "fallback; W207 M9 gate 2/2 watch (W206 finalize = bm-c top task; run staged "
    "results/_w207bmb_freeze_edits.py, anchor roll per r590); astock complete flip then moneyflow "
    "IC next_pick unlock; O-20261011-0012 CPU-max maintained; W18 drain-gated (bm-a owns w17-judge)"
)
NOW_ACTIVE = (
    "r855 closeout: T23 autofire watcher detached (pid23124, awaiting astock complete flip via "
    "quarantine-of-10 path); astock continuation tail in flight"
)
LATEST_ARTIFACT = (
    "r855: results/_r855bmb_s6chain.ps1 + results/_r855bmb_s6chain.log (41 legs, 40 rc0 + known "
    "alloc rc2) + D19 ord watermark advance receipt results/d19_watermark.json + s05 probe "
    "results/_s05_probe.bm-b.json"
)
NEXT_MILESTONE = (
    "T23 census burn on panel complete (next pass quarantines the 10 persistent failures) -> "
    "census_holds verdict window <=10-11 06:00 -> N2 U3(1) prereg / G2 fallback; O-20261011-0012 "
    "CPU-max via T23 burn + continuation refresh"
)

def load(p):
    with io.open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def dump(p, obj):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

# 1) round report append
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with io.open(rp, "r", encoding="utf-8", newline="") as f:
    body = f.read()
sep = "" if body.endswith("\n") else "\n"
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(sep + REPORT_LINE + "\n")

# 2) state.json (bm-b canonical at repo root)
sp = os.path.join(ROOT, "state.json")
st = load(sp)
st["round_no"] = 855
st["round_no_label"] = "r856"
st["round"] = 855
st["did"] = DID
st["note"] = DID
st["verdict"] = VERDICT
st["next"] = NEXT
st["current_task"] = NEXT
st["task"] = NEXT
st["now_active"] = NOW_ACTIVE
st["latest_artifact"] = LATEST_ARTIFACT
st["next_milestone"] = NEXT_MILESTONE
st["last_action"] = DID
st["last_round_at"] = ts
st["last_round_ts"] = ts
st["ts"] = ts
st["updated"] = ts
st["updated_at"] = ts
st["last_seen"] = ts
st["clock_read"] = ts
st["d19_watermark_guard"]["round_ref"] = 855
st["d19_watermark_guard"]["ts"] = ts
dump(sp, st)

# 3) heartbeat fleet/machines/bm-b.json
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = load(hp)
hb["round"] = 855
hb["round_no"] = 855
hb["now_active"] = NOW_ACTIVE
hb["current_task"] = NEXT
hb["task"] = NEXT
hb["latest_artifact"] = LATEST_ARTIFACT
hb["next_milestone"] = NEXT_MILESTONE
hb["verdict"] = VERDICT
hb["last_action"] = DID
hb["last_round_at"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["last_seen"] = ts
hb["updated"] = ts
hb["heartbeat_epoch_utc"] = epoch
dump(hp, hb)

# read-back self-check (epoch int law R170/R178 + T-separator clock law R262)
hb2 = load(hp)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"], "clock_read must be ISO T-separated"
st2 = load(sp)
assert st2["round_no"] == 855
print("closeout OK: report+state+heartbeat written, epoch=%d int, clock=%s" % (
    hb2["heartbeat_epoch_utc"], hb2["clock_read"]))
