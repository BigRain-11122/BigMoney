kit = open('results/_r463bma_w13_layer_kit.py', encoding='utf-8').read()
i = kit.find('"slope_sign_split": {', kit.find('def build_sumn_anchor'))
print(repr(kit[i:i+780]))
