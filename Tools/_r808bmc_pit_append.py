# -*- coding: utf-8 -*-
"""r808 bm-c: direct-write append of one new pit line to the rebaase
resolver domain file (r666 direct-write precedent; main CODELY.md at
30,643B / 77B headroom = over-cap red line for a ~600B entry, minisplit
deferred to next window per cap law; domain file 24,428B has headroom).
Byte-exact append, UTF-8 no BOM, LF-normalized single line."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "research" / "pit-git-resolver-rebase.md"

entry = (
    "- [2026-10-09 16:1x r808 bm-c] **rebase continue add+continue 原子环 daemon 活写面标记守卫缺口（r825/r917 族精化·当场实录）**："
    "pull --rebase 多 pick 停在 daemon 高频活写面（saturation/autofill 族每分钟续写）时，冲突停止后立即 add+continue 原子环"
    "=把冲突标记版盘面续入 commit（rebase 提交绕过 pre-commit 爪=污染直入库·本窗实弹=picks2/3 saturation 双面 12 处标记入库）"
    "→治法=heal commit（daemon 覆盖后盘面 0 标记验证再吸收·4380a35cf 73 行清除·树面 tip 复零）"
    "；**正法守卫=add 前扫盘面冲突标记（Select-String '^(<<<<<<<|=======)'）·非零即等 daemon 覆盖（≤70s）或 git checkout --theirs 取 pick 侧净版**"
    "——中间 commit 污染可容忍（git 史保全）·树面 tip 必须零标记（git grep -E '^(<<<<<<<)' HEAD 全树扫验证）。"
    "How to apply：三机一切 rebase continue 重试环必须带标记守卫腿；轮报告留痕 heal 链与守卫双验。"
)

raw = TARGET.read_bytes()
if not raw.endswith(b"\n"):
    raw += b"\n"
TARGET.write_bytes(raw + entry.encode("utf-8") + b"\n")
new = TARGET.read_bytes()
assert new.startswith(raw), "append must be pure-tail"
print("pit append OK: %d -> %d bytes (+%d)" % (len(raw), len(new), len(new) - len(raw)))
