"""Extract and execute exactly one leg from smoke_test.py (r1560 bm-b).

The legs in smoke_test.py are top-level statements that call ``check(name, cond, detail)``.
This runner slices the source between a start anchor and its closing ``check(...)`` line and
execs it in a namespace that supplies ``check``, ``json`` and ``os``, so the leg under test is
the one on disk, verbatim -- not a re-typed copy.

    python scripts/run_e529_smoke_leg.py            # run the leg
    python scripts/run_e529_smoke_leg.py --doctor   # run it against a deliberately broken face
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = "# E529: every depth-cap arm that returns a null sentinel"
END = "check(_name529, not _bad529,"


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    doctor = "--doctor" in argv
    path = os.path.join(ROOT, "smoke_test.py")
    with io.open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith(START))
    except StopIteration:
        print("the E529 leg is not in smoke_test.py")
        return 1
    stop = None
    for i in range(start, len(lines)):
        if lines[i].startswith(END):
            stop = i
            break
    if stop is None:
        print("the E529 leg has no closing check()")
        return 1
    source = "\n".join(lines[start:stop + 1])

    face_path = os.path.join(ROOT, "results", "state_tilt", "depthcapnull_latest.json")
    if doctor:
        with io.open(face_path, encoding="utf-8") as fh:
            original = fh.read()
        face = json.loads(original)
        face.setdefault("arms", [])
        if face["arms"]:
            face["arms"][0]["sentinel"] = "NO-WITNESS"
        with io.open(face_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")

    results = []

    def check(name, cond, detail=""):
        results.append((name, bool(cond), detail))

    os.chdir(ROOT)
    if os.path.join(ROOT, "scripts") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
    namespace = {"check": check, "json": json, "os": os}
    try:
        exec(compile(source, path, "exec"), namespace)
    finally:
        if doctor:
            with io.open(face_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(original)

    failed = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            print("     %s" % detail)
    print("leg529%s: %d/%d passed" % (" (doctored)" if doctor else "",
                                      len(results) - len(failed), len(results)))
    if doctor:
        # the doctored face must be refused: a green run under --doctor is the failure
        return 1 if not failed else 0
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())