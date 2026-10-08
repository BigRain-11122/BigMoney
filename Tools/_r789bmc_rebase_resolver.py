# -*- coding: utf-8 -*-
# r789 bm-c rebase pick-2 resolver (13 UU) -- r648 sha-channel blob reads, r648 marker hard-gate,
# r516/r794 deep-ts newer-wins, r685 compute_audit latest+history-union, r782 stage-semantics aware
# (rebase: stage2=onto/origin side, stage3=replayed own side). Receipt -> results/_r789bmc_rebase_resolver.json
import subprocess, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def catfile(sha: str) -> bytes:
    r = subprocess.run(["git", "cat-file", "-p", sha], capture_output=True, cwd=ROOT)
    if r.returncode != 0 or not r.stdout:
        raise SystemExit(f"blob read FAIL {sha} rc={r.returncode} len={len(r.stdout)}")
    return r.stdout

MARKERS = (b"<<<<<<<", b">>>>>>>", b"=======")

def marker_scan(name: str, b: bytes):
    hits = [m for m in MARKERS if m in b]
    if hits:
        raise SystemExit(f"MARKER POLLUTION {name}: {hits}")
    return True

def ls_unmerged():
    r = subprocess.run(["git", "ls-files", "-u"], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, f"ls-files -u rc={r.returncode}"
    m = {}
    for line in r.stdout.decode("utf-8").splitlines():
        parts = line.split("\t")
        meta, path = parts[0], parts[1]
        f = meta.split()
        m[(path, int(f[2]))] = f[1]  # (path, stage) -> sha
    return m

UNMERGED = ls_unmerged()
DECISIONS = {
    "docs/daily_report/REPORT-2026-10-09.json": "s2",
    "docs/daily_report/REPORT-2026-10-09.md": "s2",
    "docs/live_usage/LIVE-2026-10-09.json": "s2",
    "docs/live_usage/LIVE-2026-10-09.md": "s2",
    "docs/live_usage/LIVE-latest.json": "s2",
    "docs/live_usage/LIVE-latest.md": "s2",
    "results/fundamental_b_layer_filter.json": "s2",
    "results/futures_update_status.json": "s2",
    "results/lhb_update_status.json": "s2",
    "results/update_status.json": "s2",
    "results/regime_state.json": "s2",
    "scripts/perpetual_faces_n1.py": "s2",
    "results/_attrition_guard_scan.json": "s3",
    "results/token_usage.json": "s3",
    "results/compute_audit.json": "union",
}

STAGES = {}
for path, dec in DECISIONS.items():
    assert (path, 2) in UNMERGED and (path, 3) in UNMERGED, f"stage pair missing for {path}"
    STAGES[path] = (UNMERGED[(path, 2)], UNMERGED[(path, 3)], dec)

receipt = {"round": 789, "pick": "2/3", "stage_semantics": "rebase: stage2=onto(origin/bm-a r902 tip 5c96f03b6) stage3=replayed(bm-c 50b15e0aa)", "files": {}}

for path, (s2, s3, dec) in STAGES.items():
    b2, b3 = catfile(s2), catfile(s3)
    marker_scan(path + ":stage2", b2)
    marker_scan(path + ":stage3", b3)
    if dec == "s2":
        out = b2
        why = "deep-ts newer-wins: onto side 06:29-06:31 > replay side 05:18-05:19 (bm-a r902 S6 fresher); n1.py: stage2 carries W193 five-face LANDED on origin (WAVE_CONFIGS[193]+materializer face+PASS row) + SAME-semantic w137_adjudicated {94_100,94_200} set extension -- replay side's unique content = comment wording only (cosmetic); taking stage2 verbatim = zero revert of landed origin face (r609 law)"
    elif dec == "s3":
        out = b3
        why = ("attrition: replay-side scan ts 06:44:05 > onto 06:27:25 newer-wins (this machine's own S7 scan, CLEAN rc0); "
               "token_usage: own-lane measurement live-wins -- replay side carries this round's true report growth "
               "(delta_vs_prev report_tokens_growth=1174 incl. r789 line) + freshest bm-c measurements; "
               "regenerates next round regardless (O-2325 proxy estimate face)")
    else:  # union: compute_audit latest newer-wins + history union (r685)
        j2, j3 = json.loads(b2), json.loads(b3)
        assert j2["latest"]["ts"] >= j3["latest"]["ts"], "s2 latest expected newer"
        merged = dict(j2)  # latest = s2 (newer 06:29:06)
        seen, hist = set(), []
        for row in j2["history"] + j3["history"]:
            key = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.add(key)
                hist.append(row)
        hist.sort(key=lambda r: r.get("ts", ""))
        assert hist[-1]["ts"] == j2["latest"]["ts"], "union tail must equal newer latest"
        merged["history"] = hist
        out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
        why = f"r685 law: latest newer-wins (s2 06:29:06) + history union {len(j2['history'])}+{len(j3['history'])}->{len(hist)} zero-dup ts-sorted"
    if path.endswith(".json"):
        json.loads(out.decode("utf-8"))  # validity gate (r504 law)
    (ROOT / path).write_bytes(out)
    receipt["files"][path] = {"decision": dec, "stage2_sha": s2[:16], "stage3_sha": s3[:16], "out_bytes": len(out),
                             "why": why}

# n1.py syntax gate (stage2 verbatim = origin-landed bytes; assert anyway)
import py_compile, tempfile
with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tf:
    tf.write((ROOT / "scripts/perpetual_faces_n1.py").read_bytes())
    tmp = tf.name
py_compile.compile(tmp, doraise=True)
receipt["n1_pycompile"] = "PASS"

# final worktree marker sweep on resolved files (r705 law: verify leg must gate)
bad = [p for p in STAGES if any(m in (ROOT / p).read_bytes() for m in MARKERS)]
assert not bad, f"marker residue {bad}"
receipt["marker_sweep"] = "CLEAN"

outp = ROOT / "results/_r789bmc_rebase_resolver.json"
outp.write_text(json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")
print("RESOLVER_OK files=", len(STAGES), "compute_audit_out_bytes=", receipt["files"]["results/compute_audit.json"]["out_bytes"])
