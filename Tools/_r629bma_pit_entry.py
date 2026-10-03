"""r629 bm-a: pit-pool.md direct-write entry (trailing-comma raw-text pit)
+ header accounting line, per r401/r417/r628 direct-write convention."""
import hashlib

PIT = 'research/pit-pool.md'
raw = open(PIT, 'rb').read()
crlf = b'\r\n' in raw
eol = '\r\n' if crlf else '\n'

body_entry = (
    "- [2026-10-03 15:3x r629 bm-a] raw-text 删尾字段留尾逗号坑（池释放编辑实弹·r509 族新变体）："
    "raw-text 锚定删除分片尾随字段对（owner/owner_since 两行）后，前一字段（note）行尾逗号成非法尾逗号"
    "→json.loads 解析门当场拦下（池共享面 daemon ~2min 一读=无解析门即 daemon 崩窗）。正法=删行同时把前字段行尾 "
    '","\r\\n" 改 "\\"\\r\\n"（或删行前先探明 note 是否末字段）；写后必 json.loads+git diff --numstat 外科断言双门。'
    "本窗共享面曾写坏 60s 内当场修复零 daemon 伤害（_r629bma_repair1.py 留痕；repair 后 4 面 claim 释放+host_gates 全过）。")
hdr_account = (
    "> 直写行（r629 bm-a·divlowvol 池卫生件落地）：r629 尾逗号坑条 1 条直入本件（非迁移·域内 direct-write，"
    "r401/r417/r628 范式）；追加核见下一行。")

before_bytes = len(raw)
txt = raw.decode('utf-8')
assert txt.rstrip().endswith('勿疑 daemon。'), 'unexpected tail'
new = txt.rstrip('\r\n') + eol + body_entry + eol
new_raw = new.encode('utf-8')
open(PIT, 'wb').write(new_raw)
after = len(new_raw)
lf_blob = new_raw.replace(b'\r\n', b'\n')
md5 = hashlib.md5(lf_blob).hexdigest()
print(f'bytes {before_bytes} -> {after} (delta +{after-before_bytes}, LF blob md5={md5})')
