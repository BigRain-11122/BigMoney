# -*- coding: utf-8 -*-
# r570 bm-a S4: one-line pitfall append to CODELY.md tail (bytes-safe, EOL-preserving)
b = open('CODELY.md', 'rb').read()
t = b.decode('utf-8')
eol = '\r\n' if t.count('\r\n') * 2 > t.count('\n') else '\n'
if not t.endswith(eol):
    t += eol
line = (
    '- [2026-10-02 10:4x r570 bm-a] 共享 jsonl 本地 shell 重定向覆写坑（pool_core_samples 覆写实弹·r524 族新变体）：'
    '某步 shell 面把 attrition 扫描件（pretty-print 多行 JSON）整个写进共享 append-only jsonl——71 碎片行+后继合法 append 混存；'
    '唯一 tripwire=消费面崩（compute_audit AttributeError str has no get——json.loads 对裸字符串行合法返回 str）；'
    'origin 正典全健（750 行全 dict）→ 修法=origin 字节 verbatim 为底+本机合法 dict 行 union 追加（3 行活烧采样保全）+'
    'post-verify 全行 dict 断言+compute_audit 复跑红愈；本机污染未 commit=零 origin 伤害。'
    'How to apply：jsonl 读面崩先疑非 dict 行勿疑代码；共享 append-only 件一切本地异常先 git status+origin 比对定性；'
    '修复恒走 origin-union（r524 域律）禁手搓行编辑；肇事 shell 面已逝（前会话），预防=S7 步骤重定向一律显式 -RedirectStandardOutput 到专案文件禁裸 > 共享件。\n'
)
t += line
open('CODELY.md', 'wb').write(t.encode('utf-8'))
print('appended, new size:', len(t.encode('utf-8')))
