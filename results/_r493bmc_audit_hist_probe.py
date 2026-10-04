import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, timeout=30)
    return json.loads(r.stdout.decode("utf-8"))


o = show("HEAD", "results/compute_audit.json")
t = show("MERGE_HEAD", "results/compute_audit.json")
oh, th = o["history"], t["history"]
o_ts = [r.get("ts") for r in oh]
t_ts = [r.get("ts") for r in th]
print("ours hist len", len(oh), "tail5", o_ts[-5:])
print("theirs hist len", len(th), "tail5", t_ts[-5:])
print("theirs-only ts:", sorted(set(t_ts) - set(o_ts)))
print("ours-only ts:", sorted(set(o_ts) - set(t_ts)))
print("prefix identical:", o_ts[:max(len(o_ts), len(th) and 0)][:5],
      "head-equal:", o_ts[:len(t_ts)] == t_ts if len(o_ts) >= len(th)
      else t_ts[:len(o_ts)] == o_ts)
