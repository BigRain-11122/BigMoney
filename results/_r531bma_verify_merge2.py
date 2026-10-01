import os, re, ast, sys
d = os.path.join(os.environ["TEMP"], "r531_surgical")
n1 = os.path.join(d, "merged_scripts__perpetual_faces_n1.py")
n = open(n1, encoding="utf-8").read()
print("WAVE_CONFIGS keys:", re.findall(r"^\s+(\d+): \{.batch.: .PERPETUAL-N1", n, re.M))
print("_set_wave order:", re.findall(r"_set_wave\((\d+)\)", n))
try:
    ast.parse(n)
    print("AST OK")
except SyntaxError as e:
    print("AST FAIL line", e.lineno, e.msg)
i17 = n.find('17: {"batch": "PERPETUAL-N1-W17"')
i18 = n.find('18: {"batch": "PERPETUAL-N1-W18"')
i19 = n.find('19: {"batch": "PERPETUAL-N1-W19"')
print("config order 17<18<19:", -1 < i17 < i18 < i19)
print("W19 leg dep style:", "W19 in-flight" in n or "dep=W18" in n)
# show the W19 selftest leg's dep assertion text
m = re.search(r"W18 output.*?missing", n)
print("W19 leg dep on W18 output text:", bool(m))
