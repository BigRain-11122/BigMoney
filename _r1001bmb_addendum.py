# r1001 addendum: delivery-verification line + state sync entry
import json, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
SHA = 'a8568c55dce999598143ab745ef058b4309322e5'

REPORT = r'logs\iteration-loop\round_reports.md'
line = (
"2026-10-18T07:4x+08:00 | r1001-addendum | 送达核验门补行: 本地未达 origin commit 数=0（首推拒因=origin 窗中前移 2 提交[bm-c W265 finalize+W266 seat]非快进·爪 check-push 范围复查零违规[未用 --no-verify]·stash→rebase 干净重放[传入与提交面零交集]→重推 ace19ba85b..a8568c55dc DELIVERED·rev-list 0/0 双验）；W265 已 finalize+W266 席已发布=波链滚动实证（S6 时点 pool_starvation 旗已被后续事态自然消解·供给面健康）；BigHouse 仓 T-3 送达 ls-remote=3634120f 维持。"
)
with open(REPORT, 'rb') as f:
    raw = f.read()
nl = b'\r\n' if b'\r\n' in raw[-500:] else b'\n'
if raw and not raw.endswith(b'\n'):
    raw += nl
raw += line.encode('utf-8') + nl
with open(REPORT, 'wb') as f:
    f.write(raw)

with open('state.json', encoding='utf-8') as f:
    st = json.load(f)
st['sync']['last_push_ts'] = NOW
st['sync']['r1001_main_push'] = {
    'status': 'PUSHED_VERIFIED',
    'pushed_sha': SHA,
    'consumed_at': NOW,
    'behind_origin_main': 0,
    'note': 'first push rejected non-ff (origin advanced 2 bm-c commits mid-round); claw check-push re-verified zero violations on range; clean rebase replay (zero file intersection); redelivered ace19ba85b..a8568c55dc'
}
st['last_action_at'] = NOW
st['clock_read'] = NOW
with open('state.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write('\n')

hb = json.load(open(r'fleet\machines\bm-b.json', encoding='utf-8'))
hb['ts'] = NOW
hb['last_seen'] = NOW
with open(r'fleet\machines\bm-b.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('addendum written', SHA)
