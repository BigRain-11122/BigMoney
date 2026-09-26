# -*- coding: utf-8 -*-
"""R270 bm-a: register T-83 s3 GM slice2 claim row (件③⑤⑥⑦).

Checks anchor ONLY stable artifact files (R264 law). Every check string
frozen verbatim from delivered artifact content. Byte-face contract
probed pre-write (R255/R257 law): results/post_review_criteria.json =
no BOM / CRLF / indent=1 / ensure_ascii=False / NO trailing newline.
"""
import io
import json

PATH = "results/post_review_criteria.json"
c = json.load(io.open(PATH, encoding="utf-8"))

row = {
    "id": "T-83-S3-GM-SLICE2",
    "claim": "T-83 s3 GM seven-deliverable batch slice 2 of 3 (件③⑤⑥⑦ landed "
             "this round; with slice1 件①②④ R269 the seven are COMPLETE): "
             "件③ firm/DOC_HIERARCHY.md v1.0 doc-hierarchy canon (L2 21 files "
             "H0-H6 tier order + sole-duty + edit-cadence table, 5 adjudication "
             "rules incl group-repo pointer-qualification law, 4 pointer "
             "disciplines) -> 件⑤ research/ORDERS_INDEX.md v1.0 (84-order full "
             "index; GM source-text adjudication: 1 clause-level supersession "
             "edge O-20260924-1136->O-20260923-1738 retain-20% clause + 3 "
             "mechanism amendments O-2205/O-1730/O-2012 + 5 keyword false "
             "faces O-1705/O-2134/O-2210/O-2313-bm-c/O-1355; s1 nine-face "
             "count adjudicated to truth; deterministic idempotent generator "
             "results/_r270bma_orders_index_md.py reads fleet/orders/ fresh) "
             "-> 件⑥ research/AUDIT-20260926-S2-ADJUDICATION.md (12 rulings: "
             "t22 pair=lane-local big-file false-positive (.gitignore:65, "
             "on-producer verified); 3 group-repo pointers legal (FluxGroup "
             "repo existence verified); SYSTEM_LOGIC 8 legacy names + "
             "FACTOR_BLEND_V2 5 links head-noted archive-not-delete; "
             "HANDOVER append-only history rows zero-rewrite ruling; "
             "local-coding 01-10 scripts no-promotion (consumption-driven "
             "promotion law) + tasks 11/12 unimplemented (dirs 01-10 "
             "verified); 8 living-doc pointer fixes via byte-level idempotent "
             "fixer results/_r270bma_pointer_fixes.py (CASH_LEG=substring "
             "false-face self-caught zero-edit); BACKTEST_PLAN O-1738 "
             "compute-mobilization citation=non-superseded clause legal "
             "zero-edit) -> 件⑦ STRATEGY_LIBRARY §〇 product-line status "
             "single-source table (12 lines x status x judgment-face x "
             "carrier + 6-face negative/dead inventory = L7 zoo upgrade; "
             "WILD-S1 first-adjudicated negative 0/1569 g2-empty from "
             "results/wild_route/wild_route_s1.json; MATRIX/MAP "
             "single-source pointer lines wired) — s3 GM lane fully closed",
    "claim_source": "fleet/orders/O-20260926-1355-bm-a.md §三 s3 + ticket "
                    "T-2026-09-26-83-P1.json progress_r269 continuation "
                    "pointers + inputs research/AUDIT-20260926-S2.md (s2 "
                    "candidates) + results/governance_s2_20260926.json "
                    "(machine face) + delivered artifacts "
                    "firm/DOC_HIERARCHY.md + research/ORDERS_INDEX.md + "
                    "research/AUDIT-20260926-S2-ADJUDICATION.md + "
                    "research/STRATEGY_LIBRARY.md §〇",
    "status": "closed",
    "checks": [
        {"kind": "file_exists", "args": ["firm/DOC_HIERARCHY.md"]},
        {"kind": "file_contains", "args": ["firm/DOC_HIERARCHY.md", "**H0 权与法**"]},
        {"kind": "file_contains", "args": ["firm/DOC_HIERARCHY.md", "集团层指针标注律"]},
        {"kind": "file_exists", "args": ["research/ORDERS_INDEX.md"]},
        {"kind": "file_contains", "args": ["research/ORDERS_INDEX.md", "O-20260924-1136 → O-20260923-1738"]},
        {"kind": "file_contains", "args": ["research/ORDERS_INDEX.md", "生效-条款被取代"]},
        {"kind": "file_contains", "args": ["research/ORDERS_INDEX.md", "O-20260926-2000-bm-c"]},
        {"kind": "file_exists", "args": ["research/AUDIT-20260926-S2-ADJUDICATION.md"]},
        {"kind": "file_contains", "args": ["research/AUDIT-20260926-S2-ADJUDICATION.md", "消费驱动晋升律"]},
        {"kind": "file_contains", "args": ["research/AUDIT-20260926-S2-ADJUDICATION.md", "车道本地大文件面假阳"]},
        {"kind": "file_contains", "args": ["research/STRATEGY_LIBRARY.md", "## 〇、产品线状态单源表"]},
        {"kind": "file_contains", "args": ["research/STRATEGY_LIBRARY.md", "negative（S1 0/1569 过闸）"]},
        {"kind": "file_contains", "args": ["firm/PRODUCT_MATRIX.md", "线状态单源"]},
        {"kind": "file_contains", "args": ["research/PROFIT_MODEL_MAP.md", "线状态单源"]},
        {"kind": "file_exists", "args": ["results/_r270bma_orders_index_md.py"]},
        {"kind": "file_exists", "args": ["results/_r270bma_pointer_fixes.py"]},
    ],
}
assert not any(x["id"] == row["id"] for x in c["items"])
c["items"].append(row)

txt = json.dumps(c, ensure_ascii=False, indent=1)
raw = txt.encode("utf-8").replace(b"\n", b"\r\n")
assert not raw.endswith(b"\n")
with io.open(PATH, "wb") as fh:
    fh.write(raw)
print("registered T-83-S3-GM-SLICE2 (16 checks, stable-artifact anchors only)")
