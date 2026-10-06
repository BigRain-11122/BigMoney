# -*- coding: utf-8 -*-
"""r781 S6 facts split-heal: the chain (copied from r780) wrote this
round's facts into _r780bma_s6_facts.json (round-stamp patch died on
PS quoting before the chain ran). Move the fresh r781 payload to
_r781bma_s6_facts.json (round=781), restore the committed r780 facts
file from HEAD verbatim, and stamp the chain script for the record."""
import io
import json
import subprocess

P780 = r"results/_r780bma_s6_facts.json"
P781 = r"results/_r781bma_s6_facts.json"
d = json.load(io.open(P780, encoding="utf-8"))
assert d.get("round") == 780 and d.get("machine") == "bm-a", d.get("round")
d["round"] = 781
d["note"] = ("facts split-heal r781: chain payload originally written to the "
             "r780 filename (PS quoting killed the stamp patch pre-run); "
             "moved here with round=781; r780 file restored from HEAD verbatim")
io.open(P781, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
orig = subprocess.run(["git", "show", "HEAD:results/_r780bma_s6_facts.json"],
                     capture_output=True).stdout
io.open(P780, "wb").write(orig)
print("r781 facts landed (", len(d["results"]), "legs, elapsed", d["elapsed_sec"],
      "s); r780 facts restored verbatim,", len(orig), "bytes")
# stamp the chain script for the record
p = r"results/_r781bma_s6_chain.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('"round": 780', '"round": 781').replace(
    "_r780bma_s6_facts.json", "_r781bma_s6_facts.json")
io.open(p, "w", encoding="utf-8").write(s)
print("chain script stamped r781")
