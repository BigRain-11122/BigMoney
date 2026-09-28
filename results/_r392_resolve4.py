"""r392 resolve #4: parquet fail-close override (stop #4 commit 82587515).

Skill: bigmoney-conflict-resolve / parquet append-collector face.
resolve3 fail-closed on BOTH parquets because identity used the '序号'
column -- that column is the SOURCE-side per-pull row number, which
renumbers when new dates are prepended, poisoning row identity.
True identity = all columns EXCEPT '序号':
  lhb_detail.parquet    ours-only=0, theirs-only=2  (上榜日 2026-09-28)
  chunks/2026Q3.parquet ours-only=0, theirs-only=2  (上榜日 2026-09-28)
=> theirs (my round-392 pull) is a STRICT SUPERSET of ours. Whole-bytes
take side :3: = zero row loss. No same-key value drift found (both-side
rows are byte-identical after astype-str normalize).
"""
import io
import subprocess

import pandas as pd

for P in ["Money02/data/lhb/lhb_detail.parquet",
          "Money02/data/lhb/chunks/2026Q3.parquet"]:
    def blob(stage):
        return pd.read_parquet(io.BytesIO(subprocess.run(
            ["git", "show", f":{stage}:{P}"], capture_output=True).stdout))
    da, db = blob(2), blob(3)
    cols = [c for c in da.columns if c != "序号"]
    ka = set(map(tuple, da[cols].astype(str).values))
    kb = set(map(tuple, db[cols].astype(str).values))
    only_a, only_b = len(ka - kb), len(kb - ka)
    assert only_a == 0, f"{P}: ours still has unique rows, not a subset"
    raw = subprocess.run(["git", "show", f":3:{P}"], capture_output=True).stdout
    open(P, "wb").write(raw)
    check = pd.read_parquet(P)
    assert len(check) == len(db), "written parquet row count drift"
    print(f"{P}: superset take :3:theirs rows={len(db)} "
          f"(ours-only=0, theirs-only={only_b}, zero loss)")
print("resolve4 done")
