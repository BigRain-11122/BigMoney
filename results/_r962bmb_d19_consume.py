# r962 bm-b addendum: D-19 DELTA in-round consumption. Single new orders row =
# bm-c XQ wave3 A-batch receipt (MV domain, pokes bm-a director seat; not
# BigMoney/quant) -> per D-19 law non-BigMoney row = watermark move + zero
# action. Updates state.json watermarks/notes + heartbeat orders_ack/did +
# r962 round report line segments. No push (rides C-r963 blob hashing).
import datetime, json, time

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r962bmb_closeout.log'
ORD_SHA = 'e2423fefcae0e9f9f0b54e9375dd11f4d51dd14c'

def W(m):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec='seconds')
epoch = int(time.time())
W('r962 addendum: D-19 in-round consume begin')

# ---------------- state.json ----------------
st = json.load(open(BM + r'\state.json', encoding='utf-8'))
st['last_orders_sha'] = ORD_SHA
st['last_orders_at'] = iso
st['orders_delta_pending'] = False
st['last_orders_sha_note'] = ('r962 consumed 6cc07bf4->e2423fef (delta = 1 row: bm-c '
                              'xinqing wave3 A-batch 29/29 receipt row, MV domain, '
                              'not-BigMoney = zero action); view=results/_r962bmb_orders_fresh.md')
st['d19_probe_due'] = False
st['d19_probe_due_note'] = ('r962: DELTA_PRESENT consumed in-round - single new row = bm-c '
                            'XQ wave3 receipt (MV domain, pokes bm-a director seat; not '
                            'BigMoney) -> ord watermark moved to e2423fef, zero action per '
                            'D-19 non-BigMoney-row law; dec 6910a9ed unchanged')
st['did'] = (st.get('did', '') + ' | addendum: D-19 delta consumed in-round (1 row = bm-c '
             'MV receipt, not BigMoney -> ord watermark 6cc07bf4->e2423fef, zero action)')
st['last_action'] = ('r962: monitor round + C-r962 PUSHED_VERIFIED (ca485e068651) + D-19 '
                     'delta consumed in-round (watermark moved, zero action)')
st['updated'] = iso
st['updated_at'] = iso
st['ts'] = iso
json.dump(st, open(BM + r'\state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
W('state.json watermark moved ord=%s at=%s' % (ORD_SHA[:12], iso))

# ---------------- heartbeat ----------------
hb = json.load(open(BM + r'\fleet\machines\bm-b.json', encoding='utf-8'))
hb['orders_ack'] = ('r962: DELTA consumed in-round - ord 6cc07bf4->e2423fef (1 new row: '
                    'bm-c xinqing wave3 MV receipt, not BigMoney = zero action); dec '
                    '6910a9ed unchanged; zero unacked O-orders for bm-b')
hb['did'] = (hb.get('did', '') + ' (i) D-19 delta consumed in-round: ord watermark moved '
             'to e2423fef (single new row = bm-c MV receipt, not BigMoney -> zero action)')
hb['last_seen'] = iso
hb['clock_read'] = iso
hb['ts'] = iso
hb['heartbeat_epoch_utc'] = epoch
json.dump(hb, open(BM + r'\fleet\machines\bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
e2 = json.load(open(BM + r'\fleet\machines\bm-b.json', encoding='utf-8'))
assert isinstance(e2.get('heartbeat_epoch_utc'), int), 'epoch must be JSON int'
W('heartbeat orders_ack updated epoch=%d verified-int' % epoch)

# ---------------- round report line segments ----------------
rp_path = BM + r'\logs\iteration-loop\round_reports.md'
with open(rp_path, 'r', encoding='utf-8') as f:
    rp = f.read()
old_seg5 = '⑤组面 D-19 双探针=DELTA_PRESENT（fresh 视图已存·水位未动·r963 深消费）'
new_seg5 = ('⑤组面 D-19 双探针=DELTA_PRESENT→同轮消费闭环（唯一新增行=bm-c 星晴 wave3 A 批 29/29 '
            '收口回执行·MV 域 poke bm-a 导演席·不涉本仓→ord 水位前移 6cc07bf4→e2423fef 零动作）')
old_unreach = '本地未达 origin commit 数=1（C-r962 在飞·回执=r963 消费面）'
new_unreach = ('本地未达 origin commit 数=0（C-r962 已验送达 ca485e068651·D-19 消费 addendum+segment-C '
               '本地面随 C-r963 携带）')
n5 = rp.count(old_seg5)
nu = rp.count(old_unreach)
rp2 = rp.replace(old_seg5, new_seg5).replace(old_unreach, new_unreach)
with open(rp_path, 'w', encoding='utf-8') as f:
    f.write(rp2)
W('round report segments updated (seg5 x%d, unreach x%d)' % (n5, nu))
assert n5 == 1 and nu == 1, 'segment replace count mismatch (seg5=%d unreach=%d)' % (n5, nu)
W('r962 addendum done: D-19 consume closed, faces = state/heartbeat/report (ride C-r963)')
