# -*- coding: utf-8 -*-
"""R270 bm-a GM s3 件⑤：research/ORDERS_INDEX.md 生成器（CEO 令索引+取代/修正裁定面）。

- 输入：fleet/orders/O-*.md 全量原文（禁用陈旧 JSON 面——orders_index.json 为 R263 捐赠 83 单快照，缺 O-2000）
- 裁定面：本脚本内嵌 GM 裁定 dict（O-20260923-1620 非重大自决权·R270 件⑤/件⑥ 联合裁定）
- 纪律：确定性幂等（同输入重跑字节恒等）；裁定以令原文为准（s1 关键词面→GM 原文精读正典化）
- selftest：python results/_r270bma_orders_index_md.py selftest
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS_DIR = os.path.join(ROOT, "fleet", "orders")
OUT = os.path.join(ROOT, "research", "ORDERS_INDEX.md")

# ---- GM 裁定面（R270·件⑤/件⑥联合·原文精读裁定）----
# status 取值：生效 / 生效-条款被取代 / 修正后生效 / 假面裁定
RULINGS = {
    "O-20260923-1738-bm-a": {
        "status": "生效-条款被取代",
        "note": "「保留 20%」仓位条款被 O-20260924-1136 条款级取代；其余条款（含算力动员政策=BACKTEST_PLAN §六引用面）继续生效",
    },
    "O-20260923-2205-bm-a": {
        "status": "修正后生效",
        "note": "机制修正：iron_rules 熔断第三条 CEO 人工复盘环节废止→自动；令本体在册",
    },
    "O-20260924-1136-bm-a": {
        "status": "生效",
        "note": "令对令取代边唯一例：取代 O-20260923-1738「保留 20%」条款（条款级·非整令取代）",
    },
    "O-20260924-1730-bm-a": {
        "status": "修正后生效",
        "note": "机制修正：排期语（「今晚/下轮」）废止→CEO 令即时律；即时律本体=常设机制法",
    },
    "O-20260924-2012-bm-a": {
        "status": "修正后生效",
        "note": "架构修正：B_MAXDIV 全局正典→军内分散法（令文明示「不作废」）",
    },
    # 关键词假面（s1 九面中的 5 面=prose 命中非令级动作）
    "O-20260923-1705-bm-a": {
        "status": "生效",
        "note": "假面裁定：命中行=「红线永不因风格让路」纪律语，非让路令",
    },
    "O-20260923-2134-bm-a": {
        "status": "生效",
        "note": "假面裁定：命中行=「假摔收回」流派名，非收回令",
    },
    "O-20260923-2210-bm-a": {
        "status": "生效",
        "note": "假面裁定：命中行=「47 作废」批内试验作废计数，非令作废",
    },
    "O-20260925-2313-bm-c": {
        "status": "生效",
        "note": "假面裁定：「让路纪律」=生效纪律条款（主归属保主律），非本令让路",
    },
    "O-20260926-1355-bm-a": {
        "status": "生效",
        "note": "假面裁定：「让号重编 83」=派工票号撞号让路，非令取代；本令=T-83 治理审计母令",
    },
}

HEADER = """# BigMoney CEO 令索引与取代裁定（ORDERS_INDEX）v1.0

> 定位：T-83 s3 件⑤（O-20260926-1355）——L9 令面索引+取代链裁定正典。输入=s1 L9 清点（83 令关键词面）+s2 D9/D10 机械检测+**GM 原文精读裁定**（本件唯一裁定权威）。
> 生成：确定性幂等生成器 `results/_r270bma_orders_index_md.py`（直读 fleet/orders/ 原文·同输入重跑字节恒等）。
> 维护律：新令=签发机随令落册自动入索引（本件重跑即纳）；裁定修订=GM 署名 append（禁无痕改裁定面）。
> 立法：2026-09-26 R270 bm-a GM 会话署名（O-20260923-1620）。

## 一、取代链与机制修正裁定（GM 正典裁定·s1 九关键词面→裁定后真相）

| 类别 | 令 | 裁定 |
|---|---|---|
| **令对令取代边（唯一例）** | O-20260924-1136 → O-20260923-1738 | 条款级取代：O-1738「保留 20%」仓位条款被取代；**其余条款继续生效**（含算力动员政策——BACKTEST_PLAN §六引用面经 D10 核实合法零改） |
| 机制修正（3） | O-20260923-2205 | iron_rules 熔断第三条 CEO 人工复盘环节**废止→自动**；修正后生效 |
| | O-20260924-1730 | 排期语（「今晚/下轮再说」）**废止→CEO 令即时律**；常设机制法修正后生效 |
| | O-20260924-2012 | B_MAXDIV 全局正典→**军内分散法**（令文明示「不作废」）；架构修正后生效 |
| 关键词假面（5） | O-20260923-1705 / O-20260923-2134 / O-20260923-2210 / O-20260925-2313-bm-c / O-20260926-1355 | 命中行分别为纪律语/流派名/试验作废计数/让路纪律条款/票号让路——**均非令级取代·作废·收回**，五令全生效 |
| 陈令误引敞口（D10） | 轮报告三机扫描 | 取代后误引=0；正典件引用被取代令=1 件（BACKTEST_PLAN 引 O-1738 未取代条款=合法） |

**结论（承 s2 D9 互证）**：83+1 令系统内令对令取代仅 1 条条款级边——CEO 令系统无连环 supersede 链；「9 取代/让路/作废/收回面」关键词计数=1 真 edge+3 机制修正+5 假面。

## 二、全量索引（按令号升序·状态列以 §一裁定为准）

"""

FOOTER = """
## 三、引用律（DOC_HIERARCHY §二.5 同源）

1. 引用既有令前必查本索引状态列；「生效-条款被取代」令只可引其未取代条款；
2. 机制修正（§一）引用时以修正后语义为准（如 iron_rules 复盘环节=自动非 CEO 人工）；
3. 本索引状态列=唯一权威；s1/AUDIT 关键词面计数=检测面非裁定面，冲突时以本件为准。

—— v1.0 · bm-a R270 GM 会话 · 2026-09-26 · 复审锚=本文件+post_review 行 T-83-S3-GM-SLICE2
"""


def parse_order(path):
    oid = os.path.basename(path)[:-3]
    lines = open(path, encoding="utf-8").read().splitlines()
    title = ""
    quote = ""
    for l in lines[:8]:
        if l.startswith("# ") and not title:
            t = l[2:].strip()
            title = t.split("·", 1)[1].strip() if "·" in t else t
        if ("原话" in l or "收令" in l) and "「" in l and not quote:
            m = re.search(r"「(.{0,60})", l)
            if m:
                quote = m.group(1)
    return oid, title, quote


def build():
    rows = []
    for path in sorted(glob.glob(os.path.join(ORDERS_DIR, "O-*.md"))):
        oid, title, quote = parse_order(path)
        r = RULINGS.get(oid, {})
        rows.append((oid, title, quote, r.get("status", "生效"), r.get("note", "")))
    assert rows, "no orders found"
    out = [HEADER]
    out.append("| 令号 | 标题 | CEO 原话首句 | 状态 | 裁定备注 |")
    out.append("|---|---|---|---|---|")
    for oid, title, quote, status, note in rows:
        t = title.replace("|", "\\|")[:80]
        q = quote.replace("|", "\\|")[:50]
        out.append(f"| {oid} | {t} | {q} | {status} | {note} |")
    out.append(FOOTER)
    return "\n".join(out) + "\n", rows


def main():
    md, rows = build()
    n_ruled = sum(1 for r in rows if r[3] != "生效" or r[4])
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        md2, rows2 = build()
        assert md == md2 and len(rows) == len(rows2), "non-deterministic"
        assert any(r[0] == "O-20260924-1136-bm-a" for r in rows), "edge order missing"
        assert any("O-20260926-2000" in r[0] for r in rows), "O-2000 missing (stale-input trap)"
        print(f"selftest PASS: n_orders={len(rows)} n_ruled={n_ruled} deterministic ok")
        return
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print(f"wrote {OUT}: n_orders={len(rows)} n_ruled={n_ruled}")


if __name__ == "__main__":
    main()
