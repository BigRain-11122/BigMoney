"""r1630 one-shot: re-price the five cost arms of the phase atlas on ONE panel.

The arms face (results/etf_book_phase_atlas_arms.json) publishes two panel digests:
baseline + buffer arms sit on 58302d9c (last 2026-11-06), while cost0/05/20/40 and
buffer_k05_cost20 sit on a1a42aee (last 2026-10-30, 5 bars short). Until they share a
panel the whole cost axis is withheld ("MIXED_WORLDS"), so five pools of evidence are
unreadable. This runner re-prices those five arms in one serial pass and appends a
timestamped line per arm to results/_r1630_costarms.out.

Throwaway: delete after the arms face is regenerated and the digests agree.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "_r1630_costarms.out"

ARMS = [
    ("cost0", ["--cost", "0.0"], "results/etf_book_phase_atlas_cost0.json"),
    ("cost05", ["--cost", "0.0005"], "results/etf_book_phase_atlas_cost05.json"),
    ("cost20", ["--cost", "0.002"], "results/etf_book_phase_atlas_cost20.json"),
    ("cost40", ["--cost", "0.004"], "results/etf_book_phase_atlas_cost40.json"),
    ("buffer_k05_cost20", ["--k", "0.05", "--cost", "0.002"],
     "results/etf_book_phase_atlas_buffer_k05_cost20.json"),
]


def log(msg):
    line = "%s %s" % (time.strftime("%Y-%m-%dT%H:%M:%S"), msg)
    print(line, flush=True)
    with OUT.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def main():
    workers = sys.argv[1] if len(sys.argv) > 1 else "8"
    log("start workers=%s arms=%d" % (workers, len(ARMS)))
    for name, flags, out in ARMS:
        t0 = time.time()
        cmd = [sys.executable, "scripts/etf_book_phase_atlas.py", "run",
               "--workers", workers, "--out", out] + flags
        p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        tail = (p.stdout or "").strip().splitlines()[-3:]
        log("arm %-18s rc=%d %.1fs out=%s | %s"
            % (name, p.returncode, time.time() - t0, out, " / ".join(tail)[:220]))
        if p.returncode != 0:
            log("arm %-18s STDERR %s" % (name, (p.stderr or "")[-400:]))
    # let the arms summariser see the new digests
    t0 = time.time()
    p = subprocess.run([sys.executable, "scripts/etf_book_phase_atlas_arms.py", "run"],
                       cwd=str(ROOT), capture_output=True, text=True)
    log("arms summariser rc=%d %.1fs" % (p.returncode, time.time() - t0))
    try:
        d = json.loads((ROOT / "results/etf_book_phase_atlas_arms.json").read_text(encoding="utf-8"))
        pc = d.get("panel_coherence") or {}
        log("panel_coherence verdict=%s panels=%s comparable=%s withheld=%s"
            % (pc.get("verdict"), pc.get("panels"), pc.get("comparable_arms"),
               pc.get("withheld_arms")))
        for row in pc.get("panels_detail") or []:
            log("panel %s last=%s bars=%s faces=%s"
                % (row.get("digest"), row.get("last"), row.get("bars"), ",".join(row.get("faces") or [])))
    except Exception as exc:  # noqa: BLE001 - a one-shot reporter, not a gate
        log("post-read failed: %s: %s" % (type(exc).__name__, exc))
    log("done")


if __name__ == "__main__":
    main()
