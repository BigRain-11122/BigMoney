# r962 bm-b: append new pit law to repo root CODELY.md (S4, one entry) +
# fix state.json note claim ("no new pit law" -> one new pit law).
# CODELY.md append uses 'a' mode (safe on mixed-encoding file per this law).
import datetime, json, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r962bmb_closeout.log'

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

hm = time.strftime('%H:%M')
entry = (
 "[2026-10-15 %s] r962 坑律（round_reports.md 混合编码面）：轮报告文件尾部历史行含非 UTF-8 "
 "字节（0xED@2,577,414 附近·text 全读即 UnicodeDecodeError）——对该文件一切读-改-写必须二进制面"
 "（bytes.count 定位唯一段+bytes.replace·其余字节零触碰·r962 addendum 实弹），禁 errors='replace' "
 "读后重写（=毁史字节）；'a' 追加模式不受影响（r948 起全部恢复轮追加安全实证）。How to apply：消费/"
 "修订轮报告历史行一律 binary edit；新 closeout 沿用 append-only 范式。\n" % hm
)
size0 = len(open(BM + r'\CODELY.md', 'rb').read())
with open(BM + r'\CODELY.md', 'a', encoding='utf-8') as f:
    f.write(entry)
size1 = len(open(BM + r'\CODELY.md', 'rb').read())
W('CODELY.md appended +%dB (%d -> %dB, law >50KB = recompile)' % (size1 - size0, size0, size1))
assert size1 - size0 == len(entry.encode('utf-8')), 'append byte count mismatch'
assert size1 <= 50 * 1024, 'CODELY over 50KB - recompile window due'

st = json.load(open(BM + r'\state.json', encoding='utf-8'))
old = 'r962 monitor round: no new pit law; standing laws'
new = ('r962 monitor round: one new pit law (round_reports.md mixed-encoding byte-edit law, '
       'appended to CODELY.md); standing laws')
assert st['note'].count(old) == 1, 'state note anchor not unique'
st['note'] = st['note'].replace(old, new)
json.dump(st, open(BM + r'\state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('state.json note claim fixed (one new pit law)')
W('r962 round fully closed: monitor + C-r962 PUSHED_VERIFIED + D-19 in-round consume + pit law固化')
