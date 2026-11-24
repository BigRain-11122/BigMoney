"""Negative controls for r2047's cash_shelf_total_return_audit (bm-c).

Every leg drives the real code and asserts the real exit code; nothing here
touches a published file.  The four published artifacts are hashed before and
after and must come back byte-identical.

    python results/_r2047bmc_totalret_negative.py
"""

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cash_shelf_total_return_audit as M  # noqa: E402

PUBLISHED = ["scripts/cash_shelf_total_return_audit.py",
             "results/cash_shelf_total_return_audit.json",
             "research/CASH_SHELF_TOTAL_RETURN.md"]

legs = []


def leg(name, ok, detail=""):
    legs.append((name, bool(ok), detail))


def sha(rel):
    h = hashlib.sha256()
    with open(os.path.join(ROOT, rel), "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cmd()
    return rc, buf.getvalue()


def main():
    before = {p: sha(p) for p in PUBLISHED}

    published = M._load(M.FACE)
    stored = {r["code"]: (r["events"], r["dividend_source"], r["disk_vs_fresh"]) for r in published["rows"]}

    tmpdir = tempfile.mkdtemp(prefix="r2047neg_")
    up_tmp_rel = os.path.join("results", "_r2047bmc_tmp_up.json")
    face_tmp_rel = os.path.join("results", "_r2047bmc_tmp_face.json")
    doc_tmp_rel = os.path.join("research", "_r2047bmc_tmp_doc.md")
    shutil.copyfile(os.path.join(ROOT, M.UP_FACE), os.path.join(ROOT, up_tmp_rel))

    M.UP_FACE, M.FACE, M.DOC = up_tmp_rel, face_tmp_rel, doc_tmp_rel
    M.shelf_events = lambda code, px, start, end: stored[code]

    def write_face(face=None):
        f = face if face is not None else M.build()
        with io.open(os.path.join(ROOT, M.FACE), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(f, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        with io.open(os.path.join(ROOT, M.DOC), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(M.render_doc(f))
        return f

    try:
        face = write_face()
        rc, out = run(M.cmd_check)
        leg("N1 the untouched copy checks green", rc == 0, out.strip()[:160])

        # N2: a hand-nudged sourced number must fail by name, and must not be
        # reported as a stale face (r1934: the repair contract is the literal word)
        bad = json.loads(json.dumps(face))
        target = [r for r in bad["rows"] if r["code"] == "511010"][0]
        target["sourced"]["extra_cny"] = round(float(target["sourced"]["extra_cny"]) + 1.0, 2)
        write_face(bad)
        rc, out = run(M.cmd_check)
        leg("N2 a nudged sourced number fails by shelf and field, without the word STALE",
            rc == 1 and "511010" in out and "extra_cny" in out and "STALE" not in out, out.strip()[:200])

        # N3: upstream moving one byte is a stale face, not a code defect
        write_face(face)
        up_p = os.path.join(ROOT, up_tmp_rel)
        raw = io.open(up_p, encoding="utf-8").read()
        io.open(up_p, "w", encoding="utf-8", newline="\n").write(raw + " ")
        rc, out = run(M.cmd_check)
        leg("N3 upstream bytes moving one space is STALE and not CHECK FAILED",
            rc == 3 and "STALE" in out and "CHECK FAILED" not in out, out.strip()[:200])
        io.open(up_p, "w", encoding="utf-8", newline="\n").write(raw)

        # N4: turn the dividend add off -> the reading must collapse back to price-only
        real_wy = M.window_yield_bp
        M.window_yield_bp = lambda rows, bars, bpy: (0.0, 0.0)
        try:
            off = M.build()
        finally:
            M.window_yield_bp = real_wy
        row = [r for r in off["rows"] if r["code"] == "511010"][0]
        leg("N4 with the dividend add off, 511010 is back on its price line and loses the tag",
            abs(float(row["sourced"]["cagr_pct"]) - float(row["price_only"]["cagr_pct"])) < 1e-9
            and "PRICE_ONLY_UNDERSTATES_EXTRA" not in row["verdict"],
            json.dumps({"sourced": row["sourced"]["cagr_pct"],
                        "price_only": row["price_only"]["cagr_pct"],
                        "verdict": row["verdict"]}, ensure_ascii=False))

        # N5: raise the materiality bar above every observed yield -> no tag
        real_mat = M.MATERIAL_PP
        M.MATERIAL_PP = 100.0
        try:
            high = M.build()
        finally:
            M.MATERIAL_PP = real_mat
        row = [r for r in high["rows"] if r["code"] == "511010"][0]
        leg("N5 the tag is driven by MATTERIAL_PP, not hard-coded",
            "PRICE_ONLY_UNDERSTATES_EXTRA" not in row["verdict"], json.dumps(row["verdict"]))

        # N6: a missing face is stale, never a pass
        write_face(face)
        os.remove(os.path.join(ROOT, M.FACE))
        rc, out = run(M.cmd_check)
        leg("N6 a missing face is STALE, not green", rc == 3 and "STALE" in out, out.strip()[:160])

        # N7: the page losing its marker block is a defect, and is named
        write_face(face)
        doc_p = os.path.join(ROOT, M.DOC)
        doc = io.open(doc_p, encoding="utf-8").read()
        io.open(doc_p, "w", encoding="utf-8", newline="\n").write(doc.replace(M.MARK_END, ""))
        rc, out = run(M.cmd_check)
        leg("N7 a page without its marker block fails by name", rc == 1 and M.DOC in out, out.strip()[:200])

        # N8: the page printing a literal %% (r2039/r2042 family) must be caught
        write_face(face)
        io.open(doc_p, "w", encoding="utf-8", newline="\n").write(doc.replace("票面", "票面 100%%"))
        rc, out = run(M.cmd_check)
        leg("N8 a literal %%%% on the page is caught before it ships", rc == 1 and "%%" in out, out.strip()[:200])

        # N9: a hand-typed number in a rendered row must be caught, even though the
        # shelf code is still on the page (r2042 family: the page, not the JSON, ships)
        write_face(face)
        io.open(doc_p, "w", encoding="utf-8", newline="\n").write(doc.replace("| 45.9 |", "| 46.9 |"))
        rc, out = run(M.cmd_check)
        leg("N9 a hand-edited number on the page fails by shelf",
            rc == 1 and "511010" in out, out.strip()[:200])
    finally:
        for rel in (up_tmp_rel, face_tmp_rel, doc_tmp_rel):
            p = os.path.join(ROOT, rel)
            if os.path.exists(p):
                os.remove(p)
        shutil.rmtree(tmpdir, ignore_errors=True)

    after = {p: sha(p) for p in PUBLISHED}
    leg("N10 the published artifacts were never touched by this run", before == after,
        str({k: (before[k][:8], after[k][:8]) for k in before if before[k] != after[k]}))

    ok = sum(1 for _, v, _ in legs if v)
    for name, v, detail in legs:
        print(("PASS " if v else "FAIL ") + name + ((" | " + str(detail)) if (detail and not v) else ""))
    print("NEGATIVE %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


if __name__ == "__main__":
    sys.exit(main())
