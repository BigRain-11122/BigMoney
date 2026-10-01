# r502 bm-b rebase-replay conflict resolver (2026-10-01 11:2x)
# Context: crashed r502 session (died 11:17 stream-timeout) left 2 unpushed commits
# replaying onto origin which moved: bm-a double-welded O-1108 iteration_prompt (bf5f5a71e)
# and claimed T-140 (3a842a79e 11:21:01) after bm-b's local-only claim (11:15:32/commit 11:16:57).
# Resolution per bigmoney-conflict-resolve SKILL + r483 yield law + r239 collision law:
#  - Tools/iteration_prompt.txt: take origin/ours side (bm-a weld is on origin; same CEO order,
#    semantically equivalent implementation of exit-axis gate + N-line; double-weld dedupe)
#  - fleet/tasks/T-2026-10-01-140-P1.json: take origin/ours side (bm-a claim) + yield_record
import subprocess, json, sys

def show(stage, path):
    return subprocess.check_output(['git', 'show', f':{stage}:{path}'])

# 1) iteration_prompt.txt -> take ours (origin side, stage 2)
ours_prompt = show(2, 'Tools/iteration_prompt.txt')
theirs_prompt = show(3, 'Tools/iteration_prompt.txt')
with open('Tools/iteration_prompt.txt', 'wb') as f:
    f.write(ours_prompt)
print(f'iteration_prompt.txt: took ours(origin) {len(ours_prompt)}B, dropped theirs {len(theirs_prompt)}B')

# 2) T-140 ticket -> ours (bm-a claim) + yield_record field
ours_t = show(2, 'fleet/tasks/T-2026-10-01-140-P1.json')
raw = ours_t.decode('utf-8')
ticket = json.loads(raw)
assert ticket.get('claimed_by') == 'bm-a', ticket.get('claimed_by')
ticket['yield_record'] = ('r502 bm-b local claim 2026-10-01T11:15:32+08:00 (commit 9f8363825 @11:16:57, unpushed, '
                         'session died 11:17 stream-timeout) yielded to bm-a origin-landed claim 3a842a79e @11:21:01 '
                         'per r239/r483 collision law (origin-landing wins over local-only); bm-b retains action-4 '
                         'P2 prereg cross-check role per ticket note')
crlf = '\r\n' in raw
out = json.dumps(ticket, ensure_ascii=False, indent=1)
if crlf:
    out = out.replace('\n', '\r\n')
if raw.endswith(('\r\n', '\n')):
    out += '\r\n' if crlf else '\n'
data = out.encode('utf-8')
with open('fleet/tasks/T-2026-10-01-140-P1.json', 'wb') as f:
    f.write(data)
# verify parse + field survival
rt = json.loads(data.decode('utf-8'))
assert rt['claimed_by'] == 'bm-a' and 'yield_record' in rt and rt['status'] == 'claimed'
print(f'T-140: ours(bm-a claim) + yield_record, crlf={crlf}, {len(data)}B, roundtrip OK')
print('RESOLVED-OK')
