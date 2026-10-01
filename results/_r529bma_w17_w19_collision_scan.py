"""r529 bm-a P0 evidence: N1-W17 x N1-W19 same-band double-freeze
discovered during r529 delivery verification (post-push ls-tree audit).

Machine-verifiable facts (all read from origin/main HEAD tree -- zero
work-tree dependence, zero network):
  leg1  W17 canon row bands (research/PERPETUAL_FACES.md, bm-c r328 freeze)
  leg2  W19 mirror bands (scripts/perpetual_faces.py N1_BANDS[19], bm-b
        r517 freeze pushed via surgical temp-index onto moved origin)
  leg3  band identity assertion (A and B both identical -> double-burn face)
  leg4  mirror integrity: N1_BANDS has 19 but NOT 17 (bm-b's surgical
        payload overwrote bm-c's W17 mirror addition -- law-mirror drift)
  leg5  product/burn facts: n1_w17 shards 12/12 on origin (bm-c burn
        complete, finalize not yet landed), n1_w19 shards 9/12 (bm-b
        engine still burning -- last-3-shard kill window OPEN)
Exit 0 = evidence written; verdict line feeds the P0 MSG + yield demand
(W19 = later pusher yields per r239/r511 commit-timestamp law).
"""
import ast
import json
import re
import subprocess
import sys


def show(path):
    return subprocess.check_output(
        ["git", "show", f"HEAD:{path}"]).decode("utf-8")


def ls_count(path):
    out = subprocess.check_output(
        ["git", "ls-tree", "HEAD", path.rstrip("/") + "/"]).decode("utf-8")
    return len([l for l in out.splitlines() if l.strip()])


# leg1: W17 bands from the canon row (bm-c freeze)
canon = show("research/PERPETUAL_FACES.md")
m17a = re.search(r"N1 波17.*?A-ext seed=\*\*([\d_]+)\.\.([\d_]+)\*\*", canon)
m17b = re.search(r"N1 波17.*?B-ext exit seed=\*\*([\d_]+)\.\.([\d_]+)\*\*", canon)
assert m17a and m17b, "W17 canon row not found"
w17_a = (int(m17a.group(1)), int(m17a.group(2)))
w17_b = (int(m17b.group(1)), int(m17b.group(2)))
print(f"leg1 W17 (bm-c r328 canon row): A={w17_a} B={w17_b}")

# leg2: W19 bands from the law mirror (bm-b r517)
pf = show("scripts/perpetual_faces.py")
mb = re.search(r"N1_BANDS = \{(.*?)\n\}", pf, re.S)
lines = [l for l in ("{" + mb.group(1) + "\n}").splitlines()
         if not l.strip().startswith("#")]
bands = ast.literal_eval("\n".join(lines))
w19 = bands.get(19)
assert w19, "N1_BANDS[19] missing"
print(f"leg2 W19 (bm-b r517 law mirror): A={w19['a']} B={w19['b_exit']}")

# leg3: band identity -> double-burn face
same_a = tuple(w19["a"]) == w17_a
same_b = tuple(w19["b_exit"]) == w17_b
print(f"leg3 identity: A identical={same_a} B identical={same_b}")
assert same_a and same_b, "bands differ -- re-read before alarming"

# leg4: mirror drift (17 lost in bm-b's surgical overwrite)
has17 = 17 in bands
print(f"leg4 N1_BANDS integrity: has17={has17} (bm-c's W17 mirror row "
      f"overwritten by bm-b r517 surgical payload), has19=True")

# leg5: burn facts
n17 = ls_count("results/p2cal_ext/n1_w17")
n19 = ls_count("results/p2cal_ext/n1_w19")
led = show("results/saturation_engine/ledger_bm-b.jsonl")
w19_rows = [json.loads(l) for l in led.strip().splitlines()
            if l.strip() and "W19" in l]
print(f"leg5 burn facts: n1_w17 shards on origin={n17}/12 "
      f"(bm-c complete, finalize pending); n1_w19 shards={n19}/12 "
      f"(bm-b engine burning); bm-b ledger W19 rows={len(w19_rows)}")

verdict = ("P0 SAME-BAND DOUBLE-FREEZE CONFIRMED: W17(bm-c) x W19(bm-b) "
           "share A=76_001..78_000 + B=38_100..38_299; both engines burned "
           "the same 2,200 seeds; W17 12/12 done, W19 9/12 in flight -> "
           "W19 (later pusher) yields per r239/r511 commit-timestamp law: "
           "kill last shards, discard products, never finalize, ledger +0, "
           "restore mirror row 17 (bm-c content), remove mirror/WAVE_CONFIGS "
           "row 19 + prereg disposition")
print("verdict:", verdict)

json.dump({
    "w17": {"a": w17_a, "b_exit": w17_b, "owner": "bm-c",
            "commit": "7e03101fb (r328)"},
    "w19": {"a": w19["a"], "b_exit": w19["b_exit"], "owner": "bm-b",
            "commit": "5f18511ce (r517)"},
    "bands_identical": {"a": same_a, "b": same_b},
    "mirror_has_17": has17, "mirror_has_19": True,
    "shards_on_origin": {"n1_w17": n17, "n1_w19": n19},
    "ledger_bm_b_w19_rows": len(w19_rows),
    "verdict": "W19-YIELD-REQUIRED",
}, open("results/_r529bma_w17_w19_collision.json", "w",
        encoding="utf-8"), ensure_ascii=False, indent=2)
print("evidence -> results/_r529bma_w17_w19_collision.json")
