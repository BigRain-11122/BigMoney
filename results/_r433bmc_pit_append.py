# -*- coding: utf-8 -*-
"""r433 bm-c pit-git direct-write append (+1 entry, post-split convention):
dumb-terminal EDITOR false-conflict + twin mixed-side honest disclosure.
Byte-safe: preserve file EOL form, LF-blob md5 accounting, count==1 verify."""
import hashlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(REPO, 'research', 'pit-git.md')

ENTRY = (
    "- [2026-10-03 22:3x r433 bm-c] rebase --continue 哑终端 EDITOR 坑+孪生再生面混侧违例自曝（r643 孪生律同窗迟到面）："
    "①**GIT_EDITOR unset 假冲突拒**——会话壳（无 TTY）下 rebase --continue 在冲突全解、git ls-files -u=0 时仍拒，"
    "报文「error: Terminal is dumb, but EDITOR unset / could not commit staged changes」与 r427 净索引双拒族形似实异"
    "（该族=三证净仍拒需外科收口；本坑=环境 EDITOR 缺失，$env:GIT_EDITOR='true' 一行即愈零外科）；"
    "判别法=报文首行为 editor 抱怨而非「You must edit all merge conflicts」即本坑。"
    "②**孪生再生面（json+md 对）per-file 侧取会拆对**——r433 收口器（_r433bmc_rebase_resolve.py）按面独立 ts 判定，"
    "REPORT/LIVE 三对被拆成 json=mine/md=origin 混代际对（r643 21:5x 已立「孪生面必同侧字节拷贝+generated_at 权威钟」律，"
    "本窗收口时未读该律=违例自曝）；混对为同日幂等再生态、下轮任机 S6 daily_report/live_usage 原子再生自愈"
    "（勿手工修补=与对侧再生态竞速纯 churn）；正法=孪生面侧取先探 generated_at/generated 顶层权威钟"
    "（不等才落 max-ts 兜底）+对成员字节同侧拷贝。How to apply：会话壳 rebase --continue 前预设 $env:GIT_EDITOR='true'；"
    "冲突面清单先过孪生配对分组再逐组同侧取。"
)

raw = open(PATH, 'rb').read()
text = raw.decode('utf-8')
crlf = '\r\n' in text
eol = '\r\n' if crlf else '\n'

core_lf = ENTRY + '\n'          # LF blob face of the entry for accounting
core_b = len(core_lf.encode('utf-8'))
core_md5 = hashlib.md5(core_lf.encode('utf-8')).hexdigest()

ACCT = (
    "> 直写行（r433 bm-c·post-split convention direct-write）：+1 条"
    "（哑终端 EDITOR 假冲突拒=env 一行治愈判别律+孪生面混侧违例自曝·同日自愈勿手修）"
    "·追加核 %d B（LF blob 面·md5=%s）·尾部整行追加·件内对账行为准。" % (core_b, core_md5)
)

if text.count(ENTRY[:40]) != 0:
    print('FAIL anti-dup: entry head already present')
    sys.exit(2)
if not text.endswith(eol):
    text += eol
text += ENTRY + eol + ACCT + eol
blob = text.encode('utf-8')
blob.decode('utf-8')            # strict round-trip gate
open(PATH, 'wb').write(blob)

# verify: re-read, count==1, LF-blob md5 stable, no lone CR corruption
back = open(PATH, 'rb').read().decode('utf-8')
assert back.count(ENTRY[:40]) == 1, 'count!=1 after write'
assert ENTRY in back and ACCT in back, 'append missing after write'
if crlf:
    assert '\r\r' not in back.replace('\r\n', '\x00'), 'lone-CR corruption'
print('PIT-GIT APPEND OK: core=%dB md5=%s crlf=%s' % (core_b, core_md5, crlf))
