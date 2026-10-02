"""r565 bm-b: compare local crashed-session W61 shards vs origin (bm-c takeover) shards.
Per r498/r297 adjudication law: assert scientific payload equal modulo audit envelope.
Stages: for AA files, :2: = ours (onto tree = bm-c r356 shards), :3: = mine (bm-b burns).
For shard-9/10 (staged A): index = mine; origin/main (92671123d) = bm-c's.
"""
import subprocess, json

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}: {r.stderr.decode('utf-8','replace')[:200]}")
    return r.stdout

AA = [f"results/p2cal_ext/n1_w61/shard-{i}-of-12.json" for i in [0,1,2,3,4,5,6,7,8,11]]
A_MINE = ["results/p2cal_ext/n1_w61/shard-9-of-12.json", "results/p2cal_ext/n1_w61/shard-10-of-12.json"]

def load(blob_bytes):
    return json.loads(blob_bytes.decode("utf-8"))

def split_audit(d):
    aud = d.get("audit", {})
    rest = {k: v for k, v in d.items() if k != "audit"}
    return rest, aud

results = []
for p in AA:
    ours = load(git("show", f":2:{p}"))
    mine = load(git("show", f":3:{p}"))
    o_rest, o_aud = split_audit(ours)
    m_rest, m_aud = split_audit(mine)
    same = (json.dumps(o_rest, sort_keys=True) == json.dumps(m_rest, sort_keys=True))
    results.append((p, same, o_aud.get("machine"), m_aud.get("machine"),
                    o_aud.get("elapsed_sec"), m_aud.get("elapsed_sec"),
                    str(o_aud.get("code_sha", ""))[:12], str(m_aud.get("code_sha", ""))[:12]))

for p in A_MINE:
    mine = load(git("show", f":0:{p}"))
    theirs = load(git("show", f"92671123d:{p}"))
    m_rest, m_aud = split_audit(mine)
    t_rest, t_aud = split_audit(theirs)
    same = (json.dumps(t_rest, sort_keys=True) == json.dumps(m_rest, sort_keys=True))
    results.append((p, same, t_aud.get("machine"), m_aud.get("machine"),
                    t_aud.get("elapsed_sec"), m_aud.get("elapsed_sec"),
                    str(t_aud.get("code_sha", ""))[:12], str(m_aud.get("code_sha", ""))[:12]))

all_same = True
for p, same, om, mm, oe, me, ocs, mcs in results:
    print(f"{p}: payload_equal={same} origin.machine={om} mine.machine={mm} elapsed(o/m)={oe}/{me} code_sha(o/m)={ocs}/{mcs}")
    if not same:
        all_same = False
print("ALL_PAYLOAD_EQUAL:", all_same)
print("N compared:", len(results))
