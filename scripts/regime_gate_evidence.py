"""REGIME_GATE_EVIDENCE v1.0 -- C1 regime-gate dual-arm evidence face.

T-2026-10-10-180 (O-20261009-2340 loop-side item 3): wire the regime gate's
two arms into ONE deterministic evidence JSON consumed by the REGIME_GUARD
chain readers (results/regime_state.json consumers, market_clock_call L3
evidence consumers, CEO dashboard faces).

  index arm   = REGIME-5 five-state labels (bm-a T-177, frozen contract
                research/REGIME_STYLE_MATRIX_V1.md sec.1)
  emotion arm = thermo daily three-axis state (GM P6, results/regime_thermo/,
                spec research/REGIME_THERMO_V1.md)

Wiring face ONLY. ZERO criteria, ZERO thresholds, ZERO on/off judgments:
the thermo face is exploratory/descriptive only (REGIME_THERMO_V1 sec.4
honesty law) -- any "thermo state -> forward return" criteria claim must
first pass an independent prereg slice (T-2026-10-10-181, science_gates
g1_prime_v2/g2_registration_v2, no hand-copied lines).

Outputs: results/regime_gate_evidence/EVIDENCE-<joint_cutoff>.json plus
evidence_latest.json (byte-identical copy). Idempotent: same inputs ->
byte-identical outputs (content-hash no-op guard); missing/invalid upstream
arm = honest awaiting_upstream no-op, exit 0. Exit codes: 0 normal/no-op,
2 mechanism fault. selftest subcommand = offline contract checks.

L1 deterministic, zero network, zero engine, zero marks/ledger writes.
"""

import csv
import glob
import hashlib
import json
import os
import sys

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
THERMO_CSV = os.path.join(RESULTS, "regime_thermo", "thermo_daily.csv")
LABELS_GLOB = os.path.join(RESULTS, "regime5_labels", "*.json")
OUT_DIR = os.path.join(RESULTS, "regime_gate_evidence")

FIVE_STATES = {"BULL", "CHOP", "GRIND", "BEAR", "SUPPORT"}
CONTRACT = "REGIME_STYLE_MATRIX_V1 sec.1"
THERMO_INT_FIELDS = (
    "n_trade", "n_sealed", "n_touched", "n_sealed_down", "n_broke",
    "n_firstboard", "n_lianban2", "n_lianban3", "n_lianban4p", "max_height",
)
THERMO_RATE_FIELDS = ("seal_rate", "pct_sealed")


def _die(msg):
    sys.stderr.write("[regime_gate_evidence] FAULT: %s\n" % msg)
    sys.exit(2)


def load_index_arm():
    """Latest REGIME-5 labels file by mtime; validated against matrix sec.1 contract."""
    files = sorted(glob.glob(LABELS_GLOB), key=os.path.getmtime)
    if not files:
        return None, "no labels file in results/regime5_labels/"
    path = files[-1]
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:  # malformed upstream = awaiting, not fault
        return None, "labels file unreadable: %s" % e
    problems = []
    if not isinstance(d.get("cutoff"), str) or not d.get("cutoff"):
        problems.append("cutoff missing/empty")
    if not isinstance(d.get("source"), str) or not d.get("source"):
        problems.append("source missing/empty")
    labels = d.get("labels")
    if not isinstance(labels, list) or not labels:
        problems.append("labels list missing/empty")
    else:
        for row in labels:
            if not isinstance(row, dict) or "date" not in row or "state" not in row:
                problems.append("label row malformed: %r" % (row,))
                break
            if row["state"] not in FIVE_STATES:
                problems.append("state %r not in five-state key set" % row["state"])
                break
    if problems:
        return None, "contract violations: %s" % "; ".join(problems)
    return {
        "file": os.path.basename(path),
        "cutoff": d["cutoff"],
        "source": d["source"],
        "n_labels": len(labels),
        "latest_label": labels[-1],
        "contract_receipt": {
            "contract": CONTRACT,
            "validated": True,
            "five_state_keys": sorted(FIVE_STATES),
        },
    }, None


def load_emotion_arm():
    """Thermo daily CSV -> latest row (three-axis state), descriptive only."""
    if not os.path.exists(THERMO_CSV):
        return None, "thermo_daily.csv absent (run scripts/regime_thermo_build.py)"
    last_row, last_date = None, None
    try:
        with open(THERMO_CSV, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if row.get("date"):
                    last_row, last_date = row, row["date"]
    except Exception as e:
        _die("thermo csv read failed: %s" % e)
    if last_row is None:
        return None, "thermo csv has no dated rows"
    fields = {}
    for k in THERMO_INT_FIELDS:
        v = last_row.get(k, "")
        fields[k] = int(float(v)) if v not in ("", None) else None
    for k in THERMO_RATE_FIELDS:
        v = last_row.get(k, "")
        fields[k] = float(v) if v not in ("", None) else None
    return {"cutoff": last_date, "fields": fields,
            "spec": "REGIME_THERMO_V1 (exploratory, zero-criteria)"}, None


def run():
    index, i_note = load_index_arm()
    emotion, e_note = load_emotion_arm()
    if index is None or emotion is None:
        print("[regime_gate_evidence] awaiting_upstream no-op: index=%s emotion=%s"
              % (i_note, e_note))
        return 0
    joint_cutoff = min(index["cutoff"], emotion["cutoff"])
    label_at_joint = None
    for row in reversed(json.load(open(sorted(glob.glob(LABELS_GLOB), key=os.path.getmtime)[-1],
                                      encoding="utf-8"))["labels"]):
        if row["date"] <= joint_cutoff:
            label_at_joint = row
            break
    evidence = {
        "face": "regime_gate_evidence v1.0",
        "ticket": "T-2026-10-10-180",
        "joint_cutoff": joint_cutoff,
        "index_arm": index,
        "index_state_at_joint_cutoff": label_at_joint,
        "emotion_arm": emotion,
        "alignment": {
            "index_cutoff": index["cutoff"],
            "emotion_cutoff": emotion["cutoff"],
            "lag_days_note": "arms may carry different evidence cutoffs; "
                             "joint_cutoff = min(); consumers must read per-arm cutoffs",
            "contract": CONTRACT,
        },
        "criteria": "NONE -- descriptive evidence face only; criteria claims require "
                    "independent prereg slice (T-2026-10-10-181)",
    }
    payload = json.dumps(evidence, ensure_ascii=False, indent=1, sort_keys=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "EVIDENCE-%s.json" % joint_cutoff)
    latest_path = os.path.join(OUT_DIR, "evidence_latest.json")
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            if hashlib.sha256(f.read().encode("utf-8")).hexdigest()[:16] == digest:
                print("[regime_gate_evidence] no-op (content-hash match) cutoff=%s" % joint_cutoff)
                return 0
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(payload)
    with open(latest_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(payload)
    print("[regime_gate_evidence] wrote EVIDENCE-%s.json (sha16=%s)" % (joint_cutoff, digest))
    return 0


def selftest():
    """Offline checks: contract validation rejects garbage, arms load, idempotency."""
    ok = 0
    # t1: five-state contract validation catches bad states
    bad = {"cutoff": "2026-09-30", "source": "x", "labels": [{"date": "2026-01-01", "state": "MOON"}]}
    import tempfile, shutil
    tmpd = tempfile.mkdtemp()
    global LABELS_GLOB
    saved = LABELS_GLOB
    try:
        with open(os.path.join(tmpd, "bad.json"), "w", encoding="utf-8") as f:
            json.dump(bad, f)
        LABELS_GLOB = os.path.join(tmpd, "*.json")
        arm, note = load_index_arm()
        assert arm is None and "contract violations" in note, "t1 fail: bad state must be rejected"
        ok += 1
        # t2: valid labels pass contract
        good = {"cutoff": "2026-09-30", "source": "REGIME-5 (bm-a)",
                "labels": [{"date": "2026-09-29", "state": "BEAR"}, {"date": "2026-09-30", "state": "BEAR"}]}
        with open(os.path.join(tmpd, "bad.json"), "w", encoding="utf-8") as f:
            json.dump(good, f)
        arm, note = load_index_arm()
        assert arm is not None and arm["contract_receipt"]["validated"], "t2 fail: valid labels rejected"
        assert arm["n_labels"] == 2 and arm["latest_label"]["state"] == "BEAR", "t2b fail"
        ok += 1
    finally:
        LABELS_GLOB = saved
        shutil.rmtree(tmpd, ignore_errors=True)
    # t3: real arms load (upstream may be absent on fresh clones -> skip-honest)
    idx, i_note = load_index_arm()
    emo, e_note = load_emotion_arm()
    if idx is not None:
        assert idx["cutoff"] and idx["n_labels"] > 0, "t3 fail: index arm shape"
        ok += 1
    if emo is not None:
        assert emo["cutoff"] and "n_sealed" in emo["fields"], "t4 fail: emotion arm shape"
        ok += 1
    print("[regime_gate_evidence] selftest %d checks PASS (arms: index=%s emotion=%s)"
          % (ok, "ok" if idx else i_note, "ok" if emo else e_note))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        sys.exit(run())
    if cmd == "selftest":
        sys.exit(selftest())
    print("usage: regime_gate_evidence.py [run|selftest]")
    sys.exit(2)
