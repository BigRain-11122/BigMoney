# -*- coding: utf-8 -*-
"""R263 bm-a: T-83 (O-1355 nine-layer governance audit) mechanical face L9:
raw orders index generation (deterministic, zero network, zero LLM).

Scope discipline per ticket note: "mechanical sweeps ... = scriptable, any
machine". This produces the RAW index only -- id, title, CEO-quote head,
mechanical cross-reference map (which O- ids each order cites), file facts.
Supersession ADJUDICATION and stale-citation annotations = GM s3 governance
face, deliberately NOT done here.

Output: results/orders_index.json (results face, machine-checkable).
"""
import io
import json
import os
import re
import time

ORDERS_DIR = os.path.join("fleet", "orders")
OUT = os.path.join("results", "orders_index.json")
O_REF = re.compile(r"O-\d{8}-\d{4}(?:-[a-z0-9]+)*")
CEO_HEAD = re.compile(r"^>\s*(.+)$", re.M)
CEO_QUO = re.compile(r"「([^」]{4,})」")


def main() -> int:
    rows = []
    for name in sorted(os.listdir(ORDERS_DIR)):
        if not (name.startswith("O-") and name.endswith(".md")):
            continue
        path = os.path.join(ORDERS_DIR, name)
        raw = io.open(path, encoding="utf-8-sig").read()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        title = next((l.lstrip("# ").strip() for l in lines if l.startswith("#")), "")
        # CEO original-words head: first blockquote line, else first 「」 quote
        # (orders carry CEO 原话 in either convention)
        m = CEO_HEAD.search(raw)
        if not m:
            m2 = CEO_QUO.search(raw)
            quote_head = (m2.group(1).strip()[:160]) if m2 else ""
        else:
            quote_head = m.group(1).strip()[:160]
        refs = sorted(set(O_REF.findall(raw)) - {name[:-3]})
        st = os.stat(path)
        rows.append({
            "id": name[:-3],
            "title": title[:200],
            "ceo_quote_head": quote_head,
            "cites": refs,              # mechanical cross-ref map (not adjudication)
            "bytes": st.st_size,
            "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
        })
    doc = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ticket": "T-2026-09-26-83 (O-20260926-1355) mechanical face L9",
        "n_orders": len(rows),
        "scope_note": "raw index only; supersession adjudication + stale-citation "
                      "annotation = GM s3 governance face (not done here); "
                      "deterministic re-runnable idempotent",
        "orders": rows,
    }
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"orders index: {len(rows)} orders -> {OUT}")
    cites = sum(len(r["cites"]) for r in rows)
    print(f"mechanical cross-refs: {cites}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
