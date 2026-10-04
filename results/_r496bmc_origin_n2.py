"""r496 bm-c merge-prep probe: origin N2 truth check (r483-1 law) before
resolving the incoming bm-a r695/r696 wave. Read-only, zero console CJK."""
import hashlib
import json
import os
import subprocess

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
OUT = "results/_r496bmc_origin_n2.txt"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
lines = []


def gs(path):
    r = subprocess.run(["git", "show", "origin/main:" + path],
                       capture_output=True, creationflags=CNW)
    return r.returncode, r.stdout


rc, raw = gs("results/n2_w15/n2_w15_candidates.json")
if rc != 0:
    lines.append("origin candidates file: ABSENT (rc=%d)" % rc)
else:
    try:
        doc = json.loads(raw.decode("utf-8"))
        lines.append("origin candidates file: PRESENT size=%d sha256=%s" % (
            len(raw), hashlib.sha256(raw).hexdigest()))
        lines.append("  machine=%r n=%r generated=%r stage=%r" % (
            doc.get("machine"), doc.get("n"), doc.get("generated"), doc.get("stage")))
    except Exception as e:
        lines.append("origin candidates file: PRESENT but parse fail %r size=%d" % (e, len(raw)))

rc, praw = gs("results/runnable_pool.json")
if rc != 0:
    lines.append("origin pool: ABSENT rc=%d" % rc)
else:
    pool = json.loads(praw.decode("utf-8"))
    ents = [e for e in pool["entries"] if e.get("id") == "PERPETUAL-N2-W15-GENERATE"]
    if not ents:
        lines.append("origin pool: N2 entry ABSENT (retired?)")
    else:
        e = ents[0]
        lines.append("origin pool: entry status=%r done_at=%r" % (e.get("status"), e.get("done_at")))
        for s in e.get("shards", []):
            lines.append("  shard key=%r status=%r owner=%r owner_since=%r done_at=%r harvested_by=%r" % (
                s.get("key"), s.get("status"), s.get("owner"), s.get("owner_since"),
                s.get("done_at"), s.get("harvested_by")))
    lines.append("origin pool entries=%d" % len(pool["entries"]))

rc, mraw = gs("fleet/inbox/MSG-2026-10-04-2105-bma-ALL.md")
if rc == 0:
    with open("results/_r496bmc_msg2105_dump.md", "wb") as f:
        f.write(mraw)
    lines.append("MSG-2105 dumped -> results/_r496bmc_msg2105_dump.md (%d bytes)" % len(mraw))
else:
    lines.append("MSG-2105 absent at origin rc=%d" % rc)

open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("ORIGIN_N2_PROBE_DONE", OUT)
