"""r781 bm-b: probe why the autofill picker skips V (pool_empty_or_busy)."""
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'Tools'))
import autofill

print("LOW_PY_LINE =", autofill.LOW_PY_LINE)
print("STALE_MIN   =", autofill.STALE_MIN)

pool = autofill._pool_merged_view()
v = [e for e in pool.get('entries', [])
     if e.get('id') == 'FUND-VALUE-P1-NULLS'][0]
print("merged V entry status:", v.get('status'),
      "lane_owner:", v.get('lane_owner'))
print("merged V shard:", v['shards'][0].get('status'),
      "owner:", v['shards'][0].get('owner'),
      "owner_since:", v['shards'][0].get('owner_since'))

# host gate probe
gr = autofill._host_gate_reason(v)
print("host_gate_reason:", gr)

# runner-alive probe
ra = autofill._runner_alive(v['runner'])
print("runner_alive(fund_value_p1.py):", ra)

# ext claim age probe
xc = autofill._ext_claim_age_min('FUND-VALUE-P1-NULLS',
                                 'fund-value-p1-nulls-0of1')
print("ext_claim_age_min:", xc)

# data deps probe (D-20260904-02 gate)
miss = autofill._data_deps_missing(v)
print("data_deps_missing:", miss)

# full picker probe with log capture
e, sh = autofill._pick(pool, 'bm-b')
print("PICK RESULT:", e.get('id') if e else None,
      sh.get('key') if sh else None)
