# -*- coding: utf-8 -*-
"""r884 bm-b round bookkeeping: state.json + round_reports.md line + heartbeat."""
import json, io, time, datetime

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now()
tz = now.strftime("%z")  # +0800
ts_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + tz[:3] + ":" + tz[3:] if len(tz) == 5 else now.isoformat()
epoch = int(time.time())

DID = ("r884: S0 half-open rebase heal: r883 closeout pick (bfd769a80) found stalled mid-rebase onto "
       "e7725f2a1 (prior session killed 14:57:03 by 25min runner) -> 21-UU content-driven resolve via "
       "_r884bmb_rebase_resolver (r853 1-gen clone, receipt union preserved) + autostash pop conflict healed "
       "per r642 assert-before-drop: 5 daemon faces HEAD-newer checkout, runnable_pool.bm-b mirror "
       "keep-stash-side (14:56:09 > HEAD 14:46:09, r747 G4' live-wins), satengine history line-union +5 "
       "stash-only tick lines 14:52-14:56 recovered (tick 14:51 never written - disclosed), stash dropped "
       "post-superset-assert; first push claw-blocked = r811(1) stale-base (origin advanced to bm-c r878 "
       "5ccdc507b carrying w17_reform_face.json + regime_p0_slice3.py) -> second rebase leveling (3 picks, "
       "26 UU across 3 windows, resolver2 + bounded marker-guard add+continue loop) -> push landed "
       "5ccdc507b..ad057104d, delivery self-check behind=0 ahead=0")
VERDICT = ("green: dual rebase landed clean (26 UU 3 windows, zero fail-closed, marker guards green, r836 "
           "legs green: symbolic-ref=refs/heads/main + rebase-merge gone); smoke 49/49; orders diff EMPTY "
           "(195 acked/70 orders); orphan faces 0; E16 census 6/12 landed, finalize gate (12/12) not triggered")
NEXT = ("r885: E16 7..12/12 completion watch -> finalize refuse-if-exists at 12/12 -> CENSUS verdict face -> "
        "T-184 bm-a courtesy branch re-probe (byte-compare only) -> W210 freeze anchor watch -> 48h CEO "
        "report due 2026-10-13 11:2x")
TASK = "r885: E16 watch + finalize gate + CENSUS verdict + T-184 courtesy re-probe + W210 anchor watch + 48h CEO report 2026-10-13 11:2x"

# 1. state.json
state = {
    "round_no": 884, "did": DID, "verdict": VERDICT, "next": NEXT,
    "last_round_ts": ts_iso, "last_result": "ok", "current_task": TASK,
    "updated_at": ts_iso, "last_seen": ts_iso, "ts": ts_iso,
}
with io.open(REPO + r"\logs\iteration-loop\state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

# 2. round_reports.md append (per fleet README §6 fixed fields + product-priority-law visibility lines)
REPORT = ("{ts} | r884 bm-b | dept:engineering(S0 integration surgery round: half-open rebase heal - prior "
          "session died mid-rebase at S7 pull; 21-UU resolve + autostash pop heal + claw-block stale-base "
          "diagnosis + second rebase leveling 26-UU 3-windows; E16 shard-5 artifacts landed with pick) | "
          "currently-active: E16 burns 6/12 landed (autofill worker chain, shards 6-11 claimed); "
          "latest-artifact: commit ad057104d push landed 15:3x + results/alphagen_rg/shard_5of12.json "
          "15:08; next-milestone: E16 12/12 + finalize + CENSUS verdict face ~17-18:xx, 48h CEO report "
          "2026-10-13 11:2x | orphan-faces=0 (probe py_faces=13); WM-VERDICT: red=true-lane=pool-batch-"
          "runnable-idle-low-cpu=burn-ramp (E16 pool burns in-flight per O-1612 GM waiver) | "
          "verification-evidence=results/_r884bmb_rebase_resolver.json 21/21 + _r884bmb_rebase_resolver2 "
          "(21+2+3 three windows zero fail-closed) + _r884bmb_stash_assert.py 6/7 + heal union 108-line "
          "superset PASS + smoke 49/49 + push 5ccdc507b..ad057104d delivery self-check behind=0 ahead=0 | "
          "local-unreached-origin-commits=0 (post-push fetch+rev-list self-proof) | registry-zero-hit: "
          "treasure_guard restore gate rc0 7-face reproducible-artifact class | disclosure: satengine tick "
          "14:51:07 absent in both HEAD and stash (never written, no recovery source); next-pointer=r885: "
          "E16 7..12/12 watch + finalize refuse-if-exists + CENSUS verdict + T-184 bm-a courtesy re-probe + "
          "W210 anchor watch + 48h CEO report 10-13 11:2x").format(ts=ts_iso)
with io.open(REPO + r"\logs\iteration-loop\round_reports.md", "a", encoding="utf-8") as f:
    f.write("\n" + REPORT + "\n")

# 3. heartbeat fleet/machines/bm-b.json
hb_path = REPO + r"\fleet\machines\bm-b.json"
with io.open(hb_path, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "round_no": 884, "round": 884, "did": DID, "verdict": "green", "next": NEXT,
    "current_task": TASK, "task": TASK,
    "last_seen": ts_iso, "ts": ts_iso, "clock_read": ts_iso,
    "heartbeat_epoch_utc": epoch,
    "idle_rounds": 0, "agenda_starved": False,
    "last_action": "S0 half-open rebase heal + dual rebase leveling + push landed",
    "last_action_at": ts_iso, "last_round_at": ts_iso, "updated": ts_iso, "updated_at": ts_iso,
    "now_active": "E16 pool burns 6/12 landed, autofill worker chain shards 6-11",
    "latest_artifact": "commit ad057104d push landed 15:3x + results/alphagen_rg/shard_5of12.json 15:08",
    "next_milestone": "E16 12/12 + finalize + CENSUS verdict ~17-18:xx; 48h CEO report 2026-10-13 11:2x",
    "orphan_faces": 0, "orphan_face": 0,
    "free_ram_gb": 10.2, "ram_free_gb": 10.2, "cpu_cores": 16,
    "gpu_free_vram_mb": 3506, "gpu_free_vram_gb": 3.5, "vram_free_gb": 3.5,
})
with io.open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-proof: epoch must be JSON int
hb2 = json.load(io.open(hb_path, "r", encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in hb2["clock_read"], "clock_read not T-separated"
print("BOOKKEEPING-OK round=884 ts=%s epoch=%d orders_ack=%d" % (ts_iso, epoch, len(hb2.get("orders_ack", {}))))
