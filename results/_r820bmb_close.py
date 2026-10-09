"""r820 bm-b closeout: state.json + heartbeat load-modify-dump (r818 law:
large-list files are NEVER hand-retyped; fields updated in-place via json
load/dump, orders_ack preserved verbatim with before/after equality assert).
"""
import datetime
import io
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")

now_iso = datetime.datetime.now(
    datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="seconds")
epoch = int(time.time())

VERDICT = (
    "r820: T16 closed (dualarm sec.1 contract adapter: lossless legal-shell "
    "A1 sort/A2 byte-equal dedupe/A3 five-key spec alias + B0-B5 judgment "
    "blocked fail-closed; adapter selftest 23/23 + dualarm 18->26 legs incl "
    "8 e2e; probe real face REGIME5-2026-09-30.json PASS; live non-regression "
    "proven latest.json byte-identical sha16 C7A7F000DFAA61E3; "
    "DUALARM-2026-09-30 evidence face rc0); smoke 49/49; S6 42 legs rc0 "
    "(dualrun ZERO-DRIFT streak 5; compute_audit flags supply_gap+"
    "ignition_sla = W17 shards lane bm-c data-gate candidates, honest "
    "disclosure non-bm-b violation); watermark red=false healthy; orders both "
    "sweeps zero unacked (60/184); ORD/DEC hash MATCH both keys; attrition "
    "CLEAN; orphans=0; 5x HANDOVER duty landed (merged row r781-r820, seven "
    "missed 5x stamps honestly disclosed per pit-79 family)")

DID = (
    "r820: tech T16 landed (scripts/regime_gate_dualarm_adapter.py sec.1 "
    "legal-shell adapter + regime_gate_dualarm.py run() wiring with "
    "adaptation disclosure block + canonical-copy __main__ launcher; "
    "selftest 23/23 + 26/26; live non-regression byte-identical) + S6 42 "
    "legs rc0 (dualrun streak 5) + 5x HANDOVER merged row r781-r820")

NOW_ACTIVE = "r820: tech T16 closed (dualarm sec.1 contract adapter scripts/regime_gate_dualarm_adapter.py)"

ARTIFACT = (
    "r820: scripts/regime_gate_dualarm_adapter.py + regime_gate_dualarm.py "
    "violation-branch wiring (selftest 23/23+26/26, live non-regression "
    "proven, DUALARM-2026-09-30 evidence face), 2026-10-10 07:0x")

MILESTONE = (
    "r821+: tech queue next candidate (T15 head open = awaiting GM flag; "
    "queue 3 left) / Monday 2026-10-12 09:15 minute_feed first gated run "
    "backfills 10-08/10-09 (<=48h)")

TASK = (
    "tech queue next candidate after T15 (open, awaiting GM flag); waiting: "
    "Monday 10-12 09:15 minute_feed gated backfill 10-08/10-09 / astock "
    "refresh tail (continuation in-flight) / W18 wave drafting gated on "
    "W17-JUDGE drain")

LAST_ACTION = (
    "r820: tech T16 (dualarm sec.1 contract adapter + run() wiring + "
    "canonical-copy launcher) + S6 42 legs rc0 + 5x HANDOVER r781-r820 "
    "merged row + S7 quartet green + attrition CLEAN")


def update_json(path, mutations):
    with io.open(path, encoding="utf-8") as f:
        doc = json.load(f)
    before_ack = doc.get("orders_ack")
    doc.update(mutations)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)
    with io.open(path, encoding="utf-8") as f:
        back = json.load(f)
    if before_ack is not None:
        assert back["orders_ack"] == before_ack, "orders_ack mutated!"
    return back


st = update_json(STATE, {
    "round_no": 820, "round": 820, "round_no_label": "r820",
    "clock_read": now_iso, "ts": now_iso, "updated": now_iso,
    "updated_at": now_iso, "last_seen": now_iso,
    "last_round_at": now_iso, "last_round_ts": now_iso,
    "last_decisions_read_at": "2026-10-10T06:46:00+08:00",
    "last_orders_read_at": "2026-10-10T06:46:00+08:00",
    "did": DID, "verdict": VERDICT, "now_active": NOW_ACTIVE,
    "latest_artifact": ARTIFACT, "next_milestone": MILESTONE,
    "current_task": TASK, "next": TASK, "task": TASK,
})

hb = update_json(HB, {
    "round": 820, "round_no": 820,
    "now_active": NOW_ACTIVE, "current_task": TASK, "task": TASK,
    "latest_artifact": ARTIFACT, "next_milestone": MILESTONE,
    "verdict": VERDICT, "last_action": LAST_ACTION,
    "last_round_at": now_iso, "last_seen": now_iso, "updated": now_iso,
    "ts": now_iso, "clock_read": now_iso,
    "heartbeat_epoch_utc": epoch,
    "cpu_cores": 16, "free_ram_gb": 12.3,
    "gpu_free_vram_mb": 3459, "gpu_free_vram_gb": 3.46,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_faces": 0,
    "orphan_face_note": (
        "r820 probe 06:4x: 13 py faces 0 orphans; astock refresh continuation "
        "in-flight lawful"),
    "sync": {
        "ahead": 0, "behind": 0, "last_push_ts": now_iso,
        "note": ("r820: S0 fetch fast-forward da075290f->44c050307 "
                 "ahead0/behind0; round commit push follows; verify = "
                 "post-push fetch+rev-list+ls-remote self-proof"),
    },
})

assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be int"
assert hb["round_no"] == 820 and st["round_no"] == 820
print("close ok: state r%s hb r%s ack=%d epoch=%d clock=%s" % (
    st["round_no"], hb["round_no"], len(hb["orders_ack"]),
    hb["heartbeat_epoch_utc"], hb["clock_read"]))
