"""Canon hot-cold sweep driver -- O-20261003-2030 weld item1 (T-162 r434 bm-c).

The sanctioned hot-cold integration driver for canon faces, with the
treasure-protection gate EMBEDDED at every step (TREASURE_PROTECTION_LAW
v1.0 s2; O-2030 section 2.1 three-class script retrofit: archive-sweep
family). Registry faces (research/, firm/, knowledge/ treasures, results/
verdict families) are HARD-REJECT targets -- in-service law is structural
and byte-count archiving is forbidden without a group/GM ruling (r504).

Commands (run from repo root):
  python Tools/canon_sweep.py probe [face ...]
      Report-only: face sizes vs hard lines, registry-prescan class per
      face, flow-marker candidate counts. ZERO writes.
  python Tools/canon_sweep.py apply --face <rel> --marker <regex> --authorize "<reason>"
      Guarded hot-cold move of marker-matching rows:
        embedded prescan (registry hit = HARD REJECT rc3)
        -> quarantine safety snapshot (results/_quarantine/<ts>/, manifest
           compatible with treasure_guard assert)
        -> verbatim append to research/memory-archive/<YYYYMM>.md (cold
           layer, append-only direction)
        -> matched rows replaced by ONE pointer line in-face (r444 paradigm)
        -> zero-loss assert (moved bytes == archived bytes, pointer count,
           snapshot hash identity) -- FAIL rolls the face back.
  python Tools/canon_sweep.py selftest
      Hermetic (tempdir only).

Hard lines (probe reports; apply is marker+authorize driven, never
byte-count driven):
  CODELY.md         50KB watermark (D-20260925-01-04, mandatory integration)
  research/pit-*.md 10KB structural line (O-20260927-0230; r504: structural)

Exit codes: 0 ok/no-op, 2 mechanism failure, 3 registry HARD REJECT (redline).
"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import treasure_guard as tg  # noqa: E402  (embedded gate single-source)

WATERMARK_BYTES = 50 * 1024          # CODELY.md D-20260925-01-04
PIT_STRUCTURAL_BYTES = 10 * 1024     # O-20260927-0230, r504 structural note
FLOW_MARKERS = ("回执", "执行记录", "流水")
ARCHIVE_REL = "research/memory-archive"
QUARANTINE_REL = "results/_quarantine"


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rel(p):
    return p.replace("\\", "/")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def probe_faces(root):
    faces = ["CODELY.md", "HQ-FEEDBACK.md"]
    faces += sorted(_rel(os.path.relpath(p, root))
                    for p in glob.glob(os.path.join(root, "research", "pit-*.md")))
    return faces


def cmd_probe(root, faces=None):
    fam, ex, gl = tg.load_registry(root)
    rows = []
    print("canon_sweep probe (report-only, zero writes) @",
          time.strftime("%Y-%m-%dT%H:%M:%S"))
    for face in (faces or probe_faces(root)):
        fp = os.path.join(root, face)
        if not os.path.isfile(fp):
            rows.append({"face": face, "missing": True})
            print("  %-34s MISSING" % face)
            continue
        raw = open(fp, "rb").read()
        protected = tg.is_protected(face, fam, ex, gl)
        line = (WATERMARK_BYTES if face == "CODELY.md"
                else PIT_STRUCTURAL_BYTES if "pit-" in face else None)
        over = bool(line and len(raw) > line)
        cands = {m: raw.decode("utf-8", "replace").count(m) for m in FLOW_MARKERS}
        rows.append({"face": face, "size_bytes": len(raw),
                     "hard_line_bytes": line, "over_line": over,
                     "registry_class": "PROTECTED" if protected else "sweepable",
                     "flow_candidates": cands})
        print("  %-34s %7dB  line=%s  over=%-5s  registry=%-9s  flow_cands=%s"
              % (face, len(raw), line or "-", over, "PROTECTED" if protected
                 else "sweepable",
                 ",".join("%s:%d" % (m, n) for m, n in cands.items() if n)))
    prot = [r["face"] for r in rows if r.get("registry_class") == "PROTECTED"]
    print("summary: %d face(s); %d registry-PROTECTED (apply = HARD REJECT); "
          "in-service structural law is NEVER archived for byte counts (r504)"
          % (len(rows), len(prot)))
    return 0


def _quarantine_snapshot(root, face, raw, reason, ts):
    """Safety snapshot of the pre-surgery face (copy, not delete).

    Manifest uses treasure_guard's moved[] shape so
    `python Tools/treasure_guard.py assert --manifest <p>` verifies it.
    """
    qdir = os.path.join(root, QUARANTINE_REL, ts)
    dst = os.path.join(qdir, face)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(raw)
    man = {
        "ts": ts,
        "reason": reason,
        "law": "TREASURE_PROTECTION_LAW.md v1.0 s2.2 (canon_sweep safety snapshot)",
        "observation_window_days": 7,
        "moved": [{"src": face, "dst": _rel(os.path.relpath(dst, root)),
                   "sha256": sha256_bytes(raw), "size": len(raw)}],
    }
    mpath = os.path.join(qdir, "manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    return mpath


def cmd_apply(root, face, marker, authorize, dry_run=False):
    face = _rel(face)
    if not authorize or len(authorize) < 8:
        print("canon_sweep apply: --authorize requires a real reason "
              "(>=8 chars) -- byte-count sweeps are forbidden (r504)")
        return 2
    fam, ex, gl = tg.load_registry(root)
    # embedded prescan (O-2030 s2.1): registry hit = HARD REJECT
    hits = tg.hits_of([face], fam, ex, gl)
    if hits:
        print("TREASURE_GUARD EMBEDDED HARD REJECT: registry hit = redline")
        print("  HIT:", face)
        print("  (un-register needs a GM-signed ticket proving regenerability,")
        print("   TREASURE_REGISTRY.md header)")
        return 3
    fp = os.path.join(root, face)
    if not os.path.isfile(fp):
        print("canon_sweep apply: face missing:", face)
        return 2
    if _rel(ARCHIVE_REL) + "/" in face:
        print("canon_sweep apply: cold archive is a destination, never a target")
        return 2
    try:
        rx = re.compile(marker)
    except re.error as e:
        print("canon_sweep apply: bad marker regex:", e)
        return 2
    raw = open(fp, "rb").read()
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    idx = [i for i, ln in enumerate(lines) if rx.search(ln)]
    if not idx:
        print("canon_sweep apply: 0 marker rows -- honest no-op (nothing moved)")
        return 0
    moved_bytes = "".join(lines[i] for i in idx).encode("utf-8")
    eol = "\r\n" if text.count("\r\n") >= text.count("\n") - text.count("\r\n") else "\n"
    ts = time.strftime("%Y%m%d-%H%M%S")
    month = time.strftime("%Y%m")
    arch_path = os.path.join(root, ARCHIVE_REL, month + ".md")
    pointer = ("- 冷层指针（canon_sweep apply %s · O-2030 item1 焊面）：%d 行已 verbatim "
               "迁出至 %s/%s.md『热冷整编 %s · %s』节（授权：%s）——全文查该节。%s"
               % (ts, len(idx), ARCHIVE_REL, month, ts, face, authorize, eol))
    if dry_run:
        print("DRY-RUN: would move %d row(s) -> %s/%s.md; pointer x1 at line %d"
              % (len(idx), ARCHIVE_REL, month, idx[0] + 1))
        return 0
    # 1) quarantine safety snapshot
    mpath = _quarantine_snapshot(root, face, raw, authorize, ts)
    # 2) verbatim append to cold layer (append-only direction)
    os.makedirs(os.path.dirname(arch_path), exist_ok=True)
    header = "" if os.path.isfile(arch_path) else "# memory-archive %s（冷层·append-only）\n" % month
    section = ("## 热冷整编 %s · %s\n- 授权：%s\n- 来源面：%s（%d 行 verbatim 迁出）\n"
               % (ts, face, authorize, face, len(idx)))
    with open(arch_path, "ab") as f:
        f.write(header.encode("utf-8"))
        f.write(section.encode("utf-8"))
        f.write(moved_bytes)
    # 3) in-face surgery: matched rows out, ONE pointer line at first position
    new_lines = []
    for i, ln in enumerate(lines):
        if i == idx[0]:
            new_lines.append(pointer)
        if i not in idx:
            new_lines.append(ln)
    new_text = "".join(new_lines)
    with open(fp, "wb") as f:
        f.write(new_text.encode("utf-8"))
    # 4) zero-loss assert -- rollback on FAIL
    arch_raw = open(arch_path, "rb").read()
    moved_ok = moved_bytes in arch_raw
    new_raw = open(fp, "rb").read()
    new_dec = new_raw.decode("utf-8")
    ptr_ok = new_dec.count(pointer) == 1
    gone_ok = all(rx.search(ln) is None for ln in new_dec.splitlines())
    kept_ok = all(lines[i] in new_text for i in range(len(lines)) if i not in idx)
    snap_ok = open(os.path.join(root, QUARANTINE_REL, ts, face), "rb").read() == raw
    receipt = {"ts": ts, "face": face, "rows_moved": len(idx),
               "marker": marker, "authorize": authorize,
               "moved_sha256": sha256_bytes(moved_bytes),
               "moved_bytes": len(moved_bytes),
               "zero_loss": {"moved_in_archive": moved_ok, "pointer_count_1": ptr_ok,
                             "marker_gone": gone_ok, "unmatched_kept": kept_ok,
                             "snapshot_identity": snap_ok},
               "archive": _rel(os.path.relpath(arch_path, root)),
               "quarantine_manifest": _rel(os.path.relpath(mpath, root)),
               "law": "TREASURE_PROTECTION_LAW v1.0 s2 + O-2030 item1 (r434)"}
    rpath = os.path.join(root, "results", "_canon_sweep_last.json")
    if not (moved_ok and ptr_ok and gone_ok and kept_ok and snap_ok):
        # rollback: restore face + truncate archive back to pre-append size
        with open(fp, "wb") as f:
            f.write(raw)
        pre = os.path.getsize(arch_path) - len(moved_bytes) - len(section.encode("utf-8")) \
            - (len(header.encode("utf-8")) if header else 0)
        with open(arch_path, "r+b") as f:
            f.truncate(pre)
        receipt["rolled_back"] = True
        with open(rpath, "w", encoding="utf-8") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=1)
        print("canon_sweep apply ASSERT FAIL -> ROLLED BACK (zero-loss gate):",
              {k: v for k, v in receipt["zero_loss"].items() if not v})
        return 2
    with open(rpath, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("canon_sweep apply OK: %d row(s) %s -> %s; pointer x1; snapshot %s"
          % (len(idx), face, receipt["archive"], receipt["quarantine_manifest"]))
    print("zero-loss assert: all legs PASS")
    return 0


def selftest():
    ok = True

    def expect(name, cond):
        nonlocal ok
        print(("  PASS " if cond else "  FAIL ") + name)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as td:
        # fixture root: registry protecting research/ + firm/ (treasure_guard shape)
        os.makedirs(os.path.join(td, "knowledge"))
        with open(os.path.join(td, tg.REGISTRY_REL), "w", encoding="utf-8") as f:
            f.write("# fixture registry\n| research/ | all prereg |\n| firm/ | laws |\n")
        os.makedirs(os.path.join(td, "research"))
        face_rel = "CODELY.md"
        with open(os.path.join(td, face_rel), "w", encoding="utf-8") as f:
            f.write("# hot layer\n- law row keep me\n- 执行记录 r100 flow row one\n"
                    "- plain row\n- 执行记录 r101 flow row two\n")
        prot_face = "research/pit-fixture.md"
        with open(os.path.join(td, prot_face), "w", encoding="utf-8") as f:
            f.write("- pit law row\n- 回执 flow row\n")
        # leg 1: probe report-only (no writes)
        before = {p: open(os.path.join(td, p), "rb").read()
                  for p in (face_rel, prot_face)}
        rc = cmd_probe(td, [face_rel, prot_face])
        expect("probe: rc0 report-only", rc == 0)
        expect("probe: zero writes",
               all(open(os.path.join(td, p), "rb").read() == before[p]
                   for p in before))
        # leg 2: registry-hit target = embedded HARD REJECT rc3
        rc = cmd_apply(td, prot_face, "回执", "selftest registry-reject leg")
        expect("apply: registry-hit face rc3 hard reject", rc == 3)
        # leg 3: clean roundtrip
        rc = cmd_apply(td, face_rel, "执行记录", "selftest roundtrip leg")
        expect("apply: clean face rc0", rc == 0)
        arch = os.path.join(td, ARCHIVE_REL, time.strftime("%Y%m") + ".md")
        expect("apply: cold archive exists", os.path.isfile(arch))
        arch_text = open(arch, encoding="utf-8").read()
        expect("apply: moved rows verbatim in archive",
               "执行记录 r100 flow row one" in arch_text
               and "执行记录 r101 flow row two" in arch_text)
        new_text = open(os.path.join(td, face_rel), encoding="utf-8").read()
        expect("apply: pointer line x1", new_text.count("冷层指针") == 1)
        expect("apply: marker rows gone from face", "执行记录" not in new_text)
        expect("apply: unmatched rows kept verbatim",
               "- law row keep me" in new_text and "- plain row" in new_text)
        # leg 4: zero-marker no-op
        rc = cmd_apply(td, face_rel, "NOMATCHXYZ", "selftest no-op leg")
        expect("apply: zero-marker honest no-op rc0", rc == 0)
        # leg 5: authorize guard
        rc = cmd_apply(td, face_rel, "plain", "short")
        expect("apply: thin --authorize refused rc2", rc == 2)
        # leg 6: snapshot identity via treasure_guard assert shape
        snaps = glob.glob(os.path.join(td, QUARANTINE_REL, "*", "manifest.json"))
        expect("snapshot: manifest present", len(snaps) == 1)
        if snaps:
            man = json.load(open(snaps[0], encoding="utf-8"))
            expect("snapshot: manifest moved[] hash identity",
                   man["moved"][0]["sha256"] == sha256_bytes(
                       before[face_rel]))
            dst = os.path.join(td, man["moved"][0]["dst"])
            expect("snapshot: bytes identity", open(dst, "rb").read()
                   == before[face_rel])
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    root = repo_root()
    if len(argv) < 2 or argv[1] in ("probe",):
        return cmd_probe(root, argv[2:])
    if argv[1] == "apply":
        face = marker = authorize = None
        args = argv[2:]
        dry = "--dry-run" in args
        args = [a for a in args if a != "--dry-run"]
        i = 0
        while i < len(args):
            if args[i] == "--face" and i + 1 < len(args):
                face, i = args[i + 1], i + 2
            elif args[i] == "--marker" and i + 1 < len(args):
                marker, i = args[i + 1], i + 2
            elif args[i] == "--authorize" and i + 1 < len(args):
                authorize, i = args[i + 1], i + 2
            else:
                i += 1
        if not (face and marker and authorize):
            print("apply needs --face --marker --authorize (see header doc)")
            return 2
        return cmd_apply(root, face, marker, authorize, dry)
    if argv[1] == "selftest":
        return selftest()
    print("unknown command:", argv[1])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
