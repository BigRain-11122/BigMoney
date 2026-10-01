# r350 bm-c: identify SEED_REGISTRY key(s) at value 46_000 (W51+ B-window
# refusal fact for the canon row WARNING -- refusal facts must be named,
# not anonymous).
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import science_gates
hits = {k: v for k, v in science_gates.SEED_REGISTRY.items() if v == 46_000}
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print("SEED_REGISTRY keys at 46_000:", hits)
