"""r690 bm-c 5x HANDOVER chain-head live read: scripts/science_gates.py
ledger_head() single-source import (data-driven max cumulative total,
never hand-copied). Pattern credit: r685/r680 5x probe faces."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)   # knowledge package (cost_spec) lives at repo root
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import science_gates

head = science_gates.ledger_head()
print(json.dumps(head, ensure_ascii=False))
