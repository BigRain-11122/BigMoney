# -*- coding: utf-8 -*-
"""r670 bm-c S4 direct-write pit: needle same-round different-pit collision -> pit-git.md tail.

r668 same-window direct-write precedent (main headroom 619B redline, zero main
occupancy); byte equation + rerun guard + tail EOL gate."""
import hashlib

ROW = ("- [2026-10-07 11:0x r670 bm-c] **拆件 needle 同轮号异坑撞车坑（r659 自配族姊妹面·sibling already-migrated 门当场拦截实弹·fail-closed 零写出）**："
       "r670 lineage-receipt 拆件 12 needle 中裸轮号形态「[2026-10-06 19:2x r637 bm-c]」撞 pit-git-resolver.md 同轮号另一条坑"
       "（合并恢复验证 marker 扫描坑≠值锚滞代坑）——单轮多坑是常态（同窗双坑/三坑频发），裸轮号 needle 在跨件 already-migrated 扫描面=恒假撞。"
       "正法=拆件/回扫 needle 一律带坑名内容特征段（轮号+**坑名前缀短串），sibling 门拦截「needle already in」先查同轮号异坑勿误判 already-migrated。"
       "How to apply：r441/r669/r670 系拆件模板 MOVE_NEEDLES/STAY_NEEDLES 全带内容特征段；"
       "连带 r653 第三活例勘注（声明 676/803B vs 实测 677/802B 双陈旧·一切 byte gate 当场 derive 禁抄收据尾值）。")

p = r"research\pit-git.md"
raw = open(p, "rb").read()
assert raw.endswith(b"\r\n"), "tail EOL gate"
guard = "r670 bm-c] **拆件 needle".encode("utf-8")
assert guard not in raw, "rerun guard"
row_b = ROW.encode("utf-8")
new = raw + row_b + b"\r\n"
assert len(new) == len(raw) + len(row_b) + 2, "byte equation"
open(p, "wb").write(new)
print("appended", len(row_b) + 2, "B; pit-git now", len(new), "B; sha16", hashlib.sha256(row_b).hexdigest()[:16])
