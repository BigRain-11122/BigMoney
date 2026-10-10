# -*- coding: utf-8 -*-
# r853 S4: append new resolver-rebase domain law to rebase2 child (byte-safe, EOL-matched, r666 direct-write precedent)
import io

p = 'research/pit-git-resolver-rebase2.md'
raw = open(p, 'rb').read()
crlf = raw.count(b'\r\n')
lf_only = raw.count(b'\n') - crlf
eol = '\r\n' if crlf >= lf_only else '\n'
head = b'' if raw.endswith(eol.encode()) else eol.encode()

entry = (
    u'- [2026-10-11 01:5x r853 bm-b] **rebase 收口 tip 标记门 delta 化+resolver ts 探针双精度化（36-UU 双 pick 窗实弹·全 codified 律复演零新机制）**：'
    u'①r808「tip 全树 git grep 标记扫描」在含取证样本件的仓=假阳性死胡同——r505/r506 conflict-probe 取证件内容本含 <<<<<<< 行（origin 共有史），'
    u'全树扫报 tip 污染实为史迹；正法=**delta 化**：git diff --name-only <onto>..HEAD 逐件 git show HEAD:<path> 扫标记（本窗 62 面实证干净），'
    u'全树扫描仅适用于无取证件仓。'
    u'②resolver deep_ts 探针须**双精度**：p1d_gates.json meta.date=分钟精度 "2026-10-11 01:25" 被秒级 ISO 正则漏扫→fail-closed no-ts-both-sides 假闭；'
    u'正法=秒级+分钟级双正则。'
    u'③31-UU 主窗三面（LIVE md×2+dashboard_status.js）stage blob 自带标记=origin 侧污染入库（对端提交面）→r648 取对侧干净 blob 治愈零失败续证。'
    u'④可复用 resolver=results/_r853bmb_rebase_resolver.py（ls-files -u sha 通道/三态判读/jsonl union/ledger superset 探针/fail-closed 五门全带·'
    u'receipt _r853bmb_rebase_resolver.json）。How to apply：rebase 收口标记门一律 delta 化；resolver ts 探针双精度；stage 污染面 r648 继续有效。'
)
enc = entry.encode('utf-8')
open(p, 'ab').write(head + enc + eol.encode())
raw2 = open(p, 'rb').read()
print('appended=%dB file=%dB eol=%r' % (len(enc) + len(head) + len(eol), len(raw2), eol))
