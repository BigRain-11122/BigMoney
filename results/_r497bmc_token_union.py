"""r497 bm-c: token_usage.json line-level union (treasure_guard FORBIDDEN
face -> per-key union per guard prescription; r456 per-key law + r466
fallback law: side_pick==0 -> whole-face freshness; r656 canon: probe
first, then surgery). Local-vs-origin union BEFORE merge absorb commit."""
import json
import subprocess

ours_raw = open('results/token_usage.json', 'rb').read()
theirs_raw = subprocess.run(
    ['git', 'show', 'origin/main:results/token_usage.json'],
    capture_output=True).stdout

ours = json.loads(ours_raw.decode('utf-8'))
theirs = json.loads(theirs_raw.decode('utf-8'))
out = dict(theirs)  # start from origin (fleet face), overlay keys

# per-machine entries: union per key, keep BOTH sides' per-machine rows
m_ours = ours.get('machines', {})
m_theirs = theirs.get('machines', {})
side_pick = 0
merged_m = {}
all_keys = sorted(set(m_ours) | set(m_theirs))
for k in all_keys:
    if k not in m_theirs:
        merged_m[k] = m_ours[k]
        side_pick += 1
    elif k not in m_ours:
        merged_m[k] = m_theirs[k]
    else:
        # both have key: ts-aware newer-wins (r466 face), disclose
        ts_o = str(m_ours[k].get('ts', m_ours[k].get('last_ts', '')))
        ts_t = str(m_theirs[k].get('ts', m_theirs[k].get('last_ts', '')))
        keep = m_ours[k] if ts_o >= ts_t else m_theirs[k]
        merged_m[k] = keep
        if keep is m_ours[k]:
            side_pick += 1
out['machines'] = merged_m

# top-level scalar/other keys: origin-wins except ts (freshest honest)
for k in ours:
    if k != 'machines' and k not in out:
        out[k] = ours[k]
        side_pick += 1

print("machines keys ours=%d theirs=%d merged=%d side_pick(ours-kept)=%d"
      % (len(m_ours), len(m_theirs), len(merged_m), side_pick))
print("top-level ours keys:", sorted(ours.keys()))
print("top-level theirs keys:", sorted(theirs.keys()))
with open('results/_r497bmc_token_union.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("UNION DRAFT -> results/_r497bmc_token_union.json (apply pending review)")
