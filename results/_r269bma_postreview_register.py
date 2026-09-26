"""R269 bm-a: register T-83 s3 GM-deliverables claim row (件①②④ slice).

T-83 s3 = GM-signed seven deliverables (O-20260926-1355). This round lands
3 of 7 (件① judgment master map / 件② account lifecycle / 件④ KPI refresh);
件③⑤⑥⑦ continuation pointers live in ticket progress_r269. Checks anchor
ONLY stable artifact files (file_exists / file_contains per R264 law: hot
git-log windows forbidden as check anchors on canon docs that may receive
future amendments). Zero criteria invented: every check string is frozen
from the delivered artifact content itself.
Byte-face contract (R255/R257 five-face law, probed pre-write):
results/post_review_criteria.json = no BOM / CRLF / indent=1 /
ensure_ascii=False / NO trailing newline. Write replicates that face.
"""
import io
import json

PATH = "results/post_review_criteria.json"
c = json.load(io.open(PATH, encoding="utf-8"))

row = {
    "id": "T-83-S3-GM-DELIVERABLES",
    "claim": "T-83 s3 GM-signed seven-deliverable batch, slice 1 of 3 "
             "(件①②④ landed this round; 件③ doc-hierarchy / 件⑤ orders "
             "index+supersession / 件⑥ s2-candidate adjudication (24 true "
             "dead links, 19 relocations, 6 mechanism amendments, "
             "local-coding pilot promotion) / 件⑦ product-line status "
             "single-source+zoo upgrade = follow-up GM slices, pointers "
             "in ticket progress_r269): 件① firm/JUDGMENT_MATRIX.md v1.0 "
             "judgment-system master map (9 judgment faces J-TRD/J-SPM/"
             "J-AGGR/J-ALLOC/J-CN/J-WILD/J-GRID/J-PAPER/J-DATA x product "
             "line x stage, sole-authority pointer per face, zero "
             "threshold restatement, three-lines-three-judgments rule "
             "codified, s2-D1 SINA_MF zero-reference adjudicated legal "
             "collection-lane face) -> 件② firm/ACCOUNT_LIFECYCLE.md v1.0 "
             "five-ring chain canonical doc (R1 judgment->R2 paper->R3 "
             "CEO approval->R4 live-sim->R5 real-money, per-ring carriers "
             "as pointers, 8 account families x ring coverage + "
             "reporting-attribution table, marks-are-not-trial-ledgers "
             "discipline) -> 件④ org_chart.md v6 KPI refresh (research "
             "dept KPI + orthogonal-member-supply + five-line coverage "
             "face per s1-L3 lag finding; GM-office KPI + daily battle "
             "report T-75 face per O-20260926-0940) — s1 L1/L5/L3 named "
             "targets closed; GM (quant 专管会话) personally executed per "
             "order lane note",
    "claim_source": "fleet/orders/O-20260926-1355-bm-a.md §三 s3 seven "
                    "deliverables (frozen at order 13:55) + ticket "
                    "T-2026-09-26-83-P1.json spec s3 + inputs "
                    "research/AUDIT-20260926-FULL.md (s1, L1/L3/L5 "
                    "targets) + research/AUDIT-20260926-S2.md (s2, D1 "
                    "adjudication input) + delivered artifacts "
                    "firm/JUDGMENT_MATRIX.md + firm/ACCOUNT_LIFECYCLE."
                    "md + firm/org_chart.md v6 section",
    "status": "closed",
    "checks": [
        {"kind": "file_exists", "args": ["firm/JUDGMENT_MATRIX.md"]},
        {"kind": "file_contains",
         "args": ["firm/JUDGMENT_MATRIX.md", "三线三判律"]},
        {"kind": "file_contains",
         "args": ["firm/JUDGMENT_MATRIX.md", "零阈值复制"]},
        {"kind": "file_contains",
         "args": ["firm/JUDGMENT_MATRIX.md", "SINA_MF_PREREG"]},
        {"kind": "file_contains",
         "args": ["firm/JUDGMENT_MATRIX.md", "firm/ACCOUNT_LIFECYCLE.md"]},
        {"kind": "file_exists", "args": ["firm/ACCOUNT_LIFECYCLE.md"]},
        {"kind": "file_contains",
         "args": ["firm/ACCOUNT_LIFECYCLE.md", "R5 实盘"]},
        {"kind": "file_contains",
         "args": ["firm/ACCOUNT_LIFECYCLE.md", "marks 非试验账本"]},
        {"kind": "file_contains",
         "args": ["firm/org_chart.md", "v6 KPI 面刷新"]},
        {"kind": "file_contains",
         "args": ["firm/org_chart.md", "五线供给覆盖"]},
        {"kind": "file_contains",
         "args": ["firm/org_chart.md", "每日战报按期"]},
    ],
}
assert not any(x["id"] == row["id"] for x in c["items"])
c["items"].append(row)

txt = json.dumps(c, ensure_ascii=False, indent=1)
raw = txt.encode("utf-8").replace(b"\n", b"\r\n")   # probed face: CRLF
assert not raw.endswith(b"\n")                        # probed: no trailing nl
with io.open(PATH, "wb") as fh:
    fh.write(raw)
print("registered T-83-S3-GM-DELIVERABLES (11 checks, stable-artifact "
      "anchors only, byte face CRLF/no-BOM/indent1/no-trailing-nl)")
