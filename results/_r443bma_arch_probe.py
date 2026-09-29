import subprocess

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', errors='replace') if r.returncode == 0 else None

arch_o = blob(2, 'research/memory-archive/202609.md') or ''
arch_m = blob(3, 'research/memory-archive/202609.md') or ''
arch_b = blob(1, 'research/memory-archive/202609.md') or ''

probes = {
    'r433': '同门换用法反向证伪律（T-101-V4-A2-PRESCREEN 实弹定谳）',
    'r431': '探针条件率桶 map({False→x}) NaN 归桶伪影律',
    'r233': '阶梯目录消耗态盲区+既有件覆盖拦截实录',
    'r442': 'A10 组合臂判负+择时用法全谱定谳',
}
union = arch_o + '\n' + arch_m
print('archive bytes: base', len(arch_b.encode()), '| origin', len(arch_o.encode()),
      '| mine', len(arch_m.encode()))
for k, needle in probes.items():
    in_o = needle in arch_o
    in_m = needle in arch_m
    print(k, '| in origin-archive:', in_o, '| in mine-archive:', in_m,
          '| union-covered:', in_o or in_m)

# prefix identity for direct-concat feasibility
print('origin starts with base prefix:', arch_o.startswith(arch_b.rstrip('\n')))
print('mine starts with base prefix:', arch_m.startswith(arch_b.rstrip('\n')))
# suffixes
ob, mb = arch_b.rstrip('\n'), None
if arch_o.startswith(ob):
    print('origin suffix bytes:', len(arch_o[len(ob):].encode()))
if arch_m.startswith(ob):
    print('mine suffix bytes:', len(arch_m[len(ob):].encode()))
