# r670 bm-a: grammar-ledger THEME-JUDGE-P1 consumption row append (template = PERSIST row)
import json

src = open("research/TRIAL_GRAMMAR_LEDGER.md", encoding="utf-8").read()
lines = src.splitlines(keepends=True)
persist_rows = [(i, l) for i, l in enumerate(lines) if "THEME_PERSIST_P1" in l]
with open("results/_r670bma_ledger_persist_row.txt", "w", encoding="utf-8") as fh:
    fh.write(f"persist rows found: {len(persist_rows)}\n")
    for i, l in persist_rows:
        fh.write(f"--- line {i} ({len(l)} chars) ---\n{l}\n")
    fh.write("--- file tail EOL check ---\n")
    fh.write(repr(src[-20:]) + "\n")
print("persist row dumped")
