# r291 bm-b resolve: autofill_state.json rebase UU (S0 pull --rebase 撞头)
# 分类=mixed-dict+ledger (classify: launches ledger + last_tick dict, autofill_state.json 族)
# 两侧实况（blob 三面冻结于 results/_r291bmb_blobs/）：
#   base  = 13345483: launches 47, last_tick 18:20:01 bm-a, LF, indent=1, launches-first
#   ours  = origin/main 5b32474e: launches 48 (=base+1 new dce2-legacy-lb 09:40:01 bm-b),
#           last_tick 18:30:01 bm-a, LF, indent=1, last_tick-first
#   theirs= 本机 tick 自提交 7fe070c6: launches 47 (⊆base 零新), last_tick 18:30:01 bm-b,
#           CRLF(生产者翻面), indent=1, launches-first
# 配方判定：
#   launches union = base∪ours∪theirs = 48 = ours 侧全集 (theirs 零增量, set 实证) → 零丢失=ours 字节
#   last_tick 同秒 tie (18:30:01==18:30:01) → HEAD=ours (r140 律, rebase 中 HEAD=上游侧)
#   结论: union 结果与 ours blob 字节恒等 → take-side 整字节, 禁 json.dumps 重序造伪 churn (r339 律)
import json, subprocess, hashlib, shutil, os

OURS = "results/_r291bmb_blobs/ours.r291bmb.json"
TARGET = "results/autofill_state.json"

with open(OURS, "rb") as f:
    ours_bytes = f.read()
d = json.loads(ours_bytes.decode("utf-8"))          # 解析验证过才写回 (r185 律)
assert isinstance(d.get("last_tick"), dict), "last_tick must be dict (r203 律)"
assert isinstance(d.get("launches"), list) and len(d["launches"]) == 48, "union launches must be 48"

with open(TARGET, "wb") as f:
    f.write(ours_bytes)                             # 字节级 take-side, LF 原样

with open(TARGET, "rb") as f:
    back = f.read()
assert back == ours_bytes, "write-back must be byte-identical to ours"
d2 = json.loads(back.decode("utf-8"))
assert isinstance(d2["last_tick"], dict) and len(d2["launches"]) == 48
print("RESOLVED take-ours sha256", hashlib.sha256(back).hexdigest()[:16], "launches", len(d2["launches"]), "last_tick ts", d2["last_tick"]["ts"])
