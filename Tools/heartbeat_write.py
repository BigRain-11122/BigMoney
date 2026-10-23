# -*- coding: utf-8 -*-
"""heartbeat_write.py -- canonical heartbeat face writer (merge-only).

WHY (r1110 root cure, defect class live-fired by r1109 closeout):
  fleet/machines/<id>.json is the face of record for order receipts --
  Tools/orders_ack_scan.py reads ONLY the heartbeat orders_ack list. A closeout
  that rebuilds the heartbeat dict from scratch instead of merging silently
  deletes that list, and the next round reads a full board of already-consumed
  orders as P0 dispatch debt (r1052 family, second face: first the state/heart
  append asymmetry, now whole-file replace).

LAW this tool enforces:
  1. MERGE-ONLY: unknown existing keys are preserved; nothing is ever deleted by
     the writer. A caller can only set fields.
  2. ACK FACE INTEGRITY: if the state face holds order acks that the heartbeat
     does not, the heartbeat is repaired from the state face in the same write,
     and a write that would SHRINK the heartbeat ack set relative to the state
     face is refused (rc 3).
  3. INVARIANTS (smoke F7 family): heartbeat_epoch_utc must be int, clock_read
     and ts must be ISO-8601 with a 'T' separator, round/round_no ints.
  4. Post-write re-read assertion (r504 law): the caller's fields are present
     and the ack face is a superset of the state face after the write.

CLI:
  python Tools/heartbeat_write.py apply --fields <path-to-json-dict>
  python Tools/heartbeat_write.py heal            # ack face + mirrors from state
  python Tools/heartbeat_write.py selftest
Exit: 0 ok, 2 mechanism fault, 3 invariant/refusal.
"""
import io
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# mirrors kept identical on both faces (state -> heartbeat direction)
MIRROR_KEYS = (
    "orders_ack_last",
    "last_orders_sha",
    "last_decisions_sha",
    "last_orders_ts",
    "last_decisions_ts",
    "last_orders_seen",
    "last_decisions_seen",
)


def _paths(project):
    with io.open(os.path.join(project, "fleet", "machine.json"),
                 encoding="utf-8-sig") as fh:
        mid = json.load(fh)["machine_id"]
    hb = os.path.join(project, "fleet", "machines", mid + ".json")
    if mid == "bm-b":
        st = os.path.join(project, "state.json")
    else:
        st = os.path.join(project, "state-%s.json" % mid)
    return mid, st, hb


def _load(path):
    with io.open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def _dump_atomic(path, obj):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def _iso_t(ts):
    return isinstance(ts, str) and "T" in ts and len(ts) >= 19


def write(project, fields, state_path=None, heart_path=None, heal=True):
    """Merge `fields` into the heartbeat. Returns (verdict, rc)."""
    v = {"tool": "heartbeat_write", "applied": [], "healed": [],
         "mirrors_synced": {}, "warnings": []}
    mid, st_def, hb_def = _paths(project)
    st_path = state_path or st_def
    hb_path = heart_path or hb_def
    v["machine_id"] = mid
    if not os.path.exists(hb_path):
        return dict(v, error="heartbeat face missing: %s" % hb_path), 2
    try:
        hb = _load(hb_path)
    except Exception as ex:
        return dict(v, error="heartbeat unreadable: %s" % ex), 2
    if not isinstance(hb, dict):
        return dict(v, error="heartbeat is not an object"), 3
    state = {}
    if os.path.exists(st_path):
        try:
            state = _load(st_path)
        except Exception as ex:
            return dict(v, error="state unreadable: %s" % ex), 2

    prev_ack = hb.get("orders_ack")
    prev_ack = list(prev_ack) if isinstance(prev_ack, list) else []
    st_ack = state.get("orders_ack")
    st_ack = list(st_ack) if isinstance(st_ack, list) else []
    v["ack_before"] = len(prev_ack)
    v["state_ack_count"] = len(st_ack)

    # (2) ack face integrity: repair from state, never shrink below state
    heart_ack = list(prev_ack)
    for a in st_ack:
        if a not in heart_ack:
            heart_ack.append(a)
            v["healed"].append(a)
    missing_from_heart = [a for a in heart_ack if a not in st_ack]
    if missing_from_heart:
        v["warnings"].append(
            "heartbeat carries %d ack(s) absent from state (kept, not deleted)"
            % len(missing_from_heart))
    stale = [a for a in st_ack if a not in heart_ack]
    if stale:
        return dict(v, error="refused: write would shrink ack face (%d missing)"
                    % len(stale)), 3
    hb["orders_ack"] = heart_ack
    if heart_ack:
        hb.setdefault("orders_ack_last", heart_ack[-1])
    if isinstance(state.get("orders_ack_last"), str):
        if hb.get("orders_ack_last") != state["orders_ack_last"]:
            hb["orders_ack_last"] = state["orders_ack_last"]

    # mirrors state -> heartbeat
    if heal:
        for k in MIRROR_KEYS:
            if k in state and hb.get(k) != state[k]:
                v["mirrors_synced"][k] = hb.get(k)
                hb[k] = state[k]

    # (1) merge caller fields (never delete)
    for k, val in (fields or {}).items():
        if hb.get(k) != val:
            hb[k] = val
            v["applied"].append(k)

    # (3) invariants
    if not isinstance(hb.get("heartbeat_epoch_utc"), int):
        return dict(v, error="heartbeat_epoch_utc must be JSON int (R170/R178)"), 3
    for k in ("clock_read", "ts"):
        if k in hb and not _iso_t(hb[k]):
            return dict(v, error="%s must be ISO-8601 with 'T'" % k), 3
    for k in ("round", "round_no"):
        if k in hb and not isinstance(hb[k], int):
            return dict(v, error="%s must be int" % k), 3
    if hb.get("machine_id") not in (None, mid):
        return dict(v, error="machine_id mismatch: %r != %r"
                    % (hb.get("machine_id"), mid)), 3
    hb.setdefault("machine_id", mid)

    _dump_atomic(hb_path, hb)

    # (4) post-write re-read assertions
    try:
        h2 = _load(hb_path)
        for k in (fields or {}):
            assert h2.get(k) == fields[k], "field not persisted: %s" % k
        ack2 = h2.get("orders_ack")
        assert isinstance(ack2, list), "ack face not a list post-write"
        assert not [a for a in st_ack if a not in ack2], "ack face shrank"
        assert isinstance(h2.get("heartbeat_epoch_utc"), int)
    except AssertionError as ex:
        return dict(v, error="post-write assertion failed: %s" % ex), 3
    v["ack_after"] = len(h2["orders_ack"])
    return v, 0


def cmd_apply(project, fields_path):
    with io.open(fields_path, encoding="utf-8-sig") as fh:
        fields = json.load(fh)
    v, rc = write(project, fields)
    print(json.dumps(v, ensure_ascii=False))
    return rc


def cmd_heal(project):
    v, rc = write(project, {})
    print(json.dumps(v, ensure_ascii=False))
    return rc


# ------------------------------------------------------------------ selftest
def _fixture(root, state_ack, heart_ack=None, extra_heart=None,
             extra_state=None, epoch=1792000000, clock="2026-10-24T06:00:00+08:00"):
    os.makedirs(os.path.join(root, "fleet", "machines"), exist_ok=True)
    with io.open(os.path.join(root, "fleet", "machine.json"), "w",
                 encoding="utf-8") as fh:
        json.dump({"machine_id": "bm-a"}, fh)
    state = {"orders_ack": list(state_ack),
             "orders_ack_last": state_ack[-1] if state_ack else None,
             "last_orders_sha": "aa11"}
    state.update(extra_state or {})
    with io.open(os.path.join(root, "state-bm-a.json"), "w",
                 encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1)
    heart = {"machine_id": "bm-a", "ts": clock, "clock_read": clock,
             "heartbeat_epoch_utc": epoch, "round": 1, "round_no": 2,
             "status": "green", "verdict": "green"}
    if heart_ack is not None:
        heart["orders_ack"] = list(heart_ack)
    heart.update(extra_heart or {})
    hp = os.path.join(root, "fleet", "machines", "bm-a.json")
    with io.open(hp, "w", encoding="utf-8") as fh:
        json.dump(heart, fh, ensure_ascii=False, indent=1)
    return hp


def selftest():
    legs = []

    def leg(name, want, got, extra=""):
        legs.append((name, want == got))
        print("%-70s %s %s" % (name, "PASS" if want == got else "FAIL", extra))

    tmp = tempfile.mkdtemp(prefix="hbw_st_")
    A = ["O-1.md", "O-2.md"]

    # L1 r1109 regression: heartbeat with NO orders_ack key is repaired from state
    t = os.path.join(tmp, "L1")
    hp = _fixture(t, A, heart_ack=None)
    v, rc = write(t, {"round": 1110})
    h = _load(hp)
    leg("L1 whole-file-replace regression heals ack from state", True,
        rc == 0 and h["orders_ack"] == A)

    # L2 merge preserves unknown caller-unrelated keys
    t = os.path.join(tmp, "L2")
    hp = _fixture(t, A, heart_ack=A, extra_heart={"custom_key": 7})
    v, rc = write(t, {"did": "x"})
    h = _load(hp)
    leg("L2 unknown keys preserved (merge-only)", True,
        rc == 0 and h.get("custom_key") == 7 and h.get("did") == "x")

    # L3 epoch str refused
    t = os.path.join(tmp, "L3")
    hp = _fixture(t, A, heart_ack=A, epoch="1792000000")
    v, rc = write(t, {"did": "y"})
    leg("L3 epoch str refused rc3", 3, rc, v.get("error", "")[:40])

    # L4 ack shrink refused (heartbeat lacks an ack while state has it: repaired
    #    first, so use a heartbeat that would be REBUILT smaller by the caller)
    t = os.path.join(tmp, "L4")
    hp = _fixture(t, A, heart_ack=A[:1])
    v, rc = write(t, {"did": "z"})
    h = _load(hp)
    leg("L4 partial heartbeat ack face repaired, not shrunk", True,
        rc == 0 and h["orders_ack"] == A)

    # L5 clock_read without T refused
    t = os.path.join(tmp, "L5")
    _fixture(t, A, heart_ack=A)
    v, rc = write(t, {"clock_read": "2026-10-24 06:00:00"})
    leg("L5 clock_read without 'T' refused rc3", 3, rc)

    # L6 idempotent: second identical write changes nothing
    t = os.path.join(tmp, "L6")
    hp = _fixture(t, A, heart_ack=A)
    write(t, {"round": 1110, "did": "q"})
    b1 = io.open(hp, "rb").read()
    write(t, {"round": 1110, "did": "q"})
    b2 = io.open(hp, "rb").read()
    leg("L6 idempotent repeat write (byte identical)", True, b1 == b2)

    # L7 orders_ack_last mirrored from state
    t = os.path.join(tmp, "L7")
    hp = _fixture(t, A, heart_ack=A, extra_heart={"orders_ack_last": "O-0.md"})
    write(t, {"did": "m"})
    leg("L7 orders_ack_last mirror synced from state", True,
        _load(hp)["orders_ack_last"] == A[-1])

    # L8 mirror key (last_orders_sha) synced from state
    t = os.path.join(tmp, "L8")
    hp = _fixture(t, A, heart_ack=A)
    write(t, {"did": "n"})
    leg("L8 last_orders_sha mirror synced from state", "aa11",
        _load(hp).get("last_orders_sha"))

    # L9 heartbeat-only acks are kept, never deleted
    t = os.path.join(tmp, "L9")
    hp = _fixture(t, A, heart_ack=A + ["O-9.md"])
    write(t, {"did": "k"})
    leg("L9 heartbeat-only ack kept (no silent delete)", True,
        "O-9.md" in _load(hp)["orders_ack"])

    # L10 missing heartbeat face -> rc2
    t = os.path.join(tmp, "L10")
    _fixture(t, A, heart_ack=A)
    os.remove(os.path.join(t, "fleet", "machines", "bm-a.json"))
    v, rc = write(t, {"did": "w"})
    leg("L10 missing heartbeat face rc2", 2, rc)

    ok = sum(1 for _, p in legs if p)
    print("\nselftest %d/%d %s" % (ok, len(legs),
                                   "PASS" if ok == len(legs) else "FAIL"))
    return 0 if ok == len(legs) else 1


def main(argv):
    project = ROOT
    if len(argv) >= 2 and argv[1] == "selftest":
        return selftest()
    if len(argv) >= 3 and argv[1] == "apply":
        if argv[2] == "--fields" and len(argv) >= 4:
            return cmd_apply(project, argv[3])
        return 2
    if len(argv) >= 2 and argv[1] == "heal":
        return cmd_heal(project)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))