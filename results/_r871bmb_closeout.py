"""r871 bm-b closeout: append round report line, bump state.json, update heartbeat."""
import io
import json
import os
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# 1) round report append (byte-faithful, utf-8)
line_path = os.path.join(ROOT, "results", "_r871bmb_report_line.txt")
rr_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with io.open(line_path, "rb") as fh:
    line = fh.read()
if not line.endswith(b"\n"):
    line += b"\n"
with io.open(rr_path, "ab") as fh:
    fh.write(line)

# 2) state.json update (bm-b single-machine state face)
sp = os.path.join(ROOT, "state.json")
with io.open(sp, encoding="utf-8") as fh:
    st = json.load(fh)
did = (
    "r871: S0 daemon-faces absorb x3 commits + rebase x2 (429 transient healed; "
    "origin mid-round +2 bm-c r860/r861 -> first push claw-blocked on stale-base "
    "deletion set -> lawful rebase, zero --no-verify) + orphan 0 (14 py faces) + "
    "orders diff 0 both scans + D19 dual watermark identical (dec caca0c6e/ord "
    "f90233c7) + smoke 49/49; P0 HEAL = MP1 pool done-flip shared-face settle "
    "(harvest flip 08:22:03 landed lane-only, _pool_settle origin-stale refused -> "
    "shared face stuck 'ready' = phantom runnable batch; sync_face('runnable_pool') "
    "idempotent settle -> entry+shard done -> watermark re-verdict py_low_board_clear "
    "pool_ready_ids=[]); PRIMARY PRODUCT = N2-W21 supply-face adjudication + T-101 "
    "v4 22-gate consumption scout (DIGEST-20261011-w21 + probe 7/7 markers green: "
    "A158 17 + MP1 5 union 22 overlap 0; usage-line map A9/A10/A11/A12 closed, A13 "
    "predictor face OPEN positive 2/12, MP1-5 predictor usage never-tested = lawful "
    "new face; A1/C1 composite arm gated behind BAN-05 + sentiment double-negative "
    "archive, zero drafting this window) + T26 registered+claimed same round "
    "(queue_seed_gate rc0; commit 1bbd0bdfd pushed = lock); S6 41 legs all rc0 "
    "(dualrun ZERO-DRIFT streak 26; audit FLAG:supply_floor ready=0<3 response = "
    "T26 slice-3 pool submit chain; Sunday no-new-bar no-ops; thermo/dualarm/revosc/"
    "t35_export/daily_report/ceo_live_usage ORANGE_COOL cap50/build_status/token_meter "
    "green); S7 attrition CLEAN + loop pin=2 no-op + watchdog alive"
)
st["round"] = 871
st["round_no"] = 872
st["round_no_label"] = "r871"
st["clock_read"] = TS
st["ts"] = TS
st["updated"] = TS
st["updated_at"] = TS
st["last_round_at"] = TS
st["last_round_ts"] = TS
st["last_seen"] = TS
st["last_action_at"] = TS
st["last_action"] = did[:2400]
st["did"] = did
st["now_active"] = (
    "r871 closeout: W21 supply adjudication landed (alphagen family closed 2/2 = "
    "rerun ban; never-dry pivots to consumption chain); T26 claimed and pushed; "
    "MP1 pool phantom healed"
)
st["current_task"] = (
    "r872 queue: T26 slice-1 draft + fact probe (new cutoff five-member anchor + "
    "feature computability + machinery import face) -> slice-2 runner + freeze "
    "(three-step seed law + banned gate + pre-write origin check) -> slice-3 pool "
    "submit (supply floor 0->1) + burn + finalize -> W210 freeze on W209 chain watch "
    "(bm-a M9) -> O-20261011-0012 CPU-max maintained"
)
st["task"] = st["current_task"]
st["next"] = st["current_task"]
st["verdict"] = (
    "GREEN: r871 (W21 supply-face adjudication + v4 22-gate consumption scout + T26 "
    "claim pushed same round; MP1 pool done-flip shared-face P0 healed in-window "
    "(sync_face settle, watermark re-verdict py_low_board_clear); smoke 49/49; "
    "orders/d19 zero-delta; S6 41 legs rc0)"
)
st["latest_artifact"] = (
    "r871: research/digests/DIGEST-20261011-w21-supply-pivot-v4-consumption-scout.md "
    "+ results/_r871bmb_w21_v4_scout_probe.py + results/_r871bmb_w21_v4_scout.json "
    "(probe 7/7 markers green) + tech.md T26 row claimed (commit 1bbd0bdfd)"
)
st["next_milestone"] = (
    "T26 chain: slice-1 prereg draft + fact probe <=2026-10-12 -> slice-2 runner + "
    "freeze -> slice-3 pool submit (supply floor 0->1) + burn + finalize <=2026-10-13"
)
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["orphan_face_note"] = "r871 round probe: py_faces=14 alive, orphans=0"
st["note"] = (
    "r871: first push claw-block = stale-base deletion set (bm-c r861 files in "
    "origin mid-round advance) = lawful rebase remedy face, zero escape hatch; "
    "GitHub repo renamed bigmoney->BigMoney (push redirect notice, non-blocking)"
)
with io.open(sp, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# 3) heartbeat update (fleet/machines/bm-b.json)
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
with io.open(hp, encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = TS
hb["ts"] = TS
hb["clock_read"] = TS
hb["current_task"] = "r872 queue: T26 slice-1 draft+fact probe -> slice-2 runner+freeze -> slice-3 pool submit+burn (v4 22-gate A13-style predictor extension)"
hb["cpu_cores"] = 16
hb["free_ram_gb"] = 7.1
hb["gpu_free_vram_mb"] = 3440
hb["verdict"] = "GREEN: r871 W21 adjudication + T26 claim + MP1 pool heal; py_low_board_clear"
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = int(time.time())
if "orders_ack" not in hb or not isinstance(hb.get("orders_ack"), list):
    hb["orders_ack"] = []
for name in ("O-20261011-0012-bm-a.md",):
    if name not in hb["orders_ack"]:
        hb["orders_ack"].append(name)
with io.open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# verify epoch int law (smoke F7 face)
with io.open(hp, encoding="utf-8") as fh:
    check = json.load(fh)
epoch = check["heartbeat_epoch_utc"]
assert isinstance(epoch, int), "epoch must be JSON int (R170/R178 law)"
assert "T" in check["clock_read"], "clock_read must be T-separated (R262 law)"
print("closeout ok: rr_appended=1 state.round=871 round_no=872 epoch_int=", epoch)
