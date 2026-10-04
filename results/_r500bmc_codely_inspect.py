# r500 bm-c: pre-surgery inspection dump.
# Dump L6 vs L155 duplicate domain-pointer entries + L103-L138 region for eyeball diff.
import json

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
with open(REPO + r"\CODELY.md", "rb") as f:
    raw = f.read()
lines = raw.decode("utf-8").split("\n")

def get(n):  # 1-based physical line
    return lines[n - 1]

out = []
out.append("=== L6 entry (canonical candidate) ===")
out.append(get(6))
out.append("=== L155 entry (dup) ===")
out.append(get(155))
out.append("=== L103-L138 region (headers+gap) ===")
for n in range(103, 139):
    s = get(n)
    out.append("L%d[%s]: %s" % (n, "BLANK" if s.strip() == "" else "TEXT", s.strip()[:60]))
out.append("=== L32-48 region ===")
for n in range(32, 49):
    s = get(n)
    out.append("L%d[%s]: %s" % (n, "BLANK" if s.strip() == "" else "TEXT", s.strip()[:60]))
out.append("=== L70-86 region ===")
for n in range(70, 87):
    s = get(n)
    out.append("L%d[%s]: %s" % (n, "BLANK" if s.strip() == "" else "TEXT", s.strip()[:60]))
out.append("=== L196-200 tail ===")
for n in range(196, 201):
    s = get(n)
    out.append("L%d[%s]: %s" % (n, "BLANK" if s.strip() == "" else "TEXT", s.strip()[:60]))

# line-level diff between the two dup entries (r479 substring-containment law)
e6 = set(get(6).split("；"))  # increments are semicolon-separated clauses
e155 = set(get(155).split("；"))
only155 = [c for c in get(155).split("；") if c not in e6]
only6 = [c for c in get(6).split("；") if c not in e155]
out.append("=== semicolon-clause diff ===")
out.append("clauses_only_in_L155: %d" % len(only155))
for c in only155:
    out.append("  +L155only: %s" % c[:100])
out.append("clauses_only_in_L6: %d" % len(only6))
for c in only6[:12]:
    out.append("  +L6only: %s" % c[:100])

with open(REPO + r"\results\_r500bmc_codely_inspect.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("INSPECT-OK lines=%d" % len(out))
