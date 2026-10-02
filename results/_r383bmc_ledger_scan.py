"""r383 bm-c ledger-chain audit probe: replicate science_gates.ledger_head's
recursive scan (raw + void-adjusted) and list all blocks with adjusted total
> 600,000, to identify the source of prev_total=613,148 seen at W113 finalize.
Read-only. Zero-window via Invoke-SilentExe."""
import json, glob, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results"

def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None

voids = {}
blocks = []
for path in sorted(glob.glob(os.path.join(ROOT, "**", "*.json"), recursive=True)):
    d = load(path)
    if not isinstance(d, dict):
        continue
    lv = d.get("ledger_voids")
    if isinstance(lv, list):
        for v in lv:
            if (isinstance(v, dict) and isinstance(v.get("batch"), str)
                    and isinstance(v.get("voided_trials"), (int, float))
                    and v.get("active", True)):
                voids[v["batch"]] = int(v["voided_trials"])
    tl = d.get("trials_ledger")
    if tl is None:
        sg = d.get("science_gates")
        if isinstance(sg, dict) and isinstance(sg.get("ledger"), dict):
            tl = sg["ledger"]
    if isinstance(tl, dict) and isinstance(tl.get("total"), (int, float)):
        applied = tl.get("voids_applied")
        applied = set(applied) if isinstance(applied, list) else set()
        adj = int(tl["total"]) - sum(n for b, n in voids.items() if b not in applied)
        blocks.append((adj, int(tl["total"]), tl.get("prev_total"), tl.get("batch_trials"),
                        tl.get("batch"), os.path.relpath(path, ROOT),
                        ",".join(sorted(applied))))

print("ACTIVE VOIDS:", voids)
blocks.sort(reverse=True)
print("TOP BLOCKS (adj, raw, prev, trials, batch, file, voids_applied):")
for b in blocks[:15]:
    print(b)
