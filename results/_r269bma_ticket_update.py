"""R269 bm-a: T-83 progress_r269 — s3 GM slice 1 (件①②④) landed.

Byte-face contract (probed pre-write): no BOM / CRLF / indent=1 /
ensure_ascii=False / trailing newline present. The ticket has a text-level
insertion history: yield_note_bm_a carries a literal JSON escape sequence
(backslash-u00a7) amid otherwise-raw CJK — a plain json round-trip would
rewrite that line; this writer re-emits the escape verbatim so the diff is
a pure field increment (R255/R257 five-face law).
"""
import io
import json

PATH = "fleet/tasks/T-2026-09-26-83-P1.json"
raw = io.open(PATH, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf" and raw.endswith(b"\n") and b"\r\n" in raw
d = json.loads(raw.decode("utf-8-sig"))

assert "progress_r269" not in d
d["progress_r269"] = (
    "bm-a R269 (GM 专管会话): s3 GM seven-deliverable batch slice 1 of 3 "
    "LANDED — 件① firm/JUDGMENT_MATRIX.md v1.0 (9 judgment faces "
    "J-TRD/J-SPM/J-AGGR/J-ALLOC/J-CN/J-WILD/J-GRID/J-PAPER/J-DATA; "
    "sole-authority pointer per face; zero threshold restatement; "
    "三线三判 codified; s2-D1 SINA_MF zero-reference adjudicated legal "
    "collection-lane) + 件② firm/ACCOUNT_LIFECYCLE.md v1.0 (five-ring "
    "chain R1-R5 canonical doc; 8 account families x ring coverage + "
    "reporting attribution; marks-not-trial-ledger discipline) + 件④ "
    "org_chart.md v6 KPI refresh (research dept + orthogonal-member-"
    "supply + five-line coverage; GM-office + daily battle report T-75). "
    "s1 L1/L5/L3 named targets closed. post_review row "
    "T-83-S3-GM-DELIVERABLES registered (11 checks, stable-artifact "
    "anchors only per R264 law). REMAINING GM SLICES (next GM-session "
    "rounds, anti-dup: consume s2 report + orders_index.json): 件③ "
    "doc-hierarchy definition (L2 21-pointer table -> hierarchy ordering "
    "doc, candidate carrier firm/DOC_HIERARCHY.md or OPERATING_PLAN "
    "section); 件⑤ orders index + supersession adjudication (inputs: "
    "results/orders_index.json R263 donation + s2 D9: 1 explicit edge "
    "O-20260924-1136->O-20260923-1738 clause-level + 6 mechanism-"
    "amendment candidates incl O-20260923-2205 iron_rules CEO-review "
    "abolition; carrier candidate research/ORDERS_INDEX.md); 件⑥ s2-"
    "candidate adjudication (24 true dead links / 19 relocations / 6 "
    "mechanism amendments / BACKTEST_PLAN.md O-1738 partial-supersession "
    "cite / local-coding pilot 12-script promotion decision / "
    "FACTOR_BLEND_V2 archive destination); 件⑦ product-line status "
    "single-source + zoo upgrade (L4/L7: one live/research/negative "
    "status table; candidate carrier STRATEGY_LIBRARY §upgrade or "
    "PRODUCT_MATRIX extension). Ticket stays claimed by bm-b (s1/s2 "
    "owner); s3 lane note (GM-reserved) unchanged until 件③⑤⑥⑦ land."
)

txt = json.dumps(d, ensure_ascii=False, indent=1)
# re-emit the historical escape so line 14 stays byte-identical (probe:
# raw file carries backslash-u00a7 for this one token amid raw CJK)
txt = txt.replace("README.md §4 commit-time",
                  "README.md \\u00a74 commit-time")
new_raw = txt.encode("utf-8").replace(b"\n", b"\r\n") + b"\r\n"
with io.open(PATH, "wb") as fh:
    fh.write(new_raw)
print("progress_r269 written (field increment, escape preserved)")
