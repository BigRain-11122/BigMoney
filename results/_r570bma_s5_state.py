# -*- coding: utf-8 -*-
# r570 bm-a S5: state round_no 569->570 + round report line append (bytes-safe, utf-8)
import json, datetime

now = datetime.datetime.now()
ts = now.strftime('%Y-%m-%d %H:%M:%S')
iso = now.isoformat(timespec='seconds') + '+08:00'

# --- state update (round_no +1, current fields) ---
fp = 'state-bm-a.json'
st = json.load(open(fp, encoding='utf-8'))
st['round_no'] = 570
st['last_round'] = 570
st['last_round_at'] = ts
st['last_round_ts'] = iso
st['updated'] = ts
st['current_task'] = ('W73 freeze landed + burn in flight (12-shard, tick-engine self-ignited '
                      'shard-0 10:38:19 product-growth evidence r325); W72 same-window '
                      'collision yielded to bm-b c7babddec first-land (r511 commit-order, '
                      'zero-cost draft yield: FIX-A intercept, zero ignition zero push, '
                      'bitwise ADMIT = r530 family 9th cross-validation)')
open(fp, 'w', encoding='utf-8', newline='') .write(json.dumps(st, ensure_ascii=False, indent=1) + '\n')
chk = json.load(open(fp, encoding='utf-8'))
assert chk['round_no'] == 570
print('state round_no -> 570 OK')

# --- round report append (round_reports-bm-a.md) ---
line = (
    '2026-10-02 10:4x | r570 | W72同窗撞面让路bm-b（c7babddec先落·r511 commit时序·本机纯草稿零烧零推=零成本让路：FIX-A拦截防顶替r560律第9例成功·n1_w72本机零点火实证·带位逐位互证=r530族第9例）+ W73冻结落地（第六十二枚引擎波·bm-a第十七枚自有波：A 189_004..191_003/B 51_601..51_800双算术续带零跳位零分叉·gate ADMIT回执+禁向闸ADMIT+全链selftest W2..W73 PASS+MSG-0640五面纯增量冻结·席位公示MSG-1036-bma同窗让路回执内再占位r565律）+ W73点火实证（tick自燃shard-0 10:38:19产物增长面r325律·烧录在飞）| 证据：results/_r570bma_w73_band_gate.py（ADMIT）+ results/_r570bma_w72_band_gate.py（yield证据）+ selftest ST_EXIT=0 + commit cd2e57af6纯增量1789行19件零删除 + push 6eeed810f..cd2e57af6送达 | 下轮指针：W73烧毕12/12后finalize（链序前置=W71 bm-c+W72 bm-b两席落账·FAIL-CLOSED r307）；W74带闸投影已载canon行（A CLEAN/B REFUSED xstock_synth_null_b=52_000端点红·两读法恒同零分叉）| 本地未达 origin commit 数=0（push后自证）\n'
)
with open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('round report r570 appended')
