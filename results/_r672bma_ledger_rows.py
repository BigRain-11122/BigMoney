# r672 bm-a: extract THEME_JUDGE_P1 and THEME_PERSIST_P1 grammar-ledger rows to UTF-8 file
import io, os

t = io.open(r"research\TRIAL_GRAMMAR_LEDGER.md", encoding="utf-8", errors="replace").read()
out = os.path.join(os.path.dirname(__file__), "_r672bma_ledger_rows.txt")
with io.open(out, "w", encoding="utf-8") as f:
    for l in t.splitlines():
        if l.startswith("| THEME_PERSIST_P1") or l.startswith("| THEME_JUDGE_P1") or l.startswith("| LOWAMP-DEEP-P1"):
            f.write(l + "\n\n===\n\n")
print("WROTE", out)
