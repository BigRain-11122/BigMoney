src = open('results/_r472bmb_w14_runner_draft.py', encoding='utf-8').read()
i = src.find('"G-SUMN": {"pass"')
print(repr(src[i - 80:i + 300]))
