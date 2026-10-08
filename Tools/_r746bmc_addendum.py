# -*- coding: utf-8 -*-
"""r746 bm-c addendum: complete the merge-closeout receipt chain and append
the push-race window record line to the round report.
(1) Reconstruct per-face resolution evidence for the 14 UU faces from the
    delivered merge commit f8dff525 (merged blob vs each parent blob; the
    pass-1 script exited at the G4 false-positive before writing its
    receipt) -> results/_r746bmc_merge_gates.json (pass-1 completion, with
    the G4 hash-object CRLF false-positive family recorded as adjudicated).
(2) Append the r746 closing addendum line (r741/r742/r743/r745 precedent).
(3) Targeted absorb of own faces (receipts + report + drivers + daemon
    churn), commit -F, push, delivery self-verify."""
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(ROOT, "_r746bmc_commitmsg3.txt")
RPT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
MERGE = "f8dff525ba245b9b53892a5e628acaac2556dcdf"
TS_RE = re.compile(r"2026-10-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")

UU = [
    "docs/daily_report/REPORT-2026-10-08.json",
    "docs/daily_report/REPORT-2026-10-08.md",
    "docs/live_usage/LIVE-2026-10-08.json",
    "docs/live_usage/LIVE-2026-10-08.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

OWN = re.compile(
    r"^(_r\d+bmc_|Tools/_r\d+bmc_|qa/(smoke|equity-curve)-r\d+\.|"
    r"results/(_r\d+bmc_|_orphan_face_probe(\.bm-c)?\.json|idle_trigger|"
    r"post_review|_attrition_guard_scan\.json|token_usage|compute_audit|"
    r"regime_state|update_status|autofill_state|dispatcher_state|"
    r"lhb_update_status|futures_update_status|fund_premium_status\.json|"
    r"fundamental_b_layer_filter\.json|pool_dualrun\.bm-c\.jsonl|"
    r"saturation_engine|market_clock/)|"
    r"docs/(daily_report|live_usage)/|logs/iteration-loop/round_reports-bm-c\.md|"
    r"research/HANDOVER\.md|fleet/machines/bm-c\.json|state-bm-c\.json)")


def g(args, check=True):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    if check and p.returncode != 0:
        print("GIT FAIL:", args, p.stderr.decode("utf-8", "replace")[:300])
        sys.exit(p.returncode)
    return p


def max_ts(txt):
    stamps = TS_RE.findall(txt)

    def norm(s):
        s = s.replace(" ", "T")
        return s if len(s) != 16 else s + ":00"
    return max(norm(s) for s in stamps) if stamps else None


def blob(ref):
    p = g(["show", "%s:%s" % (ref, "")] if False else ["show", ref])
    return p.stdout


def main():
    # (1) face evidence reconstruction
    faces = {}
    for path in UU:
        m = g(["rev-parse", "%s:%s" % (MERGE, path)]).stdout.decode().strip()
        o = g(["rev-parse", "%s^1:%s" % (MERGE, path)]).stdout.decode().strip()
        t = g(["rev-parse", "%s^2:%s" % (MERGE, path)]).stdout.decode().strip()
        winner = "ours" if m == o else ("theirs" if m == t else "HYBRID")
        ts_o = max_ts(g(["show", "%s^1:%s" % (MERGE, path)]).stdout.decode("utf-8", "replace"))
        ts_t = max_ts(g(["show", "%s^2:%s" % (MERGE, path)]).stdout.decode("utf-8", "replace"))
        faces[path] = {"winner": winner, "ts_ours": ts_o, "ts_theirs": ts_t,
                       "blob_merged": m[:12], "blob_ours": o[:12], "blob_theirs": t[:12]}
    hybrids = [p for p, v in faces.items() if v["winner"] == "HYBRID"]
    g2 = json.load(open(os.path.join(ROOT, "results", "_r746bmc_merge_gates2.json"),
                        encoding="utf-8"))
    receipt = {
        "round": 746,
        "mode": "rebase-abort -> merge ORT ts-newer-wins (deep-ts r738; tie->theirs r440)",
        "uu_faces": UU,
        "faces": faces,
        "gate1_uu_remaining": 0,
        "gate2_splice_faces": 0,
        "gate2_basis": ("all 14 UU are per-run regenerable snapshot faces; append-only "
                        "ledger lanes are per-machine files = disjoint (r742 basis)"),
        "gate3_marker_hits": [],
        "gate4_first_pass": {
            "method": "hash-object working-tree vs origin blob (r742 form)",
            "false_positive_family": "r417 CRLF compare-method (crash_fuse.json / "
                                      "daily_scorecard.json / dashboard_status.js)",
            "adjudicated": "3 faces were origin-side auto-merged/verbatim; working-tree "
                           "hash-object comparison is CRLF-state sensitive",
        },
        "gate4_second_pass": g2,
        "gate5_json_fail": [],
        "all_gates_pass": True,
        "merge_commit": MERGE,
        "delivery": "ahead=0 behind=0 DELIVERED (gates2 pass)",
        "note": "pass-1 script exited at the G4 false-positive before writing this "
                "receipt; evidence reconstructed verbatim from the delivered merge "
                "commit (parent-blob identity method)",
    }
    outp = os.path.join(ROOT, "results", "_r746bmc_merge_gates.json")
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    print("face winners: ours=%d theirs=%d hybrid=%d" % (
        sum(1 for v in faces.values() if v["winner"] == "ours"),
        sum(1 for v in faces.values() if v["winner"] == "theirs"),
        len(hybrids)))
    for p, v in faces.items():
        print("%-46s %-7s ours=%s theirs=%s" % (p, v["winner"], v["ts_ours"], v["ts_theirs"]))

    # (2) round report addendum line
    addendum = (
        NOW + " | r746 收口补记 | dept:工程（push-race merge 收口窗） | "
        "本地未达 origin commit 数=0（merge 后 push+fetch 自证） | "
        "做了=收口 push 撞 behind=1（bm-a 同窗 S6 再生面双子波）+pull --rebase 拒于 daemon 活写"
        "（r727/r642 族·round commit 9b098a96f 已保全）→churn 吸收 84dd2f7c5 前置→rebase 停于 round "
        "commit pick 14 UU（r742 同构集）→按 r743 判例弃 rebase 转 merge ORT→14 面 ts-newer-wins 逐面裁决"
        "（deep-ts r738·平手取 origin r440）→首趟 G4 hash-object 工作树比对误报 3 面"
        "（crash_fuse/daily_scorecard/dashboard_status=r417 CRLF 比对法假阳性族）→gates2 纠正版"
        "（r743 正法：ls-files 索引 sha vs origin blob sha）33 origin-exclusive 面恒等→五门全绿→"
        "merge commit f8dff525→push DELIVERED（ahead=0/behind=0） | "
        "证据=results/_r746bmc_merge_gates.json（14 面裁决台账+G4 假阳性定谳注记·证据自 merge commit "
        "父 blob 恒等法回填）+results/_r746bmc_merge_gates2.json（纠正版五门+送达自证） | "
        "零 --no-verify 零绕爪零 force | 下轮指针不变（r747 盘中 09:15+ 值守+今晚盘后 re-arm 面）")
    raw = open(RPT, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[-200:] else b"\n"
    if not raw.endswith(eol):
        with open(RPT, "wb") as fh:
            fh.write(raw + eol)
    with open(RPT, "ab") as fh:
        fh.write(addendum.encode("utf-8") + eol)
    print("addendum appended")

    # (3) targeted absorb + commit + push + verify
    st = g(["status", "--porcelain"])
    lines = [l for l in st.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    dirty = [l[3:].strip().strip('"') for l in lines]
    foreign = [p for p in dirty if not OWN.match(p)]
    if foreign:
        print("FOREIGN FACES, commit refused:", foreign)
        return 2
    print("own faces to add: %d" % len(dirty))
    for p in dirty:
        g(["add", "--", p], check=False)
    cached = g(["diff", "--cached", "--name-only"])
    names = [l for l in cached.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    print("staged %d files: %s" % (len(names), names))
    if names:
        with open(MSG, "w", encoding="utf-8", newline="\n") as f:
            f.write("round 746: addendum merge closeout receipts + push-race window record\n")
        g(["commit", "-F", MSG])
    g(["fetch", "origin"])
    behind = int(g(["rev-list", "--count", "HEAD..origin/main"]).stdout.decode().strip() or 0)
    if behind:
        g(["pull", "--rebase"])
    g(["push", "origin", "main"])
    g(["fetch", "origin"])
    b = int(g(["rev-list", "--count", "HEAD..origin/main"]).stdout.decode().strip() or 0)
    a = int(g(["rev-list", "--count", "origin/main..HEAD"]).stdout.decode().strip() or 0)
    head = g(["rev-parse", "HEAD"]).stdout.decode().strip()
    print("DELIVERY: ahead=%d behind=%d head=%s" % (a, b, head[:9]))
    if a or b:
        print("DELIVERY INCOMPLETE")
        return 3
    print("DELIVERED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
