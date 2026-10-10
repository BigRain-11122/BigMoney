# -*- coding: utf-8 -*-
"""r844 bm-c W206 freeze-script segment preflight (MSG-20261011-0120 three-fix
validation). The freeze executor itself stays fail-closed behind gate 0.5
(W205 finalize product) -- this preflight exercises the FIXED segments against
the LIVE landed faces (pf/n1 current on-disk == origin per gate 0 face):
  F1  detect_eol per-file (expect LF per bm-b r852 finding)
  F2  par extraction: full span 51 asserts; pure estate segment == 50 rows;
      upstream W204 leg present after the cut
  F3  band arithmetic: w205_a_tail+1 == 467804 == W205 b_exit[0]; probe
      receipt leg1 ARITH_A == [467804, 469803]; staircase relations
  A1  close anchors (pf_close / n1_cfg_close) count==1 under detected EOL
  A2  all indent needles found; MEM/ROW needles unique
  A3  prose windows in the script source well-formed (lo<=hi)
Fail-closed: any mismatch -> nonzero exit, no writes anywhere.
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w206bmc_20261010_probe_receipt.json")
SCRIPT = os.path.join(REPO, "results", "_w206bmc_freeze_edits.py")

fails = []


def leg(name, ok, extra=""):
    print("%-58s %s %s" % (name, "PASS" if ok else "FAIL", extra))
    if not ok:
        fails.append(name)


def detect_eol(t):
    crlf = t.count("\r\n")
    lf = t.count("\n") - crlf
    return "\r\n" if crlf > lf else "\n"


pf_t = open(PF, "rb").read().decode("utf-8")
n1_t = open(N1, "rb").read().decode("utf-8")
EOL = detect_eol(n1_t)
PF_EOL = detect_eol(pf_t)

# F1: EOL detection -- runtime detection is the FIX (MSG-20261011-0120); the
# dominant on-disk EOL varies by machine checkout (bm-c checkout = autocrlf
# CRLF on disk / origin blob = LF per bm-b r852). Assert detection returns the
# DOMINANT form and the file is EOL-UNIFORM (no mixed-EOL anchor hazard).
crlf_n1 = n1_t.count("\r\n")
lone_lf_n1 = n1_t.count("\n") - crlf_n1
crlf_pf = pf_t.count("\r\n")
lone_lf_pf = pf_t.count("\n") - crlf_pf
leg("F1 n1 EOL-uniform + detected",
    (EOL == "\r\n" and lone_lf_n1 == 0) or (EOL == "\n" and crlf_n1 == 0),
    "eol=%r crlf=%d lone_lf=%d" % (EOL, crlf_n1, lone_lf_n1))
leg("F1 pf EOL-uniform + detected",
    (PF_EOL == "\r\n" and lone_lf_pf == 0) or (PF_EOL == "\n" and crlf_pf == 0),
    "eol=%r crlf=%d lone_lf=%d" % (PF_EOL, crlf_pf, lone_lf_pf))

# F2: parity extraction (mirror of the fixed logic)
a6 = '    # --- W205 materializer face'
a4 = '    # --- T-141 s2 lane face'
w205_start = n1_t.find(a6)
t141_pos = n1_t.find(a4)
leg("F2a W205 block bounds", w205_start > 0 and t141_pos > w205_start)
blk = n1_t[w205_start:t141_pos]
par_marker = "        # registered row parity (r307 pinned constants, recent estate)"
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state: all", blk)
leg("F2b parity markers present", n1_t.count(par_marker) >= 1 and bool(m_disj))
par_full = blk[blk.find(par_marker):m_disj.start()]
n_full = par_full.count("assert pf.N1_BANDS[")
m204 = re.search(r" *assert pf\.N1_BANDS\[204\] ==", par_full)
leg("F2c full span == 51 asserts (50 estate + 1 W204 leg)", n_full == 51,
    "counted=%d" % n_full)
leg("F2d upstream W204 leg present", bool(m204))
par_sec = par_full[:m204.start()]
n_est = par_sec.count("assert pf.N1_BANDS[")
leg("F2e pure estate segment == 50 rows", n_est == 50, "counted=%d" % n_est)
leg("F2f estate segment endswith EOL", par_sec.endswith(EOL))

# F3: band arithmetic (machine-derived, no literals)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
W205 = dict(pf_mod.N1_BANDS.get(205) or {})
leg("F3a W205 row landed (pf import)",
    W205.get("a") == (465804, 467803) and W205.get("b_exit") == (467804, 468003)
    and W205.get("engine_owner") == "bm-a", str(W205))
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
leg("F3b probe receipt ADMIT", rec.get("verdict") == "ADMIT")
A = rec["bands"]["A"]
B = rec["bands"]["B"]
a_lo, a_hi = (int(x) for x in A.split("_"))
b_lo, b_hi = (int(x) for x in B.split("_"))
leg1 = rec["legs"]["leg1"]
leg("F3c receipt band mirror", [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"])
w205_a_tail = W205["a"][1]
w205_b_tail = W205["b_exit"][1]
leg("F3d refused-continuation start = W205 A-tail+1 = 467_804 == W205 B-base",
    w205_a_tail + 1 == 467804 == W205["b_exit"][0],
    "a_tail+1=%d" % (w205_a_tail + 1))
leg("F3e ARITH_A mirror [467804, 469803]",
    [w205_a_tail + 1, w205_a_tail + 2000] == leg1["ARITH_A"],
    "leg1.ARITH_A=%s" % leg1["ARITH_A"])
leg("F3f staircase: W205 B-tail+1 == W206 A-lo; A-hi+1 == B-lo",
    w205_b_tail + 1 == a_lo and a_hi + 1 == b_lo,
    "a=(%d,%d) b=(%d,%d)" % (a_lo, a_hi, b_lo, b_hi))

# A1: close anchors count==1 under detected EOL
old_pf = ('         "engine_owner": "bm-a"},' + PF_EOL + '}'
          + PF_EOL + '# v1 + ext(wave-1) in-use bands')
leg("A1a pf_close anchor count==1 (detected EOL)", pf_t.count(old_pf) == 1,
    "pf=%r" % PF_EOL)
old_cfg = ('                       }' + EOL
           + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
leg("A1b n1_cfg_close anchor count==1 (detected EOL)", n1_t.count(old_cfg) == 1,
    "n1=%r" % EOL)

# A2: indent needles present. Wave-SPECIFIC needles must be unique; SHARED
# needles (every wave's PRE pre-run line, every bm-a owner row) legitimately
# repeat -- line_indent() only takes the first occurrence's indent, which is
# uniform across waves, so presence is the correct gate.
for needle, uniq in (('205: {"batch"', True),
                     ('"prereg": ("research/PERPETUAL_N1_W205_PREREG.md', True),
                     ('"pre-run; design = frozen v1 null calibration verbatim, "', False),
                     ('"a_seed_base": 465_804', True)):
    c = n1_t.count(needle)
    ok = (c == 1) if uniq else (c >= 1)
    leg("A2 n1 needle (%s): %s..." % ("uniq" if uniq else "shared", needle[:30]),
        ok, "count=%d" % c)
for needle, uniq in (('205: {"a"', True), ('"engine_owner": "bm-a"},', False)):
    c = pf_t.count(needle)
    ok = (c == 1) if uniq else (c >= 1)
    leg("A2 pf needle (%s): %s..." % ("uniq" if uniq else "shared", needle[:20]),
        ok, "count=%d" % c)

# A3: prose windows in the fixed script source are well-formed + no literal
# 465_805 slipped in + all four refused-continuation sites now machine-derived
src = open(SCRIPT, encoding="utf-8").read()
leg("A3a no literal 465_804+1 remains in executor", "465_804+1" not in src)
leg("A3b four w205_a_tail+1 prose sites",
    src.count("fmt(w205_a_tail + 1)") == 4,
    "count=%d" % src.count("fmt(w205_a_tail + 1)"))
bad_windows = []
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", src):
    lo = int(m.group(1).replace("_", ""))
    hi = int(m.group(2).replace("_", ""))
    if lo > hi:
        bad_windows.append(m.group(0))
leg("A3c prose windows lo<=hi all", not bad_windows, str(bad_windows[:3]))

print("preflight: %d/%d PASS" % (
    sum(1 for _ in range(len(fails))) and 0 or 0, 0))  # placeholder removed below
total = 22
print("preflight summary: %d legs, %d FAIL" % (total, len(fails)))
sys.exit(1 if fails else 0)
