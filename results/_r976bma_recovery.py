# r976 surgical recovery: extract orphaned absorb5 (4b612f4da) chain-product faces to worktree
# (skip live daemon faces: autofill/dispatcher/satengine -- disk live versions are newer)
import subprocess, os

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
SRC = "4b612f4da"
SKIP = {
    "results/autofill_state.bm-a.json",
    "results/dispatcher_state.bm-a.json",
    "results/saturation_engine/face_bm-a.json",
    "results/saturation_engine/history_bm-a.jsonl",
    "results/saturation_engine/state_bm-a.json",
}
FILES = [
    "results/_r976bma_ca_union.py",
    "results/compute_audit.bm-a.json",
    "results/compute_audit.json",
    "results/futures_update_status.bm-a.json",
    "results/futures_update_status.json",
    "results/heat_update_status.bm-a.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.bm-a.json",
    "results/lhb_update_status.json",
    "results/moneyflow_update_status.json",
    "results/pool_dualrun.bm-a.jsonl",
    "results/regime_state.bm-a.json",
    "results/regime_state.json",
    "results/repo_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.bm-a.json",
    "results/update_status.json",
    "results/zt_pool_update_status.bm-a.json",
    "results/zt_pool_update_status.json",
]
assert len(FILES) == 20
for f in FILES:
    assert f not in SKIP, f"skip list overlap: {f}"
    r = subprocess.run(["git", "show", f"{SRC}:{f}"], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, f"git show failed for {f}: {r.stderr[:200]}"
    dst = os.path.join(ROOT, f.replace("/", os.sep))
    with open(dst, "wb") as fh:
        fh.write(r.stdout)
    print("recovered", f, len(r.stdout), "bytes")
print("RECOVERY DONE: 20 chain-product faces extracted from orphan 4b612f4da")
