# -*- coding: utf-8 -*-
"""r891 retag helper: clone _r887bmb_rebase_resolver.py -> _r891bmb_rebase_resolver.py
(r836 clone law: verbatim logic; diffs confined to window tag + this window's jsonl faces)."""
import io

SRC = "results/_r887bmb_rebase_resolver.py"
DST = "results/_r891bmb_rebase_resolver.py"

src = io.open(SRC, encoding="utf-8").read()
out = src.replace("_r887bmb_rebase_resolver", "_r891bmb_rebase_resolver")
out = out.replace(
    "r887 bm-b rebase-conflict resolver (8-UU window, pick 335eb4db8 replay onto origin/main bfd691ebb)",
    "r891 bm-b rebase-conflict resolver (4-UU window, pick a5b6e0a99 replay onto origin/main 60741b0f5)")
out = out.replace(
    "Clone of results/_r853bmb_rebase_resolver.py (verbatim logic; receipt path + window header retagged",
    "Clone of results/_r887bmb_rebase_resolver.py (verbatim logic; receipt path + window header retagged")
out = out.replace("our r887 content", "our r891 content")
out = out.replace(
    '"round": "r887", "pick": "335eb4db8", "onto": "bfd691ebb"',
    '"round": "r891", "pick": "a5b6e0a99", "onto": "60741b0f5"')
out = out.replace("_r887_union_from_pick", "_r891_union_from_pick")
old_jsonl = ('JSONL_FACES = {"results/x2_watch_log.jsonl", '
             '"results/saturation_engine/history_bm-b.jsonl"}')
new_jsonl = ('JSONL_FACES = {"results/x2_watch_log.jsonl", '
             '"results/saturation_engine/history_bm-b.jsonl", '
             '"results/pool_core_samples.jsonl", '
             '"results/pool_red_flags.jsonl"}')
assert old_jsonl in out, "jsonl anchor not found"
out = out.replace(old_jsonl, new_jsonl)
io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
print("resolver clone written, bytes", len(out))
