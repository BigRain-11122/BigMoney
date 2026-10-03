"""r637 bm-a S4: pit-pool.md direct-write entry (r401/r417/r628 domain direct-write law)."""
import hashlib

ENTRY = ("- [2026-10-03 19:1x r637 bm-a] 整面回退修缮吞活认领→无主窗诱发后到重烧坑（w2-judge-3of4 实弹·r605/r608 族扩展）："
         "r636 会话为修 daemon 陈旧写（d0fa671ac 把 2of4 让路面整写覆回 bm-a）走「checkout 上一好态整面回退」路（7635f7749），"
         "把同 commit 里 daemon 对 3of4 的活认领（18:52:08·burn pid 104816 在飞）一并剥掉→共享面无主 5min→bm-c 18:57:08 合法认领重烧"
         "（~10min 双烧·本机 18:56:24 已烧完 201/201 完整产物在盘）；幸确定性 runner 双源字节恒等（sha256 a63a8f2e 实证）零数据风险，"
         "bm-c r425 交付收口。How to apply：整面回退/修缮前必对账 daemon 启动台账（autofill launches）的在飞认领——有在飞 burn 的 owner 行"
         "禁随面回退剥离（剥离=面无主=接管门洞开）；修缮用逐 hunk 锚定定点禁整文件 checkout 上一态；双烧止损先核本机产物完整性再定向"
         "（首认领+完整产物=正主，后到者 kill-advice·r297）；跨机确定性以产物字节恒等为唯一收口判据。")

ENTRY = ENTRY.replace('19:1x', '19:15')
p = 'research/pit-pool.md'
raw = open(p, 'rb').read()
blob = ENTRY.encode('utf-8').replace(b'\n', b'\x00')  # entry is single line (no \n inside)
entry_bytes = ENTRY.encode('utf-8') + b'\n'
md5 = hashlib.md5(entry_bytes).hexdigest()
assert b'\n' not in ENTRY.encode('utf-8'), 'entry must be single line'
assert raw.endswith(b'\n'), 'file must end with newline'
with open(p, 'ab') as f:
    f.write(entry_bytes)
print('entry appended bytes:', len(entry_bytes), 'md5:', md5)

hdr = ('> 直写行（r637 bm-a·整面回退吞活认领坑落件）：r637 双烧止损窗条 1 条直入本件（非迁移·域内 direct-write·r401/r417/r628 范式）'
       '·追加核 %d B（LF blob 面·md5=%s）。\n' % (len(entry_bytes), md5))
anchor = '·追加核 671 B（LF blob 面·md5=61a76e32be78b5dd2c23d129700421d1）。\n'
raw = open(p, 'rb').read()
assert raw.count(anchor.encode('utf-8')) == 1, 'header anchor'
with open(p, 'wb') as f:
    f.write(raw.replace(anchor.encode('utf-8'), anchor.encode('utf-8') + hdr.encode('utf-8')))
print('header line inserted after r629 direct-write line')

import json
json.loads(open(p, encoding='utf-8').read()[:0] or '""')  # noop
import subprocess
r = subprocess.run(['git', 'diff', '--stat', '--', 'research/pit-pool.md'], capture_output=True, text=True)
print(r.stdout)
