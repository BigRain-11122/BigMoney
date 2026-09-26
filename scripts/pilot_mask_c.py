"""T-70 C-arm blind-evaluation masking (session-2 face, prereg S6 design freeze).

Why: research/R-20260926-bma-pilot-C-arm.md S6 freezes the C-arm code-quality
blind scoring: same RUBRIC double-blind face as batch 1, new independent
session dir blind_eval_c/, per-task u/v pair = {A final, C final} (A re-scored
in-session = A' anchor so delta(C-A') is free of cross-session drift). C final
product = the delivered <name>.py (non-round* file), scored as-is regardless
of functional verdict -- same caliber as B products in batch 1.

Tamper-evidence chain (mirrors pilot_mask.py): assignment seed = os.urandom(16)
stored ONLY in blind_eval_c/.mask_map.json (gitignored until post-scoring
reveal); MANIFEST_c.json (committed BEFORE scoring) records sha256 of every
masked copy and of the map -- the reveal commit must hash-match.

Arm-marker neutralization extended to a/b/c arm forms (docstring face only,
code untouched, identical rules for both arms).

Contract: stdlib only; zero network; writes confined to
results/local_coding_pilot/blind_eval_c/. Exit 0 ok | 1 masking error | 2 usage.
"""

import hashlib
import io
import json
import os
import re
import sys

BASE = os.path.join("results", "local_coding_pilot")
TASKS = os.path.join(BASE, "tasks")
BLIND = os.path.join(BASE, "blind_eval_c")
MAP_PATH = os.path.join(BLIND, ".mask_map.json")
MANIFEST_PATH = os.path.join(BLIND, "MANIFEST_c.json")

ARM_MARK_RE = re.compile(r"(?i)\b(a|b|c)[ _-]?arm\b")


def neutralize(text):
    return ARM_MARK_RE.sub("the arm", text)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _c_final(adir):
    # delivered product = non-round* .py; round files are loop history, not product
    pys = [fn for fn in os.listdir(adir)
           if fn.endswith(".py") and not fn.startswith("round")]
    return os.path.join(adir, pys[0]) if len(pys) == 1 else None


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
        apath = os.path.join(tdir, "A")
        cpath = os.path.join(tdir, "C")
        if not (os.path.isdir(apath) and os.path.isdir(cpath)):
            continue
        a_py = _c_final(apath)
        c_py = _c_final(cpath)
        if c_py is None or a_py is None:
            continue  # not yet a dual-product task
        if name in m["tasks"] and not force:
            continue  # masked already; map stability guard
        # one-shot random u/v assignment, seed kept only in the gitignored map
        seed = os.urandom(16)
        bit = seed[0] & 1
        mapping = {"u": "A", "v": "C"} if bit else {"u": "C", "v": "A"}
        m["seed_hex"] = seed.hex()
        m["tasks"][name] = mapping
        out_dir = os.path.join(BLIND, name)
        os.makedirs(out_dir, exist_ok=True)
        entry = {"map": mapping}
        srcs = {"A": a_py, "C": c_py}
        for slot, arm in mapping.items():
            raw = io.open(srcs[arm], encoding="utf-8").read()
            masked = neutralize(raw)
            if ARM_MARK_RE.search(masked):
                print(f"{name}/{arm}: arm marker survived neutralization")
                return 1
            out = os.path.join(out_dir, f"sample-{name}-{slot}.py")
            io.open(out, "w", encoding="utf-8").write(masked)
            entry[slot + "_sha"] = _sha(io.open(out, "rb").read())
            entry[slot + "_source"] = os.path.relpath(
                srcs[arm], BASE).replace("\\", "/")
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
    full["_rules"] = ("arm markers -> 'the arm' (a/b/c forms, docstring"
                      " face); u/v assignment = one-shot urandom, seed only in"
                      " gitignored map; reveal commit must hash-match;"
                      " session-2 pairs = {A final, C final} per prereg S6")
    io.open(MANIFEST_PATH, "w", encoding="utf-8").write(json.dumps(full, indent=1))
    print("masked tasks: " + (", ".join(sorted(manifest)) or "(none new)"))
    return 0


def _selftest():
    import tempfile
    import pilot_mask_c as pm
    ok = 0
    # neutralization family (production call form; c-form extended per S6)
    cases = [
        ("linter (T-70 pilot task 02, A arm).", "linter (T-70 pilot task 02, the arm)."),
        ("written by the B arm", "written by the the arm"),
        ("C-arm self-fix product", "the arm self-fix product"),
        ("c arm loop round 2", "the arm loop round 2"),
        ("arm A reversed", "arm A reversed"),
    ]
    for src, want in cases:
        got = neutralize(src)
        assert got == want, (src, got, want)
        ok += 1
    assert not ARM_MARK_RE.search(neutralize("A arm B arm c-arm"))
    ok += 1
    # hermetic full-run fixture (production paths monkeypatched to a temp
    # tree; mirrors real call form incl. round-file exclusion -- r157 law)
    with tempfile.TemporaryDirectory() as td:
        old = (pm.BASE, pm.TASKS, pm.BLIND, pm.MAP_PATH, pm.MANIFEST_PATH)
        try:
            pm.BASE = os.path.join(td, "pilot")
            pm.TASKS = os.path.join(pm.BASE, "tasks")
            pm.BLIND = os.path.join(pm.BASE, "blind_eval_c")
            pm.MAP_PATH = os.path.join(pm.BLIND, ".mask_map.json")
            pm.MANIFEST_PATH = os.path.join(pm.BLIND, "MANIFEST_c.json")
            for arm in ("A", "C"):
                d = os.path.join(pm.TASKS, "01", arm)
                os.makedirs(d)
                io.open(os.path.join(d, "t.py"), "w",
                        encoding="utf-8").write('"""doc A arm."""\nx=1\n')
            # round files must NOT be picked as C product
            io.open(os.path.join(pm.TASKS, "01", "C", "round0_code.py"), "w",
                    encoding="utf-8").write("z=3\n")
            io.open(os.path.join(pm.TASKS, "01", "C", "round1_code.py"), "w",
                    encoding="utf-8").write("z=4\n")
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
                    and "C arm" not in body, body
                assert man["01"][slot + "_sha"] == _sha(io.open(p, "rb").read())
                # masked content must be the final product (x=1), never a
                # round file (z=3/z=4)
                assert "x=1" in body and "z=" not in body, body
            ok += 1
            # stability guard: re-run must not re-mask nor change the seed
            rc2 = pm.run()
            assert rc2 == 0
            map2 = json.loads(io.open(pm.MAP_PATH, encoding="utf-8").read())
            assert map2["seed_hex"] == map1["seed_hex"]
            assert map2["tasks"]["01"] == map1["tasks"]["01"]
            ok += 1
            # multi-pys A dir = skipped honestly (no arbitrary pick)
            io.open(os.path.join(pm.TASKS, "01", "A", "second.py"), "w",
                    encoding="utf-8").write("q=9\n")
            os.makedirs(os.path.join(pm.TASKS, "02", "A"))
            os.makedirs(os.path.join(pm.TASKS, "02", "C"))
            io.open(os.path.join(pm.TASKS, "02", "A", "one.py"), "w",
                    encoding="utf-8").write("a=1\n")
            io.open(os.path.join(pm.TASKS, "02", "A", "two.py"), "w",
                    encoding="utf-8").write("a=2\n")
            io.open(os.path.join(pm.TASKS, "02", "C", "one.py"), "w",
                    encoding="utf-8").write("c=1\n")
            rc3 = pm.run()
            assert rc3 == 0
            map3 = json.loads(io.open(pm.MAP_PATH, encoding="utf-8").read())
            assert "02" not in map3["tasks"], "multi-py A dir must be skipped"
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
    print("usage: pilot_mask_c.py run [--force] | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
