#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2111 evidence: do the pages the guard flags really carry a literal '%%' today?

reads results/page_fmt_guard.scan.json, takes every LITERAL_DOUBLE_PCT finding that sits
inside a writer call, resolves the .md path that file publishes to, and counts '%%' in the
page on disk.  A page that already carries '%%' is proof the leak shipped, not a theory.
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "page_fmt_guard.scan.json")
MD = re.compile(r"""["']((?:research|docs|results)[\\/][^"']*\.md)["']""")


def main():
    face = json.load(io.open(FACE, encoding="utf-8"))
    writer_leaks = [h for h in face["hazards"]
                    if h["kind"] == "LITERAL_DOUBLE_PCT" and h.get("where") == "writer"
                    and "page_fmt_guard" not in h["file"]]
    checked, leaked = [], []
    for h in writer_leaks:
        src = io.open(os.path.join(ROOT, h["file"]), encoding="utf-8-sig", errors="replace").read()
        for md in sorted(set(MD.findall(src))):
            path = os.path.join(ROOT, md.replace("\\", os.sep).replace("/", os.sep))
            if not os.path.exists(path) or path in checked:
                continue
            checked.append(path)
            n = io.open(path, encoding="utf-8", errors="replace").read().count("%%")
            if n:
                leaked.append({"page": md.replace("\\", "/"), "double_pct": n,
                               "script": h["file"], "line": h["line"]})
    out = {
        "schema": "page-fmt-guard-leak-verify/v1",
        "kind": "page_fmt_guard_leak_verify",
        "writer_leak_findings": len(writer_leaks),
        "pages_checked": len(checked),
        "pages_carrying_literal_double_pct": len(leaked),
        "leaked_pages": leaked,
        "verdict": "SHIPPED_LITERAL_DOUBLE_PCT" if leaked else "NO_SHIPPED_LEAK_FOUND",
    }
    path = os.path.join(ROOT, "results", "_r2111bmc_leak_verify.json")
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print("pages_checked=%d leaked=%d verdict=%s" % (len(checked), len(leaked), out["verdict"]))
    for r in leaked:
        print("  %s  %%x%d  (%s:%d)" % (r["page"], r["double_pct"], r["script"], r["line"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
