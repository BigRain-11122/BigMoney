# -*- coding: utf-8 -*-
"""R274 bm-a: T-84 ticket progress_r274 write-back (byte-face probe first per R255/R257 laws)."""
import json, subprocess, sys, hashlib

P = "fleet/tasks/T-2026-09-26-84-P1.json"
raw = open(P, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
crlf = raw.count(b"\r\n")
lf = raw.count(b"\n") - crlf
trailing_nl = raw.endswith(b"\n")
t = json.loads(raw.decode("utf-8-sig"))
ascii_face = "\\u" in raw.decode("utf-8-sig")[:2000]  # ensure_ascii probe via escaped face
# indent probe: second line leading spaces
lines = raw.decode("utf-8-sig").splitlines()
indent = len(lines[1]) - len(lines[1].lstrip()) if len(lines) > 1 else 0
print("probe:", {"bom": bom, "crlf": crlf, "lf_only": lf, "trailing_nl": trailing_nl,
                "ensure_ascii_face": ascii_face, "indent": indent, "bytes": len(raw)})
print("fields:", sorted(t.keys()))

probe = {
    "ts": "2026-09-26 22:5x",
    "drive_probe": "D:/ absent (Get-PSDrive roots=[], os.listdir FileNotFoundError) -- s1 physical hold re-verified at R274 open",
}
t["progress_r274"] = (
    "R274 s3+s4 DELIVERED (doc-basis lanes, independent of D:\\Money hold per progress_r273): "
    "s3 = research/V60_LESSONS_INTAKE.md (funnel-vs-stack isomorphism table six layers -> G1'v2/D2/DSR+PBO/regime-layering/D5-cost-v2/D6 with "
    "frozen-line vs 20->30pct-relaxation philosophy divergence noted; Top3 triplet-collapse dedup-gate lesson -> tournament/selection prereg recipe: "
    "pre-ranking portfolio-identity probe sha256(rebalance-date holdings) + pair-corr>=0.999 collapse-to-one with honest dedup disclosure, "
    "template wiring reserved for GM sign+7-day veto window; trend-as-king four-source convergence recorded as research-priority weight, zero admission credit). "
    "s4 = research/V60_ASSET_MERGE.md (asset merge list to CEO: 8-row what-merges-where table, two CEO physical items -- D:\\Money re-mount or "
    "TRANSFER plan-A git branch or lane handover; System B assets via git-branch push or croc; supply face = our LHB/moneyflow/THS collectors ready). "
    "s1 re-probe at R274 open: D:/ still absent, hold continues (sole legal deferral, resume paths in ticket). "
    "Three-state: s3/s4 legislation-committed, acceptance = next post_review; s1/s2 blocked on physical dependency."
)
out = json.dumps(t, ensure_ascii=ascii_face, indent=1, separators=(",", " : "))
if trailing_nl:
    out += "\n"
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
open(P, "wb").write(data)
print("written bytes:", len(data))
# self-verify: reload + stat face
t2 = json.loads(open(P, "rb").read().decode("utf-8-sig"))
assert t2["progress_r274"].startswith("R274"), "field missing"
print("reload ok, progress_r274 present")
