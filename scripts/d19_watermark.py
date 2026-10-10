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
PROBE_OUT = os.path.join(ROOT, "results", "_r686bmb_d19_check.json")
MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
RECEIPT = os.path.join(ROOT, "results", "d19_watermark.json")

DEC_KEY = "last_decisions_sha"
ORD_KEY = "last_orders_sha"
READ_KEYS = ("last_decisions_read_at", "last_orders_read_at")
PROV_KEY = "d19_watermark_guard"
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
        # single-source verbatim full-string write (r812)
        st[DEC_KEY] = cand_dec
        st[ORD_KEY] = cand_ord
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
        if st2.get(DEC_KEY) != cand_dec or st2.get(ORD_KEY) != cand_ord:
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
        _atomic_json_write(receipt, opts.receipt, True)
        print("%s: dec=%s ord=%s (read-back full-string equality OK)"
              % (receipt["action"].upper(), cand_dec, cand_ord))
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


def cmd_probe(opts):
    # T22: inject the machine-aware state path so the probe reads
    # state-<id>.json, never a legacy/wrong-machine watermark.
    _, state = resolve_state_path(MACHINE_JSON, ROOT)
    r = subprocess.run([sys.executable, PROBE, "--state", state], cwd=ROOT)
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

    def mkfix(state=None, machine="bm-b", mkstate=True):
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
        return mid, sp, pj, rec

    def upd(ev_dict, advance=False, state=None, machine="bm-b", mkstate=True):
        mid, sp, pj, rec = mkfix(state=state, machine=machine, mkstate=mkstate)
        if ev_dict is not None:
            json.dump(ev_dict, open(pj, "w"))
        o = argparse.Namespace(state=sp, probe_json=pj, receipt=rec,
                               advance=advance, probe_evidence=pj)
        return cmd_update(o), sp, rec

    base_state = {DEC_KEY: OLD_DEC, ORD_KEY: OLD_ORD, "round_no": 999,
                  "note": "CJK-note-\u6c34\u4f4d", "other": [1, 2, 3]}
    new_ev = {"decisions_sha": TRUE_DEC, "orders_sha": TRUE_ORD,
              "decisions_method": "sha1", "orders_method": "sha1",
              "err": None}

    # L1 advance happy path: whole-string swap, fields preserved
    def l1():
        rc, sp, rec = upd(new_ev, advance=True, state=dict(base_state))
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
        rc, sp, _ = upd(new_ev, advance=False,
                        state={**base_state, DEC_KEY: TRUE_DEC, ORD_KEY: TRUE_ORD})
        assert rc == 0, "rc=%s" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == TRUE_DEC and st[ORD_KEY] == TRUE_ORD
        assert st[PROV_KEY]["advance"] is False
    leg("L2 no-op on unchanged keys (no --advance, canonical form kept)", l2)

    # L3 delta without --advance -> refusal, state untouched (r585)
    def l3():
        rc, sp, _ = upd(new_ev, advance=False, state=dict(base_state))
        assert rc == 3, "rc=%s" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == OLD_DEC and st[ORD_KEY] == OLD_ORD
        assert PROV_KEY not in st, "refusal must not write provenance"
    leg("L3 delta without --advance refused, state untouched (r585)", l3)

    # L4 malformed candidate: 8-hex prefix (r811 splice-family write face)
    def l4():
        rc, sp, _ = upd({"decisions_sha": "a3ea37bd", "orders_sha": TRUE_ORD},
                        advance=True, state=dict(base_state))
        assert rc == 3, "rc=%s" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == OLD_DEC, "state must be untouched"
    leg("L4 8-hex prefix candidate refused (r811 family)", l4)

    # L5 non-hex candidate
    def l5():
        rc, sp, _ = upd({"decisions_sha": "z" * 40, "orders_sha": TRUE_ORD},
                        advance=True, state=dict(base_state))
        assert rc == 3, "rc=%s" % rc
        assert _load_json(sp)[DEC_KEY] == OLD_DEC
    leg("L5 non-hex candidate refused", l5)

    # L6 probe err -> mechanism fault
    def l6():
        rc, sp, _ = upd({"err": "synthetic fault"}, advance=True,
                        state=dict(base_state))
        assert rc == 2, "rc=%s" % rc
        assert _load_json(sp)[DEC_KEY] == OLD_DEC
    leg("L6 probe err -> exit 2 mechanism fault", l6)

    # L7 missing evidence file -> mechanism fault
    def l7():
        mid, sp, pj, rec = mkfix(state=dict(base_state))
        os.unlink(pj)
        o = argparse.Namespace(state=sp, probe_json=pj, receipt=rec,
                               advance=True, probe_evidence=pj)
        rc = cmd_update(o)
        assert rc == 2, "rc=%s" % rc
    leg("L7 missing probe evidence -> exit 2", l7)

    # L8 state file missing -> mechanism fault
    def l8():
        rc, sp, _ = upd(new_ev, advance=True, state=None, mkstate=False)
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
        mid, sp, pj, rec = mkfix(state={**base_state, DEC_KEY: TRUE_DEC,
                                        ORD_KEY: TRUE_ORD})
        json.dump(new_ev, open(pj, "w"))
        o = argparse.Namespace(state=sp, receipt=rec, probe_evidence=pj)
        assert cmd_verify(o) == 0
    leg("L10 verify healthy state -> 0", l10)

    # L11 verify: splice passes shape, fails full-string equality (r812 core)
    def l11():
        mid, sp, pj, rec = mkfix(state={**base_state, DEC_KEY: SPLICED,
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
        rc, sp, _ = upd(new_ev, advance=True,
                        state={**base_state, DEC_KEY: SPLICED, ORD_KEY: PHANTOM})
        assert rc == 0, "rc=%s" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == TRUE_DEC, "whole-string swap expected"
        assert st[ORD_KEY] == TRUE_ORD
    leg("L12 splice heal = whole-string swap (r812 heal law)", l12)

    # L13 case-normalized compare: uppercase stored == lowercase probe ->
    #     no --advance needed (r503/r711); write normalizes to canonical form
    def l13():
        rc, sp, _ = upd(new_ev, advance=False,
                        state={**base_state, DEC_KEY: TRUE_DEC.upper(),
                               ORD_KEY: TRUE_ORD.upper()})
        assert rc == 0, "rc=%s (case-only delta must not demand --advance)" % rc
        st = _load_json(sp)
        assert st[DEC_KEY] == TRUE_DEC, \
            "verbatim write normalizes legacy case to canonical probe form"
    leg("L13 case normalization no false delta (r503/r711)", l13)

    # L14 tampered stored key -> verify structural refusal
    def l14():
        mid, sp, pj, rec = mkfix(state={**base_state, DEC_KEY: "short",
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
    p_u.add_argument("--receipt", default=RECEIPT)

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
