import json, io, time, datetime, os, glob

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r674bmb_s7_closeout.txt"
lines = []
now = datetime.datetime.now()
iso = now.isoformat(timespec="seconds") + "+08:00"
epoch = int(time.time())

# --- state.json: round_no 674 (programmatic write + reparse self-verify, r645 law) ---
sp = os.path.join(ROOT, "state.json")
d = json.load(io.open(sp, encoding="utf-8"))
assert d.get("machine_id") == "bm-b", "identity anchor fail"
d["round_no"] = 674
d["round_no_label"] = "r674"
d["last_round_at"] = iso
d["ts"] = iso
d["updated"] = iso
d["last_seen"] = iso
d["clock_read"] = iso
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
d2 = json.loads(io.open(sp, encoding="utf-8").read())
assert d2["round_no"] == 674 and isinstance(epoch, int)
lines.append("state.json r674 written + reparse OK")

# --- heartbeat fleet/machines/bm-b.json (epoch int + T-form clock, R170/R178/R262) ---
hp = os.path.join(ROOT, r"fleet\machines\bm-b.json")
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["round_no"] = 674
h["current_task"] = ("r674: S0 absorb+merge DELIVERED (bm-a r676-679 wave, zero UU) + trio NULLS "
                     "burn watch V785/Q609/D455 + ETA face refresh + S6 38/38 (part-1 21 legs + "
                     "part-2 17 legs, update_fundamental detached fetch in flight)")
h["cpu_cores"] = 16
h["verdict"] = "healthy burning"
with io.open(hp, "w", encoding="utf-8") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
h2 = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"] and ":" in h2["clock_read"]
lines.append("heartbeat written: epoch=%d clock=%s" % (h2["heartbeat_epoch_utc"], h2["clock_read"]))

# --- trio burn live counts for report ---
for fam, p in [("VALUE", r"results\fund_value_p1\nulls.jsonl"),
               ("QUALITY", r"results\fund_quality_p1\nulls.jsonl"),
               ("DIVLOWVOL", r"results\fund_divlowvol_p1\nulls.jsonl")]:
    n = sum(1 for ln in io.open(os.path.join(ROOT, p), "rb") if ln.strip())
    lines.append("trio %s nulls rows=%d of 2000" % (fam, n))

# --- update_fundamental detached fetch liveness (absorb decision face) ---
uf_out = os.path.join(ROOT, r"results\_r674bmb_update_fundamental.out")
uf_err = os.path.join(ROOT, r"results\_r674bmb_update_fundamental.err")
lines.append("update_fundamental out=%dB err=%dB age=%.0fs" % (
    os.path.getsize(uf_out) if os.path.exists(uf_out) else -1,
    os.path.getsize(uf_err) if os.path.exists(uf_err) else -1,
    time.time() - os.stat(uf_out).st_mtime if os.path.exists(uf_out) else -1))

# --- inbox unprocessed scan ---
inbox = os.path.join(ROOT, r"fleet\inbox")
unproc = [os.path.basename(p) for p in glob.glob(os.path.join(inbox, "*.md"))]
lines.append("inbox_unprocessed=%d %s" % (len(unproc), sorted(unproc)[:8]))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(str(x) for x in lines))
print("closeout probes written")
