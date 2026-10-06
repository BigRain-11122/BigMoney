"""r643 bm-c: registry in/out record append (r441 ritual) + D-06 domain-file
size census (<=30KB gate verification face prep). Append-only, UTF-8."""
import glob
import json
import os
import time

REG = r"knowledge\TREASURE_REGISTRY.md"

line = ("- 2026-10-07 00:1x bm-c r643 CODELY 主件流水下沉批（D-20261002-06 主件 ≤30KB 判据腿·r444/r642 范式同款）："
        "prescan 如实 rc3 留痕（CODELY.md+archive 202610.md 均登记册命中·立法窗 D-20261002-06 热冷整编授权面）·"
        "r786 bm-b 三令回执行（766B）+r798 bm-a 双令执行记录（797B）verbatim 下沉 archive 202610.md"
        "『热冷整编 2026-10-07 r643 bm-c 窗批』节·主件 31,744→30,482B（≤30,720 门回归）·"
        "archive 字节增量=删除块和恒等·receipt=results/_r643bmc_codely_sink_receipt.json·"
        "出入=archive 侧纯 append 无删；主件侧删=纯流水面（正本在各令件回执节）+指针行补位。\n")

data = open(REG, "rb").read()
assert b"r643 CODELY" not in data, "registry already has r643 line (idempotency)"
open(REG, "ab").write(line.encode("utf-8"))
print("REGISTRY appended, +", len(line.encode("utf-8")), "bytes")

# D-06 verification-face prep: census of all pit/domain files vs 30KB gate
rows = []
for p in sorted(glob.glob(r"research\pit-*.md")):
    sz = os.path.getsize(p)
    rows.append({"file": p, "bytes": sz, "gate_ok": sz <= 30720})
main_sz = os.path.getsize("CODELY.md")
over = [r for r in rows if not r["gate_ok"]]
census = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"), "round": "r643 bm-c",
          "codely_main_bytes": main_sz, "main_gate_ok": main_sz <= 30720,
          "domain_files": rows, "domain_over_gate": over}
open(r"results\_r643bmc_d06_size_census.json", "w", encoding="utf-8").write(
    json.dumps(census, ensure_ascii=False, indent=1))
for r in rows:
    print(f"{r['bytes']:>7}  {'OK ' if r['gate_ok'] else 'OVER'}  {r['file']}")
print("MAIN", main_sz, "OK" if main_sz <= 30720 else "OVER")
print("OVER_COUNT", len(over))
