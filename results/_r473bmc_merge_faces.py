import subprocess, io, sys

CREATE = 0x08000000
def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True, creationflags=CREATE)
    out = (r.stdout or b"").decode("utf-8", "replace")
    return r.returncode, out

BASE = "35a0d891a"      # merge-base (pre-S0 origin tip)
ORIGIN = "origin/main"
MINE = "d9f77008f"      # my round commit
PRE_MERGE = "8496b039c" # my S0 merge point

rc, origin_faces = git("diff", "--name-only", BASE, ORIGIN)
rc2, mine_faces = git("diff", "--name-only", PRE_MERGE, MINE)
assert rc == 0 and rc2 == 0, (rc, rc2)
o = set(f.strip() for f in origin_faces.splitlines() if f.strip())
m = set(f.strip() for f in mine_faces.splitlines() if f.strip())
both = sorted(o & m)

LANE_MARKS = ("bm-c", "saturation_engine/face_bm-c", "saturation_engine_state.bm-c",
              "_r47", "_r472bmc", "_r473bmc")
def is_my_lane(f):
    return ("bm-c" in f) or f.startswith("results/_r47")

uu_expected = {"results/dashboard_status.js", "results/dashboard_status.json",
               "results/prospect_paper/_summary.json",
               "results/prospect_promotion/_summary.json",
               "results/runnable_pool.json", "results/scorecard_v1.json",
               "results/strategy_scorecard.json"}

out = io.open("results/_r473bmc_merge_faces.txt", "w", encoding="utf-8")
out.write(f"origin_wave_faces={len(o)} my_round_faces={len(m)} both_changed={len(both)}\n\n")
regen_take_origin, lane_keep_mine, pool_special = [], [], []
for f in both:
    if f == "results/runnable_pool.json":
        pool_special.append(f)
    elif is_my_lane(f):
        lane_keep_mine.append(f)
    else:
        regen_take_origin.append(f)
out.write("POOL_SPECIAL (per-entry law):\n" + "\n".join(pool_special) + "\n\n")
out.write("LANE_KEEP_MINE (ours-live-wins):\n" + "\n".join(lane_keep_mine) + "\n\n")
out.write("REGEN_TAKE_ORIGIN (origin-newer-wins):\n" + "\n".join(regen_take_origin) + "\n\n")
out.write("UU_CHECK: all 7 expected UU in both-set: " +
          str(uu_expected <= set(both)) + "\n")
out.close()
print(open("results/_r473bmc_merge_faces.txt", encoding="utf-8").read())
