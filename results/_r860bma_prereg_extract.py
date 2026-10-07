import io
src = open(r'research\TRIAL_LABOR_W16_PREREG.md', encoding='utf-8').read()
i = src.find('TRIAL_LAB_W16_JUDGE')
out = src[max(0, i - 300):i + 2600]
with open(r'results\_r860bma_prereg_judge_extract.txt', 'w', encoding='utf-8') as fh:
    fh.write(out)
print('written', len(out))
