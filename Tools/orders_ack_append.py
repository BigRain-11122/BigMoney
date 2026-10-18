#!/usr/bin/env python
# orders_ack_append.py -- canonical TWO-FACE orders ack append tool.
# Birth defect cured: r1052 pit (heartbeat ack-face asymmetry) -- r1051
# closeout hand-rolled the ack append, wrote the state face but missed
# the heartbeat face; orders_ack_scan.py reads the heartbeat only, so
# the next round start flagged a false P0 unacked debt on an order that
# was genuinely consumed. Per the gate-building law (a ledger row
# without a gate is not a fix), this tool is the structural face of
# "closeout ack appends write BOTH faces" (FLEET-OPS sec.3
# receipt-closure symmetry, r1052 CODELY.md row).
#
# Usage:
#   python Tools/orders_ack_append.py <O-file-name> [--sync-mirrors]
#   python Tools/orders_ack_append.py selftest
#
# One call writes BOTH faces:
#   state face        : state.json (bm-b) / state-<id>.json (others)
#                       -- canonical ledger face (S5 per-machine naming)
#   heartbeat face    : fleet/machines/<id>.json orders_ack
#                       -- the scanner read face
# plus orders_ack_last on each face that actually received the append.
# --sync-mirrors copies the watermark mirror fields (last_orders_sha /
# last_decisions_sha / *_ts / *_at / *_read_at) from the state canonical
# face to the heartbeat (r1052 heal recipe) -- run it after a d19
# watermark --advance in the same window.
#
# Idempotent PER FACE: an ack already present in one face is skipped in
# that face (safe re-run after partial failure; composes with closeout
# styles that already appended the state face inline).
#
# Law map:
#   - r504 law : validate-then-atomic-write (tmp + os.replace),
#                post-write re-read assertions.
#   - r1052 law: ack appends write BOTH faces in the same call.
#   - S5 law   : bm-b state face = state.json, others state-<id>.json.
#   - single-writer: heartbeat is owned by the round session (S7);
#     this tool must run inside that session's window (never from a
#     parallel session / task).
#
# Exit codes:
#   0 = ok (appended where missing; idempotent skips disclosed)
#   2 = mechanism fault (bad args / unreadable or missing faces; NO
#       write happens -- both faces are read before the first write)
#   3 = post-write assertion failure (faces must not be trusted;
#       re-run heals the partial face via per-face idempotency)
#
# selftest: offline fixture trees only, zero live-face writes.
# ENCODING: pure ASCII (repo law: zh-CN hosts decode BOM-less as GBK).
import json
import os
import sys
import tempfile

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mirror fields synced by --sync-mirrors (r1052 heal recipe set).
MIRROR_KEYS = (
    "last_orders_sha", "last_decisions_sha",
    "last_orders_ts", "last_orders_at", "last_orders_read_at",
    "last_decisions_ts", "last_decisions_at", "last_decisions_read_at",
)


def state_face_path(base_dir, machine_id):
    """S5 per-machine naming: bm-b carries state.json, others state-<id>."""
    if machine_id == "bm-b":
        return os.path.join(base_dir, "state.json")
    return os.path.join(base_dir, "state-%s.json" % machine_id)


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _dump_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def append_ack(base_dir, target, sync_mirrors=False, machine_id=None,
               state_path=None, heart_path=None):
    """Append target ack to BOTH faces. Returns (verdict_dict, exit_code).
    Paths may be injected for the selftest; both are read BEFORE any
    write so a missing/unreadable face aborts with zero disk changes."""
    v = {
        "tool": "orders_ack_append",
        "target": target,
        "machine_id": machine_id,
        "state_appended": False,
        "heart_appended": False,
        "mirrors_synced": {},
    }
    if not target or os.sep in target or os.altsep and os.altsep in target:
        v["error"] = "bad target (empty or contains path separator)"
        return v, 2
    if machine_id is None:
        mjson = os.path.join(base_dir, "fleet", "machine.json")
        if not os.path.isfile(mjson):
            v["error"] = "fleet/machine.json missing (S0-1 anchor first)"
            return v, 2
        try:
            machine_id = _load_json(mjson).get("machine_id")
        except Exception as ex:
            v["error"] = "machine.json unreadable: %s" % ex
            return v, 2
        if not machine_id:
            v["error"] = "machine.json has no machine_id"
            return v, 2
        v["machine_id"] = machine_id
    if state_path is None:
        state_path = state_face_path(base_dir, machine_id)
    if heart_path is None:
        heart_path = os.path.join(base_dir, "fleet", "machines",
                                  machine_id + ".json")
    # read both faces first: all-or-nothing at the read stage
    for path, face in ((state_path, "state"), (heart_path, "heartbeat")):
        if not os.path.isfile(path):
            v["error"] = "%s face missing: %s" % (face, path)
            return v, 2
    try:
        state = _load_json(state_path)
        heart = _load_json(heart_path)
    except Exception as ex:
        v["error"] = "face unreadable: %s" % ex
        return v, 2
    for face, obj in (("state", state), ("heartbeat", heart)):
        if not isinstance(obj.get("orders_ack"), list):
            v["error"] = "%s face orders_ack is not a list" % face
            return v, 2
    # state face append (idempotent)
    if target not in state["orders_ack"]:
        state["orders_ack"].append(target)
        state["orders_ack_last"] = target
        v["state_appended"] = True
    # heartbeat face append (idempotent)
    if target not in heart["orders_ack"]:
        heart["orders_ack"].append(target)
        heart["orders_ack_last"] = target
        v["heart_appended"] = True
    # optional mirror sync state -> heartbeat (r1052 heal recipe)
    if sync_mirrors:
        for k in MIRROR_KEYS:
            if k in state and heart.get(k) != state[k]:
                v["mirrors_synced"][k] = (heart.get(k), state[k])
                heart[k] = state[k]
    # heartbeat epoch type invariant (R170/R178): never regress to str
    if "heartbeat_epoch_utc" in heart and \
            not isinstance(heart["heartbeat_epoch_utc"], int):
        v["error"] = "heartbeat_epoch_utc not int (R170/R178) -- abort"
        return v, 2
    _dump_atomic(state_path, state)
    _dump_atomic(heart_path, heart)
    # post-write re-read assertions (r504 law)
    try:
        s2 = _load_json(state_path)
        h2 = _load_json(heart_path)
        assert target in s2["orders_ack"], "target absent from state post-write"
        assert target in h2["orders_ack"], "target absent from heart post-write"
        if v["state_appended"]:
            assert s2.get("orders_ack_last") == target
        if v["heart_appended"]:
            assert h2.get("orders_ack_last") == target
        assert isinstance(h2.get("orders_ack"), list)
        if "heartbeat_epoch_utc" in h2:
            assert isinstance(h2["heartbeat_epoch_utc"], int)
    except AssertionError as ex:
        v["error"] = "post-write assertion failed: %s" % ex
        return v, 3
    v["state_ack_count"] = len(s2["orders_ack"])
    v["heart_ack_count"] = len(h2["orders_ack"])
    return v, 0


def main(argv):
    args = [a for a in argv[1:] if a != "--sync-mirrors"]
    sync = "--sync-mirrors" in argv[1:]
    if args and args[0] == "selftest":
        return selftest()
    if len(args) != 1:
        print("usage: python Tools/orders_ack_append.py <O-file-name> "
              "[--sync-mirrors] | selftest")
        return 2
    v, rc = append_ack(PROJECT, args[0], sync_mirrors=sync)
    print(json.dumps({k: v[k] for k in v if k != "mirrors_synced" or v[k]},
                     ensure_ascii=False))
    if rc == 0:
        print("APPEND-OK target=%s state=%s heart=%s mirrors=%d" %
              (v["target"], "APPENDED" if v["state_appended"] else "skip",
               "APPENDED" if v["heart_appended"] else "skip",
               len(v["mirrors_synced"])))
    return rc


def _mk_fixture(root, machine_id, state_name, ack_s, ack_h, extra_state=None,
                extra_heart=None):
    os.makedirs(os.path.join(root, "fleet", "machines"), exist_ok=True)
    with open(os.path.join(root, "fleet", "machine.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"machine_id": machine_id}, fh)
    state = {"orders_ack": ack_s, "orders_ack_last": ack_s[-1] if ack_s else None}
    state.update(extra_state or {})
    with open(os.path.join(root, state_name), "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1)
    heart = {"orders_ack": ack_h, "heartbeat_epoch_utc": 1792000000}
    heart.update(extra_heart or {})
    with open(os.path.join(root, "fleet", "machines",
                           machine_id + ".json"), "w", encoding="utf-8") as fh:
        json.dump(heart, fh, ensure_ascii=False, indent=1)
    return os.path.join(root, state_name), \
        os.path.join(root, "fleet", "machines", machine_id + ".json")


def selftest():
    legs = []

    def leg(name, want, got, extra=""):
        ok = want == got
        legs.append((name, ok))
        print("%-64s %s %s" % (name, "PASS" if ok else "FAIL", extra))

    tmp = tempfile.mkdtemp(prefix="oaa_st_")
    try:
        T = "O-20261018-0948-bm-a.md"
        # L1: fresh append -> both faces, orders_ack_last on both.
        f1 = os.path.join(tmp, "L1")
        sp, hp = _mk_fixture(f1, "bm-a", "state-bm-a.json",
                             ["O-1.md"], ["O-1.md"])
        v, rc = append_ack(f1, T, state_path=sp, heart_path=hp)
        ok = (rc == 0 and v["state_appended"] and v["heart_appended"] and
              _load_json(sp)["orders_ack_last"] == T and
              _load_json(hp)["orders_ack_last"] == T)
        leg("L1 fresh append writes both faces + ack_last", True, ok)
        # L2: idempotent re-run -> skips, ack_last untouched.
        v2, rc2 = append_ack(f1, T, state_path=sp, heart_path=hp)
        h2 = _load_json(hp)
        ok = (rc2 == 0 and not v2["state_appended"] and
              not v2["heart_appended"] and
              h2["orders_ack_last"] == T and
              len(h2["orders_ack"]) == 2)
        leg("L2 idempotent re-run skips both faces", True, ok)
        # L3: partial-face heal (state has it, heartbeat missing).
        f3 = os.path.join(tmp, "L3")
        sp3, hp3 = _mk_fixture(f3, "bm-a", "state-bm-a.json",
                               ["O-1.md", T], ["O-1.md"])
        v3, rc3 = append_ack(f3, T, state_path=sp3, heart_path=hp3)
        ok = (rc3 == 0 and not v3["state_appended"] and v3["heart_appended"])
        leg("L3 partial-face heal heart-only append", True, ok)
        # L4: --sync-mirrors copies mirror fields state -> heartbeat.
        f4 = os.path.join(tmp, "L4")
        sp4, hp4 = _mk_fixture(f4, "bm-a", "state-bm-a.json", ["O-1.md"],
                               ["O-1.md"],
                               extra_state={"last_orders_sha": "ab" * 20,
                                            "last_decisions_sha": "cd" * 20},
                               extra_heart={"last_orders_sha": "zz" * 20})
        v4, rc4 = append_ack(f4, "O-9.md", sync_mirrors=True,
                             state_path=sp4, heart_path=hp4)
        h4 = _load_json(hp4)
        ok = (rc4 == 0 and h4["last_orders_sha"] == "ab" * 20 and
              h4["last_decisions_sha"] == "cd" * 20 and
              len(v4["mirrors_synced"]) == 2)
        leg("L4 --sync-mirrors copies both shas", True, ok)
        # L5: missing state face -> rc2, zero writes (heartbeat untouched).
        f5 = os.path.join(tmp, "L5")
        sp5, hp5 = _mk_fixture(f5, "bm-a", "state-bm-a.json", [], [])
        os.remove(sp5)
        v5, rc5 = append_ack(f5, "O-1.md", state_path=sp5, heart_path=hp5)
        ok = (rc5 == 2 and _load_json(hp5)["orders_ack"] == [])
        leg("L5 missing state face -> rc2 no write", True, ok)
        # L6: bad target (path separator) -> rc2.
        f6 = os.path.join(tmp, "L6")
        sp6, hp6 = _mk_fixture(f6, "bm-a", "state-bm-a.json", [], [])
        v6, rc6 = append_ack(f6, "fleet/x.md", state_path=sp6, heart_path=hp6)
        leg("L6 path-separator target -> rc2", 2, rc6)
        # L7: bm-b naming law -> state face path resolves to state.json.
        p = state_face_path(f6, "bm-b")
        ok = os.path.basename(p) == "state.json"
        legs.append(("L7 bm-b state face = state.json", ok))
        print("%-64s %s" % ("L7 bm-b state face = state.json",
                            "PASS" if ok else "FAIL"))
        # L8: epoch type guard -> str epoch aborts rc2, no write.
        f8 = os.path.join(tmp, "L8")
        sp8, hp8 = _mk_fixture(f8, "bm-a", "state-bm-a.json", [], [],
                               extra_heart={"heartbeat_epoch_utc": "x"})
        v8, rc8 = append_ack(f8, "O-1.md", state_path=sp8, heart_path=hp8)
        ok = rc8 == 2 and _load_json(sp8)["orders_ack"] == []
        leg("L8 str heartbeat_epoch_utc aborts (R170)", True, ok)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    fails = [n for n, ok in legs if not ok]
    print("selftest: %d/%d PASS" % (len(legs) - len(fails), len(legs)))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
