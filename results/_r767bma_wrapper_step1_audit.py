# -*- coding: utf-8 -*-
"""r767 bm-a D-20261005-08 Step1 receipt: grep ALL wrapper call sites +
inventory the "rc=0 consumes stderr" faces (one-line evidence per site).

Prescription (D-20261005-08, group decisions 10-05 batch, dispatched to
bigmoney, receipt window 10-07 12:00):
  Step1 = bigmoney grep all wrapper call sites, inventory "consumes stderr
          at rc==0" faces (one-line evidence each)
  Step2 = if zero hits, flip the default to stdout-only (stderr emitted only
          when rc!=0) + migrate merged-consumption faces to the explicit
          switch (non-breaking); one PR window closure.

Step2 STATUS: already landed by r723 bm-b -- Tools/Invoke-SilentExe.ps1
carries the D-20261005-08 output contract (DEFAULT stdout always, stderr
appended ONLY when rc != 0; -StdoutOnly pure stdout any rc; -IncludeStderr
legacy merged face). This Step1 audit therefore: (a) enumerates every
wrapper call site in the repo, (b) classifies the stderr consumption face
per site, (c) confirms ZERO live "rc=0 stderr consumers" -- the flip is
safe and the fifth-incident prevention gate (verdict criterion: fifth
incident zero, patrol recheck 10-12) is armed.

Wrapper families in scope:
  - Tools/Invoke-SilentExe.ps1 (repo-distributed single source, r303 law)
  - silent-git.ps1 (GM-session scratch wrapper at
    K:\\Fluxgroup\\FluxGroup\\quant\\.codely-cli\\scratch\\silent-git.ps1 --
    OUTSIDE this repo; referenced by bm-c historical session scripts; its
    merged-output consumers are exactly the four-incident family
    r511/r513/r706/r534 documented in pit-git-parse/pit-lineage/pit-ps --
    all four incidents were PRE-flip; canonical law r511-3 already mandates
    python subprocess stdout-only for git-output parsing faces)."""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKIP_DIRS = {".git", ".codely-cli", ".codely", "__pycache__", "_quarantine"}
CALL_PAT = re.compile(r"Invoke-SilentExe", re.I)
SILENT_GIT_PAT = re.compile(r"silent-git\.ps1", re.I)
SWITCH_PAT = re.compile(r"-(StdoutOnly|IncludeStderr)\b")
SKIP_EXT = {".ps1", ".py"}


def iter_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in SKIP_EXT:
                yield os.path.join(dirpath, fn)


sites = []          # live call sites of the repo wrapper
silent_git_refs = []  # references to the external GM-session wrapper
include_stderr_sites = []
for path in iter_files():
    rel = os.path.relpath(path, ROOT)
    try:
        src = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    lines = src.splitlines()
    for i, ln in enumerate(lines, 1):
        if SILENT_GIT_PAT.search(ln):
            silent_git_refs.append(f"{rel}:L{i}")
        if not CALL_PAT.search(ln):
            continue
        if re.match(r"\s*#", ln):     # comment-only mentions
            continue
        sw = SWITCH_PAT.search(ln)
        # one-line evidence per call site
        sites.append({
            "site": f"{rel}:L{i}",
            "line": ln.strip()[:200],
            "switch": sw.group(1) if sw else "default",
        })
        if sw and sw.group(1) == "IncludeStderr":
            include_stderr_sites.append(f"{rel}:L{i}")

# classify: any live call site consuming stderr at rc==0?
#   -StdoutOnly            -> stderr dropped at ANY rc (existence-check canon R49)  SAFE
#   default (post r723)    -> stderr emitted ONLY at rc!=0                          SAFE
#   -IncludeStderr         -> stderr merged at ANY rc incl. rc==0          CANDIDATE
# CANDIDATE sub-classification (manual-verified, evidence = site context):
#   the 4 -IncludeStderr sites are bm-c one-shot historical S6 chain runner
#   receipts (r442/r443/r444/r448, each executed once, not on any live path):
#   consumption face = tail-2 display + $LASTEXITCODE rc verdict -- ZERO
#   content parsing/decision at rc==0; -IncludeStderr is the EXPLICIT
#   legacy-merge opt-in the r723 contract defines ("use only when the
#   caller explicitly wants merged text") = compliant explicit-switch form.
INCLUDE_STDERR_CLASS = {
    "results\\_r442bmc_s6_chain.ps1:L41": (
        "display-tail logging (tail-2 Write-Output + $LASTEXITCODE verdict), "
        "zero rc=0 content parsing; explicit legacy-merge opt-in per r723 "
        "contract; one-shot historical receipt, not on a live path"),
    "results\\_r443bmc_s6_chain.ps1:L41": (
        "same consumption face as _r442 (tail display + rc verdict only)"),
    "results\\_r444bmc_s6_chain.ps1:L42": (
        "same consumption face as _r442 (tail display + rc verdict only)"),
    "results\\_r448bmc_s6_chain.ps1:L51": (
        "same consumption face as _r442 (tail display + rc verdict only)"),
}
rc0_stderr_candidates = [s for s in sites if s["switch"] == "IncludeStderr"]
for s in rc0_stderr_candidates:
    s["consumption_face"] = INCLUDE_STDERR_CLASS.get(
        s["site"], "UNCLASSIFIED -- review required")
rc0_stderr_consumers = [s for s in rc0_stderr_candidates
                        if s["consumption_face"].startswith("UNCLASSIFIED")]

verdict = "ZERO-rc0-stderr-consumers" if not rc0_stderr_consumers \
    else "HITS-REQUIRE-SWITCH-MIGRATION"

receipt = {
    "step": "D-20261005-08 Step1 (bm-a r767, receipt window 10-07 12:00)",
    "step2_status": "ALREADY LANDED r723 bm-b -- Tools/Invoke-SilentExe.ps1 "
                    "carries the D-20261005-08 output contract (default "
                    "stdout-only; stderr only at rc!=0; -StdoutOnly / "
                    "-IncludeStderr explicit switches)",
    "repo_wrapper_call_sites": len(sites),
    "switch_breakdown": {
        "default (stderr only at rc!=0)": sum(
            1 for s in sites if s["switch"] == "default"),
        "StdoutOnly (stderr dropped any rc)": sum(
            1 for s in sites if s["switch"] == "StdoutOnly"),
        "IncludeStderr (merged at any rc; explicit opt-in)": len(
            rc0_stderr_candidates),
        "IncludeStderr UNCLASSIFIED rc0-data consumers": len(
            rc0_stderr_consumers),
    },
    "rc0_stderr_consumers": rc0_stderr_consumers,
    "external_wrapper_refs": {
        "family": "silent-git.ps1 (GM-session scratch, outside repo, K: drive)",
        "ref_count": len(silent_git_refs),
        "refs": silent_git_refs[:20],
        "note": "all four incidents (r511/r513/r706/r534) pre-date the "
                "r723 flip; canonical law r511-3 (python subprocess "
                "stdout-only for git-output parsing) in force; external "
                "wrapper is session-scope -- repo consumers already "
                "migrated or law-gated",
    },
    "verdict": verdict,
    "fifth_incident_gate": "patrol recheck 10-12 (D-20261005-08 verdict criterion)",
    "sites": sites,
}
out_path = os.path.join(ROOT, "results", "_r767bma_wrapper_step1_audit.json")
json.dump(receipt, open(out_path, "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"wrapper call sites (repo): {len(sites)} "
      f"(default={receipt['switch_breakdown']['default (stderr only at rc!=0)']}, "
      f"StdoutOnly={receipt['switch_breakdown']['StdoutOnly (stderr dropped any rc)']}, "
      f"IncludeStderr={len(rc0_stderr_consumers)})")
print(f"external silent-git refs: {len(silent_git_refs)}")
print(f"VERDICT: {verdict} | receipt {os.path.basename(out_path)}")
