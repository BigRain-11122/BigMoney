# -*- coding: utf-8 -*-
"""r119: autofill_state.json diff3 resolution - last_tick = freshest ts
(r349 classifier take-side-3 fresher; mine 00:40:02 bm-c > HEAD 00:30:01)."""
import re, json

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\autofill_state.json"
src = open(P, encoding="utf-8").read()
pat = re.compile(
    r"<<<<<<< HEAD\n(.*?)\n\|\|\|\|\|\|\| [^\n]*\n(.*?)\n=======\n(.*?)"
    r"\n>>>>>>> [^\n]*", re.S)
blocks = pat.findall(src)
print("diff3 blocks:", len(blocks))
out = src
for head, base, mine in blocks:
    # verify the hunk is the last_tick freshness family
    ts_h = re.search(r'"ts": "([^"]+)"', head)
    ts_m = re.search(r'"ts": "([^"]+)"', mine)
    print("HEAD ts:", ts_h and ts_h.group(1), "| MINE ts:",
          ts_m and ts_m.group(1))
    assert ts_h and ts_m and ts_m.group(1) > ts_h.group(1), \
        "freshest-side law violated - manual review needed"
    out = out.replace(pat.search(out).group(0), mine)
json.loads(out)
with open(P, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(out)
d = json.loads(out)
print("resolved: last_tick", d["last_tick"]["ts"], d["last_tick"]["machine"],
      "| launches:", len(d["launches"]))
