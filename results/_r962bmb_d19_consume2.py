# r962 bm-b addendum fix: byte-level segment replace on round_reports.md
# (file has legacy non-UTF-8 bytes near tail; text-mode read crashed at
# 2577414 = 0xed GBK-family byte. Binary replace = zero touch on all other
# bytes. state/heartbeat already updated by _r962bmb_d19_consume.py run 1.)
import datetime

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r962bmb_closeout.log'
RP = BM + r'\logs\iteration-loop\round_reports.md'

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

old_seg5 = '⑤组面 D-19 双探针=DELTA_PRESENT（fresh 视图已存·水位未动·r963 深消费）'
new_seg5 = ('⑤组面 D-19 双探针=DELTA_PRESENT→同轮消费闭环（唯一新增行=bm-c 星晴 wave3 A 批 29/29 '
            '收口回执行·MV 域 poke bm-a 导演席·不涉本仓→ord 水位前移 6cc07bf4→e2423fef 零动作）')
old_unreach = '本地未达 origin commit 数=1（C-r962 在飞·回执=r963 消费面）'
new_unreach = ('本地未达 origin commit 数=0（C-r962 已验送达 ca485e068651·D-19 消费 addendum+segment-C '
               '本地面随 C-r963 携带）')

with open(RP, 'rb') as f:
    rp = f.read()
o5 = old_seg5.encode('utf-8'); n5b = new_seg5.encode('utf-8')
ou = old_unreach.encode('utf-8'); nub = new_unreach.encode('utf-8')
c5 = rp.count(o5); cu = rp.count(ou)
W('byte-level counts seg5=%d unreach=%d (file=%dB)' % (c5, cu, len(rp)))
assert c5 == 1 and cu == 1, 'segment byte count mismatch (seg5=%d unreach=%d)' % (c5, cu)
rp2 = rp.replace(o5, n5b).replace(ou, nub)
with open(RP, 'wb') as f:
    f.write(rp2)
W('round report segments updated byte-level (delta=%+dB)' % (len(rp2) - len(rp)))
W('r962 addendum done (fix leg): state/heartbeat from run 1 + report from this leg; ride C-r963')
