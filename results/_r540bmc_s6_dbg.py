# r540 bm-c: debug firstpass gate on S6 log parse
import re
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r540bmc_s6_log.txt"
s6 = open(p, encoding="utf-8-sig", errors="replace").read()
legs = re.findall(r'^=== (\S+) rc=(\d+)', s6, re.M)
bad = [n + '(rc=' + rc + ')' for n, rc in legs if rc != '0']
m2 = re.search(r'S6 chain end .* bad=\[(.*)\]\s*$', s6)
print("n_legs=", len(legs), "bad=", bad)
print("bad_end_match=", repr(m2.group(1)) if m2 else None)
print("tail=", repr(s6[-80:]))
