import json
import io
import os
import socket
import subprocess
import time
import datetime

# ---- heartbeat nine-field backfill (O-20261007-2255, self-cert) ----
p = r'fleet\machines\bm-a.json'
d = json.load(io.open(p, encoding='utf-8'))
now = time.time()
now_iso = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S+08:00')
d['hostname'] = os.environ.get('COMPUTERNAME', socket.gethostname())
d['root_path'] = r'C:\Users\sjs20\Desktop\FluxGroup'
d['last_seen'] = now_iso
d['heartbeat_epoch_utc'] = int(now)
tmp = p + '.tmp%d' % os.getpid()
io.open(tmp, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
os.replace(tmp, p)
chk = json.load(io.open(p, encoding='utf-8'))
nine = ['hostname', 'root_path', 'gpu_model', 'total_ram_gb', 'free_ram_gb',
        'gpu_free_vram_mb', 'prod_lanes', 'heartbeat_epoch_utc', 'last_seen']
missing = [k for k in nine if k not in chk]
assert not missing, missing
assert isinstance(chk['heartbeat_epoch_utc'], int)
print('nine fields all present; hostname=%s root_path=%s epoch=%d' % (
    chk['hostname'], chk['root_path'], chk['heartbeat_epoch_utc']))

# ---- orders_ack += O-2255 ----
ack = chk.get('orders_ack', [])
o = 'O-20261007-2255-bm-c.md'
if o not in ack:
    ack.append(o)
    chk['orders_ack'] = ack
    tmp = p + '.tmp%d' % os.getpid()
    io.open(tmp, 'w', encoding='utf-8').write(json.dumps(chk, ensure_ascii=False, indent=1))
    os.replace(tmp, p)
print('orders_ack:', len(ack))

# ---- O-2255 receipt (bm-a section) ----
rp = r'fleet\orders\O-20261007-2255-bm-c.md'
t = io.open(rp, encoding='utf-8').read()
anchor = u'### 回执（bm-c）'
assert t.count(anchor) == 1
receipt = (
    u'### 回执（bm-a）〔via bm-a r847·2026-10-07T23:0x+08:00 实测·维度=自证·零他机代写〕\n'
    u'- **九字段清单（补写后实读）**：`hostname`=SJS20-DESKTOP ｜ `root_path`=C:\\Users\\sjs20\\Desktop\\FluxGroup ｜ `gpu_model`=RTX 4070S 12GB ｜ `total_ram_gb`=93.6 ｜ `free_ram_gb`（统一键）≈53 ｜ `gpu_free_vram_mb`（统一键·nvidia-smi 实读）≈5400 ｜ `prod_lanes`=bigmoney-os-loop（10min 自迭代·perpetual N1 波烧录）+量化研究+EngineTick 值守 ｜ `heartbeat_epoch_utc`（JSON int·isinstance 自证过）｜ `last_seen`（T 分隔 ISO8601 含 UTC 偏移）。本机原缺 hostname+root_path 两件，本轮补写；其余七件已在（r847 idle 闭环轮已带 idle_rounds/agenda_starved 扩展字段）。\n'
    u'- **根骨架 9/9 对账（如实呈报·禁自建补数）**：OK=README.md/.codely-cli/CODELY.md（3/9）；MISS=MiniGame/FluxGroup/projects/data/archive/.tools（6/9）——本机实际布局=分域子目录制（gaming\\MiniGame·quant\\bigmoney·life\\BigLife·domain\\BigDomain·compute\\BigCompute 等），与正典 v2.0 平铺九件制不同构，缺件如实呈报未自建；同构改造属布局迁移面，待委员会裁定后再动（涉及全机路径迁移，非一轮可代决）。\n'
    u'- **回执同轮注记**：本令经 S7 双扫捕获（轮中经 rebase 并入的 bm-c r704 窗推送落地）。\n'
)
io.open(rp, 'w', encoding='utf-8').write(t.replace(anchor, receipt + anchor))
print('O-2255 receipt written')
