# -*- coding: utf-8 -*-
# r386 bm-c bookkeeping: T-147 progress + CODELY pit law + METHODOLOGY E09 card
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# ---- 1. T-147 ticket progress (LF json) ----
tp = REPO + r"\fleet\tasks\T-2026-10-02-147-P1.json"
t = json.loads(open(tp, encoding="utf-8").read())
t["progress"] = ("r385 claim+recon; r386 s1 DONE (results/lowamp_p3/s1_evidence_extract.json 11.3KB): "
    "16-face table + deep-axis per-start dists (12m: LA-REP 85.1% positive / 46.5% beat / median +3.2%; "
    "24m same face) + double-nulls support (block bootstrap B2000 p05 0.977 stable, sign-flip p~0 "
    "strongly positive daily mean; deep same-mask nulls NOT burned -> s2 prereg must include) + "
    "REFINE_BENCH sec.2 ranked variant table (entry-filter/exit/position/timing axes) + "
    "FINDING: P3 runner sizing dead-letter -- spec['sizing'] never consumed by _cell_task/_cont_task, "
    "judged 4 cells all ran invvol, 'LA-EQ' = mislabeled invvol twin (pos-aligned 2760/2760 starts "
    "byte-identical, cont faces identical), eq never truly burned in judged cells; headline LA-REP ran "
    "as declared -> P3 judged-negative verdict unaffected; sens draws (L516-534 consume sizing "
    "correctly) = only true eq-vs-invvol evidence: invvol p50 1.2135 > eq p50 1.1192. "
    "Next (s2): family prereg draft -- deep-axis named face (W grid {89,104}, N=2, invvol evidenced "
    "sizing) as main judge, new runner MUST consume sizing explicitly + production-path selftest leg "
    "(assert eq != invvol through cell executor), deep-axis same-mask nulls in batch, born-main-exam "
    "gates, exit-axis sec.0.6 double channel verbatim from P3, new-evidence-delta declaration vs "
    "closed lowamp_daily_xs (M3 reopen channel).")
with open(tp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(t, fh, ensure_ascii=False, indent=1)
print("T147 progress updated")

# ---- 2. CODELY.md pit law append (CRLF) ----
cp = REPO + r"\CODELY.md"
b = open(cp, "rb").read()
entry = ("- [2026-10-02 22:2x r386 bm-c] P3 runner sizing 死信坑（LOWAMP-P3 judged cells 定谳·T-147 s1 实弹）："
 "lowamp_p3.py _cell_task/_cont_task 调 build_signal(W,N) 从不消费 CELLS[cell]['sizing']——build_signal 恒返 invvol 权重"
 "→judged 4 cells 实跑全 invvol；「LA-EQ(eq)」=贴错标签的 invvol 孪生（pos 对齐 2760/2760 starts 全字段零差·cont 面恒等·"
 "文件行序错位时 naive zip 给假 571/480 必 pos 对齐）；eq sizing 在 judged cells 从未真烧（sens 腿 L516-534 才是真消费 sizing 的面）。"
 "selftest F3「eq path」腿手搓平行路径全绿盖不住产线死信（r494 族复发）。headline LA-REP 按申报 invvol 实跑→P3 判负结论不受扰；"
 "家族 PBO 在 3 独立配置+1 重复上算（0.4857>0.25 判负不变）。How to apply：新家族 runner 必须显式消费 sizing+产线路径 selftest 腿"
 "（build_signal 过 cell executor 断言 eq≠invvol）；一切 config spec 字段做消费点追踪（声明≠实装·r300 同族）；"
 "冻结批 runner 不回改（as-burned 重放完整性）。\r\n")
open(cp, "wb").write(b + entry.encode("utf-8"))
print("CODELY appended, new size", len(b) + len(entry.encode('utf-8')))

# ---- 3. METHODOLOGY_ASSETS E09 card (CRLF) ----
mp = REPO + r"\knowledge\METHODOLOGY_ASSETS.md"
b = open(mp, "rb").read().decode("utf-8")
anchor = "- **E08 撤-FF-重落环+D 面清零门**"
assert anchor in b
e09 = ("- **E09 spec 字段消费点追踪法**（proven）：config spec 声明的每个字段必须追踪到产线消费点——「声明≠实装」；"
 "selftest 腿必须走产线路径（跑信号构建过真实 cell executor 断言差异）禁手搓平行路径（平行路径全绿盖不住产线死信）。"
 "证据：LOWAMP-P3 sizing 死信（spec['sizing'] 从未被 _cell_task 消费→judged 4 cells 全 invvol·LA-EQ=错标孪生 2760/2760 starts "
 "恒等·T-147 s1 r386 bm-c 定谳）；r522 出场死信/r494 selftest 盖不住真跑路径/r300 命名≠实装同族。\r\n")
i = b.index("## 三、负方法资产")
assert i > b.index(anchor)
b = b[:i] + e09 + b[i:]
tail_anchor = "- 2026-10-02 21:5x（bm-b r595）：工程净路收口步 append E08"
assert tail_anchor in b
b = b.replace(tail_anchor, tail_anchor, 1)
inv_line = ("- 2026-10-02 22:2x（bm-c r386）：审计收口步 append E09（spec 字段消费点追踪法·LOWAMP-P3 sizing 死信定谳·"
 "捕获律第三次 live 实证·T-147 s1）。\r\n")
b = b.rstrip("\r\n") + "\r\n" + inv_line
open(mp, "wb").write(b.encode("utf-8"))
print("METHODOLOGY E09 appended, new size", len(b.encode('utf-8')))
# verify
b2 = open(mp, "rb").read().decode("utf-8")
assert "E09 spec 字段消费点追踪法" in b2 and "E08" in b2 and "N01" in b2
print("METHODOLOGY verify OK")
