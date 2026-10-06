# -*- coding: utf-8 -*-
"""r775 bm-a CODELY.md execution-record append (multi-writer file: python
single-file fresh-read-append per the replace-ban law; one line, one lesson,
memory-gate four questions honored: long-term value = W159+ freezer editors;
no restating of orders/commit text; lesson-first; single item <1.5KB)."""
import io

path = "CODELY.md"
entry = (
    "- [2026-10-06 13:0x r775 bm-a] **冻结编辑器 vmap 碎片断行坑（r773 坑律 pf.py 面漏治收口+W158 freeze 实弹扩展）**："
    "①r773 heal 只治了 n1.py WAVE_CONFIGS cfg 散文，pf.py W157 块投影段两畸形窗（362_204..362_003 / 362_404..360_403）"
    "仍带病灶——r774 交接「pf.py W157 prose heal same-window」r775 已治愈（值=r772 gate leg3 on-disk derive·全件 start>end 扫零残留·pf selftest 9/9）；"
    "②投影散文的 old 串必须按**物理碎片形态**取（跨 python 字符串续行/注释行的逻辑串被引号+缩进+CRLF 打断——逻辑串 old count==0 假阴；"
    "正法=probe dump 全文后按物理行取碎片级 old，或窗值级最小替换）；③W158 freeze（6957f509e）TOK 表全程无裸 seed 前缀 token、"
    "复合带串整串入 TOK、裸 157/156 兜底永远最后跑——r773 坑律全执法闭环实证（18 件 probe 回执在仓）。"
    "How to apply：W159+ 冻结机照 _r775bma_w158_freeze_edits.py 血统（pre-TOK 实证清单→整串 token→碎片级修正→双件全扫）。\n"
)
src = io.open(path, encoding="utf-8", newline="").read()
assert "r775 bm-a" not in src, "double-append guard"
with io.open(path, "a", encoding="utf-8", newline="") as f:
    f.write(entry)
src2 = io.open(path, encoding="utf-8", newline="").read()
assert entry in src2 and len(entry) < 1600
print("CODELY.md r775 line appended,", len(entry), "bytes")
