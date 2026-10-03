"""r445 bm-c merge UU triage: inspect stage2(ours)/stage3(theirs) shapes for
token_usage.json + compute_audit.json (cross-machine union faces) and list
ts/machine keys for the newer-wins measurement faces. Read-only."""
import json
import subprocess
import sys

CREATE = 0x08000000
R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def stage(path, n):
    p = subprocess.run(["git", "-C", R, "show", f":{n}:{path}"],
                       capture_output=True, creationflags=CREATE)
    if p.returncode != 0:
        return None
    return p.stdout


for f in ("results/token_usage.json", "results/compute_audit.json"):
    print("=====", f)
    for n, tag in ((1, "BASE"), (2, "OURS"), (3, "THEIRS")):
        b = stage(f, n)
        if b is None:
            print(tag, "<absent>")
            continue
        try:
            d = json.loads(b)
        except Exception as e:
            print(tag, "parse-fail", e)
            continue
        if isinstance(d, dict):
            print(tag, "dict keys:", sorted(d.keys())[:12],
                  "| ts:", d.get("ts"), "| len:", len(d))
            for k, v in list(d.items())[:6]:
                if isinstance(v, (list, dict)):
                    print("   ", k, type(v).__name__, len(v),
                          (v[-1] if isinstance(v, list) and v else ""))
                else:
                    print("   ", k, "=", str(v)[:60])
        elif isinstance(d, list):
            print(tag, "list len:", len(d), "| last:", str(d[-1])[:120])
