# r1029 bm-c closeout: state + heartbeat + round report (canon clone of r1028 pattern)
# utf-8, epoch int assert, clock_read T-separator assert (R170/R178/R262 laws)
import datetime
import json
import time
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

DID = ("r1029 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=2 zero-kill "
       "+ S0 stash-bridge ff-merge 650953086 (bm-a r1017 W246 freeze chain + bm-b r981; 4 overlapping "
       "regenerable faces stash-dropped live-wins) + S0 pit healed same-window: stale index.lock "
       "(15:36 dead, zero git proc in repo) cleared -EA Stop+Test-Path recheck + MIS-DROP heal "
       "(stash push failed on lock -> stash drop killed r1008 pre-rebase bridge stash 4c444159 -> "
       "RESTORED via git stash store, zero loss); (2) S0.5 ORD delta TRUE consumed 3b1ca198->1835852b "
       "(1 row = 10-15 15:3x CEO live order approval Qwen switchover v3 final, bm-a-executed, zero "
       "bm-c leg; watermark advanced read-back verified; DEC ab3f0cc9 hold) + tail dual-scan FALSE "
       "both; unacked=0; (3) S1 smoke 49/49; (4) DEBT CLEARED: O-20261014-1230 @bm-c cross-machine "
       "35B probe NEVER answered in any prior round (grep round reports zero REACHABLE) -> executed "
       "this window: curl http://100.110.185.62:8090/health = {\"status\":\"ok\"} exit 0 = REACHABLE "
       "-> tailnet cross-machine reachability CONFIRMED, NO firewall command needed (bm-a two-gap "
       "item-1 closed from bm-c side); (5) S3: satengine ALIVE rc0 (burns 0 queue 0) + wm "
       "red=pool-batch-runnable-idle-low-cpu (4 W20 SCREEN shards ready, RAM gate 1.7GB<4GB "
       "park-honest, night-window autofill claims) + idle green_idle=False RAM 8.0pct honest + jobs 0 "
       "+ fleet tasks 0 open + inbox 3 MSGs all addressed HQ-CEOProxy/bm-a zero bm-c debt; (6) S6 "
       "full chain 43/43 rc0 (r1029 driver canon clone of r1026; 5-min shell timeout killed parent at "
       "leg 42 -> build_status+token_meter closed standalone rc0 both; bars 10-15 NOT on sina at "
       "15:52 nor 16:03 -> cutoff 10-14, failures 0, papers debt=0 waits-source, 16:05 window recheck) "
       "+ audit FLAG supply_gap+ignition_sla (W20 fresh-enrollment RAM-gate answered-by-design, 2nd "
       "window same face) + dualrun drift=False + fund_premium no-op (NAV 10-14 covered) + token "
       "delta=0; (7) S7: post_review YES=45 NO=0 + attrition 4 CLEAN + quad green (loop pin=5 no-op "
       "first fire 16:05, watchdog registered [S4U XML flip WARN = standing adjudicated "
       "default-principal face r1023], claws x2 installed); counter 1029->1030")

VERDICT = ("green: 35B cross-machine probe debt cleared (REACHABLE, no firewall cmd, O-20261014-1230 "
           "after 28h) + S6 43/43 rc0 green + W20 4 shards RAM-gated park-honest (autofill "
           "night-window) + MV V4 still awaiting bm-a director review (no review row on origin "
           "through 16:03) + bars 10-15 sina-lag (next window recheck fires papers chain)")

NOTE = ("r1029: 35B probe REACHABLE receipt (O-20261014-1230 debt cleared) + S6 43/43 | bars 10-15 "
        "sina-lag, recheck next window | W20 4 shards RAM-gated night-window autofill | MV V4 gated "
        "on bm-a director review | mis-drop heal: r1008 stash restored 4c444159")

NEXTP = ("r1030: (1) bars 10-15 recheck (sina lag; if landed -> papers full chain: live.paper enforce "
         "+ t35_openfill + t24 x2 + aggr + alloc + grid + cta_p1 + system_v1 + t35_export + "
         "daily_scorecard + daily_report + ceo_live_usage + dashboard); (2) W20 SCREEN: autofill "
         "claims SHARD-0..3 on RAM free (night window) -> burn complete 231/231 -> screen-finalize "
         "-> survivors + family axe -> judge chain -> intake -> sec.7 backfill + 48h CEO clock + "
         "attrition 2 rows; (3) MV V4: watch bm-a director review of JAY-REDO-KF-BOARD-r1025.jpg -> "
         "i2v INT8 768P full batch (batch-sampling law O-20261014-1325); (4) U256 bmc-w001/w003 "
         "claims on RAM gate open; (5) W246 finalize watch (bm-a chain) -> W247 seat cycle per "
         "chain-order; (6) CPU backfill pool: claim-and-burn when bm-a publishes (MSG-0825 standing)")

ARTIFACT = ("r1029: S6 chain driver clone Tools/_r1029bmc_s6.py + results/_r1029bmc_s6_log.txt "
            "(43/43 rc0) + 35B REACHABLE probe receipt (heartbeat did, O-20261014-1230 debt cleared) "
            "+ watermark advance 1835852b + closeout writes (this commit)")

PROD_LANES = ("CPU=W20 SCREEN 4 shards ready lane-pinned bm-c (RAM gate 1.7GB<4GB park-honest; "
              "autofill claims on night-window RAM free) -> screen-finalize next ; GPU=MV V4 "
              "POOL-0014 awaiting bm-a director review (no review row through 16:03) -> i2v INT8 "
              "768P full batch next + ComfyUI 常驻 + album serve ; N1=W246 bm-a seat (freeze landed "
              "650953086, finalize in-flight theirs) ; U256 w001/w003 = RAM gate deferred ; "
              "MEMORY-GATE=HQ-MemoryBudgetGate armed 4h (bm-c leg closed r1027)")

CLOSEOUT_NOTE = ("r1029 closeout: clean continuation window (state round_no=1029 at open, executed "
                 "r1029, advanced 1029->1030 so next=r1030); zero absorb owed (r1028 closeout landed "
                 "clean); zero double-count: S0.5 ORD delta consumed THIS window (3b1ca198->1835852b, "
                 "1 row bm-a-executed zero bm-c leg; DEC hold), tail dual-scan FALSE both; products = "
                 "O-20261014-1230 35B probe debt cleared (REACHABLE) + S6 43/43 rc0 + mis-drop heal "
                 "(r1008 stash restored); pit same-window: git stash push failure on index.lock -> "
                 "blind stash drop kills PRE-EXISTING stash (always verify push rc + stash list "
                 "identity before drop; PowerShell bare stash@{0} arg mangles -> quote it)")

SELFPROOF = {
    "占用一行": ("CPU=W20 SCREEN 4 shards enrolled (RAM gate 1.7GB<4GB park-honest, autofill burns "
                "on night-window RAM free) ; GPU=MV 车道候 bm-a 导演席批 (POOL-0014 KF 14/14+"
                "LOOKBOARD 已交付·未批) + ComfyUI 常驻 + album serve"),
    "当前活": "r1029 closeout (35B probe debt cleared REACHABLE + S6 43/43 + W20 RAM-park watch)",
    "最近实物": ("Tools/_r1029bmc_s6.py + results/_r1029bmc_s6_log.txt (43/43 rc0) + 35B probe "
                "receipt in heartbeat did + watermark advance 1835852b（16:1x·本窗 commit）"),
    "下个交付物": ("bars 10-15 papers 全链（sina 落即发）+ W20 SCREEN 烧完→screen-finalize（夜窗 "
                  "RAM 释后 autofill）+ MV V4 i2v 全批候 bm-a 批（窗≤48h）"),
    "队列水位": ("池 ready=4（全 W20 screen·lane bm-c）·N1 引擎 0 在烧（W246 bm-a 在飞）·U256 候 "
                "RAM 门·P2/P3 空·jobs 0"),
}


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(p, d):
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n" if not open(p, "rb").read().endswith(b"\n") else "")


def main():
    st = load(STATE)
    hb = load(HEART)

    st["round_no"] = 1030
    st["round_no_label"] = "r1029"
    st["last_round"] = "r1029"
    st["last_round_label"] = "r1029"
    st["clock_read"] = now
    st["ts"] = now
    st["last_seen"] = now
    st["last_seen_at"] = now
    st["updated"] = now
    st["updated_at"] = now
    st["last_round_at"] = now
    st["last_round_ts"] = now
    st["last_round_closed"] = now
    st["last_round_summary_at"] = now
    st["last_action"] = "r1029 closeout (35B probe debt cleared + S6 43/43 + quad green)"
    st["last_action_at"] = now
    st["current_task"] = "r1029 closeout: 35B probe debt cleared (REACHABLE) + S6 43/43 + W20 RAM-park watch"
    st["current_task_at"] = now
    st["current_task_ts"] = epoch
    st["heartbeat_epoch_utc"] = epoch
    st["did"] = DID
    st["verdict"] = VERDICT
    st["note"] = NOTE
    st["next"] = NEXTP
    st["next_pointer"] = NEXTP
    st["next_milestone"] = "r1030+: bars 10-15 papers full chain on sina landing + W20 screen burn (autofill on RAM free) -> screen-finalize -> judge; MV V4 i2v on bm-a director approval"
    st["prod_lanes"] = PROD_LANES
    st["latest_artifact"] = ARTIFACT
    st["last_artifact"] = ARTIFACT
    st["recent_artifact"] = ARTIFACT
    st["last_round_summary"] = ("r1029: 35B cross-machine probe debt cleared (REACHABLE, O-20261014-1230 "
                                "after 28h) + S6 43/43 rc0 (bars 10-15 sina-lag, papers next window) + "
                                "W20 4 shards RAM-gated + S7 quad green")
    st["full_load_selfproof"] = SELFPROOF
    st["activity_now"] = "2026-10-15T16:1x | r1029 | bm-c: closeout (35B probe REACHABLE + S6 43/43 + watermark advance) | counter 1029->1030 (r1029 exec)"
    st["now_active"] = st["activity_now"]
    st["orphan_face"] = 2
    st["orphan_faces"] = 2
    st["free_ram_gb"] = 1.7
    st["ram_free_gb"] = 1.7
    st["idle_ram_gb"] = 1.7
    st["gpu_free_vram_mb"] = 15120
    st["gpu_util_pct"] = 0
    st["r1029_closeout_note"] = CLOSEOUT_NOTE
    st["last_orders_seen"] = now
    st["last_orders_read_at"] = now
    st["last_decisions_seen"] = now
    st["last_decisions_read_at"] = now
    if isinstance(st.get("d19_watermark_guard"), dict):
        st["d19_watermark_guard"]["round_ref"] = 1030
        st["d19_watermark_guard"]["ts"] = now

    hb.update({k: st[k] for k in (
        "round_no", "round_no_label", "last_round", "last_round_label", "clock_read", "ts",
        "last_seen", "last_seen_at", "updated", "updated_at", "last_round_at", "last_round_ts",
        "last_round_closed", "last_round_summary_at", "last_action", "last_action_at",
        "current_task", "current_task_at", "current_task_ts", "heartbeat_epoch_utc", "did",
        "verdict", "note", "next", "next_pointer", "next_milestone", "prod_lanes",
        "latest_artifact", "last_artifact", "recent_artifact", "last_round_summary",
        "full_load_selfproof", "activity_now", "now_active", "orphan_face", "orphan_faces",
        "free_ram_gb", "ram_free_gb", "idle_ram_gb", "gpu_free_vram_mb", "gpu_util_pct",
        "last_orders_seen", "last_orders_read_at", "last_decisions_seen",
        "last_decisions_read_at", "d19_watermark_guard") if k in st})
    hb["last_round_at"] = now

    dump(STATE, st)
    dump(HEART, hb)

    row = ("%s | r1029 | bm-c: 35B cross-machine probe debt CLEARED (O-20261014-1230: curl "
           "100.110.185.62:8090/health = status ok exit 0 = REACHABLE, no firewall cmd; never "
           "answered in any prior round, grep-verified) + S0 stash-bridge ff 650953086 + S0.5 ORD "
           "3b1ca198->1835852b (1 row Qwen switchover bm-a-executed zero bm-c leg) + smoke 49/49 + "
           "S6 43/43 rc0 (bars 10-15 sina-lag cutoff 10-14, papers debt=0, recheck next window; "
           "audit FLAG supply_gap+ignition_sla=W20 RAM-gate answered-by-design; dualrun drift=False; "
           "token delta=0) + S7 quad green + mis-drop heal (r1008 stash restored 4c444159) + pit: "
           "stash push fail on index.lock -> blind drop kills pre-existing stash | "
           "results/_r1029bmc_s6_log.txt 43 rc0 + heartbeat did probe receipt + d19 watermark json | "
           "r1030: bars recheck papers full chain + W20 autofill screen burn on RAM free + MV V4 "
           "i2v on bm-a review + U256 on RAM gate\n") % now

    with io.open(REPORT, "a", encoding="utf-8", newline="\n") as f:
        f.write(row)

    # self-verify (R170/R178/R262: epoch int + T-separator + json round-trip)
    st2 = load(STATE)
    hb2 = load(HEART)
    assert isinstance(st2["heartbeat_epoch_utc"], int), "epoch not int"
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "hb epoch not int"
    assert "T" in st2["clock_read"] and "+" in st2["clock_read"], "clock_read format"
    assert st2["round_no"] == 1030 and st2["last_round_label"] == "r1029"
    print("CLOSEOUT-OK round_no=1030 label=r1029 epoch=%d clock=%s" % (
        st2["heartbeat_epoch_utc"], st2["clock_read"]))


if __name__ == "__main__":
    main()
