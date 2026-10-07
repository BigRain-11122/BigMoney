"""r731 bm-c S3 probe: SAT engine status, board open count, post_review
carryover face, idle verdict, orphan face count. Facts JSON ->
results/_r731bmc_s3probe.json. Pattern credit: r726-r730 round S3 faces."""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    facts = {"round": 731}
    # SAT engine liveness (bm-c = Tools face)
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Tools",
                        "saturation_engine.py"), "status"],
                       capture_output=True, cwd=ROOT)
    facts["sat_rc"] = p.returncode
    facts["sat_tail"] = p.stdout.decode("utf-8", "replace").strip().splitlines()[-1:] \
        if p.stdout else []

    # board: fleet/tasks/*.json total + open
    total = 0
    openn = 0
    for f in glob.glob(os.path.join(ROOT, "fleet", "tasks", "*.json")):
        total += 1
        try:
            with open(f, encoding="utf-8") as fh:
                t = json.load(fh)
            if str(t.get("status", "")).lower() == "open":
                openn += 1
        except Exception:
            pass
    facts["board_total"] = total
    facts["board_open"] = openn

    # post_review carryover: latest daily report post_review line
    facts["post_review"] = None
    rp = os.path.join(ROOT, "docs", "daily_report", "REPORT-20261008.md")
    if os.path.exists(rp):
        txt = open(rp, encoding="utf-8", errors="replace").read()
        m = re.search(r"(?im)^.*post[_ ]review.*$", txt)
        if m:
            facts["post_review"] = m.group(0).strip()[:400]

    # idle verdict face (EngineTick carrier writes this)
    facts["idle"] = None
    ip = os.path.join(ROOT, "results", "idle_trigger.bm-c.json")
    if os.path.exists(ip):
        try:
            facts["idle"] = json.load(open(ip, encoding="utf-8"))
        except Exception:
            pass

    # orphan face count (round-zero probe report)
    facts["orphans"] = None
    op = os.path.join(ROOT, "results", "_orphan_face_probe.json")
    if os.path.exists(op):
        try:
            oj = json.load(open(op, encoding="utf-8"))
            facts["orphans"] = oj.get("orphans")
        except Exception:
            pass

    out = os.path.join(ROOT, "results", "_r731bmc_s3probe.json")
    json.dump(facts, open(out, "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: v for k, v in facts.items() if k != "idle"}, indent=1))
    idle = facts.get("idle") or {}
    print("idle face: green=%s idle_rounds=%s agenda_starved=%s ram_free_pct=%s" % (
        idle.get("green_idle"), idle.get("idle_rounds"),
        idle.get("agenda_starved"), idle.get("ram_free_pct")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
