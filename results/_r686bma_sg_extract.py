import io
t = open(r"scripts\science_gates.py", encoding="utf-8").read()
i = t.find('"mass_trial_w2_judge"')
seg = t[max(0, i - 900):i + 1300]
with io.open(r"results\_r686bma_sg_ctx.txt", "w", encoding="utf-8") as f:
    f.write(seg)
print("written", len(seg))
