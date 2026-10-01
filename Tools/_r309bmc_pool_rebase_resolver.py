"""r309 bm-c: runnable_pool.json rebase-conflict resolver (r294 union
domain law -- conflict region only, no global dedup).

Ours (:2, origin) = bm-a flipped N3-R1's 6 entries to dual-done.
Theirs (:3, this commit) = bm-c W5 12-entry dual-flip + 12 W6 additions.
Union = origin base + my W5 flips + my W6 verbatim additions; updated_at
= newer wins. Written via the generator's _pool_write_mirror (r289).
"""
import json
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import perpetual_faces as pf  # noqa: E402

POOL_REL = "results/runnable_pool.json"
ours = json.loads(subprocess.check_output(
    ["git", "show", ":2:" + POOL_REL]).decode("utf-8-sig"))
theirs = json.loads(subprocess.check_output(
    ["git", "show", ":3:" + POOL_REL]).decode("utf-8-sig"))

t_entries = theirs.get("entries", [])
t_vals = t_entries.values() if isinstance(t_entries, dict) else t_entries
t_by_id = {str(e.get("id")): e for e in t_vals}

merged = ours  # origin base: keeps bm-a's N3-R1 dual-done flips verbatim
m_entries = merged.setdefault("entries", [])
m_list = (list(m_entries.values()) if isinstance(m_entries, dict)
          else m_entries)

flipped = 0
for e in m_list:
    eid = str(e.get("id", ""))
    if not eid.startswith("PERPETUAL-N1-W5-SHARD-"):
        continue
    src = t_by_id.get(eid)
    if src is None:
        continue
    if e.get("status") == "ready" and src.get("status") == "done":
        e.update({k: src[k] for k in
                  ("status", "done_at", "done_by", "done_note")})
        for sh_m, sh_s in zip(e.get("shards", []), src.get("shards", [])):
            if sh_m.get("status") != "done":
                sh_m["status"] = sh_s["status"]
                sh_m["shard_done_note"] = sh_s["shard_done_note"]
        flipped += 1
    elif e.get("status") == "done":
        flipped += 1  # already landed (idempotent face)

added = 0
have = {str(e.get("id")) for e in m_list}
for e in [e for e in t_vals
          if str(e.get("id", "")).startswith("PERPETUAL-N1-W6-SHARD-")]:
    if str(e.get("id")) not in have:
        m_list.append(e)
        added += 1

merged["updated_at"] = max(str(ours.get("updated_at", "")),
                           str(theirs.get("updated_at", "")))
pf._pool_write_mirror(merged)
print(f"resolve: W5 flips carried={flipped}/12, W6 added={added}/12, "
      f"N3-R1 origin flips preserved="
      f"{sum(1 for e in m_list if str(e.get('id','')).startswith('PERPETUAL-N3-R1-') and e.get('status')=='done')}/6")
