"""r380 bm-b push-storm pre-resolve probe: HANDOVER anchor sides + REPORT twin ts."""
import subprocess
import re


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                          capture_output=True).stdout


for st in ("2", "3"):
    b = blob(st, "research/HANDOVER.md").decode("utf-8", errors="replace")
    heads = [l[:90] for l in b.splitlines()
             if l.startswith("> bm-a round") or l.startswith("> bm-b round")
             or l.startswith("> bm-c round") or l.startswith("## 一、")]
    print(f"--- HANDOVER stage :{st}: first 4 head/anchor lines:")
    for h in heads[:4]:
        print("   ", h)

print()
for st in ("2", "3"):
    b = blob(st, "docs/daily_report/REPORT-2026-09-28.json")
    m = re.findall(rb'"generated"\s*:\s*"([^"]+)"', b)
    print(f"REPORT.json stage :{st}: generated={m[:1]}")
    b2 = blob(st, "docs/daily_report/REPORT-2026-09-28.md")
    m2 = re.findall(rb"generated[^\n]{0,40}", b2)[:1]
    print(f"REPORT.md   stage :{st}: {m2}")

print()
# quick ts probe across all snapshot faces: deepest wall-clock value per side
FACES = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/dashboard_status.js",
]
TSRE = re.compile(rb'"((?:[a-z_]*ts|generated|updated|asof|as_of|state_updated'
                  rb'|last_seen)[a-z_]*)"\s*:\s*"?(20\d{2}-\d{2}-\d{2}'
                  rb'[T ]\d{2}:\d{2}:\d{2})')
for p in FACES:
    out = []
    for st in ("2", "3"):
        b = blob(st, p)
        hits = TSRE.findall(b)
        mx = max((h[1].decode() for h in hits), default="NONE")
        out.append(mx)
    print(f"{p}: :2:={out[0]} :3:={out[1]}")
