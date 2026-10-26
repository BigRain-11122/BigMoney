"""Memory-face guard for this repo's CODELY.md (D-20261027-08 ③).

The 2026-10-27 incident: a writer appended memory rows by re-writing the whole
document as one line in a different encoding.  The file stayed in git, so the
damage was invisible until someone tried to read it -- structure gone, every
CJK character double-encoded, 19 private-use characters nobody can decode.

This guard is the cheap tripwire that makes that state impossible to commit
silently.  It checks the face, not the content:

  * the file must be real UTF-8 (no replacement characters, no PUA)
  * it must still be a multi-line document (LF count >= 5)
  * the section headings and entry markers must parse as lines
  * the entry count must not go backwards against HEAD

Usage:
  python Tools/memory_face_guard.py check [path]     # rc 0 clean, 2 breach
  python Tools/memory_face_guard.py selftest         # offline, no repo needed
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

ENTRY_RE = re.compile(r"^- \[20\d\d-", re.M)
MIN_LF = 5


def pua_count(text: str) -> int:
    return sum(1 for ch in text if 0xE000 <= ord(ch) <= 0xF8FF)


def measure(raw: bytes) -> dict:
    """Return the structural facts about a memory file's bytes."""
    facts = {"bytes": len(raw), "decodable": True}
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        facts.update({"decodable": False, "error": str(exc)})
        return facts
    facts.update({
        "chars": len(text),
        "lf": text.count("\n"),
        "sections": len(re.findall(r"^### ", text, re.M)),
        "entries": len(ENTRY_RE.findall(text)),
        "pua": pua_count(text),
        "replacement": text.count("\ufffd"),
    })
    return facts


def verdict(facts: dict, baseline_entries: int | None = None) -> list[str]:
    """Return the list of breaches; an empty list means the face is clean."""
    out = []
    if not facts.get("decodable"):
        return ["not valid utf-8 (a foreign encoding was written over it)"]
    if facts["lf"] < MIN_LF:
        out.append("flattened: only %d newlines" % facts["lf"])
    if facts["pua"]:
        out.append("%d private-use characters" % facts["pua"])
    if facts["replacement"]:
        out.append("%d replacement characters" % facts["replacement"])
    if facts["sections"] == 0:
        out.append("no '### ' section heading survived")
    if baseline_entries is not None and facts["entries"] < baseline_entries:
        out.append("entries went backwards %d -> %d"
                   % (baseline_entries, facts["entries"]))
    return out


def head_bytes(path: str) -> bytes | None:
    """Bytes of the same path at HEAD, or None when it is not in git yet."""
    try:
        proc = subprocess.run(["git", "show", "HEAD:%s" % path],
                              cwd=os.path.dirname(os.path.dirname(
                                  os.path.abspath(__file__))),
                              capture_output=True)
    except Exception:
        return None
    return proc.stdout if proc.returncode == 0 else None


def check(path: str) -> int:
    if not os.path.exists(path):
        print("memory_face_guard: %s absent -- nothing to check" % path)
        return 0
    raw = open(path, "rb").read()
    facts = measure(raw)
    rel = path.replace("\\", "/")
    prev = head_bytes(rel)
    base_entries = None
    if prev:
        prev_facts = measure(prev)
        if prev_facts.get("decodable") and prev_facts["lf"] >= MIN_LF:
            base_entries = prev_facts["entries"]
    breaches = verdict(facts, base_entries)
    print("memory_face_guard %s: bytes=%s lf=%s sections=%s entries=%s "
          "pua=%s baseline=%s"
          % (rel, facts.get("bytes"), facts.get("lf"), facts.get("sections"),
             facts.get("entries"), facts.get("pua"), base_entries))
    if breaches:
        for b in breaches:
            print("BREACH:", b)
        print("memory_face_guard: FAIL -- do not commit this face; rebuild it "
              "from the last healthy blob instead of rewriting it whole")
        return 2
    print("memory_face_guard: PASS")
    return 0


def selftest() -> int:
    checks = []

    def eq(name, got, want):
        checks.append((name, got == want, got, want))

    healthy = ("# title\n\n### User\n- [2026-10-27 04:5x r1164 bm-b] row one\n"
               "- [2026-10-27 r1165 bm-b] row two\n").encode("utf-8")
    f = measure(healthy)
    eq("healthy decodable", f["decodable"], True)
    eq("healthy entries", f["entries"], 2)
    eq("healthy lf", f["lf"], 5)
    eq("healthy clean", verdict(f), [])

    flat = healthy.replace(b"\n", b"")
    f2 = measure(flat)
    eq("flattened detected", any("flattened" in b for b in verdict(f2)), True)

    pua = healthy + "\ue511".encode("utf-8")
    f3 = measure(pua)
    eq("pua detected", any("private-use" in b for b in verdict(f3)), True)

    gbk = "- [2026-10-27 04:5x r1164] 记忆行\n".encode("gbk")
    f4 = measure(gbk)
    eq("non-utf8 detected", f4["decodable"], False)
    eq("non-utf8 message", "not valid utf-8" in verdict(f4)[0], True)

    eq("entry regression",
       any("backwards" in b for b in verdict(f, baseline_entries=3)), True)
    eq("entry growth ok", verdict(f, baseline_entries=1), [])

    passed = sum(1 for c in checks if c[1])
    for name, ok, got, want in checks:
        print("[%s] %s" % ("PASS" if ok else "FAIL", name)
              + ("" if ok else " got=%r want=%r" % (got, want)))
    print("memory_face_guard selftest %d/%d" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        path = argv[2] if len(argv) > 2 else "CODELY.md"
        return check(os.path.abspath(path))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))