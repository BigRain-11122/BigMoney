"""D-19 dual watermark write-side integrity guard (tech-queue T13;
pit-protocol-d19.md r812 splice-defect family mechanized; O-20261009-1246 P2).

The r810/r811/r812 family proved the D-19 watermark *write* path is where
integrity dies: PS-pipe phantom tails, prefix-only heal verification, and a
hand-spliced "true-8-hex + phantom-32-hex" string that was structurally a
valid 40-hex token yet byte-wrong. This guard is THE single legal write
path for the two state watermark keys. Laws mechanized (research/pit-
protocol-d19.md):

  r686/r814  read/compare via the canonical probe only -- python
             subprocess raw-bytes, never a PS pipe, never a disk copy;
  r711/r503  comparisons case-normalized (lower()) on both sides;
  r537       algorithm picked by stored-key length (40-hex -> SHA-1,
             64-hex -> SHA-256); stored value written VERBATIM from the
             probe output -- no re-casing, no splicing, no truncation;
  r812       writes = single-source python FULL string; heal = swap the
             WHOLE string, never the head; prefix match is NOT a
             content-unchanged judgment basis;
  r585       consumption receipt and watermark advance must land in the
             SAME round -- enforced by refusing a delta without an
             explicit --advance (atomicity gate);
  r582       bm-b state file = state.json, other machines state-<id>.json
             (machine_id from fleet/machine.json; never guessed);
  T22        every probe invocation is passed --state (machine-aware); the
             probe asserts basename == machine-derived filename (r954 bm-a
             defect: probe read bm-b's watermark and cried false delta).

Subcommands
  probe     run the canonical read probe and print its summary (read-only);
  update    run a fresh canonical probe (or --probe-json for offline
            injection), validate candidates (full hex, 40/64 length),
            then: unchanged -> no --advance needed, keys rewritten
            verbatim (case-normalizes to the canonical probe form);
            delta -> REFUSE without --advance, swap whole strings with it;
            atomic write + read-back full-string equality assertion;
  verify    read-side assertion: structural shape of both keys + optional
            equality cross-check against probe evidence;
  selftest  offline fixtures in a temp sandbox, zero network, zero repo
            mutation.

Exit codes: 0 = ok/no-op/healthy; 2 = mechanism fault (probe failure,
missing evidence/state file); 3 = validation refusal (malformed candidate,
delta without --advance, malformed stored key in verify). Receipt:
results/d19_watermark.json.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE = os.path.join(ROOT, "results", "_r686bmb_d19_check.py")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
# r1081: probe evidence + run receipt are per-machine daemon live-tick faces
# (D-20261015-02 family). Live-fire: shared tracked path _r686bmb_d19_check.json
# was a three-machine overwrite race (bm-a rebase pop-UU vs bm-c r1121 same
# window; every round's S0.5 probe rewrote one tracked path). Shared-name
# legacy files stay tracked-but-dormant on origin (claw-clean, no writer).


def _mid(machine_json=MACHINE_JSON):
    with open(machine_json, encoding="utf-8") as f:
        return json.load(f)["machine_id"]


PROBE_OUT = os.path.join(ROOT, "results", "_r686bmb_d19_check.%s.json" % _mid())
RECEIPT = os.path.join(ROOT, "results", "d19_watermark.%s.json" % _mid())

DEC_KEY = "last_decisions_sha"
ORD_KEY = "last_orders_sha"
READ_KEYS = ("last_decisions_read_at", "last_orders_read_at")
PROV_KEY = "d19_watermark_guard"
# D-20261024-03 triple watermark (addition, not replacement): the legacy
# full-digest keys above stay the verbatim anchor; these carry the
# reproducible <sha16>@<commit7>/<bytes> form so a comparison can fail on
# commit+length before it ever hashes anything.
TRIPLE_DEC_KEY = "last_decisions_watermark"
TRIPLE_ORD_KEY = "last_orders_watermark"
# r1090 two-face patch (r1051 lineage recurring face / r1052 连带律 mechanized): update --advance
# wrote the STATE face only; the heartbeat mirror fields went stale every advance and needed a
# manual same-window sync script (r1089 receipt _r1089bmc_heart_wm_sync). Law now welded in-tool:
# BOTH faces are written in the SAME update, with read-back assertions on each.
HEART_KEYS = ("last_orders_sha", "last_decisions_sha", "last_orders_read_at",
              "last_decisions_read_at", "last_orders_at", "last_decisions_at",
              "last_orders_seen", "last_decisions_seen",
              "last_orders_watermark", "last_decisions_watermark")
HEX_CHARS = set("0123456789abcdefABCDEF")
VALID_LENS = (40, 64)


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def resolve_state_path(machine_json_path, state_dir):
    with open(machine_json_path, encoding="utf-8") as f:
        mid = json.load(f)["machine_id"]
    fname = "state.json" if mid == "bm-b" else "state-%s.json" % mid
    return mid, os.path.join(state_dir, fname)


def validate_candidate(v):
    """Full-string shape gate: hex, exact 40/64 length, zero padding.
    A hand-spliced 8+32 string passes SHAPE -- only full-string equality
    vs the recomputed probe value catches it (r812); shape is necessary,
    not sufficient."""
    if not isinstance(v, str) or v == "":
        return False, "missing/empty"
    if v != v.strip():
        return False, "whitespace-padded"
    if len(v) not in VALID_LENS:
        return False, "length %d not full-hash (40/64)" % len(v)
    if not all(c in HEX_CHARS for c in v):
        return False, "non-hex chars"
    return True, "ok"


def validate_triple(v):
    """D-20261024-03 shape gate: <sha16>@<commit7 or 40>/<bytes>.
    Shape-only like validate_candidate: a well-formed but wrong triple is
    caught by the probe's live recomputation, not by this gate."""
    if not isinstance(v, str) or v == "":
        return False, "missing/empty"
    if v != v.strip():
        return False, "whitespace-padded"
    if "@" not in v or "/" not in v:
        return False, "missing @ or /"
    sha, rest = v.split("@", 1)
    commit, _, nbytes = rest.partition("/")
    if len(sha) != 16:
        return False, "sha16 length %d" % len(sha)
    if len(commit) not in (7, 40):
        return False, "commit length %d not 7/40" % len(commit)
    if not nbytes.isdigit():
        return False, "bytes not numeric"
    if not all(c in HEX_CHARS for c in sha + commit):
        return False, "non-hex chars"
    return True, "ok"


def _atomic_json_write(obj, path, ascii_mode):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(prefix=".d19w_", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=ascii_mode, indent=1)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sync_heartbeat(state, machine_id, heartbeat_path, receipt):
    """r1090 two-face patch: mirror the watermark fields from the state canonical
    face into the heartbeat (fleet/machines/<id>.json) in the SAME update, with
    read-back assertion. Only keys present in state are mirrored (zero
    fabrication); heartbeat keys absent from state are left untouched. Missing
    heartbeat file = honest skip (receipt-noted), never a fault -- sandboxes
    and exotic hosts may legitimately have no heartbeat."""
    receipt["heartbeat_sync"] = {"path": heartbeat_path, "synced": {},
                                 "readback_ok": None, "note": None}
    if not os.path.isfile(heartbeat_path):
        receipt["heartbeat_sync"]["note"] = "heartbeat file absent -> skipped (honest)"
        return
    hb = _load_json(heartbeat_path)
    synced = {}
    for k in HEART_KEYS:
        if k in state and state[k] != hb.get(k):
            synced[k] = {"from": hb.get(k), "to": state[k]}
            hb[k] = state[k]
    if not synced:
        receipt["heartbeat_sync"]["note"] = "mirrors already equal (no-op)"
        receipt["heartbeat_sync"]["readback_ok"] = True
        return
    _atomic_json_write(hb, heartbeat_path, False)
    hb2 = _load_json(heartbeat_path)
    ok = all(hb2.get(k) == state.get(k) for k in synced)
    if not ok:
        raise AssertionError("heartbeat mirror read-back equality failed")
    receipt["heartbeat_sync"]["synced"] = synced
    receipt["heartbeat_sync"]["readback_ok"] = ok


def _changed(cur, cand):
    return (cand or "").lower() != (cur or "").lower()


def cmd_update(opts):
    """Single legal watermark write path. Returns exit code."""
    ts = now_iso()
    receipt = {"ts": ts, "cmd": "update", "advance": bool(opts.advance),
               "state_path": opts.state, "action": None, "changed": {},
               "reasons": [], "err": None}
    try:
        if opts.probe_json:
            ev_path = opts.probe_json
        else:
            rc = subprocess.run(
                [sys.executable, PROBE, "--state", opts.state],
                cwd=ROOT, capture_output=True).returncode
            if rc != 0:
                receipt["action"] = "refused"
                receipt["err"] = "canonical probe rc=%d" % rc
                _atomic_json_write(receipt, opts.receipt, True)
                print("REFUSED: canonical probe rc=%d (mechanism fault)" % rc)
                return 2
            ev_path = PROBE_OUT
        if not os.path.isfile(ev_path):
            receipt["action"] = "refused"
            receipt["err"] = "probe evidence missing: %s" % ev_path
            _atomic_json_write(receipt, opts.receipt, True)
            print("REFUSED: probe evidence missing (mechanism fault)")
            return 2
        ev = _load_json(ev_path)
        if ev.get("err"):
            receipt["action"] = "refused"
            receipt["err"] = "probe err: %s" % ev.get("err")
            _atomic_json_write(receipt, opts.receipt, True)
            print("REFUSED: probe err present (mechanism fault)")
            return 2
        cand_dec, cand_ord = ev.get("decisions_sha"), ev.get("orders_sha")
        reasons = []
        ok_dec, why_dec = validate_candidate(cand_dec)
        if not ok_dec:
            reasons.append("decisions_sha: %s" % why_dec)
        ok_ord, why_ord = validate_candidate(cand_ord)
        if not ok_ord:
            reasons.append("orders_sha: %s" % why_ord)
        if reasons:
            receipt["action"] = "refused"
            receipt["reasons"] = reasons
            _atomic_json_write(receipt, opts.receipt, True)
            print("REFUSED: malformed candidate -> %s" % "; ".join(reasons))
            return 3
        if not os.path.isfile(opts.state):
            receipt["action"] = "refused"
            receipt["err"] = "state file missing: %s" % opts.state
            _atomic_json_write(receipt, opts.receipt, True)
            print("REFUSED: state file missing (mechanism fault)")
            return 2
        st = _load_json(opts.state)
        ch_dec = _changed(st.get(DEC_KEY), cand_dec)
        ch_ord = _changed(st.get(ORD_KEY), cand_ord)
        receipt["changed"] = {"decisions": ch_dec, "orders": ch_ord}
        if (ch_dec or ch_ord) and not opts.advance:
            receipt["action"] = "refused"
            receipt["reasons"] = [
                "delta without --advance (r585 atomicity gate): "
                "consume the delta in THIS round, then rerun with --advance"]
            receipt["delta"] = {DEC_KEY: st.get(DEC_KEY),
                                "candidate": cand_dec}
            _atomic_json_write(receipt, opts.receipt, True)
            print("REFUSED: delta present (dec=%s ord=%s) without --advance "
                  "-- consume first, rerun with --advance (r585)"
                  % (ch_dec, ch_ord))
            return 3
        # D-20261024-03: triples ride the same atomic write. Absent evidence =
        # skip (mid-migration machines stay honest, no fabrication).
        triples = {}
        for key, val in ((TRIPLE_DEC_KEY, ev.get("decisions_triple")),
                         (TRIPLE_ORD_KEY, ev.get("orders_triple"))):
            if val is None:
                continue
            ok_t, why_t = validate_triple(val)
            if not ok_t:
                reasons.append("%s: %s" % (key, why_t))
            else:
                triples[key] = val
        if reasons:
            receipt["action"] = "refused"
            receipt["reasons"] = reasons
            _atomic_json_write(receipt, opts.receipt, True)
            print("REFUSED: malformed triple -> %s" % "; ".join(reasons))
            return 3
        receipt["triples"] = triples
        # single-source verbatim full-string write (r812)
        st[DEC_KEY] = cand_dec
        st[ORD_KEY] = cand_ord
        for k, v in triples.items():
            st[k] = v
        for k in READ_KEYS:
            st[k] = ts
        if ch_dec:
            st["last_decisions_at"] = ts
        st[PROV_KEY] = {
            "tool": "scripts/d19_watermark.py",
            "probe": "results/_r686bmb_d19_check.py",
            "probe_evidence": os.path.abspath(ev_path),
            "method_decisions": ev.get("decisions_method"),
            "method_orders": ev.get("orders_method"),
            "verbatim": True, "advance": bool(opts.advance),
            "round_ref": st.get("round_no"), "ts": ts,
        }
        before_bytes = open(opts.state, "rb").read()
        _atomic_json_write(st, opts.state, False)
        # read-back full-string equality assertion (r812 heal law)
        st2 = _load_json(opts.state)
        if (st2.get(DEC_KEY) != cand_dec or st2.get(ORD_KEY) != cand_ord
                or any(st2.get(k) != v for k, v in triples.items())):
            # read-back failed -> byte-exact restore, honest fault report
            with open(opts.state, "wb") as f:
                f.write(before_bytes)
            receipt["action"] = "readback_failed"
            receipt["err"] = "read-back equality assertion failed"
            _atomic_json_write(receipt, opts.receipt, True)
            print("FAULT: read-back full-string equality failed")
            return 2
        receipt["action"] = "advanced" if (ch_dec or ch_ord) else "noop"
        receipt["written"] = {DEC_KEY: cand_dec, ORD_KEY: cand_ord}
        # r1090 two-face law: heartbeat mirrors ride the SAME update (r1052 连带律 in-tool)
        try:
            _mj = getattr(opts, "machine_json", None) or MACHINE_JSON
            with open(_mj, encoding="utf-8") as _f:
                mid = json.load(_f)["machine_id"]
            hb_path = getattr(opts, "heartbeat", None) or os.path.join(
                ROOT, "fleet", "machines", "%s.json" % mid)
            sync_heartbeat(st2, mid, hb_path, receipt)
        except Exception as e:
            # heartbeat sync failure must NOT silently pass (r1052 family: a stale
            # mirror = next-round false P0 debt); restore state bytes + fail loud
            with open(opts.state, "wb") as f:
                f.write(before_bytes)
            receipt["action"] = "heartbeat_sync_failed"
            receipt["err"] = "heartbeat sync: %r" % e
            _atomic_json_write(receipt, opts.receipt, True)
            print("FAULT: heartbeat mirror sync failed (state rolled back): %r" % e)
            return 2
        _atomic_json_write(receipt, opts.receipt, True)
        _hs = receipt.get("heartbeat_sync", {})
        print("%s: dec=%s ord=%s (read-back full-string equality OK; heartbeat mirrors %s)"
              % (receipt["action"].upper(), cand_dec, cand_ord,
                 "synced %d" % len(_hs.get("synced", {})) if _hs.get("readback_ok")
                 else _hs.get("note") or "unclear"))
        return 0
    except Exception as e:
        receipt["action"] = "fault"
        receipt["err"] = repr(e)
        try:
            _atomic_json_write(receipt, opts.receipt, True)
        except Exception:
            pass
        print("FAULT: %r" % e)
        return 2


def cmd_verify(opts):
    ts = now_iso()
    out = {"ts": ts, "cmd": "verify", "state_path": opts.state,
           "structural": {}, "probe_equality": {}}
    try:
        st = _load_json(opts.state)
    except Exception as e:
        out["err"] = "state unreadable: %r" % e
        _atomic_json_write(out, opts.receipt, True)
        print("FAULT: state unreadable")
        return 2
    rc = 0
    for key in (DEC_KEY, ORD_KEY):
        ok, why = validate_candidate(st.get(key))
        out["structural"][key] = {"ok": ok, "why": why,
                                  "len": len(st[key]) if isinstance(st.get(key), str) else None}
        if not ok:
            rc = 3
    for key in (TRIPLE_DEC_KEY, TRIPLE_ORD_KEY):
        val = st.get(key)
        if val is None:
            out["structural"][key] = {"ok": True, "why": "absent (migrating)"}
            continue
        ok_t, why_t = validate_triple(val)
        out["structural"][key] = {"ok": ok_t, "why": why_t}
        if not ok_t:
            rc = 3
    if os.path.isfile(opts.probe_evidence):
        ev = _load_json(opts.probe_evidence)
        for key, ek in ((DEC_KEY, "decisions_sha"), (ORD_KEY, "orders_sha")):
            cand = ev.get(ek)
            out["probe_equality"][key] = {
                "equal": (cand or "").lower() == (st.get(key) or "").lower(),
                "fresh": cand,
            }
    _atomic_json_write(out, opts.receipt, True)
    print(json.dumps({"structural_ok": rc == 0,
                     "probe_equality": out["probe_equality"]}))
    return rc


def _relay_child_streams(r):
    """r1045 pit fix: on this Win/Py3.14 host a pass-through subprocess child
    (stdout=None) never reaches the parent's inherited handle -- the child's
    print vanishes even under `> file` redirect (empirical: parent prints
    land, child prints do not; 0-byte capture face). cmd_probe relied on that
    pass-through, so the loop read silence+rc0 as 'hold' while a real orders
    delta existed (r1044 missed 4 group orders commits for 2+ hours). All
    child summaries must be captured and re-printed by the parent."""
    out = getattr(r, "stdout", None) or ""
    err = getattr(r, "stderr", None) or ""
    if not isinstance(out, str):
        out = out.decode("utf-8", "replace")
    if not isinstance(err, str):
        err = err.decode("utf-8", "replace")
    if out:
        sys.stdout.write(out)
        sys.stdout.flush()
    if err:
        sys.stderr.write(err)
        sys.stderr.flush()


def cmd_probe(opts):
    # T22: inject the machine-aware state path so the probe reads
    # state-<id>.json, never a legacy/wrong-machine watermark.
    _, state = resolve_state_path(MACHINE_JSON, ROOT)
    # r1045: capture + relay (pass-through face is swallowed on this host;
    # see _relay_child_streams docstring). rc semantics unchanged.
    r = subprocess.run([sys.executable, PROBE, "--state", state],
                       cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    _relay_child_streams(r)
    return r.returncode


def selftest():
    """Offline fixtures in a temp sandbox: zero network, zero repo mutation."""
    tmp = tempfile.mkdtemp(prefix="d19w_selftest_")
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as e:
            legs.append((name, False, str(e)))
        except Exception as e:
            legs.append((name, False, repr(e)))

    TRUE_DEC = "a3ea37bd" + "70fd5acc83bcf51939874cffd59f1811"
    TRUE_ORD = "e286f84287331c99e5c2d3c4dda391617f301a99"
    OLD_DEC = "0123456789abcdef0123456789abcdef01234567"
    OLD_ORD = "fedcba9876543210fedcba9876543210fedcba98"
    # r811 splice family: true 8-hex head + phantom 32-hex tail
    SPLICED = "a3ea37bd" + "7c856e4b649f52b77212c57a2abe3776"
    PHANTOM = "b148d0ad" + "1111111111111111111111111111111"

    def mkfix(state=None, machine="bm-b", mkstate=True, mkheartbeat=True):
        d = os.path.join(tmp, "fix%d" % len(os.listdir(tmp)))
        os.makedirs(d)
        mj = os.path.join(d, "machine.json")
        json.dump({"machine_id": machine}, open(mj, "w"))
        mid, sp = resolve_state_path(mj, d)
        if mkstate and state is not None:
            json.dump(state, open(sp, "w", encoding="utf-8"), indent=1)
        pj = os.path.join(d, "probe.json")
        json.dump({}, open(pj, "w"))
        rec = os.path.join(d, "receipt.json")
        # r1090 two-face fixtures: heartbeat with STALE mirrors + a foreign key
        hb = os.path.join(d, "fleet", "machines", "%s.json" % mid)
        if mkheartbeat:
            os.makedirs(os.path.dirname(hb))
            json.dump({"machine_id": mid, "last_orders_sha": OLD_ORD,
                       "last_decisions_sha": OLD_DEC, "last_orders_seen": "stale",
                       "extra_foreign_key": "keep-me"}, open(hb, "w", encoding="utf-8"))
        return mid, sp, pj, rec, mj, hb

    def upd(ev_dict, advance=False, state=None, machine="bm-b", mkstate=True,
            mkheartbeat=True, heartbeat_override="USE_FIXTURE"):
        mid, sp, pj, rec, mj, hb = mkfix(state=state, machine=machine,
                                         mkstate=mkstate, mkheartbeat=mkheartbeat)
        if ev_dict is not None:
            json.dump(ev_dict, open(pj, "w"))
        o = argparse.Namespace(state=sp, probe_json=pj, receipt=rec,
                               advance=advance, probe_evidence=pj,
                               machine_json=mj,
                               heartbeat=hb if heartbeat_override == "USE_FIXTURE"
                               else heartbeat_override)
        return cmd_update(o), sp, rec, hb

    base_state = {DEC_KEY: OLD_DEC, ORD_KEY: OLD_ORD, "round_no": 999,
                  "note": "CJK-note-\u6c34\u4f4d", "other": [1, 2, 3]}
    new_ev = {"decisions_sha": TRUE_DEC, "orders_sha": TRUE_ORD,
              "decisions_method": "sha1", "orders_method": "sha1",
              "err": None}

    # L1 advance happy path: whole-string swap, fields preserved
    def l1():
        rc, sp, rec, _hb = upd(new_ev, advance=True, state=dict(base_state))
        assert rc == 0, "rc=%s" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == TRUE_DEC and st[ORD_KEY] == TRUE_ORD
        assert st["round_no"] == 999 and st["other"] == [1, 2, 3]
        assert st["note"] == "CJK-note-\u6c34\u4f4d"
        assert st[PROV_KEY]["verbatim"] is True
        assert os.path.isfile(rec)
    leg("L1 advance happy path (verbatim swap, fields preserved)", l1)

    # L2 idempotent no-op: content unchanged -> no --advance, keys stay canonical
    def l2():
        rc, sp, _, _hb = upd(new_ev, advance=False,
                        state={**base_state, DEC_KEY: TRUE_DEC, ORD_KEY: TRUE_ORD})
        assert rc == 0, "rc=%s" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == TRUE_DEC and st[ORD_KEY] == TRUE_ORD
        assert st[PROV_KEY]["advance"] is False
    leg("L2 no-op on unchanged keys (no --advance, canonical form kept)", l2)

    # L3 delta without --advance -> refusal, state untouched (r585)
    def l3():
        rc, sp, _, _hb = upd(new_ev, advance=False, state=dict(base_state))
        assert rc == 3, "rc=%s" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == OLD_DEC and st[ORD_KEY] == OLD_ORD
        assert PROV_KEY not in st, "refusal must not write provenance"
    leg("L3 delta without --advance refused, state untouched (r585)", l3)

    # L4 malformed candidate: 8-hex prefix (r811 splice-family write face)
    def l4():
        rc, sp, _, _hb = upd({"decisions_sha": "a3ea37bd", "orders_sha": TRUE_ORD},
                        advance=True, state=dict(base_state))
        assert rc == 3, "rc=%s" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == OLD_DEC, "state must be untouched"
    leg("L4 8-hex prefix candidate refused (r811 family)", l4)

    # L5 non-hex candidate
    def l5():
        rc, sp, _, _hb = upd({"decisions_sha": "z" * 40, "orders_sha": TRUE_ORD},
                        advance=True, state=dict(base_state))
        assert rc == 3, "rc=%s" % rc
        assert _load_json(sp)[DEC_KEY] == OLD_DEC
    leg("L5 non-hex candidate refused", l5)

    # L6 probe err -> mechanism fault
    def l6():
        rc, sp, _, _hb = upd({"err": "synthetic fault"}, advance=True,
                        state=dict(base_state))
        assert rc == 2, "rc=%s" % rc
        assert _load_json(sp)[DEC_KEY] == OLD_DEC
    leg("L6 probe err -> exit 2 mechanism fault", l6)

    # L7 missing evidence file -> mechanism fault
    def l7():
        mid, sp, pj, rec, _mj, _hb = mkfix(state=dict(base_state))
        os.unlink(pj)
        o = argparse.Namespace(state=sp, probe_json=pj, receipt=rec,
                               advance=True, probe_evidence=pj,
                               machine_json=_mj, heartbeat=_hb)
        rc = cmd_update(o)
        assert rc == 2, "rc=%s" % rc
    leg("L7 missing probe evidence -> exit 2", l7)

    # L8 state file missing -> mechanism fault
    def l8():
        rc, sp, _, _hb = upd(new_ev, advance=True, state=None, mkstate=False)
        assert rc == 2, "rc=%s" % rc
        assert not os.path.isfile(sp)
    leg("L8 missing state file -> exit 2 (never auto-create)", l8)

    # L9 machine path law: bm-c -> state-bm-c.json, bm-b -> state.json (r582)
    def l9():
        d = os.path.join(tmp, "fix_m")
        os.makedirs(d)
        json.dump({"machine_id": "bm-c"}, open(os.path.join(d, "machine.json"), "w"))
        _, sp = resolve_state_path(os.path.join(d, "machine.json"), d)
        assert sp.endswith("state-bm-c.json"), sp
        json.dump({"machine_id": "bm-b"}, open(os.path.join(d, "machine.json"), "w"))
        _, sp = resolve_state_path(os.path.join(d, "machine.json"), d)
        assert sp.endswith("state.json"), sp
    leg("L9 state path per machine_id (r582: bm-b=state.json)", l9)

    # L10 verify healthy -> 0
    def l10():
        mid, sp, pj, rec, _mj, _hb = mkfix(state={**base_state, DEC_KEY: TRUE_DEC,
                                        ORD_KEY: TRUE_ORD})
        json.dump(new_ev, open(pj, "w"))
        o = argparse.Namespace(state=sp, receipt=rec, probe_evidence=pj)
        assert cmd_verify(o) == 0
    leg("L10 verify healthy state -> 0", l10)

    # L11 verify: splice passes shape, fails full-string equality (r812 core)
    def l11():
        mid, sp, pj, rec, _mj, _hb = mkfix(state={**base_state, DEC_KEY: SPLICED,
                                        ORD_KEY: TRUE_ORD})
        json.dump(new_ev, open(pj, "w"))
        o = argparse.Namespace(state=sp, receipt=rec, probe_evidence=pj)
        assert cmd_verify(o) == 0, "splice is structurally valid 40-hex"
        out = _load_json(rec)
        assert out["probe_equality"][DEC_KEY]["equal"] is False, \
            "only full-string equality catches the splice"
    leg("L11 splice passes shape, fails equality (r812 lesson)", l11)

    # L12 splice heal via update: WHOLE string swapped, not the head
    def l12():
        rc, sp, _, _hb = upd(new_ev, advance=True,
                        state={**base_state, DEC_KEY: SPLICED, ORD_KEY: PHANTOM})
        assert rc == 0, "rc=%s" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == TRUE_DEC, "whole-string swap expected"
        assert st[ORD_KEY] == TRUE_ORD
    leg("L12 splice heal = whole-string swap (r812 heal law)", l12)

    # L13 case-normalized compare: uppercase stored == lowercase probe ->
    #     no --advance needed (r503/r711); write normalizes to canonical form
    def l13():
        rc, sp, _, _hb = upd(new_ev, advance=False,
                        state={**base_state, DEC_KEY: TRUE_DEC.upper(),
                               ORD_KEY: TRUE_ORD.upper()})
        assert rc == 0, "rc=%s (case-only delta must not demand --advance)" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == TRUE_DEC, \
            "verbatim write normalizes legacy case to canonical probe form"
    leg("L13 case normalization no false delta (r503/r711)", l13)

    # L14 tampered stored key -> verify structural refusal
    def l14():
        mid, sp, pj, rec, _mj, _hb = mkfix(state={**base_state, DEC_KEY: "short",
                                        ORD_KEY: TRUE_ORD})
        json.dump(new_ev, open(pj, "w"))
        o = argparse.Namespace(state=sp, receipt=rec, probe_evidence=pj)
        assert cmd_verify(o) == 3
    leg("L14 verify malformed stored key -> 3", l14)

    # L15 T22 probe machine-context law: probe resolves state-<id>.json from
    #     machine.json (bm-b -> state.json legacy); --state pointing at a
    #     wrong machine's file = hard mismatch fault (r954 defect face)
    def l15():
        import importlib.util
        os.environ.pop("D19_STATE", None)
        spec = importlib.util.spec_from_file_location("_d19_probe_t22", PROBE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        d = os.path.join(tmp, "fix_t22")
        os.makedirs(os.path.join(d, "fleet"))
        mj = os.path.join(d, "fleet", "machine.json")
        json.dump({"machine_id": "bm-a"}, open(mj, "w"))
        p, mid, err = mod.resolve_state(d)
        assert err is None and mid == "bm-a" and p.endswith("state-bm-a.json")
        json.dump({"machine_id": "bm-b"}, open(mj, "w"))
        p, mid, err = mod.resolve_state(d)
        assert err is None and p.endswith("state.json"), "bm-b legacy name"
        json.dump({"machine_id": "bm-a"}, open(mj, "w"))
        p, mid, err = mod.resolve_state(d, os.path.join(d, "state.json"))
        assert err and "mismatch" in err, "wrong-machine --state must fault"
        p, mid, err = mod.resolve_state(d, os.path.join(d, "state-bm-a.json"))
        assert err is None and p.endswith("state-bm-a.json"), "explicit ok"
    leg("L15 T22 probe reads state-<id>.json (machine derive + mismatch gate)",
        l15)

    # L16 D-20261024-03 triple shape gate
    def l16():
        assert validate_triple("3cfdec0c0a664129@67cd15d/203087")[0] is True
        assert validate_triple("3cfdec0c0a664129@67cd15d")[0] is False, "no /bytes"
        assert validate_triple("3cfdec0c0a66412@67cd15d/203087")[0] is False, \
            "sha must be 16 hex"
        assert validate_triple("3cfdec0c0a664129@67cd15/203087")[0] is False, \
            "commit must be 7/40"
        assert validate_triple("3cfdec0c0a664129@67cd15d/abc")[0] is False, \
            "bytes numeric"
        assert validate_triple(" 3cfdec0c0a664129@67cd15d/203087")[0] is False, \
            "whitespace"
    leg("T1 triple shape gate (D-20261024-03)", l16)

    # L17 probe-side triple comparison: commit+length first, digest second,
    #     legacy prefix fallback when no triple is stored
    def l17():
        import importlib.util
        spec = importlib.util.spec_from_file_location("_d19_probe_triple", PROBE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        t_now = "3cfdec0c0a664129@67cd15d/203087"
        assert mod._parse_triple(t_now) == ("3cfdec0c0a664129", "67cd15d", 203087)
        assert mod._parse_triple("not-a-triple") is None
        assert mod._watermark_changed("f" * 64, "0123456789", t_now, t_now) is False
        assert mod._watermark_changed(
            "f" * 64, "0123456789",
            "3cfdec0c0a664129@67cd15d/203088", t_now) is True, "bytes delta"
        assert mod._watermark_changed(
            "f" * 64, "0123456789",
            "3cfdec0c0a664129@aaaaaaa/203087", t_now) is True, "commit delta"
        assert mod._watermark_changed(
            "f" * 64, "0123456789", t_now, None) is True, "legacy fallback"
        assert mod._watermark_changed(
            "f" * 64, "f" * 10, t_now, None) is False, "legacy prefix equal"
    leg("T2 triple compare = commit+bytes first, digest second (probe)", l17)

    # L18 update writes triples verbatim + mirrors them into the heartbeat
    def l18():
        ev = dict(new_ev)
        ev["decisions_triple"] = "a3ea37bd70fd5acc@67cd15d/203087"
        ev["orders_triple"] = "e286f84287331c99@67cd15d/370071"
        rc, sp, rec, hb = upd(ev, advance=True, state=dict(base_state))
        assert rc == 0, "rc=%s" % rc
        st = _load_json(sp)
        assert st[TRIPLE_DEC_KEY] == ev["decisions_triple"]
        assert st[TRIPLE_ORD_KEY] == ev["orders_triple"]
        assert _load_json(hb)[TRIPLE_DEC_KEY] == ev["decisions_triple"], \
            "heartbeat mirror must carry the triple in the same update"
        assert st[DEC_KEY] == TRUE_DEC, "legacy key still verbatim"
    leg("T3 update writes triples + heartbeat mirror (same window)", l18)

    # L16/L17 r1045 relay face: captured child stdout/stderr must reach the
    # parent's streams (pass-through spawn is swallowed on this Win/Py3.14
    # host; loop read silence as 'hold' and missed a real orders delta)
    def l16():
        import io
        fake = type("R", (), {"stdout": '{"orders_changed": true}\n',
                              "stderr": ""})()
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            _relay_child_streams(fake)
        finally:
            sys.stdout = old
        assert buf.getvalue() == '{"orders_changed": true}\n', \
            "relay lost child stdout: %r" % buf.getvalue()
    leg("L16 r1045 relay reprints captured child stdout", l16)

    def l17():
        import io
        fake = type("R", (), {"stdout": b'{"ok": 1}\n\xff\xfe',
                              "stderr": b"warn\n"})()
        bufo, bufe = io.StringIO(), io.StringIO()
        so, se = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = bufo, bufe
        try:
            _relay_child_streams(fake)
        finally:
            sys.stdout, sys.stderr = so, se
        assert bufo.getvalue().startswith('{"ok": 1}'), "bytes stdout lost"
        assert bufe.getvalue() == "warn\n", "bytes stderr lost"
    leg("L17 r1045 relay decodes bytes face", l17)


    # L18/L19/L20 r1090 two-face law: heartbeat mirrors ride the same update,
    # read-back asserted; absent heartbeat = honest skip; zero fabrication
    def l18():
        rc, sp, rec, hb = upd(new_ev, advance=True, state=dict(base_state))
        assert rc == 0, "rc=%s" % rc
        h2 = _load_json(hb)
        assert h2["last_orders_sha"] == TRUE_ORD and h2["last_decisions_sha"] == TRUE_DEC, \
            "heartbeat mirrors not synced"
        assert h2["extra_foreign_key"] == "keep-me", "foreign key must be preserved"
        r = _load_json(rec)
        assert r["heartbeat_sync"]["readback_ok"] is True
        assert r["heartbeat_sync"]["synced"]["last_orders_sha"]["to"] == TRUE_ORD
    leg("L18 heartbeat mirrors synced in same update + read-back (r1052 in-tool)", l18)

    def l19():
        rc, sp, rec, hb = upd(new_ev, advance=True, state=dict(base_state),
                              mkheartbeat=False)
        assert rc == 0, "absent heartbeat must not fault: rc=%s" % rc
        assert not os.path.isfile(hb)
        r = _load_json(rec)
        assert "skipped" in (r["heartbeat_sync"]["note"] or ""), \
            "expected honest skip note, got %r" % r["heartbeat_sync"]
    leg("L19 absent heartbeat = honest skip (never a fault)", l19)

    def l20():
        st_min = {DEC_KEY: OLD_DEC, ORD_KEY: OLD_ORD, "round_no": 7,
                  "last_orders_read_at": "t0", "last_decisions_read_at": "t0",
                  "last_decisions_at": "t0"}  # NO last_orders_at/*_seen keys in state
        rc, sp, rec, hb = upd(new_ev, advance=True, state=st_min)
        assert rc == 0, "rc=%s" % rc
        h2 = _load_json(hb)
        assert h2["last_orders_seen"] == "stale", \
            "keys absent from state must not be fabricated/overwritten in heartbeat"
        s2 = _load_json(sp)
        assert h2["last_orders_read_at"] == s2["last_orders_read_at"], \
            "present state keys must mirror state post-write truth"
        r = _load_json(rec)
        assert "last_orders_seen" not in r["heartbeat_sync"]["synced"], \
            "absent-in-state key must not appear in synced map"
    leg("L20 zero fabrication: only state-present keys mirrored", l20)

    fails = [l for l in legs if not l[1]]
    for name, ok, why in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                           (" -- " + why) if why else ""))
    print("selftest: %d/%d PASS" % (len(legs) - len(fails), len(legs)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="D-19 watermark write-side guard")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("probe")

    p_u = sub.add_parser("update")
    p_u.add_argument("--advance", action="store_true",
                     help="acknowledge delta consumed THIS round (r585)")
    p_u.add_argument("--probe-json", default=None,
                     help="offline evidence injection (tests); live path "
                          "always runs the canonical probe fresh")
    p_u.add_argument("--state", default=None)
    p_u.add_argument("--machine-json", default=MACHINE_JSON)
    p_u.add_argument("--receipt", default=RECEIPT,
                     help="receipt evidence FILE PATH (not text; default "
                          "results/d19_watermark.json)")
    p_u.add_argument("--heartbeat", default=None,
                     help="heartbeat file for the two-face mirror write "
                          "(default fleet/machines/<machine_id>.json; r1090 "
                          "two-face law: state + heartbeat written in the "
                          "SAME update with read-back assertions)")

    p_v = sub.add_parser("verify")
    p_v.add_argument("--state", default=None)
    p_v.add_argument("--machine-json", default=MACHINE_JSON)
    p_v.add_argument("--probe-evidence", default=PROBE_OUT)
    p_v.add_argument("--receipt", default=RECEIPT)

    sub.add_parser("selftest")

    opts = ap.parse_args(argv)
    if not getattr(opts, "cmd", None):
        ap.print_help()
        return 2
    if opts.cmd == "probe":
        return cmd_probe(opts)
    if opts.cmd == "selftest":
        return selftest()
    # resolve machine-aware state path unless overridden
    if not opts.state:
        _, opts.state = resolve_state_path(opts.machine_json, ROOT)
    if opts.cmd == "update":
        return cmd_update(opts)
    return cmd_verify(opts)


if __name__ == "__main__":
    sys.exit(main())
