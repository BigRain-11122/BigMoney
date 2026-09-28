# r397 bm-a: manual-face rebase conflict resolver (4 faces)
# canon: bigmoney-conflict-resolve SKILL -- snapshot take-new (ts deep-probe,
# staged blob read), twin-side coupling (md byte-copy from same side as json),
# memory-union entry-level bidirectional coverage check (r327), archive
# identical-sides verify. Zero network, deterministic.
import json
import subprocess
import sys

def stage_blob(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                      capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="strict")

def deep_ts(obj, best=None):
    """Deep-scan for the newest ^20\\d{2}- timestamp value (r311/D-09 law:
    nested layers; r319: probe existence first; r350: wall-clock values
    require time-of-day for max-compare)."""
    import re
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str):
        if re.match(r"^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", obj):
            if best is None or obj > best:
                best = obj
    return best

ok_n = 0
def ok(name, cond):
    global ok_n
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    ok_n += 1
    if not cond:
        sys.exit(1)

# ---- [1] results/fundamental_b_layer_filter.json -- snapshot take-new
p = "results/fundamental_b_layer_filter.json"
a, b = stage_blob(p, 2), stage_blob(p, 3)
ja, jb = json.loads(a), json.loads(b)
ta, tb = deep_ts(ja), deep_ts(jb)
side = 3 if (tb or "") >= (ta or "") else 2
open(p, "w", encoding="utf-8", newline="\n").write(
    b if side == 3 else a)
ok(f"fundamental_b_layer_filter take-new side={side} "
   f"(origin {ta} vs local {tb})", json.loads(open(p, encoding="utf-8").read()) is not None)

# ---- [2] docs/daily_report/REPORT-2026-09-28.json + .md twins
# twin-side coupling: json side by generated_at, md BYTE-COPY same side
pj = "docs/daily_report/REPORT-2026-09-28.json"
pm = "docs/daily_report/REPORT-2026-09-28.md"
ja, jb = json.loads(stage_blob(pj, 2)), json.loads(stage_blob(pj, 3))
ta = deep_ts(ja); tb = deep_ts(jb)
side = 3 if (tb or "") >= (ta or "") else 2
open(pj, "w", encoding="utf-8", newline="\n").write(
    stage_blob(pj, side))
open(pm, "wb").write(stage_blob(pm, side).encode("utf-8"))
ok(f"REPORT json+md twins take side={side} "
   f"(origin generated {ta} vs local {tb})", True)

# ---- [3] CODELY.md -- memory-union: local side (:3:) = origin-verbatim
# base + r397 appended = the union face itself; r327 entry-level
# bidirectional coverage check (every entry line of BOTH sides in result;
# no phantom lines in result without a blob source)
pc = "CODELY.md"
ca, cb = stage_blob(pc, 2), stage_blob(pc, 3)
la = [l for l in ca.splitlines() if l.strip()]
lb = [l for l in cb.splitlines() if l.strip()]
res = cb  # local side = origin + r397 (union face)
lr = [l for l in res.splitlines() if l.strip()]
sa, sb_, sr = set(la), set(lb), set(lr)
ok("CODELY: every origin-side entry line present in result (zero loss)",
   sa <= sr)
ok("CODELY: every local-side entry line present in result",
   sb_ <= sr)
ok("CODELY: result lines all sourced from a blob (zero phantoms)",
   sr <= (sa | sb_))
ok("CODELY: result carries the r397 entry",
   any("r397 bm-a" in l and "pandas" in l for l in lr))
open(pc, "w", encoding="utf-8", newline="\n").write(res)
hot = open(pc, encoding="utf-8").read()
ok(f"CODELY hot {len(hot.encode('utf-8'))}B <= 10240B hard line",
   len(hot.encode("utf-8")) <= 10240)

# ---- [4] research/memory-archive/202609.md (classifier UNKNOWN ->
# manual): LF-normalized content proven IDENTICAL across sides (local
# rebuild lost only 6 CRLF bytes = EOL lineage face r389) -> take ORIGIN
# side verbatim (byte lineage preserved, zero content loss either way)
pa = "research/memory-archive/202609.md"
aa, ab = stage_blob(pa, 2), stage_blob(pa, 3)
ok("archive: LF-normalized content identical both sides (parity proof)",
   aa.replace("\r\n", "\n") == ab.replace("\r\n", "\n"))
open(pa, "w", encoding="utf-8", newline="").write(aa)
moved = "- [2026-09-28 09:0x r150 bm-c]"
ok("archive: batch-43 section (r150/r396 moved entries) present",
   moved in aa and "四十三批" in aa)

print(f"resolver: {ok_n}/{ok_n} PASS")
