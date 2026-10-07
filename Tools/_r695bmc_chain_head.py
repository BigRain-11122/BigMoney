"""r695 bm-c unified-chain live head read: science_gates.ledger_head()
actual-read per r690 chain-probe canon (never key-guess)."""
import json
import os
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.path.insert(0, REPO)                    # root: knowledge.* imports
sys.path.insert(0, os.path.join(REPO, "scripts"))  # scripts: science_gates
import science_gates  # noqa: E402

facts = {}
try:
    head = science_gates.ledger_head()
    facts["ledger_head"] = head
except Exception as e:
    facts["error"] = repr(e)[:300]
    # fallback: try common attr names
    for name in ("ledger_head", "LIVE_HEAD", "live_head"):
        if hasattr(science_gates, name):
            try:
                facts[f"attr_{name}"] = getattr(science_gates, name)()
            except Exception as e2:
                facts[f"attr_{name}_err"] = repr(e2)[:200]

out = os.path.join(REPO, "results", "_r695bmc_chain_head.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print(json.dumps(facts, indent=1, ensure_ascii=False))
