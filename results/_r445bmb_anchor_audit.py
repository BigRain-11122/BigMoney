# -*- coding: utf-8 -*-
"""_r445bmb_anchor_audit.py -- W12 surgeon full-anchor audit (read-only
w.r.t. surgeon itself): patch sub1/subn/segment die->record+continue,
redirect draft/report to AUDIT throwaway paths, exec, print ALL anchor
failures in one shot. Draft/reports from this probe are garbage and get
deleted; only the failure list matters."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = open("results/_r445bmb_w12_surgeon.py", encoding="utf-8").read()

P1 = ('def sub1(src, old, new, what):\n'
      '    """Count-verified single replace (exactly one hit)."""\n'
      '    if src.count(old) != 1:\n'
      '        die("anchor not unique (%d hits): %r" % (src.count(old),\n'
      '                                                 old[:70]) + " | " + what)\n'
      '    return src.replace(old, new)')
P1N = ('FAILS = []\n'
       'def sub1(src, old, new, what):\n'
       '    """audit: record+continue"""\n'
       '    if src.count(old) != 1:\n'
       '        FAILS.append((what, src.count(old), old))\n'
       '        return src\n'
       '    return src.replace(old, new)')
P2 = ('def subn(src, old, new, n, what):\n'
      '    """Count-verified n-hit replace."""\n'
      '    if src.count(old) != n:\n'
      '        die("anchor count %d != %d: %r" % (src.count(old), n,\n'
      '                                           old[:70]) + " | " + what)\n'
      '    return src.replace(old, new)')
P2N = ('def subn(src, old, new, n, what):\n'
       '    """audit: record+continue"""\n'
       '    if src.count(old) != n:\n'
       '        FAILS.append((what, src.count(old), old))\n'
       '        return src\n'
       '    return src.replace(old, new)')
P3 = ('def segment(src, start_marker, end_marker, include_start=True,\n'
      '            include_end=False):\n'
      '    """Cut [start_marker .. end_marker) by marker text (unique hit)."""\n'
      '    i = src.find(start_marker)\n'
      '    if i < 0:\n'
      '        die("start marker not found: %r" % start_marker[:60])\n'
      '    if src.find(start_marker, i + 1) >= 0:\n'
      '        die("start marker not unique: %r" % start_marker[:60])\n'
      '    j = src.find(end_marker, i + len(start_marker))\n'
      '    if j < 0:\n'
      '        die("end marker not found after start: %r" % end_marker[:60])')
P3N = ('def segment(src, start_marker, end_marker, include_start=True,\n'
       '            include_end=False):\n'
       '    """audit: record+continue"""\n'
       '    i = src.find(start_marker)\n'
       '    if i < 0 or src.find(start_marker, i + 1) >= 0:\n'
       '        FAILS.append(("segment:" + repr(start_marker[:50]), -1, start_marker))\n'
       '        return "", -1, -1\n'
       '    j = src.find(end_marker, i + len(start_marker))\n'
       '    if j < 0:\n'
       '        FAILS.append(("segment-end:" + repr(end_marker[:50]), -2, end_marker))\n'
       '        return "", -1, -1')
DST_OLD = 'DST = os.path.join("results", "_r445bmb_w12_runner_draft.py")'
DST_NEW = 'DST = os.path.join("results", "_r445bmb_w12_draft_AUDIT.py")'
REP_OLD = 'REPORT = os.path.join("results", "_r445bmb_w12_surgery_report.json")'
REP_NEW = 'REPORT = os.path.join("results", "_r445bmb_w12_report_AUDIT.json")'

for pat, rep, what in ((P1, P1N, "sub1"), (P2, P2N, "subn"),
                       (P3, P3N, "segment"), (DST_OLD, DST_NEW, "DST"),
                       (REP_OLD, REP_NEW, "REPORT")):
    if src.count(pat) != 1:
        print("AUDIT-PATCH-FAIL", what, src.count(pat))
        sys.exit(2)
    src = src.replace(pat, rep)

ns = {"__name__": "__main__"}
try:
    exec(compile(src, "surgeon-audit", "exec"), ns)
except SystemExit as e:
    print("[audit caught SystemExit]", e)
fails = ns.get("FAILS", [])
print("=== AUDIT RESULT: %d anchor failures ===" % len(fails))
for what, cnt, old in fails:
    print("--- [%s] count=%d" % (what, cnt))
    print("    old=%r" % (old[:180],))
    if len(old) > 180:
        print("    ...len=%d tail=%r" % (len(old), old[-90:]))
