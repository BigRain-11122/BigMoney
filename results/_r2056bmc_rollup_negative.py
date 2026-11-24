#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Negative control for scripts/bench_night_rollup.py

Proves the guards actually fire, on this box, with the published files restored
byte-for-byte afterwards.  Three different failures must produce three different
sentences, because the chain decides what to do by reading the word:

    STALE        an input cell moved  -> the writer should be paid to re-run
    CHECK FAILED the face disagrees with itself -> a real defect, never "stale"

and the classification layer (silent vs finding) must react to the cell's own
power stamp, not to anything this roll-up decides for itself.

Nothing published is left modified: every test runs against copies under
results/_r2056bmc_*.json, and the run asserts the published trio's sha256 is
unchanged at the end.
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import bench_night_rollup as R  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
PUBLISHED = [R.OUT_PATH, R.DOC_PATH]
TMP_PREFIX = "_r2056bmc_"


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def copy_json(src, dst):
    with open(src, encoding="utf-8") as f:
        payload = json.load(f)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    return payload


def main():
    legs = []
    before = {p: sha(p) for p in PUBLISHED if os.path.exists(p)}
    if len(before) != 2:
        print("REFUSE: the published faces are not on disk")
        return 2

    real_out, real_doc, real_queue = R.OUT_PATH, R.DOC_PATH, R.QUEUE_PATH
    temps = []

    def tmp(suffix):
        fd, path = tempfile.mkstemp(prefix=TMP_PREFIX, suffix=suffix, dir=RESULTS)
        os.close(fd)
        temps.append(path)
        return path

    try:
        # ---------------------------------------------------------- N1: a hand-edited number
        body = json.load(open(real_out, encoding="utf-8"))
        body["cells"][0]["mde_min_pp"] = round(body["cells"][0]["mde_min_pp"] + 0.01, 2)
        p = tmp(".json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(body, f, ensure_ascii=False, indent=1)
        R.OUT_PATH = p
        rc, msg = R.check()
        legs.append((rc == 1 and "CHECK FAILED" in msg and "STALE" not in msg
                     and body["cells"][0]["id"] in msg,
                     "a hand-edited mde reads CHECK FAILED and names the cell (%s)" % msg))

        # ---------------------------------------------------------- N2: an input cell moved
        q = json.load(open(real_queue, encoding="utf-8"))
        target = None
        for c in q.get("cells", []):
            if c.get("result") == "results/bench_pair_index_60d.json":
                target = c
                break
        if target is None:
            legs.append((False, "the roll-up's queue pointer for pair_index_60d is gone"))
        else:
            src = os.path.join(ROOT, target["result"].replace("/", os.sep))
            moved = tmp(".json")
            payload = copy_json(src, moved)
            payload["arms"][0]["mde_pp"] = round(payload["arms"][0]["mde_pp"] + 0.05, 2)
            with open(moved, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=1)
            target["result"] = os.path.relpath(moved, ROOT).replace("\\", "/")
            qp = tmp(".json")
            with open(qp, "w", encoding="utf-8") as f:
                json.dump(q, f, ensure_ascii=False, indent=1)
            R.QUEUE_PATH = qp
            R.OUT_PATH = real_out
            rc, msg = R.check()
            legs.append((rc == 3 and "STALE" in msg and "CHECK FAILED" not in msg,
                         "one input byte moved reads STALE with no CHECK FAILED (%s)" % msg))

            # ------------------------------- N3: classification follows the cell's own stamp
            saved = payload["arms"][0].get("powered_for_target")
            payload["arms"][0]["powered_for_target"] = (not saved)
            with open(moved, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=1)
            face = R.build()
            flip = next(c for c in face["cells"] if c["id"] == "pair_index_60d")
            want = "FINDING" if not saved else "SILENT"
            legs.append((flip["reading"] == want,
                         "flipping the cell's own power stamp moves it to %s (got %s)"
                         % (want, flip["reading"])))
            payload["arms"][0]["powered_for_target"] = saved
            with open(moved, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=1)
            R.QUEUE_PATH = real_queue

        # ---------------------------------------------------------- N4: page block hand-edited
        R.OUT_PATH = real_out
        text = open(real_doc, encoding="utf-8").read()
        doc = tmp(".md")
        with open(doc, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace("9.40 倍", "9.41 倍", 1))
        R.DOC_PATH = doc
        rc, msg = R.check()
        legs.append((rc == 1 and "CHECK FAILED" in msg and "page block" in msg,
                     "a hand-edited page digit reads CHECK FAILED (%s)" % msg))

        # ---------------------------------------------------------- N5: page block removed
        with open(doc, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace(R.MARK_BEGIN, "").replace(R.MARK_END, ""))
        rc, msg = R.check()
        legs.append((rc == 1 and "no readings block" in msg,
                     "a page without markers reads CHECK FAILED (%s)" % msg))

        # ---------------------------------------------------------- N6: output face missing
        R.DOC_PATH = real_doc
        gone = tmp(".json")
        os.remove(gone)
        R.OUT_PATH = gone
        rc, msg = R.check()
        legs.append((rc == 3 and "STALE" in msg and "missing" in msg,
                     "a missing output face reads STALE, not CHECK FAILED (%s)" % msg))

        # ---------------------------------------------------------- N7: an unknown verdict is surfaced
        R.OUT_PATH = real_out
        legs.append((R.classify("SOMETHING_ELSE", "POWERED_ALL") == "UNCLASSIFIED",
                     "an unknown verdict word cannot hide inside a bucket"))

    finally:
        R.OUT_PATH, R.DOC_PATH, R.QUEUE_PATH = real_out, real_doc, real_queue
        for p in temps:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

    after = {p: sha(p) for p in PUBLISHED if os.path.exists(p)}
    legs.append((before == after, "the three published files are byte-identical afterwards"))

    real_rc, real_msg = R.check()
    legs.append((real_rc == 0, "with every copy gone the real face still checks green (%s)" % real_msg))

    passed = sum(1 for ok, _ in legs if ok)
    for ok, name in legs:
        print(("PASS  " if ok else "FAIL  ") + name)
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


if __name__ == "__main__":
    sys.exit(main())
