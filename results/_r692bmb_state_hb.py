# r692 bm-b closeout: state.json + heartbeat update (json.dump programmatic + self-verify, r645 law)
import json, time, datetime

now_iso = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# ---- state.json (bm-b lane file per S5 rule) ----
sp = "state.json"
s = json.load(open(sp, encoding="utf-8"))
s["round_no"] = 692
s["note"] = ("r692: N2-W15 dual-shard dual-machine claim adjudicated (bm-a daemon post-yield re-claim on bare key "
             "=r694-i blindspot recurrence; seeded deterministic + refuse-if-exists = zero product harm; MSG-2025 "
             "cleanup request + product-first waiver first-landed=canonical) + pool claim truth-key law (entries[]."
             "shards[].owner layer) + S6 38/38 rc0 + smoke 48/48")
s["last_round_at"] = now_iso
s["ts"] = now_iso
s["updated"] = now_iso
s["last_seen"] = now_iso
s["round_no_label"] = "round 692 (bm-b)"
s["clock_read"] = now_iso
s["next"] = ("(a) old-code 40min-cap exit + daemon new-code relaunch receipt (log RAM-GATE flush lines = public "
             "self-proof); (b) bm-a bare-shard cleanup response watch (MSG-2025 three requests); (c) trio V close "
             "10-06T17 -> FUND VALUE nulls finalize candidate window + N2 generate lands at RAM window (either-"
             "machine, first-landed=canonical) -> same-window done-flip; (d) W3 judge bm-c ~22:1x landing watch "
             "(id dup probe r482 law, owner-side); (e) 10-09 market-open data-chain check")
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
chk = json.load(open(sp, encoding="utf-8"))
assert chk["round_no"] == 692 and chk["round_no_label"] == "round 692 (bm-b)"

# ---- heartbeat fleet/machines/bm-b.json ----
hp = "fleet/machines/bm-b.json"
h = json.load(open(hp, encoding="utf-8"))
h["last_seen"] = now_iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now_iso
h["round_no"] = 692
h["round_no_label"] = "round 692 (bm-b)"
h["current_task"] = ("r692 closed: N2-W15 dual-shard dual-machine claim adjudicated (bm-a daemon re-claimed bare key "
                     "generate-0of1 at 20:09:38 post-yield = r694-i blindspot recurrence; product-safe: seeded "
                     "deterministic + refuse-if-exists; MSG-2025 cleanup request + product-first waiver) + trio NULLS "
                     "three burns V936/Q738/D569 of 2000 keepalive-fresh + S6 38/38 rc0; next = generate lands (RAM "
                     "window / bm-a first-landed dual channel) -> done-flip -> screen-prep + 12-shard SCREEN relay "
                     "(<=10-08)")
h["verdict"] = "healthy burning (trio NULLS + N2 generate RAM-gated wait + dual-claim adjudicated)"
h["ts"] = now_iso
h["updated"] = now_iso
h["updated_at"] = now_iso
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be JSON int (F7 law)"
assert chk2["round_no"] == 692
assert "T" in chk2["clock_read"]

print("STATE+HB OK round=692 epoch=%d (int type verified) clock=%s" % (epoch, now_iso))
