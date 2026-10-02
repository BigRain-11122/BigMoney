# -*- coding: utf-8 -*-
# r592 bm-b closeout: round-report line append + state.json round_no++ (field-set preserving)
import json, time, datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S%z')  # +0800, T separator per F5

report_line = (
    "2026-10-02T" + now.strftime('%H:%M') + "+08:00 | round 592 (bm-b) | "
    "WM verdict: GREEN (watermark_red red=false lane=healthy; py_low_with_claimed-pick legal idle -- "
    "next_pick moneyflow IC claimed-but-panel-blocked since 09-25 source conn-level, same four standing-wait lanes as r591) | "
    "did: PRODUCT FACE -- town.html alloc building v5-canon restoration (J12 CEO-named visualization line): "
    "r538 bm-a had re-anchored alloc under 组合与资金部 citing a 'v6 ten-dept regroup r277' proven nonexistent "
    "by git log -S (十部门 zero hits in all history; 新立第八部门 intact since founding dc8991115; org_chart current v5 section + "
    "visualization note 资产组合研究部楼↔资产组合研究部（v5） both present) -> surgical 5-line restore per canon, "
    "working-tree blob e902ba6de byte-identical to pre-r538 version (rev-parse pipe-free verify; r538's gate asserted only "
    "its own edit product not the canon source = self-certifying loop) | "
    "verify: _r592bmb_town_v5_gate.py 17/17 ALL PASS incl org_chart canon-source 3 assertions; node --check rc0; "
    "Edge headless render DOM correct-term x5 / wrong-term x0; multimodal PNG confirms plaque 资产组合研究部 + zero 资产配置研究组 "
    "+ normal render (evidence results/_r592bmb_town.png); S6 33 legs rc0 (dualrun ZERO-DRIFT streak 36/3; "
    "t35 export stale-takeover by bm-b legal per O-2100 s2.4, bm-a heartbeat 32min stale); attrition guard CLEAN 4 ledgers; "
    "smoke 47/47; S7 self-heal 4/4 no-op (loop pin :2 alive + watchdog + pre-commit/pre-push claws byte-match); "
    "orders 143/143 head-scan zero-pending + tail double-scan zero-pending; D-19 honest skip r481 special "
    "(937A373D 3-machine consistent via bm-a r590/bm-c r381/r591); CODELY.md +1 pit entry (63.3KB in-service canon per r504 no-archival) | "
    "next: CEO visibility -- active: town.html v5 alignment fix landing this commit; latest artifact: town.html blob e902ba6de + "
    "gate results/_r592bmb_town_v5_gate.py + render evidence results/_r592bmb_town.png; next milestone: W112 finalize lands on origin "
    "-> W113 bm-c freeze/burn queues -> bm-b engine rotation resumes (<=48h); moneyflow IC fires when panel completes; "
    "paper block lifts 2026-10-09 first post-holiday bar"
)

# append to round report (CRLF preserving)
rp = r'logs\iteration-loop\round_reports.md'
raw = open(rp, 'rb').read()
crlf = b'\r\n' in raw[:2000]
sep = '\r\n' if crlf else '\n'
if not raw.endswith(b'\n'):
    raw += sep.encode()
new = raw + report_line.encode('utf-8') + sep.encode()
open(rp, 'wb').write(new)
print('report appended, crlf=', crlf, 'line_len=', len(report_line))

# state.json update (bm-b field set preserved verbatim, dynamic fields only)
sp = 'state.json'
raw = open(sp, 'rb').read()
crlf_s = b'\r\n' in raw
st = json.loads(raw.decode('utf-8'))
st['round_no'] = 592
st['note'] = ('r592: town.html alloc building v5-canon restoration (J12 line) -- r538 bm-a re-anchor under 组合与资金部 '
              'cited nonexistent v6 ten-dept regroup (git log -S proven false, 新立第八部门 intact since dc8991115); '
              '5-line surgical restore to pre-r538 blob e902ba6de byte-identical; gate 17/17 + node rc0 + Edge render 5/0 + '
              'multimodal PNG verified; S6 33 legs rc0 (dualrun streak 36/3); smoke 47/47; attrition CLEAN; self-heal 4/4 no-op; '
              'orders 143/143; D-19 honest skip r481 special; waiting lanes unchanged: W112 finalize pending origin, '
              'W113 bm-c seated, moneyflow panel-blocked, W14 GM-parked, paper Golden-Week block')
st['last_round_at'] = iso
st['last_round_ts'] = iso
st['ts'] = iso
st['updated'] = iso
st['updated_at'] = iso
out = json.dumps(st, ensure_ascii=False, indent=1)
if crlf_s:
    out = out.replace('\n', '\r\n')
open(sp, 'wb').write(out.encode('utf-8'))
print('state round_no=592 written, crlf=', crlf_s)

# self-verify epoch type sanity for heartbeat step readiness
print('epoch now int:', int(time.time()))
