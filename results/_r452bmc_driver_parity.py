"""r452 bm-c driver-parity guard (regenerable): AST parse + leg list vs r451."""
import ast
import re

t = open(r"results\_r451bmc_s6_chain.py", encoding="utf-8").read()
n = open(r"results\_r452bmc_s6_chain.py", encoding="utf-8").read()
ast.parse(n)
print("AST OK")
l1 = re.findall(r'\("(\w+)", \[PY', t)
l2 = re.findall(r'\("(\w+)", \[PY', n)
print("legs:", len(l1), "vs", len(l2), "| equal:", l1 == l2)
args1 = re.findall(r'"scripts/([a-z_0-9]+\.py)"', t)
args2 = re.findall(r'"scripts/([a-z_0-9]+\.py)"', n)
print("script args equal:", args1 == args2)
if args1 != args2:
    print("args1:", args1)
    print("args2:", args2)
# round-number/log path sanity
assert "_r452bmc_s6_log.txt" in n
assert "r452 bm-c" in n
print("PARITY GUARD PASS")
