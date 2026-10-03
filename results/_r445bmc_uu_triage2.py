"""r445 bm-c merge UU triage leg-2: token_usage.machines both sides +
compute_audit.latest ts both sides. Read-only."""
import json
import subprocess

CREATE = 0x08000000
R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def stage(path, n):
    p = subprocess.run(["git", "-C", R, "show", f":{n}:{path}"],
                       capture_output=True, creationflags=CREATE)
    return p.stdout if p.returncode == 0 else None


for f in ("results/token_usage.json", "results/compute_audit.json"):
    print("=====", f)
    for n, tag in ((2, "OURS"), (3, "THEIRS")):
        d = json.loads(stage(f, n))
        if f.endswith("token_usage.json"):
            m = d["machines"]
            print(tag, "generated", d["generated"])
            for k, v in m.items():
                if isinstance(v, dict):
                    keys = sorted(v.keys())
                    ts_like = {kk: v[kk] for kk in keys
                               if any(t in kk for t in ("ts", "at", "time", "updated", "generated"))}
                    print("  ", k, "subkeys:", keys[:8], "| ts-ish:", ts_like)
                else:
                    print("  ", k, "=", str(v)[:80])
        else:
            print(tag, "latest.ts =", d["latest"].get("ts"),
                  "| hist[0].ts =", d["history"][0]["ts"],
                  "| hist[-1].ts =", d["history"][-1]["ts"],
                  "| len =", len(d["history"]))
