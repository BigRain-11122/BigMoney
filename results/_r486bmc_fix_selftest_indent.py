"""r486 bm-c: repair the mangled indentation of the reinstated r685
selftest leg in scripts/science_gates.py (7-space indent from a fuzzy
replace). Byte-level: locate region between the CLOSED_FAMILIES registry
check closing line and the n_fail line, rewrite at correct 4-space
function-body indent, preserve file EOL convention, ast.parse verify."""
import ast

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts\science_gates.py"
src = open(P, encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in src else "\n"
norm = src.replace("\r\n", "\n")
lines = norm.split("\n")

i_reg = None
for j, l in enumerate(lines):
    if l.strip() == "<= set(CLOSED_FAMILIES_REOPEN_RULES))":
        i_reg = j
if i_reg is None:
    raise SystemExit("anchor CLOSED_FAMILIES close not found")
i_nf = None
for j in range(i_reg + 1, len(lines)):
    if lines[j].strip() == "n_fail = sum(1 for _, c in checks if not c)":
        i_nf = j
if i_nf is None or i_nf - i_reg > 40:
    raise SystemExit("n_fail anchor not found in range (%r)" % i_nf)

block = [
    "",
    "    # r685 bm-a: quarantine-window aside-copies must not enter the chain scan",
    "    # (TREASURE_PROTECTION_LAW s2 vs recursive glob; live instance: quarantined",
    "    # W3 summary re-entered ledger_head as the head block and double-counted).",
    "    # (reinstated r486 bm-c: clobbered by r687 file-level yield merge)",
    "    import tempfile",
    "    with tempfile.TemporaryDirectory() as td:",
    "        qd = os.path.join(td, \"_quarantine\", \"aside\")",
    "        os.makedirs(qd, exist_ok=True)",
    "        json.dump({\"trials_ledger\": {\"total\": 999_999_999}},",
    "                  open(os.path.join(qd, \"bogus.json\"), \"w\", encoding=\"utf-8\"))",
    "        json.dump({\"trials_ledger\": {\"total\": 100}},",
    "                  open(os.path.join(td, \"real.json\"), \"w\", encoding=\"utf-8\"))",
    "        ok(\"ledger_head ignores _quarantine aside-copies (r685)\",",
    "           ledger_head(td)[\"total\"] == 100)",
    "",
    "    n_fail = sum(1 for _, c in checks if not c)",
]
new_lines = lines[:i_reg + 1] + block + lines[i_nf + 1:]
out = "\n".join(new_lines)
ast.parse(out)  # verify BEFORE write
with open(P, "w", encoding="utf-8", newline="") as f:
    f.write(out.replace("\n", eol) if eol == "\r\n" else out)
ast.parse(open(P, encoding="utf-8").read())
print("REGION REBUILT ok: lines %d..%d -> %d lines, eol=%r, ast PASS"
      % (i_reg + 1, i_nf, len(block)))
