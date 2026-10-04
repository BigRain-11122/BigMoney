# -*- coding: utf-8 -*-
"""r682 bm-a: append ONE pit line to CODELY.md (byte mode, utf-8, no CRLF
translation per r641 law); verify count==1 anchor + size after."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(REPO, 'CODELY.md')
LINE = ("- [2026-10-04 15:5x r682 bm-a] N4 新家族窗 gap-finder 活跃梯子地雷（B4 踏勘实证·零烧零注册）："
        "「family window 之上首个 ≥1,497 净窗」裸 gap-finder 产出 275_004..276_500=恰为 N1 A 阶梯活跃续带路径"
        "（注册 A 墙止于表尾 W115=275_003·W116 即取 275_004..277_003·bm-b 在飞）——"
        "N1 波带表只含已注册行，never-dry 泵梯子无表内终点（A-ladder 2,000/波·B-ladder 200/波皆无终点），"
        "任何「表尾后首个净窗」都坐在活跃梯子路径上。正法=种子域新窗分配必带梯子 horizon 门："
        "窗下限≥当前 A 头+130 波×2,000（B1 自家「~130+ 波」先例）且扫描面并 B-ladder 跳位投影+SEED_REGISTRY 活值+实际流全域；"
        "N4-B4 另有 B3 §5 冻结句「无余尾即无 B4 时点」（O-20260930-1901 意义门·满耗收口即家族面完备）"
        "=新窗唯一合法开窗条件=月界成员变更。证据=results/_r682bma_n4b4_band_scan.py+fleet/inbox/MSG-2026-10-04-1600-bma-ALL.md。"
        "How to apply：未来任何种子域窗口分配（N4 新家族窗/N2 后续波带/N3 域扩展）先过梯子 horizon 门勿信「表内无冲突」；表尾≠梯子尾。\n")
b = open(FP, 'rb').read()
assert b.count('275_004..276_500'.encode('utf-8')) == 0, "anchor already present (dup append)"
# detect file EOL convention for the tail join
tail_lf_only = b.endswith(b'\n')
with open(FP, 'ab') as fh:
    if not tail_lf_only:
        fh.write(b'\n')
    fh.write(LINE.encode('utf-8'))
b2 = open(FP, 'rb').read()
assert b2.count('275_004..276_500'.encode('utf-8')) == 1, "post-append count!=1"
assert b2[:len(b)] == b or (b + LINE.encode('utf-8') == b2), "non-append mutation"
print("CODELY appended 1 line; size:", len(b), "->", len(b2), "bytes")
