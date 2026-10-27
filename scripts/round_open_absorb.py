"""Which of the files in this working tree did a dead window leave behind?

`state-bm-c.json` carries ~70 `absorb_note` keys: windows that wrote real work and died
before the closeout commit. Detecting them has been done by hand every time, in a
different way each time (compare `git log` to `round_no`, re-read the shard dir, look at
mtimes), and the r1308 window is the current instance -- two new scripts, a new artifact,
a new digest and a smoke edit sat uncommitted at round open with no record of intent.

The hand test does not actually work at the moment it matters. Tonight `git log` and
`round_no` AGREED (both 1307) because the dead window never advanced the counter, so the
r1219 "the two faces disagree -> absorb" rule sees nothing. What distinguishes a dead
window's product from ordinary round noise is not the round number, it is the KIND of file:
the chain rewrites `results/`, `docs/`, `fleet/machines/`, `data/` every round, but nothing
but a person (or an agent) writes `scripts/`, `research/digests/`, `knowledge/`, `Tools/`,
`firm/` or `smoke_test.py`.

So: a dirty SOURCE-side file, or any new file that is not scratch, is work that is not
where work belongs -- it is only in this tree. A dirty regenerable face is what the chain
looks like mid-round. That classification is the whole tool.

  python scripts/round_open_absorb.py            # read-only report, rc 3 if absorb is owed
  python scripts/round_open_absorb.py --selftest

Exit codes: 0 = clean or chain-noise only, 3 = a dead window's product is uncommitted
(also printed one path per line), 2 = git could not be read.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Faces the S6 chain, the updaters and the round closeout rewrite every round. A dirty
# TRACKED file here is what a half-finished round looks like, not a lost product.
VOLATILE_PREFIXES = (
    "results/",
    "docs/",
    "data/",
    "fleet/machines/",
    "logs/",
    "media/",
)
VOLATILE_FILES = (
    "fleet/machine-health.json",
    "fleet/backlog.md",
)

# Scratch and caches: never reported either way.
IGNORE_PREFIXES = (
    ".codely-cli/",
    ".git/",
    "__pycache__/",
    ".venv/",
    "node_modules/",
)
IGNORE_SUFFIXES = (".pyc", ".log", ".tmp")

VERDICT_CLEAN = "CLEAN"
VERDICT_NOISE = "NOISE_ONLY"
VERDICT_ABSORB = "ABSORB_OWED"


def _norm(path):
    return path.replace("\\", "/")


def _is_ignored(path):
    p = _norm(path)
    if any(p.startswith(pref) for pref in IGNORE_PREFIXES):
        return True
    if "/__pycache__/" in p or p.startswith("__pycache__/"):
        return True
    return p.endswith(IGNORE_SUFFIXES)


def _is_volatile(path, untracked):
    """Untracked is decisive: a NEW artifact under results/ is a product, not a face.

    The r1308 case is exactly this -- `results/etf_book_window_decomp.json` was brand new
    on disk and appeared in no commit. `git status` says `??`, which no chain leg produces
    (the chain overwrites tracked faces, it does not invent files).
    """
    if untracked:
        return False
    p = _norm(path)
    if p in VOLATILE_FILES:
        return True
    return any(p.startswith(pref) for pref in VOLATILE_PREFIXES)


def classify(entries):
    """entries: iterable of (code, path). Returns (verdict, absorb, noise, ignored).

    `code` is the two-character porcelain code; `untracked` is code == '??'.
    """
    absorb, noise, ignored = [], [], []
    for code, path in entries:
        if _is_ignored(path):
            ignored.append((code, path))
            continue
        untracked = code.strip() in ("??", "A", "AM")
        if _is_volatile(path, untracked):
            noise.append((code, path))
        else:
            absorb.append((code, path))
    if absorb:
        verdict = VERDICT_ABSORB
    elif noise:
        verdict = VERDICT_NOISE
    else:
        verdict = VERDICT_CLEAN
    return verdict, absorb, noise, ignored


def read_porcelain(root=ROOT):
    """Parse `git status --porcelain -z`. Rename entries carry a second NUL field."""
    out = subprocess.run(
        ["git", "status", "--porcelain", "-z"],
        cwd=root, capture_output=True, timeout=120,
    )
    if out.returncode != 0:
        raise RuntimeError("git status rc=%d: %s"
                           % (out.returncode, out.stderr.decode("utf-8", "replace")[:200]))
    tokens = out.stdout.decode("utf-8", "replace").split("\0")
    entries, i = [], 0
    while i < len(tokens):
        tok = tokens[i]
        i += 1
        if len(tok) < 4:
            continue
        code, path = tok[:2], tok[3:]
        if code[0] in "RC":  # rename/copy: origin path follows in its own field
            i += 1
        entries.append((code, path))
    return entries


def main(argv):
    if "--selftest" in argv:
        return selftest()
    try:
        entries = read_porcelain()
    except Exception as exc:  # noqa: BLE001 - reported, not swallowed
        print("MECHANISM-FAILURE %s" % exc)
        return 2
    verdict, absorb, noise, ignored = classify(entries)
    payload = {
        "schema": "round_open_absorb/v1",
        "machine": "bm-c",
        "verdict": verdict,
        "n_absorb": len(absorb),
        "n_noise": len(noise),
        "n_ignored": len(ignored),
        "absorb": [{"code": c, "path": p} for c, p in absorb],
        "noise": [{"code": c, "path": p} for c, p in noise],
        "read": (
            "source-side dirt or a never-committed file is a dead window's product; a "
            "dirty regenerable face is what a chain run looks like"
        ),
    }
    path = os.path.join(ROOT, "results", "_round_open_absorb.bm-c.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("verdict=%s absorb=%d noise=%d ignored=%d -> %s"
          % (verdict, len(absorb), len(noise), len(ignored),
             os.path.relpath(path, ROOT)))
    for code, p in absorb:
        print("  ABSORB %s %s" % (code, p))
    return 3 if verdict == VERDICT_ABSORB else 0


def selftest():
    legs = []

    def eq(label, got, want):
        legs.append((label, got == want, "got=%r" % (got,)))

    # 1. an untracked script is a lost product
    v, a, _, _ = classify([("??", "scripts/new_thing.py")])
    eq("untracked script => ABSORB", (v, len(a)), (VERDICT_ABSORB, 1))

    # 2. an edited smoke file is a lost product
    v, _, _, _ = classify([(" M", "smoke_test.py")])
    eq("edited smoke_test.py => ABSORB", v, VERDICT_ABSORB)

    # 3. a dirty chain face is noise, not a product
    v, _, n, _ = classify([(" M", "results/etf_book_production/CARD.md")])
    eq("dirty card face => NOISE", (v, len(n)), (VERDICT_NOISE, 1))

    # 4. but a NEW artifact under results/ is a product -- the r1308 case exactly
    v, a, _, _ = classify([("??", "results/etf_book_window_decomp.json")])
    eq("new results artifact => ABSORB", (v, len(a)), (VERDICT_ABSORB, 1))

    # 5. nothing dirty
    eq("empty tree => CLEAN", classify([])[0], VERDICT_CLEAN)

    # 6. scratch is ignored either way
    v, _, _, ig = classify([("??", ".codely-cli/tmp/scratch.py"),
                            ("??", "scripts/__pycache__/x.pyc")])
    eq("scratch ignored", (v, len(ig)), (VERDICT_CLEAN, 2))

    # 7. a deleted source file is a product too (someone removed a module on purpose)
    v, _, _, _ = classify([(" D", "scripts/old_thing.py")])
    eq("deleted script => ABSORB", v, VERDICT_ABSORB)

    # 8. knowledge/ and research/ edits are product
    v, a, _, _ = classify([(" M", "knowledge/METHODOLOGY_ASSETS.md"),
                           ("??", "research/digests/DIGEST-x.md")])
    eq("knowledge+digest => ABSORB(2)", (v, len(a)), (VERDICT_ABSORB, 2))

    # 9. absorb wins when both classes are present (the r1308 tree is exactly mixed)
    v, a, n, _ = classify([("??", "scripts/a.py"), (" M", "docs/live_usage/LIVE-latest.md")])
    eq("mixed tree => ABSORB, both counted", (v, len(a), len(n)), (VERDICT_ABSORB, 1, 1))

    # 10. exit-code contract: 0 clean/noise, 3 absorb
    eq("rc map", (0 if classify([(" M", "results/x.json")])[0] != VERDICT_ABSORB else 3,
                  0 if classify([])[0] != VERDICT_ABSORB else 3,
                  3 if classify([("??", "Tools/t.py")])[0] == VERDICT_ABSORB else 0),
       (0, 0, 3))

    # 11. a rename entry reports the destination as the product (parser, not classifier)
    entries = [("R ", "scripts/b.py", "scripts/a.py")]
    v, a, _, _ = classify([(e[0], e[1]) for e in entries])
    eq("rename reports destination", (v, a[0][1]), (VERDICT_ABSORB, "scripts/b.py"))

    # 12. the live tree is readable and yields a known verdict (this is the round-open call)
    try:
        live = read_porcelain()
        lv = classify(live)[0]
        ok, detail = lv in (VERDICT_CLEAN, VERDICT_NOISE, VERDICT_ABSORB), "live=%s n=%d" % (lv, len(live))
    except Exception as exc:  # noqa: BLE001
        ok, detail = False, str(exc)
    legs.append(("live tree readable", ok, detail))

    failed = [l for l in legs if not l[1]]
    for label, ok, detail in legs:
        print("[%s] %s | %s" % ("PASS" if ok else "FAIL", label, detail))
    print("selftest %d/%d PASS" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))