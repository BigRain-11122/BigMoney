import json
p = 'fleet/tasks/T-2026-10-02-145-P1.json'
d = json.load(open(p, encoding='utf-8'))
d['progress_r626_bma_gate_state'] = (
    'engine/transfer gate state r626 (bm-a): ALL bm-a furnace legs hard-gated on T-156 p1c swap -- '
    'off-caliber cache (r615) quarantine swap waits on croc pairing; receiver camping 31+min no-pairing '
    '-> kill-advice MSG-2026-10-03-1410 sent (MSG-1214 sec.4 trigger); divlowvol 4-sig fuse keep-blocks '
    'live (REFUSE evidence 13:48), QUALITY-SENS + 90-row nulls re-claims queued behind swap per division; '
    'x1/x2 cell verdicts already canonical on bm-b correct-caliber data (no re-burn needed). Also diagnosed '
    'same window: saturation engine idle since 05:40 (queue 0) + perpetual generator starve-verdict '
    'false-negative (counts fuse-gated ready entries as live supply -> starving=False -> no N-wave '
    'materialization); N2-W15 runner (sequencing law next) deliberately deferred pending W14 GM '
    'dual-ruling (MSG-0436) since N2 consumes trial grammar face under adjudication.'
)
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('progress note written, keys:', len(d))
