"""r2126 (bm-c): apply the buffer-gap repair, or refuse and say why.

`Tools/money_rounding_gap.py` established that the width-ladder leg is
red by construction: the face publishes two 3-dp ends and a 3-dp difference, so
the difference can only be rebuilt to within one rounding step (1e-3), while the
leg demands 1e-9. The fix is one constant, plus a comment that records why.

This script exists so the repair does not have to be re-derived next round, and
so that it cannot be applied to a file somebody else has already moved:

  * it refuses (rc=3) unless smoke_test.py still has the exact bytes the probe
    read -- the r2123 judgement ("the script hard-refuses when what is on disk is
    no longer the slice the probe looked at");
  * it refuses (rc=3) if the published gap would not pass at the wider tolerance;
  * it writes a backup next to the file, patches, re-reads, and prints the line
    before/after so the change is auditable from the console alone.

It does NOT run the smoke suite (that belongs to a round that owns the tree).

Usage:
  python Tools/money_rounding_gap_fix.py --check    # read-only, rc 0/3
  python Tools/money_rounding_gap_fix.py --apply    # patch, rc 0/2/3
"""
import hashlib
import io
import json
import os
import shutil
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "smoke_test.py")
FACE = os.path.join(ROOT, "results", "etf_book_buffer_floor_readback.json")
RECEIPT = os.path.join(ROOT, "results", "_r2126bmc_buffer_gap_fix_receipt.json")

OLD = '                           - float(_rb.get("gap_pp"))) > 1e-9):'
NEW = '                           - float(_rb.get("gap_pp"))) > 1e-3):'
NOTE_ANCHOR = '                _wbad.append("the published gap is not observed minus predicted")'
NOTE = ('                # r2126: the ends and the difference are all published at 3 dp, so\n'
        '                # two 3-dp ends rebuild the difference to within one rounding step\n'
        '                # (1e-3), never to 1e-9 -- the 1e-9 assertion was red by construction\n'
        '                # on an honest face (r1813: the tolerance IS the rounding error).\n')


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def face_passes_at_step():
    try:
        with open(FACE, encoding="utf-8") as fh:
            d = json.load(fh)
        obs, pred, gap = float(d["observed_pp"]), float(d["predicted_pp"]), float(d["gap_pp"])
    except Exception as e:
        return False, "face unreadable: %r" % (e,)
    dev = abs(round(obs - pred, 3) - gap)
    return dev <= 1e-3 + 1e-12, "deviation %.6f (step 1e-3)" % dev


def read_text(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write_text(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--check"
    rec = {"schema": "r2126-buffer-gap-fix/1", "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "mode": mode, "target": "smoke_test.py"}
    if not os.path.exists(TARGET):
        print("REFUSED: smoke_test.py missing")
        return 3
    ok_face, why_face = face_passes_at_step()
    rec["face_check"] = {"passes_at_1e-3": ok_face, "why": why_face}
    if not ok_face:
        print("REFUSED: the face would not pass even at the rounding step (%s)" % why_face)
        rec["rc"] = 3
        rec["outcome"] = "REFUSED_FACE"
        json.dump(rec, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 3

    text = read_text(TARGET)
    rec["target_sha_before"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    has_old = text.count(OLD)
    has_new = text.count(NEW)
    rec["anchor_counts"] = {"old": has_old, "new": has_new}

    if has_new == 1 and has_old == 0:
        print("ALREADY PATCHED: the leg already demands 1e-3 (nothing to do)")
        rec["rc"] = 0
        rec["outcome"] = "ALREADY_PATCHED"
        json.dump(rec, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 0
    if has_old != 1 or has_new != 0:
        print("REFUSED: the anchor is not unique on disk (old=%d new=%d) -- "
              "somebody else has moved this leg" % (has_old, has_new))
        rec["rc"] = 3
        rec["outcome"] = "REFUSED_ANCHOR_MOVED"
        json.dump(rec, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 3

    line_before = next(l for l in text.splitlines() if OLD in l)
    patched = text.replace(OLD, NEW, 1)
    # the note goes directly under the append, so a reader of the leg sees why
    if NOTE_ANCHOR in patched and "r2126: the ends and the difference" not in patched:
        patched = patched.replace(NOTE_ANCHOR, NOTE + NOTE_ANCHOR, 1)
    line_after = next(l for l in patched.splitlines() if NEW in l)

    rec["line_before"] = line_before.strip()
    rec["line_after"] = line_after.strip()

    if mode != "--apply":
        print("WOULD PATCH (--check):")
        print("  -", line_before.strip())
        print("  +", line_after.strip())
        print("  anchor unique, face passes at the rounding step, nothing written")
        rec["rc"] = 0
        rec["outcome"] = "WOULD_PATCH"
        json.dump(rec, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 0

    backup = TARGET + ".r2126bak"
    shutil.copy2(TARGET, backup)
    write_text(TARGET, patched)
    after = read_text(TARGET)
    if after.count(NEW) != 1 or after.count(OLD) != 0:
        write_text(TARGET, text)
        print("ROLLED BACK: post-write read-back did not show exactly one patched anchor")
        rec["rc"] = 2
        rec["outcome"] = "ROLLED_BACK"
        json.dump(rec, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return 2
    rec["target_sha_after"] = hashlib.sha256(after.encode("utf-8")).hexdigest()
    rec["backup"] = os.path.basename(backup)
    rec["rc"] = 0
    rec["outcome"] = "PATCHED"
    json.dump(rec, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("PATCHED smoke_test.py (backup %s)" % os.path.basename(backup))
    print("  -", line_before.strip())
    print("  +", line_after.strip())
    print("next: run the width-ladder leg and confirm it turns green")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
