"""E298 -- every published control, and whether it says which panel it re-derived on.

E243 shipped a replay control that re-derived over the live panel and read its own vintage as a
reproduction failure (r1316). The repair added four fields to that one block
(``window_used`` / ``window_source`` / ``live_panel_last`` / ``sessions_past_the_pinned_window``),
which is a fix to ONE face. What the family has never measured is how many published controls are
in the same position: a control that recomputes a number without saying whether the data it
recomputed on is the vintage the face was published on or whatever sits on disk now.

This face is a census, not a new experiment. It reads the published evidence files under
``results/state_tilt/`` and asks of each control block:

  * KIND   -- is it an identity check (re-derives from the face's OWN published records, so a
              later panel cannot move it) or a replay of an upstream face (so the vintage matters)?
  * BASIS  -- does the block declare which window/vintage it re-derived on?
                pinned_upstream  a window_source that names the reference face's window
                pinned_literal   the block carries its own window/pin/vintage/cutoff field
                live_declared    it names the live panel AND how far past the window it went
                undeclared       nothing -- the panel it used is not recoverable from the face

DECISION RULE, declared before a number is read:
  a replay control with a ``live_declared`` or ``pinned_*`` basis is measured as SAFE;
  a replay control with ``undeclared`` basis is published as UNMEASURABLE, never defaulted to
  either safe or broken -- "cannot tell which panel it used" is not "used the wrong panel";
  an identity control is never graded on basis at all, because it cannot be moved by a vintage.

The answer is a count plus an explicit list of the blocks that cannot state their basis, so the
next round reads a name instead of re-deriving the question. Nothing is recomputed here: no draw
stream, no band, no engine. Measurement only, and every number is arithmetic over published JSON.

Second reading, same rule: a study that published several vintages of the same control (ADDOS
2026-10-29 vs 2026-10-30) shows its basis CHANGE across vintages. Those transitions are published
one by one, because "the block stopped being undeclared" is the only direct evidence that the
r1316 repair landed rather than being described in a digest.
"""

import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E298_replay_control_census"
TITLE = ("which published controls re-derive over a live panel, and how many of them say so?")
FACE = "REPLAYCENSUS-%s.json"
LATEST = "replaycensus_latest.json"

CONTROL_KEY_RE = re.compile(r"(replay|reproduc|re_derive|rederive|identity_check)", re.I)
IDENTITY_KEY_RE = re.compile(r"(identity_check|rederive|re_derive)", re.I)
FACE_NAME_RE = re.compile(r"^[A-Z][A-Z0-9]*-\d{4}-\d{2}-\d{2}\.json$")

# which fields make a block's panel recoverable
PIN_TOKENS = ("window", "window_used", "pin", "vintage", "cutoff")
LIVE_TOKENS = ("live_panel_last", "sessions_past", "panel_last", "live_panel")

VERDICT_VOCAB = (
    "every_published_control_declares_its_basis",
    "controls_that_cannot_state_their_basis_exist",
    "no_published_controls_found",
)

NO_BILL = ("measurement only: every number below is arithmetic over the published JSON under "
           "results/state_tilt/. No panel is re-read, no face is rebuilt, no engine runs, no "
           "draw stream is regenerated. A control's BASIS is read from the keys it publishes, "
           "not inferred from the code that wrote it.")


# ------------------------------------------------------------------ io
def _read(path):
    fh = io.open(path, "r", encoding="utf-8")
    try:
        return json.load(fh)
    finally:
        fh.close()


def write_face(face, outdir=None):
    outdir = outdir or OUTDIR
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE % face["evidence_cutoff"], LATEST):
        fh = io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n")
        try:
            fh.write(text)
        finally:
            fh.close()


def load(name, outdir=None):
    return _read(os.path.join(outdir or OUTDIR, name))


# ------------------------------------------------------------------ classification
def classify_kind(key):
    """identity controls re-derive from the face's own records; replays depend on a vintage."""
    return "identity" if IDENTITY_KEY_RE.search(str(key)) else "replay"


def _basis_fields(block):
    """Every key the block (and its one-level nested dicts) publishes, lowercased."""
    fields = []
    if not isinstance(block, dict):
        return fields
    for key, value in block.items():
        fields.append(str(key))
        if isinstance(value, dict):
            fields.extend(str(k) for k in value.keys())
    return fields


def classify_basis(block):
    """Return (basis, evidence). Basis is read from published keys only."""
    fields = _basis_fields(block)
    low = [f.lower() for f in fields]
    live_hit = [f for f in low if any(t in f for t in LIVE_TOKENS)]
    if live_hit:
        return "live_declared", sorted(set(live_hit))
    src = block.get("window_source") if isinstance(block, dict) else None
    if isinstance(src, str) and src:
        # "e240_reference.window" names another face's window: the control is pinned upstream
        return ("pinned_upstream" if ("." in src or "reference" in src.lower())
                else "pinned_declared"), ["window_source"]
    pin_hit = [f for f in low if any(f == t or f.startswith(t) or f.endswith(t) for t in PIN_TOKENS)]
    if pin_hit:
        return "pinned_literal", sorted(set(pin_hit))
    return "undeclared", []


def _scalar(value):
    return value if isinstance(value, (bool, int, float, str)) or value is None else None


def census_face(face_name, face):
    """Walk one published face and return its control containers and leaf witnesses."""
    containers, leaves = [], []

    def walk(node, path):
        if isinstance(node, dict):
            for key, value in node.items():
                here = path + "/" + str(key)
                if isinstance(value, dict):
                    if CONTROL_KEY_RE.search(str(key)):
                        basis, evidence = classify_basis(value)
                        kind = classify_kind(key)
                        containers.append({
                            "face": face_name,
                            "path": here,
                            "key": str(key),
                            "kind": kind,
                            "basis": basis,
                            "basis_evidence": evidence,
                            "tolerance": _scalar(value.get("tolerance")),
                            "status": _scalar(value.get("status")),
                            "reproduced": _scalar(value.get("reproduced")),
                            # a replay that cannot name its panel cannot be called safe
                            "at_risk": kind == "replay" and basis == "undeclared",
                        })
                    walk(value, here)
                elif isinstance(value, list):
                    walk(value, here + "[]")
                elif CONTROL_KEY_RE.search(str(key)):
                    leaves.append({"face": face_name, "path": here,
                                   "key": str(key), "value": _scalar(value)})
        elif isinstance(node, list):
            for item in node[:200]:
                walk(item, path + "[]")

    walk(face, "")
    return containers, leaves


def _max_cutoff(face_names):
    dates = sorted(re.findall(r"(\d{4}-\d{2}-\d{2})", " ".join(face_names)))
    return dates[-1] if dates else "unknown"


def vintage_transitions(controls):
    """Between two vintages of the same face name, did the basis change?"""
    by_study = {}
    for c in controls:
        m = re.match(r"^([A-Z][A-Z0-9]*)-(\d{4}-\d{2}-\d{2})\.json$", c["face"])
        if not m:
            continue
        by_study.setdefault((m.group(1), c["path"]), []).append((m.group(2), c))
    out = []
    for (study, path), rows in sorted(by_study.items()):
        rows.sort(key=lambda r: r[0])
        for (d0, c0), (d1, c1) in zip(rows, rows[1:]):
            if c0["basis"] != c1["basis"]:
                out.append({"study": study, "path": path, "from_date": d0, "to_date": d1,
                            "from_basis": c0["basis"], "to_basis": c1["basis"],
                            "statement": ("the %s control of %s changed its declared basis %s -> %s "
                                          "between these two vintages"
                                          % (c1["kind"], study, c0["basis"], c1["basis"]))})
    return out


def build(outdir=None):
    outdir = outdir or OUTDIR
    paths = sorted(glob.glob(os.path.join(outdir, "*.json")))
    faces, mirrors = [], 0
    self_files = []
    for p in paths:
        name = os.path.basename(p)
        # The census lives in the directory it scans, so it must never grade itself (E180 family).
        # Counted by STUDY, not by file: this study publishes one dated vintage per day it runs, and
        # counting files made every later run disagree with what it published (self_faces_excluded
        # 2 -> 3 the next day, leaving smoke's "summary does not re-derive" red forever).
        if name.startswith("REPLAYCENSUS-") or name == LATEST:
            self_files.append(name)
        elif FACE_NAME_RE.match(name):
            faces.append((name, _read(p)))
        elif name.endswith("_latest.json"):
            mirrors += 1

    # one self face (however many vintages of it sit on disk) plus its mirror when present
    self_faces = (1 if any(n.startswith("REPLAYCENSUS-") for n in self_files) else 0) \
        + (1 if LATEST in self_files else 0)

    controls, leaves = [], []
    for name, payload in faces:
        if not isinstance(payload, dict):
            continue
        c, l = census_face(name, payload)
        controls.extend(c)
        leaves.extend(l)

    cutoff = _max_cutoff([n for n, _ in faces])
    with_controls = sorted({c["face"] for c in controls})

    by_kind, by_basis = {}, {}
    for c in controls:
        by_kind[c["kind"]] = by_kind.get(c["kind"], 0) + 1
        by_basis[c["basis"]] = by_basis.get(c["basis"], 0) + 1

    at_risk = [c for c in controls if c["at_risk"]]
    per_face = {}
    for c in controls:
        rec = per_face.setdefault(c["face"], {"controls": 0, "at_risk": 0})
        rec["controls"] += 1
        rec["at_risk"] += 1 if c["at_risk"] else 0

    if not controls:
        verdict = "no_published_controls_found"
    elif at_risk:
        verdict = "controls_that_cannot_state_their_basis_exist"
    else:
        verdict = "every_published_control_declares_its_basis"

    n_replay = by_kind.get("replay", 0)
    n_declared = sum(by_basis.get(b, 0) for b in ("pinned_upstream", "pinned_literal",
                                                  "pinned_declared", "live_declared"))
    summary = {
        "faces_scanned": len(faces),
        "mirror_files_excluded": mirrors,
        "self_faces_excluded": self_faces,
        "self_face_files_on_disk": len(self_files),
        "faces_with_controls": len(with_controls),
        "n_control_containers": len(controls),
        "n_leaf_witnesses": len(leaves),
        "by_kind": by_kind,
        "by_basis": by_basis,
        "n_replay_controls": n_replay,
        "n_replay_with_declared_basis": sum(1 for c in controls
                                            if c["kind"] == "replay" and c["basis"] != "undeclared"),
        "n_replay_that_rederive_on_the_live_panel_and_say_so": by_basis.get("live_declared", 0),
        "n_at_risk": len(at_risk),
        "at_risk_faces": sorted({c["face"] for c in at_risk}),
        "per_face": per_face,
        "statement": None,
    }
    summary["statement"] = (
        "%d control block(s) across %d published face(s); %d of them are replays, %d of those "
        "declare their basis and %d cannot, so %d replay control(s) are published as "
        "reacting-to-an-unknown-panel rather than as safe or broken."
        % (len(controls), len(with_controls), n_replay,
           summary["n_replay_with_declared_basis"], len(at_risk), len(at_risk)))

    identity = {
        "face_counter_agrees": len(with_controls) == len({c["face"] for c in controls}),
        "kind_partition_sums_to_controls": sum(by_kind.values()) == len(controls),
        "basis_partition_sums_to_controls": sum(by_basis.values()) == len(controls),
        "every_at_risk_is_a_replay": all(c["kind"] == "replay" for c in at_risk),
        "every_at_risk_has_no_basis_evidence": all(not c["basis_evidence"] for c in at_risk),
        "no_leaf_reached_the_container_census": all(
            isinstance(c["path"], str) and c["path"].startswith("/") for c in controls),
        "per_face_sums_to_controls": sum(v["controls"] for v in per_face.values()) == len(controls),
        "per_face_at_risk_sums": sum(v["at_risk"] for v in per_face.values()) == len(at_risk),
    }
    identity["all_checks"] = all(identity.values())

    return {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": cutoff,
        "decision_rule": ("replay + pinned/live_declared basis = safe; replay + undeclared basis = "
                          "unmeasurable (never defaulted); identity controls are not graded on "
                          "basis at all"),
        "no_bill": NO_BILL,
        "controls": controls,
        # the path alone is NOT an identity: two vintages of one study share it (ADDOS 10-29 vs
        # 10-30 carry the same /e240_replay and differ only in basis), so every row repeats the
        # face it belongs to and a reader never has to join on a non-unique key.
        "at_risk": [{"face": c["face"], "path": c["path"], "key": c["key"],
                     "kind": c["kind"], "basis": c["basis"]} for c in at_risk],
        "vintage_transitions": vintage_transitions(controls),
        "summary": summary,
        "identity_check": identity,
        "verdict": verdict,
        "verdict_reason": summary["statement"],
    }


# ------------------------------------------------------------------ commands
def cmd_run():
    import datetime
    face = build()
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    s = face["summary"]
    print("E298 %s" % face["verdict"])
    print("  %d face(s) scanned (%d mirror(s) excluded), cutoff %s"
          % (s["faces_scanned"], s["mirror_files_excluded"], face["evidence_cutoff"]))
    print("  %d control block(s) in %d face(s): %s"
          % (s["n_control_containers"], s["faces_with_controls"],
             ", ".join("%s=%d" % kv for kv in sorted(s["by_kind"].items()))))
    print("  basis: %s" % ", ".join("%s=%d" % kv for kv in sorted(s["by_basis"].items())))
    print("  replays: %d, %d declare a basis, %d re-derive live and say so, %d cannot say"
          % (s["n_replay_controls"], s["n_replay_with_declared_basis"],
             s["n_replay_that_rederive_on_the_live_panel_and_say_so"], s["n_at_risk"]))
    for c in face["at_risk"]:
        print("    UNMEASURABLE %-34s %s" % (c["face"], c["path"]))
    for t in face["vintage_transitions"]:
        print("    VINTAGE %s %s -> %s (%s)" % (t["study"], t["from_basis"], t["to_basis"],
                                                t["path"]))
    print("  identity_check: %s" % ("ALL PASS" if face["identity_check"]["all_checks"]
                                    else "FAILED"))
    return 0


def cmd_verify():
    stored = load(FACE % build()["evidence_cutoff"])
    live = build()
    problems = []
    for key in ("verdict", "summary", "identity_check", "controls", "at_risk",
                "vintage_transitions"):
        if stored.get(key) != live.get(key):
            problems.append("%s does not re-derive" % key)
    if stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    if not (stored.get("identity_check") or {}).get("all_checks"):
        problems.append("identity_check is not all green")
    if problems:
        for p in problems:
            print("FAIL %s" % p)
        return 1
    print("E298 verify: the published face re-derives (%d controls, verdict %s)"
          % (len(live["controls"]), live["verdict"]))
    return 0


def cmd_selftest():
    ok = 0
    fails = []

    def leg(name, cond, detail=None):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append("%s (%r)" % (name, detail))

    # L1 a replay block with no basis field is undeclared and at risk
    f = {"e240_replay": {"cell": "all_five", "tolerance": 1e-9, "status": "reproduced",
                         "reproduced": True}}
    c, l = census_face("X-2026-01-01.json", f)
    leg("L1", len(c) == 1 and c[0]["basis"] == "undeclared" and c[0]["at_risk"] is True, c)

    # L2 a block that names another face's window is pinned upstream, not at risk
    f = {"e240_replay": {"window_source": "e240_reference.window",
                         "window_used": {"first": "2020-11-17", "last": "2026-10-29"}}}
    c, _ = census_face("X-2026-01-01.json", f)
    leg("L2", c[0]["basis"] == "pinned_upstream" and c[0]["at_risk"] is False, c[0]["basis"])

    # L3 a block that names the live panel and the overshoot is live_declared (still safe)
    f = {"reproducibility": {"live_panel_last": "2026-10-30",
                             "sessions_past_the_pinned_window": 1}}
    c, _ = census_face("X-2026-01-01.json", f)
    leg("L3", c[0]["basis"] == "live_declared" and c[0]["at_risk"] is False, c[0]["basis"])

    # L4 a block carrying its own window field is pinned_literal
    f = {"reproduction": {"window": {"first": "a", "last": "b"}, "agrees_at_1e9": True}}
    c, _ = census_face("X-2026-01-01.json", f)
    leg("L4", c[0]["basis"] == "pinned_literal", c[0]["basis"])

    # L5 an identity check is never graded on basis, even with no window at all
    f = {"identity_check": {"checked": 3, "mismatched": 0}}
    c, _ = census_face("X-2026-01-01.json", f)
    leg("L5", c[0]["kind"] == "identity" and c[0]["at_risk"] is False, c[0])

    # L6 a leaf boolean named 'reproduced' is a witness, never a container
    f = {"rows": [{"reproduced": True}, {"reproduced": False}]}
    c, l = census_face("X-2026-01-01.json", f)
    leg("L6", not c and len(l) == 2 and l[0]["value"] is True, (len(c), len(l)))

    # L7 the vintage transition is detected when only the basis changed
    a = {"e240_replay": {"tolerance": 1e-9}}
    b = {"e240_replay": {"tolerance": 1e-9, "window_source": "e240_reference.window"}}
    ca, _ = census_face("ADDOS-2026-10-29.json", a)
    cb, _ = census_face("ADDOS-2026-10-30.json", b)
    tr = vintage_transitions(ca + cb)
    leg("L7", len(tr) == 1 and tr[0]["from_basis"] == "undeclared"
        and tr[0]["to_basis"] == "pinned_upstream", tr)

    # L8 identical bases across vintages produce no transition claim
    tr = vintage_transitions(ca + ca)
    leg("L8", tr == [], tr)

    # L9 the cutoff derives from the face names, not from the wall clock
    leg("L9", _max_cutoff(["X-2026-01-01.json", "Y-2026-03-04.json"]) == "2026-03-04")

    # L10 an empty directory is 'no controls', not 'all safe'
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e298_empty_")
    face = build(tmp)
    leg("L10", face["verdict"] == "no_published_controls_found"
        and face["summary"]["n_control_containers"] == 0, face["verdict"])

    # L11 mirrors are excluded from the census but counted; so is the census itself
    tmp2 = tempfile.mkdtemp(prefix="e298_mirror_")
    for name, payload in (("AAA-2026-02-02.json", {"replay_x": {"cell": "a"}}),
                          ("aaa_latest.json", {"replay_x": {"cell": "a"}}),
                          ("REPLAYCENSUS-2026-02-02.json", {"replay_self": {"cell": "a"}})):
        fh = io.open(os.path.join(tmp2, name), "w", encoding="utf-8", newline="\n")
        try:
            fh.write(json.dumps(payload))
        finally:
            fh.close()
    face = build(tmp2)
    leg("L11", face["summary"]["faces_scanned"] == 1
        and face["summary"]["mirror_files_excluded"] == 1
        and face["summary"]["self_faces_excluded"] == 1
        and face["summary"]["n_control_containers"] == 1, face["summary"]["faces_scanned"])

    # L11b yesterday's vintage is still this study: counting files made the census drift one a day
    tmp2b = tempfile.mkdtemp(prefix="e298_selfvint_")
    for name in ("AAA-2026-02-02.json", "REPLAYCENSUS-2026-02-02.json",
                 "REPLAYCENSUS-2026-02-03.json", "replaycensus_latest.json"):
        fh = io.open(os.path.join(tmp2b, name), "w", encoding="utf-8", newline="\n")
        try:
            fh.write(json.dumps({"replay_x": {"cell": "a"}}))
        finally:
            fh.close()
    face = build(tmp2b)
    leg("L11b two vintages of this census count as one self face, and both files are disclosed",
        face["summary"]["self_faces_excluded"] == 2
        and face["summary"]["self_face_files_on_disk"] == 3
        and face["summary"]["faces_scanned"] == 1, face["summary"])

    # L12 the partitions are exhaustive on a mixed fixture
    f = {"identity_check": {"checked": 1}, "e240_replay": {"tolerance": 1e-9},
         "probe_reproduction": {"window": "x"}}
    c, _ = census_face("X-2026-01-01.json", f)
    leg("L12", len(c) == 3 and sum(1 for x in c if x["kind"] == "identity") == 1
        and sum(1 for x in c if x["at_risk"]) == 1, [(x["kind"], x["at_risk"]) for x in c])

    # L13 'cannot say' is never converted into a claim that it used the wrong panel
    f = {"e240_replay": {"tolerance": 1e-9, "reproduced": True}}
    c, _ = census_face("X-2026-01-01.json", f)
    leg("L13", c[0]["at_risk"] is True and c[0]["basis"] == "undeclared"
        and c[0]["reproduced"] is True, c[0])

    # L14 on the real faces: the census is non-trivial and its partitions hold
    live = build()
    s, idn = live["summary"], live["identity_check"]
    leg("L14", s["n_control_containers"] >= 10 and s["faces_with_controls"] >= 5, s)
    leg("L15", idn["all_checks"] is True, idn)
    leg("L16", live["verdict"] in VERDICT_VOCAB, live["verdict"])
    leg("L17", (live["verdict"] == "controls_that_cannot_state_their_basis_exist")
        == (s["n_at_risk"] > 0), (live["verdict"], s["n_at_risk"]))
    leg("L18", all(x["path"].startswith("/") for x in live["at_risk"]), live["at_risk"][:2])
    leg("L19", s["n_replay_with_declared_basis"] + s["n_at_risk"] == s["n_replay_controls"],
        (s["n_replay_with_declared_basis"], s["n_at_risk"], s["n_replay_controls"]))
    leg("L20", all(t["from_basis"] != t["to_basis"] for t in live["vintage_transitions"]),
        live["vintage_transitions"][:2])

    # L21 two vintages of one study carry the SAME control path, so a path is not an identity:
    # the census must keep both as distinct controls and repeat the face on every at-risk row
    a = {"e240_replay": {"tolerance": 1e-9}}
    b = {"e240_replay": {"tolerance": 1e-9, "window_source": "e240_reference.window"}}
    mixed = {"ADDOS-2026-10-29.json": a, "ADDOS-2026-10-30.json": b}
    rows = []
    for name, payload in mixed.items():
        rows.extend(census_face(name, payload)[0])
    leg("L21", len(rows) == 2 and len({(r["face"], r["path"]) for r in rows}) == 2
        and len({r["path"] for r in rows}) == 1, rows)

    print("E298 selftest: %d/%d" % (ok, ok + len(fails)))
    for f_ in fails:
        print("  FAIL %s" % f_)
    return 0 if not fails else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))