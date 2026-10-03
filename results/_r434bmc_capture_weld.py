"""r434 bm-c O-2030 item3: per-runner finalize capture-comment weld.

Surgical trio per r429 pit: count anchor == 1 -> insert -> target-line
assert (anchor still 1, block count == anchors, block directly above each
anchor) + py_compile. Comment-only insertions; zero logic touch.
Idempotent: files already carrying the block are skipped (verified).
"""
import glob
import json
import os
import py_compile
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK_LINES = [
    "# TREASURE-CAPTURE (O-20261003-2030 s2.2 five-collection-point weld, r434 bm-c):",
    "# at this finalize's closeout ask \"any new treasure in this batch?\" -- yes ->",
    "# append one row to knowledge/TREASURE_REGISTRY.md; new methodology ->",
    "# METHODOLOGY_ASSETS.md card (O-2100 same-window step). Registry is",
    "# append-only; deleting a listed face = redline P0 (TREASURE_PROTECTION_LAW s5).",
]
TARGETS = []
for f in sorted(glob.glob(os.path.join(ROOT, "scripts", "trial_labor_w*.py"))):
    TARGETS.append((f, ["def cmd_screen_finalize() -> int:",
                        "def cmd_judge_finalize() -> int:"]))
TARGETS.append((os.path.join(ROOT, "scripts", "mass_trial_w1.py"),
                ["def cmd_finalize(args):", "def cmd_judge_finalize(args):"]))
TARGETS.append((os.path.join(ROOT, "Tools", "_r426bmc_w2_judge_finalize.py"),
                ["def spawn():"]))


def main():
    receipt = {"ts": "r434", "weld": "O-2030 item3 per-runner capture comments",
               "files": [], "ok": True}
    for path, anchors in TARGETS:
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        raw = open(path, "rb").read()
        text = raw.decode("utf-8")
        if "\r\n" not in text:
            print("ABORT %s: expected CRLF face" % rel)
            receipt["ok"] = False
            continue
        frec = {"file": rel, "anchors": {}, "action": "welded"}
        if BLOCK_LINES[0] in text:
            # idempotence: strict check every anchor's predecessor is block tail
            lines = text.splitlines(keepends=True)
            strict = all(
                i > 0 and lines[i - 1].rstrip("\r\n") == BLOCK_LINES[-1]
                for i, l in enumerate(lines) if l.rstrip("\r\n") in anchors)
            frec["action"] = "already-welded (strict-covered=%s)" % strict
            receipt["files"].append(frec)
            continue
        for a in anchors:
            n = text.count(a)
            if n != 1:
                print("ABORT %s: anchor count %d != 1 for %r" % (rel, n, a))
                receipt["ok"] = False
                frec["anchors"][a] = "COUNT-%d-ABORT" % n
                break
            block = "\r\n".join(BLOCK_LINES) + "\r\n"
            text = text.replace(a, block + a, 1)
            frec["anchors"][a] = "inserted"
        else:
            # post-weld asserts
            lines = text.splitlines(keepends=True)
            for a in anchors:
                assert text.count(a) == 1, "anchor drift " + a
                idx = [i for i, l in enumerate(lines) if l.rstrip("\r\n") == a]
                assert len(idx) == 1 and idx[0] > 0
                assert lines[idx[0] - 1].rstrip("\r\n") == BLOCK_LINES[-1], \
                    "block not directly above anchor in " + rel
            assert text.count(BLOCK_LINES[0]) == len(anchors), "block count drift"
            new_raw = text.encode("utf-8")
            open(path, "wb").write(new_raw)
            py_compile.compile(path, doraise=True)
            frec["bytes_before"] = len(raw)
            frec["bytes_after"] = len(new_raw)
            frec["delta"] = len(new_raw) - len(raw)
        receipt["files"].append(frec)
    # global re-verify pass over fresh disk state
    for path, anchors in TARGETS:
        text = open(path, "rb").read().decode("utf-8")
        for a in anchors:
            if text.count(a) != 1:
                print("VERIFY FAIL:", os.path.relpath(path, ROOT), a)
                receipt["ok"] = False
        n_block = text.count(BLOCK_LINES[0])
        if n_block < len(anchors):
            print("VERIFY FAIL: block below anchors:", os.path.relpath(path, ROOT))
            receipt["ok"] = False
    total_anchors = sum(len(a) for _, a in TARGETS)
    receipt["total_targets"] = total_anchors
    out = os.path.join(ROOT, "results", "_r434bmc_capture_weld.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("weld receipt:", os.path.relpath(out, ROOT))
    print("RESULT:", "OK" if receipt["ok"] else "FAIL")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
