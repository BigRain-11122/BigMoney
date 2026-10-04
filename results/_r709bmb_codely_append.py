# r709 bm-b CODELY.md append (S4 memory gate: format-asymmetry false-tie pit)
import time, os

p = 'CODELY.md'
raw = open(p, 'rb').read()
sep = b'' if raw.endswith(b'\n') else b'\n'
entry = (
    '- [2026-10-05 04:' + time.strftime('%M') + ' r709 bm-b] '
    '**merge resolver ts 比较格式异构假 tie 坑（r709 双弹实弹·断言层当场抓回零 origin 伤害）**：'
    '池面 UU per-entry newer-wins 决策器禁全字段 ts 字符串漫游比较——owner_since 为空格式'
    '（"2026-10-05 03:47:08"）而 entry 级 updated_at 为 T 格式（"2026-10-05T01:13:21+08:00"），'
    "字典序 ' '<'T' ⇒ 真新鲜空格式值恒输 T 格式旧值=v1 探针恒假 tie→keep-ours=推 stale 池面"
    '=MSG-0612 爪拦截面（实弹：SHARD-10/2 ours done@03:42:03 vs theirs ready@03:47:08/49 假 tie）。'
    '正法=比较定向 owner_since/claimed_at/cleared_ts 字段族（v2 治愈）+写盘反读==theirs 恒等断言（r704 律）。'
    '附：ready/done 瞬态翻面=keepalive claim-refresh 与 harvest 握手竞态自然面'
    '（03:47 ready→03:50/04:08 harvest 翻回 done·与 F-04 座宣告自洽），'
    'merge 窗见翻面勿惊动定性、owner_since newer-wins 即正解。'
    'How to apply：复制 r70x merge resolver 血统先核 ts 比较定向性；见假 tie 先查格式异构勿信。'
)
b = (entry + '\n').encode('utf-8')
with open(p, 'ab') as f:
    f.write(sep + b)
back = open(p, 'rb').read()
assert back.endswith(b) and back.count(b) == 1
print('appended bytes=%d total=%d over50KB=%s' % (len(b), len(back), len(back) > 50 * 1024))
