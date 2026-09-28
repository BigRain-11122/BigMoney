import sys
sys.path.insert(0, 'scripts')
import science_gates
regs = {k: v for k, v in science_gates.SEED_REGISTRY.items() if isinstance(v, int)}
print("total int keys:", len(regs))
for k, v in sorted(regs.items(), key=lambda x: x[1]):
    print(f"{v:>12}  {k}")
