# -*- coding: utf-8 -*-
# r667 bm-b round report addendum: push-race closeout record (r641 append pattern)
import io, datetime

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
entry = f"""- 追记 {now} (S7 收口窗 push-race 实弹): bm-a r673 同窗推 origin -> 首推 non-FF 拒 (fetch first) -> r437 净路: churn absorb 饱和引擎 3 活面 (789ca2c83) + merge origin 14 UU -> 分类器 7 分类 + 7 UNKNOWN 手工定性 (_r667bmb_uu_probe.py 双侧 ts 实证) -> audit/regime (ts,canon) union 零丢失 + token_usage per-key union (r456 side-pick 律防 bm-b 条目回退) + 12 面按嵌入 ts take-side (docs 日报/LIVE 四件取 bm-a 侧新 1-2s; futures/lhb/update_status/regime 取本机侧新) -> reparse/marker/trio containment/state-heartbeat 断言全过 (_r667bmb_merge_resolve.json) -> merge commit 2391e053a push_verify DELIVERED (ahead=0); 本地未达 origin commit 数=0
"""
with io.open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(entry)
d = io.open(r"logs\iteration-loop\round_reports.md", "rb").read()
tail = d[-400:].decode("utf-8", "replace")
assert "2391e053a" in tail and "本地未达" in tail, "addendum verify failed"
print("addendum appended OK")
