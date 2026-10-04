# -*- coding: utf-8 -*-
"""r455 bm-c structure peek for the two union faces (compute_audit history
entry identity keys; token_usage machines blocks). Read-only."""
import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(side, path):
    r = subprocess.run(
        ["git", "show", ":%s:%s" % (side, path)],
        capture_output=True, cwd=ROOT)
    return r.stdout


def main():
    for side in ("2", "3"):
        j = json.loads(blob(side, "results/compute_audit.json"))
        print("== compute_audit :%s:" % side)
        print("  top keys:", sorted(j.keys()))
        lat = j.get("latest", {})
        print("  latest keys:", sorted(lat.keys())[:10] if isinstance(lat, dict) else type(lat))
        print("  latest ts:", lat.get("ts") if isinstance(lat, dict) else "-")
        h = j.get("history", [])
        if h:
            e = h[-1]
            print("  history n=%d last-entry keys=%s" % (len(h), sorted(e.keys())[:12]))
            print("  history last entry:", json.dumps(e, ensure_ascii=False)[:260])
            print("  history first ts:", h[0].get("ts", "?"), " last ts:", e.get("ts", "?"))
            m = j.get("machines")
            if isinstance(m, dict):
                print("  machines keys:", sorted(m.keys()))
                for k, v in list(m.items())[:3]:
                    print("    %s -> %s" % (k, json.dumps(v, ensure_ascii=False)[:200]))
        print()
    for side in ("2", "3"):
        j = json.loads(blob(side, "results/token_usage.json"))
        print("== token_usage :%s:" % side)
        print("  generated:", j.get("generated"))
        m = j.get("machines")
        if isinstance(m, dict):
            for k, v in m.items():
                print("    machine %s -> %s" % (k, json.dumps(v, ensure_ascii=False)[:220]))
        print("  delta_vs_prev:", json.dumps(j.get("delta_vs_prev"), ensure_ascii=False)[:200])
    print("PEEK_DONE")


if __name__ == "__main__":
    main()
