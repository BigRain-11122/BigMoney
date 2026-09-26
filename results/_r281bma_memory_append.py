# -*- coding: utf-8 -*-
"""R281 bm-a memory append (two entries, four-gate law: long-term value,
no-restating, lesson-first, one-thing-per-entry)."""
import os

P = "CODELY.md"
raw = open(P, "rb").read()
assert raw.endswith(b"\n"), "no tail newline"
entries = (
    " - [2026-09-27 00:5x] 坑律（bm-a R281·共享 JSON 写回 ensure_ascii 探针方向面"
    "·r255 家族新参·E1 写回期自捕零外泄）：**「文件含裸非 ASCII」＝原写手 "
    "ensure_ascii=False 的证据（探针方向不可反读）——反读成 True=全文中文转 "
    "\\uXXXX 整文件伪重排（runnable_pool 25 删行 --stat 当场自捕，restore 重注）；"
    "连带=union 型 resolver 的 EOL 探针在混面 blob（36 行 CRLF+1866 行 LF 共存）上按"
    "「存在 CRLF」取 \\r\\n join=全文 LF→CRLF 翻面 +1902/−1866 整文件伪 diff，"
    "正解=LF 归一写回（r270 producer 归一律，修正面 +72/−36 纯增量）。"
    "指针=results/_r281bma_pool_register.py 修正段+results/_r281bma_resolve2.py "
    "EOL 病腿+amend 463bde3a\n"
    " - [2026-09-27 00:5x] 坑律（bm-a R281·rev_osc 复发射前双雷排爆·g2 合同面"
    "+ledger 键双病·E1 审读期自捕）：**cscv_pbo 返回完整记录 dict 而 "
    "g2_registration_v2 收 pbo 浮点（float(dict)=TypeError）——finalize 原样传 "
    "dict＝「跑完 30min 算力后必崩」型雷（cn_regime_policy float(pbo[\"pbo\"]) "
    "已证调用形）；连病=ledger 嵌块键名 ledger≠正典 trials_ledger（r252 链盲面）；"
    "零判产物窗工程修合法（r253）；连带=自测桩形状必须随真函数合同走（rev_osc 桩 "
    "lambda:0.1→改 {\"pbo\":0.1}）。指针=scripts/rev_osc_stock_p1.py r281 "
    "AMENDMENT 段+scripts/cn_trend_etf_p1.py finalize pbo_val 段\n"
)
with open(P, "ab") as fh:
    fh.write(entries.encode("utf-8"))
print("appended, new size", os.path.getsize(P))
assert os.path.getsize(P) < 50_000 or print("WATERMARK: >=50KB hot-cold due")
