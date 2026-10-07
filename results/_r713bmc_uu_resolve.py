# -*- coding: utf-8 -*-
# r713 bm-c rebase UU resolver v2: 3-way (diff3) single-hunk ts face,
# newer-wins keep. Hard gates: marker-free + valid JSON + ts = newest.
import re, json

PATH = "results/_attrition_guard_scan.json"
raw = open(PATH, encoding="utf-8-sig").read()

pat = re.compile(
    r"<<<<<<<[^\n]*\n(?P<ours>.*?)\n\|\|\|\|\|\|\|[^\n]*\n(?P<base>.*?)\n=======\n(?P<theirs>.*?)\n>>>>>>>[^\n]*\n?",
    re.S)
m = pat.search(raw)
assert m, "no diff3 hunk found"

def ts_of(block):
    t = re.search(r'"ts"\s*:\s*"([^"]+)"', block)
    return t.group(1) if t else ""

t_ours, t_theirs = ts_of(m.group("ours")), ts_of(m.group("theirs"))
keep = m.group("ours") if t_ours > t_theirs else m.group("theirs")
out = raw[:m.start()] + keep + "\n" + raw[m.end():]

for marker in ("<<<<<<<", "=======", ">>>>>>>", "|||||||"):
    assert marker not in out, "marker remains: " + marker
d = json.loads(out)
assert d.get("active_loss") is False and d.get("rc") == 0, "shape gate"
assert d["ts"] == max(t_ours, t_theirs), "ts newest gate"
print("ours ts:", t_ours, "| theirs ts:", t_theirs, "| kept:", d["ts"])

with open(PATH, "w", encoding="utf-8", newline="") as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
print("resolved+written, valid JSON, active_loss=False rc=0")
