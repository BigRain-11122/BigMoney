"""D-20261028-11 census -- the two shapes the decision widened the group-root/dialect
rule to, measured on THIS repo instead of asserted.

Shape A (PowerShell only): `$x = Get-Item ...` / `$x = Get-ChildItem ...` followed by a
read of `$x.Path`. `Get-Item` returns a FileInfo/DirectoryInfo with no `.Path`, so the
group root silently becomes an empty string and every probe built from it goes
`Test-Path` false while still reporting OK (FluxVerse F-20261028-01). Only
Resolve-Path's PathInfo carries `.Path`.

Shape B (dialect): a freshness gate that hashes WORKTREE bytes and compares the digest
with a recorded constant. This repo runs `core.autocrlf=true`, so the same blob is LF in
git and CRLF on disk; a digest taken over disk bytes is a property of the checkout, not
of the file (r1317 in this repo: monthly_exam_prep hashed CRLF and every frozen face
"drifted" against its own recorded triple; bm-b r1195 is the same class). A safe gate
hashes the LF-normalised bytes, which equal the blob bytes.

Both are CENSUSES, not verdicts: each hit is bucketed and the JSON face carries the
evidence, because a heuristic over 600 files has no business failing a build silently.
exit 0 = clean, 1 = a hard hit in shape A (a group-root assignment actually in use),
2 = mechanism failure.

Shape C (liveness, added r1324) is the question shape B cannot answer: a constant that
matches neither digest is either a real freeze anchor pointing at a version of the file
that is no longer current (the gate works, and every rerun aborts), or a number that is
not any version of the file (the gate never could pass). The dialect census called both
"stale"; they are opposite failures, so shape C resolves each constant against committed
blob bytes and says which one it is.

    python scripts/group_root_dialect_census.py            # write results/...+report
    python scripts/group_root_dialect_census.py --check    # exit code only (chain leg)
    python scripts/group_root_dialect_census.py --selftest # offline fixtures
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "group_root_dialect_census.json")
SKIP_DIRS = {".git", "node_modules", "_quarantine", "logs", "__pycache__",
             ".codely-cli", "media", "data"}
# Shape B only needs the RESIDENT code face. The first cut walked every .py in the tree
# and spent 64.7s of every round on 6,158 archived round scripts under results/ -- cost
# with no bearing on the question ("is a live gate hashing worktree bytes"). Archival
# trees (results/, legacy/, Money0x) are excluded by construction, not by name pattern.
RESIDENT_DIRS = ("scripts", "Tools", "firm", "live", "monitor", "engine",
                 "strategies", "content", "screening", "config", "research")

ASSIGN_A = re.compile(r"\$(?P<var>[A-Za-z_]\w*)\s*=\s*Get-(?P<cmd>Item|ChildItem)\b")
CONST_B = re.compile(r"(?P<name>FROZEN_[A-Z0-9_]*SHA[A-Z0-9_]*)\s*=\s*[\"'](?P<sha>[0-9a-f]{16,64})[\"']")
RAW_HASH = re.compile(r"sha256\(\s*(?P<fh>[A-Za-z_]\w*)\.read\(\)\s*\)")
LF_HASH = re.compile(r"sha256\(\s*[^()]*?\.replace\(\s*b?[\"']\\r\\n[\"']\s*,"
                     r"\s*b?[\"']\\n[\"']\s*\)\s*\)")
# PREREG_PATH = os.path.join(ROOT, "research", "CTA_P1.md") -- the parts after the root
# expression are joined, not just the first one (a first-cut bug here hashed the
# "research" DIRECTORY, silently produced no measurement, and printed a clean face).
PREREG_PATH = re.compile(r"PREREG_PATH\s*=\s*os\.path\.join\(\s*[A-Za-z_]\w*\s*,"
                         r"(?P<parts>(?:\s*[\"'][^\"']+[\"']\s*,?)+)\s*\)")
PART = re.compile(r"[\"']([^\"']+)[\"']")


def _walk_resident(ext):
    """Root-level files plus the resident code dirs (archival trees excluded).

    Deduplicated: the roots overlap (ROOT's walk already descends into scripts/ and
    Tools/), so yielding per root visited every resident file TWICE and the face
    published `py_files_scanned 10,736 / gated 6` for what are really 5,368 files and 3
    gates. A census whose denominator double counts is worse than no census -- the shape
    C rows printed each gate twice, which is how it was caught.
    """
    seen = set()

    def emit(p):
        if os.path.splitext(p)[1].lower() != ext:
            return None
        key = os.path.normcase(os.path.abspath(p))
        if key in seen:
            return None
        seen.add(key)
        return p

    # root-level FILES only: walking ROOT instead would descend into results/ (6,158
    # archived round scripts) and legacy/, which is the archival face this walk exists to
    # skip -- the earlier comment claimed that exclusion while the code walked the whole
    # tree, so "by construction" was untrue until the roots were narrowed here.
    for f in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, f)
        if os.path.isfile(p):
            got = emit(p)
            if got:
                yield got
    for d in RESIDENT_DIRS:
        base_root = os.path.join(ROOT, d)
        if not os.path.isdir(base_root):
            continue
        for base, dirs, files in os.walk(base_root):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for f in files:
                got = emit(os.path.join(base, f))
                if got:
                    yield got


def _walk(exts):
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1].lower() in exts:
                yield os.path.join(base, f)


def shape_a():
    """PowerShell group-root assignments that end up read as .Path."""
    files, hits = 0, []
    for p in _walk({".ps1", ".psm1"}):
        files += 1
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in ASSIGN_A.finditer(text):
            var = m.group("var")
            if re.search(r"\$" + re.escape(var) + r"\.Path\b", text):
                hits.append({"file": os.path.relpath(p, ROOT).replace("\\", "/"),
                             "line": text[:m.start()].count("\n") + 1,
                             "variable": var, "cmdlet": "Get-" + m.group("cmd")})
    return {"files": files, "hits": hits, "unaffected": files - len({h["file"] for h in hits})}


def _digests(path):
    try:
        raw = open(path, "rb").read()
    except OSError:
        return None
    return {"bytes": len(raw), "worktree_crlf": b"\r\n" in raw,
            "raw": hashlib.sha256(raw).hexdigest(),
            "lf": hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()}


def shape_b():
    """Frozen-hash gates: is the comparison taken over worktree bytes?

    For each file that carries a FROZEN_*SHA* constant next to a raw sha256(read())
    call, classify the gate and -- when the file also names its prereg path -- measure
    which digest the constant actually equals. That turns "is this a dialect bug"
    into a column: matches_lf means the constant was recorded blob-side (a raw read is
    therefore a latent false red), matches_raw means it was recorded checkout-side,
    neither means the artefact changed after the freeze and dialect is not the cause.
    """
    files, gated = 0, []
    for p in _walk_resident(".py"):
        files += 1
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        consts = list(CONST_B.finditer(text))
        if not consts or not RAW_HASH.search(text):
            continue
        rel = ["/".join(PART.findall(m.group("parts"))) for m in PREREG_PATH.finditer(text)]
        classes = []
        for c in consts:
            row = {"constant": c.group("name"), "sha16": c.group("sha")[:16],
                   "sha_full": c.group("sha"),
                   "lf_normalised_present": bool(LF_HASH.search(text))}
            if rel:
                d = _digests(os.path.join(ROOT, rel[0]))
                if d:
                    row["artifact"] = rel[0]
                    row["artifact_worktree_crlf"] = d["worktree_crlf"]
                    row["matches_raw"] = d["raw"] == c.group("sha")
                    row["matches_lf"] = d["lf"] == c.group("sha")
                    row["dialect_state"] = ("matches_raw" if row["matches_raw"] else
                                            "matches_lf" if row["matches_lf"] else
                                            "matches_neither")
            classes.append(row)
        gated.append({"file": os.path.relpath(p, ROOT).replace("\\", "/"),
                      "raw_hash_calls": len(RAW_HASH.findall(text)),
                      "constants": classes})
    latent = sum(1 for g in gated for c in g["constants"]
                 if c.get("dialect_state") == "matches_lf")
    return {"files": files, "gated_files": len(gated),
            "lf_latent_false_red": latent, "gates": gated}


def _git(args, binary=False):
    """Run git read-only from the repo root; None on any failure (never raise)."""
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True)
    except OSError:
        return None
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def _revision_digests(rel_path, limit=40):
    """Newest-first [(rev, subject, sha256(blob_bytes))], or None when git cannot answer.

    Blob bytes, not worktree bytes: on an autocrlf checkout the worktree is a property of
    this clone, while the constant was recorded against the artefact (r1317).
    """
    log = _git(["log", "--format=%H%x1f%s", "-n", str(limit), "--", rel_path])
    if log is None:
        return None
    out = []
    for line in log.splitlines():
        if not line.strip():
            continue
        rev, _, subject = line.partition("\x1f")
        blob = _git(["show", "%s:%s" % (rev, rel_path)], binary=True)
        if blob is None:
            continue
        out.append((rev, subject, hashlib.sha256(blob).hexdigest()))
    return out


def classify_freeze(constant, revisions):
    """Three states, because "stale" conflates two opposite failures.

    alive                the newest committed blob equals the constant -- the gate passes.
    amended_post_freeze  an older blob equals it and HEAD does not: the artefact moved
                         after the freeze, so the gate is working and will now abort every
                         rerun (the S7/S8 backfill case; a two-anchor gate would separate
                         "frozen" from "current" instead of blocking both).
    unmatched            no committed blob of this file equals it: the constant is not any
                         version of the file -- typed by hand, hashed with different
                         normalisation, or lifted from a different artefact.
    """
    if not revisions:
        return {"state": "no_history"}
    if revisions[0][2] == constant:
        return {"state": "alive", "head_rev": revisions[0][0][:10]}
    for i, (rev, subject, digest) in enumerate(revisions):
        if digest == constant:
            newer = revisions[:i]
            return {"state": "amended_post_freeze", "frozen_rev": rev[:10],
                    "frozen_subject": subject[:100],
                    "n_amendments": len(newer),
                    "amendments": [{"rev": r[:10], "subject": s[:100]}
                                   for r, s, _ in newer[:3]]}
    return {"state": "unmatched_any_committed_blob"}


def shape_c(gated):
    """Resolve every recorded freeze constant against git history."""
    rows, states = [], {"alive": 0, "amended_post_freeze": 0, "unmatched_any_committed_blob": 0,
                        "no_history": 0}
    for g in gated:
        for c in g["constants"]:
            art, const = c.get("artifact"), c.get("sha_full")
            if not art or not const:
                continue
            cls = classify_freeze(const, _revision_digests(art))
            states[cls["state"]] = states.get(cls["state"], 0) + 1
            row = {"file": g["file"], "constant": c["constant"], "sha16": c["sha16"],
                   "artifact": art}
            row.update(cls)
            rows.append(row)
    return {"gates": len(rows), "states": states, "rows": rows,
            "note": "blob-side resolution: 'amended_post_freeze' means the constant is a "
                    "real freeze anchor and the artefact has legitimately moved since; "
                    "'unmatched' means the gate could never have passed."}


def build():
    a, b = shape_a(), shape_b()
    c = shape_c(b["gates"])
    return {
        "script": "scripts/group_root_dialect_census.py",
        "decision": "D-20261028-11",
        "shapes": {
            "A_powershell_dot_path": {
                "ps_files_checked": a["files"], "hits": len(a["hits"]),
                "unaffected": a["unaffected"], "detail": a["hits"]},
            "B_prereg_digest_dialect": {
                "py_files_scanned": b["files"], "gated_files": b["gated_files"],
                "lf_latent_false_red": b["lf_latent_false_red"], "gates": b["gates"]},
            "C_freeze_gate_liveness": c,
        },
        "verdict": {
            "shape_a_clean": not a["hits"],
            "shape_b_latent_false_red": b["lf_latent_false_red"] == 0,
            "shape_c_no_unmatched": c["states"]["unmatched_any_committed_blob"] == 0,
        },
        "note": "census, not a verdict: shape B counts gates whose recorded constant "
                "equals the blob-side digest, i.e. the ones a raw worktree read would "
                "misreport on this autocrlf checkout.",
    }


def selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(("PASS " if cond else "FAIL ") + name + (" " + detail if detail else ""),
              flush=True)

    tmp = tempfile.mkdtemp(prefix="d11_census_")
    try:
        # shape A fixture: a bad assignment, a safe Resolve-Path, and a $x.Path that
        # belongs to a different variable (must not be reported).
        bad = os.path.join(tmp, "bad.ps1")
        open(bad, "w", encoding="utf-8").write(
            "$root = Get-Item -LiteralPath $PSScriptRoot\n"
            "$ctx.root = $root.Path\n")
        good = os.path.join(tmp, "good.ps1")
        open(good, "w", encoding="utf-8").write(
            "$root = (Resolve-Path -LiteralPath $PSScriptRoot).Path\n"
            "Write-Output $root\n")
        other = os.path.join(tmp, "other.ps1")
        open(other, "w", encoding="utf-8").write(
            "$a = Get-Item -LiteralPath .\n$b = 1\nWrite-Output $b.Path\n")
        saved = globals()["ROOT"]
        try:
            globals()["ROOT"] = tmp
            a = shape_a()
        finally:
            globals()["ROOT"] = saved
        got = {h["file"] for h in a["hits"]}
        chk("shape A flags the Get-Item .Path assignment", got == {"bad.ps1"}, str(sorted(got)))
        chk("shape A ignores Resolve-Path and unrelated variables",
            "good.ps1" not in got and "other.ps1" not in got)

        # the resident walk must not visit an overlapping root twice: the archived face
        # published gated 6 for 3 gates because every resident file was counted twice.
        os.makedirs(os.path.join(tmp, "scripts", "deep"), exist_ok=True)
        for rel in ("top.py", "scripts/a.py", "scripts/deep/b.py",
                    "results/archived_c.py"):
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)) or tmp, exist_ok=True)
            open(os.path.join(tmp, rel), "w", encoding="utf-8").write("x = 1\n")
        try:
            globals()["ROOT"] = tmp
            walked = list(_walk_resident(".py"))
        finally:
            globals()["ROOT"] = saved
        names = [os.path.relpath(p, tmp).replace("\\", "/") for p in walked]
        chk("resident walk counts each file once and skips archival trees",
            sorted(names) == ["scripts/a.py", "scripts/deep/b.py", "top.py"], str(sorted(names)))

        # shape B fixture: an LF-recorded constant (must read as latent false red) and a
        # CRLF-recorded one (a raw read is correct there, so it must NOT be flagged).
        # The fixture file must be CRLF ON DISK, otherwise raw == lf and the two states
        # are indistinguishable -- the first cut of this test passed a clean face while
        # measuring nothing (r1261 class: prove the mechanism actually happened).
        os.makedirs(os.path.join(tmp, "research"), exist_ok=True)
        doc = "line one\nline two\n"
        with open(os.path.join(tmp, "research", "p.md"), "wb") as fh:
            fh.write(doc.replace("\n", "\r\n").encode())
        with open(os.path.join(tmp, "research", "q.md"), "wb") as fh:
            fh.write(b"stale body\n")
        lf_sha = hashlib.sha256(doc.encode()).hexdigest()
        crlf_sha = hashlib.sha256(doc.replace("\n", "\r\n").encode()).hexdigest()
        stale_sha = hashlib.sha256(b"some older body\n").hexdigest()

        def _gate(name, const):
            open(os.path.join(tmp, name), "w", encoding="utf-8").write(
                'import hashlib, os\nROOT = "."\n'
                'PREREG_PATH = os.path.join(ROOT, "research", "p.md")\n'
                'FROZEN_PREREG_SHA = "%s"\ndef s(p):\n    with open(p, "rb") as fh:\n'
                '        return hashlib.sha256(fh.read()).hexdigest()\n' % const)

        _gate("gate_lf.py", lf_sha)
        _gate("gate_crlf.py", crlf_sha)
        _gate("gate_stale.py", stale_sha)
        try:
            globals()["ROOT"] = tmp
            b = shape_b()
        finally:
            globals()["ROOT"] = saved
        rows = {g["file"]: g["constants"][0] for g in b["gates"]}
        states = {k: v.get("dialect_state") for k, v in rows.items()}
        chk("shape B fixture really sits on a CRLF-checkout shape",
            all(v.get("artifact_worktree_crlf") for v in rows.values()),
            str({k: v.get("artifact_worktree_crlf") for k, v in rows.items()}))
        chk("shape B says a blob-side constant is a latent false red",
            states.get("gate_lf.py") == "matches_lf", str(states))
        chk("shape B does not cry wolf on a checkout-side constant",
            states.get("gate_crlf.py") == "matches_raw", str(states))
        chk("shape B names a stale constant as stale, not as a dialect bug",
            states.get("gate_stale.py") == "matches_neither", str(states))
        chk("shape B counts exactly the latent one", b["lf_latent_false_red"] == 1,
            "latent=%d" % b["lf_latent_false_red"])
        chk("shape B ignores files with no frozen constant",
            all(g["file"] in ("gate_lf.py", "gate_crlf.py", "gate_stale.py")
                for g in b["gates"]))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    # shape C: the classifier is pure, so its three states are pinned without git.
    # Newest-first (rev, subject, digest), exactly the shape _revision_digests returns.
    revs = [("r3" + "0" * 38, "backfill S7/S8", "new" + "0" * 61),
            ("r2" + "0" * 38, "batch finalize", "mid" + "0" * 61),
            ("r1" + "0" * 38, "prereg frozen", "frz" + "0" * 61)]
    alive = classify_freeze(revs[0][2], revs)
    chk("shape C says alive when HEAD blob equals the constant", alive["state"] == "alive",
        alive["state"])
    amended = classify_freeze(revs[2][2], revs)
    chk("shape C separates 'amended after the freeze' from 'stale' -- the gate still "
        "points at a real version of the file",
        amended["state"] == "amended_post_freeze" and amended["n_amendments"] == 2
        and amended["frozen_rev"] == "r1" + "0" * 8,
        "%s n=%s" % (amended["state"], amended.get("n_amendments")))
    unmatched = classify_freeze("zzz" * 21 + "z", revs)
    chk("shape C calls a constant that is not any committed version unmatched",
        unmatched["state"] == "unmatched_any_committed_blob", unmatched["state"])
    chk("shape C refuses to call an empty history alive",
        classify_freeze("frz" + "0" * 61, [])["state"] == "no_history")
    # the fixture gates live in a temp dir that is not a repo: shape C must degrade to
    # no_history rather than crash or claim a state it did not measure.
    try:
        globals()["ROOT"] = tmp
        cfix = shape_c(b["gates"])
    finally:
        globals()["ROOT"] = saved
    chk("shape C degrades to no_history outside a repo instead of guessing",
        cfix["states"].get("no_history", 0) == len(cfix["rows"]) and cfix["rows"],
        str(cfix["states"]))

    # live face: a mechanism failure has to be loud, a clean census quiet
    live = build()
    chk("live census produces both buckets",
        live["shapes"]["A_powershell_dot_path"]["ps_files_checked"] > 0
        and live["shapes"]["B_prereg_digest_dialect"]["py_files_scanned"] > 0,
        "ps=%d py=%d" % (live["shapes"]["A_powershell_dot_path"]["ps_files_checked"],
                         live["shapes"]["B_prereg_digest_dialect"]["py_files_scanned"]))
    lc = live["shapes"]["C_freeze_gate_liveness"]
    chk("live face resolves every recorded freeze constant to a state",
        lc["rows"] and all(r.get("state") for r in lc["rows"]), str(lc["states"]))
    print("SELFTEST " + ("OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    face = build()
    if "--check" not in argv:
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
            json.dump(face, f, ensure_ascii=False, indent=1)
        sh = face["shapes"]
        print("[d11] shape A: %d ps files / %d hits / %d unaffected"
              % (sh["A_powershell_dot_path"]["ps_files_checked"],
                 sh["A_powershell_dot_path"]["hits"],
                 sh["A_powershell_dot_path"]["unaffected"]))
        print("[d11] shape B: %d py files / %d gated / %d latent false red"
              % (sh["B_prereg_digest_dialect"]["py_files_scanned"],
                 sh["B_prereg_digest_dialect"]["gated_files"],
                 sh["B_prereg_digest_dialect"]["lf_latent_false_red"]))
        cs = sh["C_freeze_gate_liveness"]
        print("[d11] shape C: %d freeze gates / %d alive / %d amended-after-freeze / "
              "%d unmatched" % (cs["gates"], cs["states"]["alive"],
                                cs["states"]["amended_post_freeze"],
                                cs["states"]["unmatched_any_committed_blob"]))
        for r in cs["rows"]:
            if r["state"] == "amended_post_freeze":
                print("[d11]   %s %s(%s) frozen at %s, %d amendment(s) since"
                      % (r["artifact"], r["constant"], r["sha16"], r["frozen_rev"],
                         r["n_amendments"]))
            elif r["state"] == "unmatched_any_committed_blob":
                print("[d11]   DEAD GATE %s %s(%s): no committed blob matches"
                      % (r["artifact"], r["constant"], r["sha16"]))
    return 0 if face["verdict"]["shape_a_clean"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))