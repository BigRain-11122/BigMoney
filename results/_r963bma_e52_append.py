# append E52 methodology card to knowledge/METHODOLOGY_ASSETS.md (UTF-8, append-only)
import io

card = """
- **E52 混合时间戳格式字典序假序坑（twin/snapshot deep-ts 探针归一律）**：proven·工程面。deep-ts take-newer 探针对混排时间戳面（"2026-10-11 00:48:00" 空格式 vs "2026-10-11T00:47:32+08:00" T 格式）做裸字符串 max 比较=假序——空格(0x20)<"T"(0x54) 使空格式面恒判小，跨格式侧永不胜出（r963 实弹：REPORT twin origin 00:48:00 实新于 replay 00:47:32，裸比较反取 replay 侧=错账当场自捕改判 :2:）。正法=探针比较前归一（空格→"T"、剥时区后缀）或 datetime.fromisoformat 解析比较；r100/R350 探针硬化律只覆盖了键名面与值形状面，**格式面归一=第三面缺口本卡补位**——一切 resolver/探针脚本写 max(ts) 前必带归一断言。证据：results/_r963bma_resolve3.py 首跑错侧+同窗改判零错账落地（bm-a r963 S0 双 rebase 风暴窗）。
- 2026-10-11 01:1x·bm-a r963（W205 finalize 收口步·O-20261002-2100 捕获律）·单获例 append E52 混合时间戳格式字典序假序坑（live 实证：resolve3 REPORT twin 错侧自捕改判 :2: 零错账）。
"""

p = 'knowledge/METHODOLOGY_ASSETS.md'
with io.open(p, 'r', encoding='utf-8') as f:
    content = f.read()
assert 'E52' not in content, 'E52 already present'
with io.open(p, 'a', encoding='utf-8', newline='') as f:
    f.write(card)
print('E52 appended OK')
