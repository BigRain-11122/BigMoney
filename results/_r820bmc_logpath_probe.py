src = open('Tools/autofill.py', encoding='utf-8').read()
i = src.find('}.log')
print(src[max(0, i-400):i+80])
