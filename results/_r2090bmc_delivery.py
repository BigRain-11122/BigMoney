# r2090b bm-c delivery proof: one state field + one report addendum line.
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

PROOF = ("commit **8c55b99d22** 已直推 origin/main（712e7075c6..8c55b99d22，无 non-FF）；"
         "fetch 后 `git rev-list --left-right --count origin/main...HEAD` = **0/0**；"
         "`git ls-tree origin/main` 核验五件在位（Tools/s6_chain_bmc.py、scripts/smoke_red_recheck.py、"
         "results/etf_book_phase_atlas_arms.json、results/smoke_red_recheck.bm-c.json、"
         "research/ETF_BOOK_PHASE_ATLAS_ARMS.md）→ **本地未达 origin commit 数=0**")

LINE = ("2026-11-25T15:2x+08:00 | r2090a | bm-c | 送达补记：" + PROOF +
        "。工作树余五张对端面（research/ARBITER-BOARD.md、research/QUANT-BLOCK-BOARD.md、"
        "results/arbiter/STATE.json、results/quant_block_board.json、results/queue_head_collision_probe.json）未吞；"
        "心跳 GPU 族走 `Tools/gpu_face.py apply` 统一为一次探针（audit findings=[] 33 键一致）。"
        "| 记账：本行 1 处（累计 5）")

raw = open(STATE, "rb").read()
d = json.loads(raw.decode("utf-8"))
assert (json.dumps(d, ensure_ascii=False, indent=1).replace("\n", "\r\n")
        + "\r\n").encode("utf-8") == raw, "state round-trip not byte-identical"
d["送达自证_r2090"] = PROOF
with open(STATE, "wb") as fh:
    fh.write((json.dumps(d, ensure_ascii=False, indent=1).replace("\n", "\r\n")
              + "\r\n").encode("utf-8"))

with open(REPORT, "ab") as fh:
    fh.write(b"\r\n" + LINE.encode("utf-8"))
print("delivery proof written")
