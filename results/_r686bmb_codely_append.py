"""r686 bm-b: append one CODELY.md pit line (probe-reuse law, r680 two-false-alarm
composite). Idempotence: assert marker count==0 before append, ==1 after (r679 law)."""
import io

ROOT = "CODELY.md"
marker = "r680 bm-b] D-19 平行探针双律丢失两连假警坑"
txt = open(ROOT, encoding="utf-8", errors="replace").read()
assert txt.count(marker) == 0, "marker already present (r679 replay law)"

line = ("- [2026-10-04 16:3x r680 bm-b] D-19 平行探针双律丢失两连假警坑（r503 大小写×r458/r672 口径复合面）："
        "从零新写 D-19 水位探针丢两律=两连假 CHANGED——①hexdigest 小写 vs 水位存大写=形态假警"
        "（正典 Tools/d19_check.py 已带 r503 upper() 归一·仅 decisions 腿）②orders 键=SHA-1 40-hex "
        "（state 无 last_orders_sha_method 键）而探针默认算 SHA-256 64-hex=口径假警（r458 原坑+r672 "
        "值长度自证律）。How to apply：D-19 双键检查一律复用仓内最新探针范式改造"
        "（r686=results/_r686bmb_d19_check.py 双律内建版），禁从零平行新写；见「orders_changed=true 但前轮曾 MATCH」"
        "先查自探针双律再上报（r641 复现证伪律族）。\n")

if not txt.endswith("\n"):
    txt += "\n"
with io.open(ROOT, "a", encoding="utf-8", newline="") as f:
    f.write(line)
txt2 = open(ROOT, encoding="utf-8", errors="replace").read()
assert txt2.count(marker) == 1, "marker count must be exactly 1 after append"
print("CODELY line appended; delta chars:", len(txt2) - len(txt))
