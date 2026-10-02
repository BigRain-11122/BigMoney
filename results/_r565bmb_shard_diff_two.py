"""r565 bm-b: locate exact char difference in preregistered_doc string (mine vs origin)."""
import subprocess, json

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}")
    return r.stdout

p = "results/p2cal_ext/n1_w61/shard-0-of-12.json"
mine_s = json.loads(git("show", f":3:{p}").decode())["preregistered_doc"]
ours_s = json.loads(git("show", f":2:{p}").decode())["preregistered_doc"]
print("mine len:", len(mine_s), " origin len:", len(ours_s), " equal:", mine_s == ours_s)
# find first difference
n = min(len(mine_s), len(ours_s))
i = 0
while i < n and mine_s[i] == ours_s[i]:
    i += 1
print("first diff at char", i)
print("mine  [...]:", repr(mine_s[max(0,i-80):i+220]))
print("origin[...]:", repr(ours_s[max(0,i-80):i+220]))
# verify families/shard/a_range/b_range/batch/evidence_cutoff/law_ref/nshards equal across all 12
import difflib
AA = [f"results/p2cal_ext/n1_w61/shard-{k}-of-12.json" for k in [0,1,2,3,4,5,6,7,8,11]]
A910 = ["results/p2cal_ext/n1_w61/shard-9-of-12.json", "results/p2cal_ext/n1_w61/shard-10-of-12.json"]
allok = True
for pth in AA + A910:
    if pth in A910:
        m = json.loads(git("show", f":0:{pth}").decode())
        o = json.loads(git("show", f"92671123d:{pth}").decode())
    else:
        m = json.loads(git("show", f":3:{pth}").decode())
        o = json.loads(git("show", f":2:{pth}").decode())
    sci_keys = ["a_range", "b_range", "batch", "evidence_cutoff", "families", "law_ref", "nshards", "shard"]
    ok = all(json.dumps(m[k], sort_keys=True) == json.dumps(o[k], sort_keys=True) for k in sci_keys)
    pd_same = m["preregistered_doc"] == o["preregistered_doc"]
    if not ok:
        allok = False
    print(f"{pth.split('/')[-1]}: sci_payload_equal={ok} prereg_doc_equal={pd_same}")
print("ALL_SCI_EQUAL:", allok)
