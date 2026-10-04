"""r685 bm-a: append two CODELY pit entries (UTF-8, append-only)."""
import io

ENTRIES = [
    "- [2026-10-04 16:3x r685 bm-a] trials 链扫描器×quarantine 退证面回流坑（science_gates.ledger_head/active_voids 递归 glob 不排除 results/_quarantine/**.json——TREASURE 保护律 s2 aside 正径的隔离件回流链头：r685 实弹 bogus W3 summary（complete=false·total 648,026）隔离后仍被 ledger_head 吃作 prev_total=648,026 进新块=W3 双计 6041）→ 修=两扫描环加 path-segment `os.sep+'_quarantine'+os.sep` skip（段匹配防裸子串误伤 quarantine 命名合法件）+ selftest 临时目录腿（70/70 PASS）。How to apply：隔离区挪 trials_ledger/账本类 json 件=修已落则照挪、未落链扫描面必先核排除；他机未合并本修前勿按「隔离即安全」直觉挪账本件（cherry-pick 本 commit 或先查 _quarantine 排除在位）。",
    "- [2026-10-04 16:3x r685 bm-a] dup 探针时点×fleet push-race 回流坑（r482 bm-c「finalize 前 id 零重探针」的时点盲区：分片收口窗探针绿后 3min 内 git auto-merge 回流他机在飞重烧 1227 dup-id 行〔both-sides-append 文本自动合并=行集并集不 id 去重·我方零改动面=静默 take theirs〕→ finalize 撞 6136 行产出 bogus 账本块〔幸未推送·quarantine 两件治愈〕）。How to apply：id-dup 探针必须与 finalize 同窗（post-merge 后立即跑、finalize 消费同一产物文件），分片收口窗的绿探针不作 finalize 窗充分证据；checkpoint 类 append-only 面经任一 merge 后必复跑 dup 探针；见 dup>0 即 keep-first id 去重（elapsed_s-only 方差断言=零信息损失）再 finalize。",
]

with io.open("CODELY.md", "a", encoding="utf-8", newline="") as f:
    for e in ENTRIES:
        f.write(e + "\n")
print(json_ok := "appended 2 entries")
# verify
raw = open("CODELY.md", "rb").read().decode("utf-8")
assert raw.count("r685 bm-a") >= 2, "entries missing"
print("verify: r685 entries present =", raw.count("[2026-10-04 16:3x r685 bm-a]"))
