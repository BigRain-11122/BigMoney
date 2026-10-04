# r670 bm-a: dump sec.5 predictions for reconciliation (file out)
src = open("research/THEME_JUDGE_P1.md", encoding="utf-8").read()
s5 = src[11416:12845]
with open("results/_r670bma_sec5_view.txt", "w", encoding="utf-8") as fh:
    fh.write(s5)
print("sec5 dumped", len(s5))
