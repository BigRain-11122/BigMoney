# r695 bm-a: state round_no absolute write + heartbeat update (roundtrip-checked)
import datetime, json, time

now = datetime.datetime.now().astimezone()
clock = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# -- state: absolute value write (r694 law) + reparse self-verify
SP = r"state-bm-a.json"
s_raw = open(SP, "rb").read()
s = json.loads(s_raw.decode("utf-8"))
s["round_no"] = "695"
s["round"] = "r695"
s["last_round"] = "r695"
s["last_round_at"] = clock
s["last_round_ts"] = clock
s["next"] = ("r696+: (1) W3 judge product FIRST CHECK (bm-c pid 33768, ETA ~22:1x; "
             "probe results/_r693bma_w3_adopt_probe.py --live -> ADOPTION_READY -> "
             "adoption commit + CEO 48h clock); (2) CONTEST-RC anchor ruling watch "
             "(bm-b MSG-2110 three options; fuse-blocked unit zero-surgery per pit r695); "
             "(3) N2 generate harvest on bm-b landing -> screen-prep -> 12-shard SCREEN "
             "enrollment (r481 recipe + r670 tiling); (4) W117 finalize on bm-b W116 "
             "landing (rehearsal r684 armed); (5) fund trio NULLS finalize watch 10-05..09 "
             "(bm-b canonical)")
out = json.dumps(s, ensure_ascii=False, indent=1)
if not out.endswith("\n"):
    out += "\n"
open(SP, "wb").write(out.encode("utf-8"))
chk = json.loads(open(SP, "rb").read().decode("utf-8"))
assert chk["round_no"] == "695" and chk["round"] == "r695"
print("state ok round_no=695 reparse PASS")

# -- heartbeat: epoch int (R170/R178 law) + clock T-format (R262 law)
HP = r"fleet\machines\bm-a.json"
h_raw = open(HP, "rb").read()
h = json.loads(h_raw.decode("utf-8"))
h["last_seen"] = clock
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = clock
h["verdict"] = ("watermark=green; RC-fuse root cause ADJUDICATED (b_layer_mask live-regen "
                "x exact-parity anchor, 15-probe chain, MSG-2110 to bm-b three options; "
                "P2 judgment legal as-of-snapshot); W3 judge product watch (bm-c pid 33768)")
h["current_task"] = ("r695: CONTEST-RC fuse adjudication delivered (owner ruling pending); "
                     "W3 adoption probe watch; N2 generate burn in flight bm-b")
open(HP, "wb").write(json.dumps(h, ensure_ascii=False, indent=1).encode("utf-8"))
chk2 = json.loads(open(HP, "rb").read().decode("utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int) and not isinstance(
    chk2["heartbeat_epoch_utc"], bool)
assert "T" in chk2["clock_read"] and "+" in chk2["clock_read"]
print("heartbeat ok epoch=%d int-verified clock T-format PASS" % chk2["heartbeat_epoch_utc"])
