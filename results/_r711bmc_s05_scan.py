# -*- coding: utf-8 -*-
# r711 bm-c S0.5 sweep: orders set-diff (exact) + D-19 DEC sha256 / ORD sha1 watermark gate
# (r710 facts shape; r717bmb template; group-tree origin blob read, zero tree-touch)
import json, io, os, subprocess, hashlib, sys, datetime

out = {}
facts = {}

# 1) orders set-diff (heartbeat orders_ack vs disk)
hb = json.load(io.open('fleet/machines/bm-c.json', encoding='utf-8'))
ack_raw = hb.get('orders_ack', [])
ack = set()
for a in ack_raw:
    ack.add(a if isinstance(a, str) else a.get('file', json.dumps(a)))
disk = set(f for f in os.listdir('fleet/orders') if f.lower().endswith('.md') and f != 'README.md')
unacked = sorted(disk - ack)
ghost = sorted(ack - disk)
facts['orders_disk_count'] = len(disk)
facts['orders_ack_count'] = len(ack)
facts['unacked'] = unacked
facts['ghost_ack_non_archive'] = ghost
facts['selfcheck'] = 'disk non-empty PASS (r669)' if disk else 'disk EMPTY FAIL'

# 2) D-19: group tree origin blob hashes (DEC sha256 / ORD sha1, ALGORITHM PIN r537 law)
st = json.load(io.open('state-bm-c.json', encoding='utf-8'))
dec_prev = st.get('last_decisions_sha')
ord_prev = st.get('last_orders_sha')
GROUP = r"K:\Fluxgroup\FluxGroup"
content = {}
if os.path.isdir(os.path.join(GROUP, '.git')):
    subprocess.run(["git", "-C", GROUP, "fetch", "origin"], capture_output=True)
    for key, doc in (("dec", "docs/decisions.md"), ("ord", "docs/orders.md")):
        r = subprocess.run(["git", "-C", GROUP, "show", "origin/main:" + doc], capture_output=True)
        if r.returncode == 0 and r.stdout:
            algo = hashlib.sha256() if key == "dec" else hashlib.sha1()
            algo.update(r.stdout)
            content[key] = algo.hexdigest()
    out['d19_source'] = 'group tree %s' % GROUP
else:
    out['d19_source'] = 'UNAVAILABLE (no group tree)'

facts['ts'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
facts['dec_sha'] = content.get('dec')
facts['ord_sha'] = content.get('ord')
facts['dec_prev'] = dec_prev
facts['ord_prev'] = ord_prev
facts['dec_changed'] = (content.get('dec') or '') != '' and content.get('dec', '').lower() != (dec_prev or '').lower()
facts['ord_changed'] = (content.get('ord') or '') != '' and content.get('ord', '').lower() != (ord_prev or '').lower()

with io.open('results/_r711bmc_s05_facts.json', 'w', encoding='utf-8') as f:
    json.dump(facts, f, ensure_ascii=True, indent=1)

lines = ["ts=%s" % facts['ts'],
         "orders disk=%d ack=%d unacked=%s" % (facts['orders_disk_count'], facts['orders_ack_count'], unacked),
         "ghost_ack(count)=%d" % len(ghost),
         "dec sha=%s prev=%s changed=%s" % (facts['dec_sha'], facts['dec_prev'], facts['dec_changed']),
         "ord sha=%s prev=%s changed=%s" % (facts['ord_sha'], facts['ord_prev'], facts['ord_changed'])]
sys.stdout.buffer.write(("\n".join(lines)).encode('ascii', 'backslashreplace'))
print()
