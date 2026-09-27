# -*- coding: utf-8 -*-
"""r378 runnable_pool reconcile-drift diff (D-03 batch gate: full diff
before any conclusion; observation-window catch #4 candidate)."""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts")
import merge_lane_views as mlv

face = "runnable_pool"
sources = mlv.load_sources(face)
print("sources:", [(name, "present") for name, _ in sources])
res = mlv.merge_face(face, sources)
merged, notes = res if isinstance(res, tuple) else (res, [])
for n in notes:
    print("note:", n)
with open("results/runnable_pool.json", encoding="utf-8") as fh:
    shared = json.load(fh)

m_ids = {e.get("id"): e for e in merged.get("entries", [])}
s_ids = {e.get("id"): e for e in shared.get("entries", [])}
only_m = [i for i in m_ids if i not in s_ids]
only_s = [i for i in s_ids if i not in m_ids]
print(f"entries merged={len(m_ids)} shared={len(s_ids)} only-merged={only_m} only-shared={only_s}")

for eid in m_ids:
    if eid in s_ids and m_ids[eid] != s_ids[eid]:
        me, se = m_ids[eid], s_ids[eid]
        print(f"-- entry {eid} field diffs:")
        keys = set(me) | set(se)
        for k in sorted(keys):
            if me.get(k) != se.get(k):
                print(f"   {k}: merged={json.dumps(me.get(k), ensure_ascii=False)[:200]}")
                print(f"   {k}: shared={json.dumps(se.get(k), ensure_ascii=False)[:200]}")
        mks = {x.get('key'): x for x in me.get('shards', [])}
        sks = {x.get('key'): x for x in se.get('shards', [])}
        for k in sorted(set(mks) | set(sks)):
            if mks.get(k) != sks.get(k):
                print(f"   shard {k}:")
                print(f"      merged={json.dumps(mks.get(k), ensure_ascii=False)[:300]}")
                print(f"      shared={json.dumps(sks.get(k), ensure_ascii=False)[:300]}")
