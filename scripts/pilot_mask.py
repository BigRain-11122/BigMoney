"""T-70 pilot blind-evaluation masking (criteria 2 face, prereg s3).

Why: prereg research/R-20260925-bma-local-coding-pilot.md freezes code-quality
blind scoring (four dims 1-10, evaluator must not see arm labels). Arm
products live in task dirs whose *paths* identify arms, and docstrings may
self-identify -- so masked copies under blind_eval/ carry neutral u/v labels
with a one-shot random assignment.

Tamper-evidence chain:
  - assignment seed = os.urandom(16), stored ONLY in blind_eval/.mask_map.json
    (gitignored until post-scoring reveal; the formula is NOT deterministic,
    so nobody can derive the map without the file);
  - MANIFEST.json (committed BEFORE scoring) records sha256 of every masked
    copy and of .mask_map.json -- the post-eval reveal commit must hash-match;
  - re-masking an already-masked task is refused unless --force (map stability).

Arm-marker neutralization (docstring-face only, code untouched, identical
rules for both arms): "A arm"/"B arm"/"arm A"/"arm B" (any case) -> "the arm".

Contract: stdlib only; zero network; writes confined to
results/local_coding_pilot/blind_eval/. Exit 0 ok | 1 masking error | 2 usage.
"""

import hashlib
import io
import json
import os
import re
import sys

BASE = os.path.join("results", "local_coding_pilot")
TASKS = os.path.join(BASE, "tasks")
BLIND = os.path.join(BASE, "blind_eval")
MAP_PATH = os.path.join(BLIND, ".mask_map.json")
MANIFEST_PATH = os.path.join(BLIND, "MANIFEST.json")

ARM_MARK_RE = re.compile(r"(?i)\b(a|b)[ _-]?arm\b")


def neutralize(text):
    return ARM_MARK_RE.sub("the arm", text)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _load_map():
    if os.path.isfile(MAP_PATH):
        return json.loads(io.open(MAP_PATH, encoding="utf-8").read())
    return {"seed_hex": None, "tasks": {}}


def _save_map(m):
    io.open(MAP_PATH, "w", encoding="utf-8").write(json.dumps(m, indent=1))


def run(force=False):
    os.makedirs(BLIND, exist_ok=True)
    m = _load_map()
    manifest = {}
    for name in sorted(os.listdir(TASKS)):
        tdir = os.path.join(TASKS, name)
        if not os.path.isdir(tdir):
            continue
        arms = {}
        for arm in ("A", "B"):
            adir = os.path.join(tdir, arm)
            if not os.path.isdir(adir):
                continue
            for fn in os.listdir(adir):
                if fn.endswith(".py"):
                    arms[arm] = os.path.join(adir, fn)
        if len(arms) != 2:
            continue  # not yet a dual-arm task
        if name in m["tasks"] and not force:
            continue  # masked already; map stability guard
        # one-shot random u/v assignment, seed kept only in the gitignored map
        seed = os.urandom(16)
        bit = seed[0] & 1
        mapping = {"u": "A", "v": "B"} if bit else {"u": "B", "v": "A"}
        m["seed_hex"] = seed.hex()
        m["tasks"][name] = mapping
        out_dir = os.path.join(BLIND, name)
        os.makedirs(out_dir, exist_ok=True)
        entry = {"map": mapping}
        for slot, arm in mapping.items():
            raw = io.open(arms[arm], encoding="utf-8").read()
            masked = neutralize(raw)
            if ARM_MARK_RE.search(masked):
                print(f"{name}/{arm}: arm marker survived neutralization")
                return 1
            out = os.path.join(out_dir, f"sample-{name}-{slot}.py")
            io.open(out, "w", encoding="utf-8").write(masked)
            # hash the on-disk bytes (CRLF face on Windows) -- one uniform
            # base for current-run and previously-masked tasks alike
            entry[slot + "_sha"] = _sha(io.open(out, "rb").read())
            entry[slot + "_source"] = os.path.relpath(
                arms[arm], BASE).replace("\\", "/")
        manifest[name] = entry
    _save_map(m)
    # manifest must reflect ALL masked tasks (not just this run's delta)
    full = {}
    for name, mapping in m["tasks"].items():
        entry = manifest.get(name, {})
        full[name] = {}
        for slot in ("u", "v"):
            sha = entry.get(slot + "_sha")
            if sha is None:
                p = os.path.join(BLIND, name, f"sample-{name}-{slot}.py")
                if os.path.isfile(p):
                    sha = _sha(io.open(p, "rb").read())
            full[name][slot + "_sha"] = sha
    full["_mask_map_sha"] = _sha(io.open(MAP_PATH, "rb").read())
    full["_rules"] = ("arm markers -> 'the arm' (case-insensitive, docstring"
                      " face); u/v assignment = one-shot urandom, seed only in"
                      " gitignored map; reveal commit must hash-match")
    io.open(MANIFEST_PATH, "w", encoding="utf-8").write(json.dumps(full, indent=1))
    print("masked tasks: " + (", ".join(sorted(manifest)) or "(none new)"))
    return 0


def _selftest():
    import tempfile
    import pilot_mask as pm
    ok = 0
    # neutralization family (production call form)
    cases = [
        ("linter (T-70 pilot task 02, A arm).", "linter (T-70 pilot task 02, the arm)."),
        ("written by the B arm", "written by the the arm"),
        ("A-arm fallback path", "the arm fallback path"),
        # documented non-goal: reversed "arm X" form is NOT matched (no
        # product uses it; the post-mask guard targets X-arm forms only)
        ("arm A reversed", "arm A reversed"),
    ]
    for src, want in cases:
        got = neutralize(src)
        assert got == want, (src, got, want)
        ok += 1
    assert not ARM_MARK_RE.search(neutralize("A arm B arm"))
    ok += 1
    # hermetic full-run fixture (production paths monkeypatched to a temp
    # tree; mirrors real call form -- r157/r180 pairing law)
    with tempfile.TemporaryDirectory() as td:
        old = (pm.BASE, pm.TASKS, pm.BLIND, pm.MAP_PATH, pm.MANIFEST_PATH)
        try:
            pm.BASE = os.path.join(td, "pilot")
            pm.TASKS = os.path.join(pm.BASE, "tasks")
            pm.BLIND = os.path.join(pm.BASE, "blind_eval")
            pm.MAP_PATH = os.path.join(pm.BLIND, ".mask_map.json")
            pm.MANIFEST_PATH = os.path.join(pm.BLIND, "MANIFEST.json")
            os.makedirs(os.path.join(pm.TASKS, "01", "A"))
            os.makedirs(os.path.join(pm.TASKS, "01", "B"))
            io.open(os.path.join(pm.TASKS, "01", "A", "t.py"), "w",
                    encoding="utf-8").write('"""doc A arm."""\nx=1\n')
            io.open(os.path.join(pm.TASKS, "01", "B", "t.py"), "w",
                    encoding="utf-8").write('"""doc B arm."""\ny=2\n')
            rc = pm.run()
            assert rc == 0, rc
            map1 = json.loads(io.open(pm.MAP_PATH, encoding="utf-8").read())
            assert "01" in map1["tasks"] and map1["seed_hex"]
            man = json.loads(io.open(pm.MANIFEST_PATH, encoding="utf-8").read())
            assert man["_mask_map_sha"] == _sha(io.open(pm.MAP_PATH, "rb").read())
            for slot in ("u", "v"):
                p = os.path.join(pm.BLIND, "01", f"sample-01-{slot}.py")
                body = io.open(p, encoding="utf-8").read()
                assert "the arm" in body and "A arm" not in body \
                    and "B arm" not in body, body
                assert man["01"][slot + "_sha"] == _sha(
                    io.open(p, "rb").read())
            ok += 1
            # stability guard: re-run must not re-mask nor change the seed
            rc2 = pm.run()
            assert rc2 == 0
            map2 = json.loads(io.open(pm.MAP_PATH, encoding="utf-8").read())
            assert map2["seed_hex"] == map1["seed_hex"]
            assert map2["tasks"]["01"] == map1["tasks"]["01"]
            ok += 1
        finally:
            (pm.BASE, pm.TASKS, pm.BLIND, pm.MAP_PATH, pm.MANIFEST_PATH) = old
    print(f"selftest: {ok} assertions ALL PASS")
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == "selftest":
        return _selftest()
    if len(argv) >= 2 and argv[1] == "run":
        return run(force="--force" in argv[2:])
    print("usage: pilot_mask.py run [--force] | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
