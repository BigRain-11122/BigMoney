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
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# every GPU spelling the fleet face has ever used (see Tools/gpu_face.py); a caller
# may not supply these -- they are replaced by one probe (r1284)
GPU_KEY_RE = re.compile(r"^gpu.*(free|used|idle|mem|vram|util)")

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


def _gpu_face_mod():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from Tools import gpu_face
    return gpu_face


def _nested_is_gpu(block, gf):
    """One-level dict whose sub-keys spell GPU memory or utilisation (r1381)."""
    for sk in block:
        low = str(sk).lower()
        if gf.gpu_mem_family("gpu_%s" % low)[0] or low.startswith(("util", "load")):
            return True
    return False


def _owned_nested(block, gf, probe):
    """Restate a one-level GPU block from the SAME probe (r1381).

    The flat chokepoint keys on a `gpu...` spelling, so {"gpu": {"free_gb": ...,
    "total_gb": ..., "util": ...}} walked straight through with the caller's own
    sample; merge-only then kept it forever. Live evidence: bm-c's heartbeat
    carried gpu.free_gb 14.4 beside gpu_free_vram_gb 14.3 (102.4 MiB of spread
    between two keys that both look authoritative) and smoke's
    `fleet: GPU face self-consistent on heartbeat` went red with gpu_face_ts
    freshly stamped -- the writer had run, it just never owned the block.
    Sub-keys the probe cannot state are preserved unchanged.
    """
    out = {}
    for sk, sv in block.items():
        low = str(sk).lower()
        fam, unit = gf.gpu_mem_family("gpu_%s" % low)
        if fam == "free":
            v = probe["total_mib"] - probe["used_mib"]
        elif fam == "used":
            v = probe["used_mib"]
        elif fam == "total":
            v = probe["total_mib"]
        else:
            fam = None
        if fam:
            out[sk] = round(v / 1024.0, 1) if unit == "gb" else v
        elif low.startswith(("util", "load")):
            out[sk] = probe["util_pct"]
        else:
            out[sk] = sv
    return out


def gpu_chokepoint(fields, verdict):
    """Replace every caller-supplied GPU spelling with one probe's whole face.

    WHY (r1284): the heartbeat is merge-only, so a per-round closeout script that
    hand-wrote nine aliases at its own sample left two other aliases at an older
    one -- the face then read free=15065 beside free=15252 MiB and smoke went red
    on `fleet: GPU face self-consistent`. Tools/gpu_face.apply already owns the
    face, but only an S6 leg calls it, so any ad-hoc writer could half-own it
    again. This is the chokepoint: GPU numbers are not a caller's to set.
    A failed probe drops them (warning) rather than inventing a number.
    """
    gpu_keys = [k for k in (fields or {}) if GPU_KEY_RE.match(k)]
    gf = _gpu_face_mod()
    nested_keys = [k for k, val in (fields or {}).items()
                   if isinstance(val, dict) and val
                   and not GPU_KEY_RE.match(k)
                   and _nested_is_gpu(val, gf)]
    if not gpu_keys and not nested_keys:
        return fields
    kept = {k: val for k, val in fields.items()
            if not GPU_KEY_RE.match(k) and k not in nested_keys}
    try:
        gf = _gpu_face_mod()
        probe = gf.probe_live()
    except Exception as ex:
        dropped = gpu_keys + nested_keys
        verdict["warnings"].append(
            "gpu probe failed, %d caller GPU key(s) dropped: %s"
            % (len(dropped), str(ex)[:120]))
        verdict["gpu_dropped"] = dropped
        return kept
    kept.update(gf.fields_from(probe, gf._stamp()))
    for k in nested_keys:
        kept[k] = _owned_nested(fields[k], gf, probe)
    verdict["gpu_probe"] = probe
    verdict["gpu_replaced"] = gpu_keys
    if nested_keys:
        verdict["gpu_nested_restated"] = nested_keys
    return kept


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
    fields = gpu_chokepoint(fields, v)
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

    # L11 r1284: a caller's partial GPU face is replaced by one probe, so the face
    #     stays self-consistent (the defect: 9 keys at one sample, 2 at another)
    t = os.path.join(tmp, "L11")
    hp = _fixture(t, A, heart_ack=A,
                  extra_heart={"gpu_free_mem_mib": 15252, "gpu_idle_mib": 15252,
                               "gpu_mem_total_mib": 16384})
    gf = _gpu_face_mod()
    real = gf.probe_live
    gf.probe_live = lambda smi=None: {"util_pct": 0.0, "used_mib": 1125,
                                      "total_mib": 16384}
    try:
        v, rc = write(t, {"did": "g", "gpu_free_mib": 15065,
                          "gpu_free_mb": 15065, "gpu_used_mib": 1319})
    finally:
        gf.probe_live = real
    h = _load(hp)
    leg("L11 caller GPU spellings replaced by one probe (face consistent)", True,
        rc == 0 and gf.audit(h) == [] and h.get("gpu_free_mib") == 15259
        and h.get("gpu_used_mib") == 1125,
        "audit=%s free=%s" % (gf.audit(h) or "none", h.get("gpu_free_mib")))

    # L12 a failed probe drops the caller's GPU keys instead of inventing a face
    t = os.path.join(tmp, "L12")
    hp = _fixture(t, A, heart_ack=A,
                  extra_heart={"gpu_free_mib": 15259, "gpu_used_mib": 1125,
                               "gpu_mem_total_mib": 16384})
    real = gf.probe_live
    gf.probe_live = lambda smi=None: (_ for _ in ()).throw(RuntimeError("no smi"))
    try:
        v, rc = write(t, {"did": "f", "gpu_free_mib": 1, "gpu_used_mib": 1})
    finally:
        gf.probe_live = real
    h = _load(hp)
    leg("L12 failed probe: GPU keys dropped, rest written", True,
        rc == 0 and h.get("did") == "f" and h.get("gpu_free_mib") == 15259
        and bool(v.get("gpu_dropped")), "dropped=%s" % (v.get("gpu_dropped"),))

    # L13 r1381: a caller-supplied NESTED GPU block is restated from the same
    #     probe. The flat regex could not see {"gpu": {"free_gb": ...}}: it went
    #     through with the caller's number, merge-only kept it, and the live
    #     face audited 102.4 MiB of spread with a fresh gpu_face_ts.
    t = os.path.join(tmp, "L13")
    hp = _fixture(t, A, heart_ack=A,
                  extra_heart={"gpu": {"free_gb": 14.4, "total_gb": 16.0,
                                       "util": 3, "vendor": "nvidia"}})
    real = gf.probe_live
    gf.probe_live = lambda smi=None: {"util_pct": 0.0, "used_mib": 1125,
                                      "total_mib": 16384}
    try:
        v, rc = write(t, {"did": "h",
                          "gpu": {"free_gb": 15.0, "total_gb": 16.0,
                                  "util": 9, "vendor": "nvidia"}})
    finally:
        gf.probe_live = real
    h = _load(hp)
    g = h.get("gpu") or {}
    leg("L13 nested GPU block restated from the probe (not the caller)", True,
        rc == 0 and gf.audit(h) == [] and g.get("free_gb") == 14.9
        and g.get("util") == 0 and g.get("vendor") == "nvidia",
        "audit=%s gpu=%s restated=%s" % (gf.audit(h) or "none", g,
                                         v.get("gpu_nested_restated")))

    # L14 a failed probe drops the caller's nested block too (old face survives)
    t = os.path.join(tmp, "L14")
    hp = _fixture(t, A, heart_ack=A,
                  extra_heart={"gpu": {"free_gb": 14.4, "total_gb": 16.0,
                                       "util": 3}})
    gf.probe_live = lambda smi=None: (_ for _ in ()).throw(RuntimeError("no smi"))
    try:
        v, rc = write(t, {"did": "i",
                          "gpu": {"free_gb": 1.0, "total_gb": 16.0, "util": 99}})
    finally:
        gf.probe_live = real
    h = _load(hp)
    leg("L14 failed probe: nested GPU block dropped, old face kept", True,
        rc == 0 and h.get("did") == "i"
        and (h.get("gpu") or {}).get("free_gb") == 14.4
        and "gpu" in (v.get("gpu_dropped") or []),
        "dropped=%s" % (v.get("gpu_dropped"),))

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