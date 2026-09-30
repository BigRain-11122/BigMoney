# r491 bm-a context probe for banned-gate build (adopt per r471)
# Reads remote RETAIL_QUANT_TRACK.md canon + local registry; writes UTF-8 JSON evidence.
import json, subprocess, io, sys

out = {}
# 1) remote canon: sections around banned-direction gate mentions
track = subprocess.run(['git', 'show', 'origin/main:research/RETAIL_QUANT_TRACK.md'],
                       capture_output=True).stdout.decode('utf-8', 'replace')
hits = []
needle = '\u7981\u5f00'  # 禁开
i = track.find(needle)
while i >= 0 and len(hits) < 12:
    hits.append(track[max(0, i - 120):i + 260])
    i = track.find(needle, i + 1)
out['remote_track_ban_hits'] = hits
out['remote_track_len'] = len(track)
# 2) local vs remote track length
local_track = io.open('research/RETAIL_QUANT_TRACK.md', encoding='utf-8').read()
out['local_track_len'] = len(local_track)
# 3) template section 0.5 exact text (staged)
tpl = io.open('research/PREREG_TEMPLATE.md', encoding='utf-8').read()
i0 = tpl.find('\u00a70.5')
out['template_s05'] = tpl[i0:i0 + 700] if i0 >= 0 else 'MISSING'
# 4) registry usage line + required fields
d = json.load(io.open('research/BANNED_DIRECTIONS.json', encoding='utf-8'))
out['usage_line'] = d.get('usage')
out['required_fields'] = d.get('required_fields_in_prereg_on_match')
# 5) remote prereg template state
r = subprocess.run(['git', 'show', 'origin/main:research/PREREG_TEMPLATE.md'], capture_output=True)
rtpl = r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else 'MISSING'
out['remote_template_has_s05'] = ('\u00a70.5' in rtpl) or (needle in rtpl)
out['remote_template_len'] = len(rtpl)

io.open('results/_r491bma_gate_context_probe.json', 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=1))
print('probe done, keys:', list(out.keys()))
