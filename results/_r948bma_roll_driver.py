import io
src = io.open(r'results\_r945bma_s6_driver.py', encoding='utf-8').read()
src = src.replace('_r945bma_s6_chain.json', '_r948bma_s6_chain.json')
src = src.replace('r942 bm-a S6 chain driver (r942 bloodline rolled one generation',
                  'r948 bm-a S6 chain driver (r945 bloodline rolled one generation')
old_env = '    env = dict(os.environ)'
new_env = ('    env = dict(os.environ)\n'
           '    env.setdefault("PYTHONIOENCODING", "utf-8")')
assert old_env in src
src = src.replace(old_env, new_env, 1)
io.open(r'results\_r948bma_s6_driver.py', 'w', encoding='utf-8', newline='').write(src)
print('driver written', len(src))
