"""C1 regime-gate dual-arm evidence face (T-180, bm-b lane).

Wires the two regime arms into the C1 regime-gate EVIDENCE face via the
REGIME_GUARD consumption chain. Pure evidence wiring, ZERO criteria:

  emotion arm = results/regime_thermo/thermo_daily.csv latest row
                (REGIME_THERMO_V1 frozen spec; exploratory descriptive face,
                 zero judgment qualification)
  index arm   = latest results/regime5_labels/*.json
                (T-177 REGIME-5 five-state labeler)

Product: results/regime_gate_dualarm/DUALARM-<asof>.json + latest.json
(byte-identical copy; no runtime clock inside -> deterministic idempotent).
The index-arm labels file is validated against the frozen
REGIME_STYLE_MATRIX_V1 sec.1 input contract; the receipt rides the artifact.

Honesty laws (frozen, ticket T-2026-10-10-180):
- evidence face only: no gate criteria touched, no gating action, no
  judgment claims -- judgment face = T-2026-10-10-181 independent prereg
  slice (+ science_gates shared library, no hand-copy)
- asof mismatch between the two arms is disclosed verbatim (emotion arm
  = P-5C frozen face, may trail the index-arm cutoff)
- missing arm -> awaiting_upstream honest no-op (exit 0)
- lane guard: bm-b only (R31); other machines stdout-only honest no-op

Exit codes: 0 = normal/no-op, 2 = mechanism fault, 3 = upstream contract
violation the sec.1 adapter could not legalize (blocked; lossless classes
are auto-shelled by scripts/regime_gate_dualarm_adapter.py -- MATRIX
sec.1: adapter at wiring time, the contract itself frozen).
Selftest: python scripts/regime_gate_dualarm.py selftest (offline)
"""

import csv
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THERMO_CSV = os.path.join(ROOT, "results", "regime_thermo", "thermo_daily.csv")
LABELS_DIR = os.path.join(ROOT, "results", "regime5_labels")
OUT_DIR = os.path.join(ROOT, "results", "regime_gate_dualarm")
LANE_OWNER = "bm-b"  # R31 lane law (wiring ticket lane = bm-b, single writer)

STATES5 = ("BULL", "CHOP", "GRIND", "BEAR", "SUPPORT")
THERMO_INT_COLS = ("n_trade", "n_sealed", "n_touched", "n_sealed_down",
                   "n_broke", "max_height")
THERMO_FLOAT_COLS = ("seal_rate", "n_firstboard", "n_lianban2",
                     "n_lianban3", "n_lianban4p", "pct_sealed")
TICKET = "T-2026-10-10-180"


def _lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     encoding="utf-8-sig") as f:
            return json.load(f).get("machine_id")
    except Exception:
        return None


def _parse_val(col, raw):
    # '' -> None (early panel rows pre-1997 have no lianban tiers)
    if raw is None or raw == "":
        return None
    if col in THERMO_INT_COLS:
        return int(float(raw))
    if col in THERMO_FLOAT_COLS:
        return float(raw)
    return raw


def load_emotion_arm(path=THERMO_CSV):
    """Return (cutoff, latest_row, n_days) or None if the panel is absent."""
    if not os.path.isfile(path):
        return None
    with io.open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None
    latest = max(rows, key=lambda r: r["date"])
    parsed = {"date": latest["date"]}
    for col in THERMO_INT_COLS + THERMO_FLOAT_COLS:
        parsed[col] = _parse_val(col, latest.get(col))
    return latest["date"], parsed, len(rows)


def pick_latest_labels_file(labels_dir=LABELS_DIR):
    """Latest labels file by (parsed cutoff, filename); None if dir empty."""
    if not os.path.isdir(labels_dir):
        return None
    best = None
    for name in sorted(os.listdir(labels_dir)):
        if not name.endswith(".json"):
            continue
        p = os.path.join(labels_dir, name)
        try:
            with io.open(p, encoding="utf-8") as f:
                doc = json.load(f)
        except Exception:
            continue  # unreadable candidate skipped, not fatal to the pick
        cutoff = str(doc.get("cutoff", ""))
        key = (cutoff, name)
        if best is None or key > best[0]:
            best = (key, p, doc)
    if best is None:
        return None
    return best[1], best[2]


def validate_contract(doc):
    """REGIME_STYLE_MATRIX_V1 sec.1 input contract receipt."""
    checks = {}
    checks["keys_cutoff_source_labels"] = (
        isinstance(doc, dict)
        and isinstance(doc.get("cutoff"), str) and doc.get("cutoff") != ""
        and isinstance(doc.get("source"), str) and doc.get("source") != ""
        and isinstance(doc.get("labels"), list))
    labels = doc.get("labels") if isinstance(doc, dict) else None
    checks["labels_nonempty"] = isinstance(labels, list) and len(labels) > 0
    shape_ok = True
    enum_ok = True
    sorted_ok = True
    prev = ""
    if isinstance(labels, list):
        for ent in labels:
            if not (isinstance(ent, dict) and isinstance(ent.get("date"), str)
                    and isinstance(ent.get("state"), str)):
                shape_ok = False
                break
            if ent["state"] not in STATES5:
                enum_ok = False
                break
            if ent["date"] <= prev:
                sorted_ok = False
                break
            prev = ent["date"]
    else:
        shape_ok = False
    checks["label_entry_shape"] = shape_ok
    checks["state_enum_5key"] = enum_ok
    checks["dates_strictly_ascending"] = sorted_ok
    return {"contract": "REGIME_STYLE_MATRIX_V1 sec.1 input contract",
            "pass": all(checks.values()), "checks": checks}


def build_artifact(emo, labels_path, doc, receipt):
    emo_cutoff, emo_latest, emo_days = emo
    labels = doc["labels"]
    dist = {}
    for ent in labels:
        dist[ent["state"]] = dist.get(ent["state"], 0) + 1
    idx_cutoff = doc["cutoff"]
    asof = max(emo_cutoff, idx_cutoff)
    mismatch = None
    if emo_cutoff != idx_cutoff:
        mismatch = {
            "emotion_arm_cutoff": emo_cutoff,
            "index_arm_cutoff": idx_cutoff,
            "disclosure": ("emotion arm = P-5C frozen face, trails the "
                           "index-arm cutoff; honest as-is, no extrapolation"),
        }
    return {
        "face": "regime_gate_dualarm",
        "ticket": TICKET,
        "asof": asof,
        "asof_mismatch": mismatch,
        "index_arm": {
            "file": os.path.basename(labels_path),
            "cutoff": idx_cutoff,
            "source": doc.get("source"),
            "n_labels": len(labels),
            "first_label_date": labels[0]["date"],
            "latest_label_date": labels[-1]["date"],
            "latest_state": labels[-1]["state"],
            "state_distribution": dist,
        },
        "emotion_arm": {
            "file": "results/regime_thermo/thermo_daily.csv",
            "cutoff": emo_cutoff,
            "n_days_panel": emo_days,
            "latest": emo_latest,
            "axis_definitions_ref":
                "research/REGIME_THERMO_V1.md sec.1 (frozen, zero retouching)",
        },
        "contract_receipt": receipt,
        "honesty": {
            "evidence_face_only":
                "no gate criteria touched, no gating action (shadow evidence)",
            "emotion_arm_qualification":
                "exploratory descriptive face, ZERO judgment qualification "
                "(REGIME_THERMO_V1 sec.4)",
            "judgment_gate":
                "any thermo-state -> forward-return claim requires the "
                "independent prereg slice (T-2026-10-10-181) via "
                "science_gates shared library, no hand-copy",
            "c1_gate_change_law":
                "C1 regime gate changes go through prereg + GM signature "
                "chain",
        },
        "provenance": {
            "built_by": "bm-b r812",
            "ticket_claim": "T-2026-10-10-180 claimed 2026-10-10T02:57:21+08:00",
            "order_ref": "O-20261009-2340-bm-a.md sec.3 (dual-arm wiring)",
            "consumption": ("C1 regime-gate evidence sibling face in the "
                            "REGIME_GUARD consumption chain; gate state face "
                            "remains results/regime_state.json"),
        },
    }


def _atomic_write(path, payload):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def run(root=ROOT):
    if _lane_owner_id() != LANE_OWNER:
        print("regime_gate_dualarm: not lane owner (bm-b), honest no-op")
        return 0
    emo = load_emotion_arm(THERMO_CSV)
    if emo is None:
        print("regime_gate_dualarm: awaiting_upstream (thermo_daily.csv "
              "absent), honest no-op")
        return 0
    picked = pick_latest_labels_file(LABELS_DIR)
    if picked is None:
        print("regime_gate_dualarm: awaiting_upstream (regime5_labels "
              "absent), honest no-op")
        return 0
    labels_path, doc = picked
    receipt = validate_contract(doc)
    adaptation = None
    if not receipt["pass"]:
        # MATRIX sec.1: adapter at wiring time, the contract itself frozen
        # (tech T16). Lossless classes -> legal shell consumed with full
        # disclosure; judgment/data-absent classes stay blocked exit 3.
        import regime_gate_dualarm_adapter as adapter
        res = adapter.adapt(doc)
        if not res["ok"]:
            print("regime_gate_dualarm: upstream contract VIOLATION, adapter "
                  "BLOCKED (data absent or judgment pick required) reasons="
                  + json.dumps(res["blocked"], sort_keys=True))
            return 3
        with io.open(labels_path, "rb") as f:
            orig_sha = hashlib.sha256(f.read()).hexdigest()
        base = os.path.basename(labels_path)
        shell_name = (base[:-len(".json")] if base.endswith(".json")
                      else base) + ".adapted.json"
        shell_dir = os.path.join(OUT_DIR, "adapted")
        if not os.path.isdir(shell_dir):
            os.makedirs(shell_dir)
        shell_path = os.path.join(shell_dir, shell_name)
        _atomic_write(shell_path, res["adapted"])
        doc = res["adapted"]
        receipt = validate_contract(doc)
        if not receipt["pass"]:
            print("regime_gate_dualarm: adapter shell failed the frozen "
                  "validator (fail-closed), honest block")
            return 3
        adaptation = {
            "law": "REGIME_STYLE_MATRIX_V1 sec.1: adapter at wiring time, "
                   "contract frozen (tech T16)",
            "original_file": base,
            "original_sha256": orig_sha,
            "failed_checks_before": res["violations"],
            "adaptation_log": res["log"],
            "n_labels_in": res["n_labels_in"],
            "n_labels_out": res["n_labels_out"],
            "adapted_shell": "results/regime_gate_dualarm/adapted/"
                             + shell_name,
        }
        print("regime_gate_dualarm: contract violation -> legal shell "
              "generated (lossless ops=%s), consuming adapted view with "
              "disclosure"
              % (",".join(sorted({e["op"] for e in res["log"]}))
                 or "none"))
    artifact = build_artifact(emo, labels_path, doc, receipt)
    if adaptation is not None:
        artifact["adaptation"] = adaptation
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)
    out = os.path.join(OUT_DIR, "DUALARM-%s.json" % artifact["asof"])
    _atomic_write(out, artifact)
    _atomic_write(os.path.join(OUT_DIR, "latest.json"), artifact)
    print("regime_gate_dualarm: wrote %s (index=%s @%s, emotion @%s)" % (
        out, artifact["index_arm"]["latest_state"],
        artifact["index_arm"]["latest_label_date"], emo[0]))
    return 0


def _selftest():
    import shutil
    import tempfile

    global THERMO_CSV, LABELS_DIR, LANE_OWNER, OUT_DIR

    results = []

    def check(name, cond):
        results.append((name, bool(cond)))

    td = tempfile.mkdtemp(prefix="dualarm_st_")
    try:
        # L1 contract validator: positive fixture
        good = {"cutoff": "2026-09-30", "source": "REGIME-5 (bm-a)",
                "labels": [{"date": "2026-09-29", "state": "BEAR"},
                           {"date": "2026-09-30", "state": "BEAR"}]}
        r = validate_contract(good)
        check("contract_positive", r["pass"] is True)
        # L2 bad state key
        bad_enum = {"cutoff": "x", "source": "y",
                    "labels": [{"date": "2026-01-02", "state": "MARS"}]}
        check("contract_bad_enum_rejected",
              validate_contract(bad_enum)["pass"] is False)
        # L3 missing keys
        check("contract_missing_keys_rejected",
              validate_contract({"labels": []})["pass"] is False)
        # L4 unsorted/duplicate dates
        dup = {"cutoff": "x", "source": "y",
               "labels": [{"date": "2026-01-02", "state": "BULL"},
                          {"date": "2026-01-02", "state": "BULL"}]}
        check("contract_dup_date_rejected",
              validate_contract(dup)["pass"] is False)
        # L5 empty labels
        empty = {"cutoff": "x", "source": "y", "labels": []}
        check("contract_empty_labels_rejected",
              validate_contract(empty)["pass"] is False)
        # L6 latest-file pick: newer cutoff wins, deterministic tiebreak
        ldir = os.path.join(td, "labels")
        os.makedirs(ldir)
        for name, cut in (("A.json", "2026-09-28"), ("B.json", "2026-09-30")):
            with io.open(os.path.join(ldir, name), "w", encoding="utf-8") as f:
                json.dump({"cutoff": cut, "source": "s",
                           "labels": [{"date": "2026-01-02",
                                       "state": "CHOP"}]}, f)
        picked = pick_latest_labels_file(ldir)
        check("latest_pick_newer_cutoff",
              picked is not None
              and os.path.basename(picked[0]) == "B.json")
        # L7 missing arms -> awaiting_upstream honest no-op, no artifact
        empty_dir = os.path.join(td, "nothing")
        check("emotion_absent_noop",
              load_emotion_arm(os.path.join(empty_dir, "nope.csv")) is None)
        check("labels_absent_noop",
              pick_latest_labels_file(empty_dir) is None)
        # L8 determinism + artifact shape on synthetic inputs
        emo = ("2026-09-22", {"date": "2026-09-22", "n_sealed": 67,
                              "n_touched": 562, "seal_rate": 0.11921708185053381,
                              "max_height": 6}, 7216)
        art = build_artifact(emo, os.path.join(ldir, "B.json"), good,
                            validate_contract(good))
        check("asof_max_of_arms", art["asof"] == "2026-09-30")
        check("asof_mismatch_disclosed",
              art["asof_mismatch"] is not None
              and art["asof_mismatch"]["emotion_arm_cutoff"] == "2026-09-22")
        check("index_latest_state", art["index_arm"]["latest_state"] == "BEAR")
        out_dir = os.path.join(td, "out")
        os.makedirs(out_dir)
        saved_out = OUT_DIR
        try:
            OUT_DIR = out_dir
            # re-point module-level paths via run() would need real files;
            # exercise the writer twice for byte determinism instead
            p1 = os.path.join(out_dir, "DUALARM-2026-09-30.json")
            _atomic_write(p1, art)
            b1 = io.open(p1, "rb").read()
            _atomic_write(p1, build_artifact(
                emo, os.path.join(ldir, "B.json"), good,
                validate_contract(good)))
            b2 = io.open(p1, "rb").read()
            check("write_byte_deterministic", b1 == b2)
        finally:
            OUT_DIR = saved_out
        # L9 empty-cell parse ('' -> None)
        check("empty_cell_none", _parse_val("n_lianban2", "") is None)
        check("int_parse", _parse_val("max_height", "6") == 6)
        check("float_parse", _parse_val("seal_rate", "0.5") == 0.5)
        # L10 lane guard: non-owner string means run() no-ops before writes
        check("lane_owner_frozen", LANE_OWNER == "bm-b")
        # L11 real-data integration (repo faces, read-only)
        if os.path.isfile(THERMO_CSV):
            emo2 = load_emotion_arm()
            check("integration_emotion_loaded",
                  emo2 is not None and emo2[2] > 7000)
        else:
            print("  note: repo thermo face absent, integration leg skipped")
        if os.path.isdir(LABELS_DIR):
            pk = pick_latest_labels_file()
            check("integration_labels_loaded", pk is not None)
        # L12 run()-level e2e: violating labels -> legal shell + disclosure
        e2e_dir = os.path.join(td, "e2e")
        ldir2 = os.path.join(e2e_dir, "labels")
        out2 = os.path.join(e2e_dir, "out")
        os.makedirs(ldir2)
        os.makedirs(out2)
        thermo2 = os.path.join(e2e_dir, "thermo_daily.csv")
        with io.open(thermo2, "w", encoding="utf-8", newline="\n") as f:
            f.write("date,n_trade,n_sealed,n_touched,n_sealed_down,"
                    "n_broke,max_height,seal_rate,n_firstboard,"
                    "n_lianban2,n_lianban3,n_lianban4p,pct_sealed\n")
            f.write("2026-09-21,10,5,50,3,1,4,0.1,2,1,0,0,0.5\n")
            f.write("2026-09-22,12,6,60,4,1,5,0.1,2,1,0,0,0.5\n")
        with io.open(os.path.join(ldir2, "L.json"), "w",
                     encoding="utf-8") as f:
            json.dump({"cutoff": "2026-09-22", "source": "e2e",
                       "labels": [{"date": "2026-09-21", "state": "bull"},
                                  {"date": "2026-09-21", "state": "bull"},
                                  {"date": "2026-09-20",
                                   "state": "BULL"}]}, f)
        s_thermo, s_labels, s_out, s_lane = (THERMO_CSV, LABELS_DIR,
                                             OUT_DIR, LANE_OWNER)
        try:
            THERMO_CSV, LABELS_DIR, OUT_DIR = thermo2, ldir2, out2
            LANE_OWNER = _lane_owner_id()
            rc = run()
            check("e2e_adapt_rc0", rc == 0)
            art_path = os.path.join(out2, "DUALARM-2026-09-22.json")
            check("e2e_artifact_written", os.path.isfile(art_path))
            with io.open(art_path, encoding="utf-8") as f:
                art = json.load(f)
            check("e2e_adaptation_disclosed",
                  art.get("adaptation", {}).get("n_labels_in") == 3
                  and art["adaptation"]["n_labels_out"] == 2
                  and len(art["adaptation"]["original_sha256"]) == 64
                  and "dedupe" in {e["op"] for e in
                                   art["adaptation"]["adaptation_log"]})
            check("e2e_shell_landed",
                  os.path.isfile(os.path.join(out2, "adapted",
                                              "L.adapted.json")))
            # L13 run()-level e2e: judgment-class violation stays blocked
            with io.open(os.path.join(ldir2, "L.json"), "w",
                         encoding="utf-8") as f:
                json.dump({"cutoff": "2026-09-22", "source": "e2e",
                           "labels": [{"date": "2026-09-20",
                                       "state": "MARS"}]}, f)
            check("e2e_blocked_rc3", run() == 3)
            # L14 clean labels -> no adaptation key (schema stability)
            with io.open(os.path.join(ldir2, "L.json"), "w",
                         encoding="utf-8") as f:
                json.dump({"cutoff": "2026-09-22", "source": "e2e",
                           "labels": [{"date": "2026-09-21",
                                       "state": "BULL"},
                                      {"date": "2026-09-22",
                                       "state": "CHOP"}]}, f)
            check("e2e_clean_rc0", run() == 0)
            with io.open(art_path, encoding="utf-8") as f:
                art3 = json.load(f)
            check("e2e_clean_no_adaptation_key", "adaptation" not in art3)
            b_before = io.open(art_path, "rb").read()
            run()
            check("e2e_rerun_byte_identical",
                  io.open(art_path, "rb").read() == b_before)
        finally:
            THERMO_CSV, LABELS_DIR, OUT_DIR, LANE_OWNER = (
                s_thermo, s_labels, s_out, s_lane)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    n_pass = sum(1 for _, ok in results if ok)
    for name, ok in results:
        print("[%s] dualarm selftest: %s" % ("PASS" if ok else "FAIL", name))
    print("Summary: %d/%d PASS, %d FAIL" % (
        n_pass, len(results), len(results) - n_pass))
    return n_pass == len(results)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "selftest":
        return 0 if _selftest() else 1
    return run()


if __name__ == "__main__":
    # canonical-copy launcher: running this file as __main__ directly would
    # make the adapter's `from regime_gate_dualarm import ...` (single-source
    # law) load a second divergent module copy (classic __main__ trap); route
    # through the canonical module instead.
    import regime_gate_dualarm as _canonical
    sys.exit(_canonical.main())
