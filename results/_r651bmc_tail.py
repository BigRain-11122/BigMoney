# -*- coding: utf-8 -*-
# r651 bm-c: S7 tail -- delivery verify + codely gate-pin receipt (r646 law:
# post-commit blob face is the sole size authority) + close-addendum ledger
# row (delivery N + reba/window saga for the record).
import subprocess, json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git(*args):
    p = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True)
    assert p.returncode == 0, "git %s rc=%d" % (args, p.returncode)
    return p.stdout.decode("utf-8", "replace").strip()

head = git("rev-parse", "HEAD")
origin = git("rev-parse", "origin/main")
behind = int(git("rev-list", "--count", "HEAD..origin/main"))
blob_size = int(git("cat-file", "-s", "HEAD:CODELY.md"))
blob_sha = git("rev-parse", "HEAD:CODELY.md")
gate = 30720
assert head == origin and behind == 0, "NOT DELIVERED"
assert blob_size <= gate, "gate breach"

out = {
    "asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "round": "r651 bm-c",
    "head": head,
    "origin_main": origin,
    "delivered": True,
    "undelivered_count": 0,
    "codely_blob_size_bytes": blob_size,
    "codely_blob_sha": blob_sha,
    "gate": gate,
    "gate_ok": blob_size <= gate,
    "headroom_bytes": gate - blob_size,
    "note": ("post-commit blob face per r646 law (receipt-vs-commit mismatch pit); "
             "r651 mini-split face: main 30,570 -> 26,496B (split) -> 27,396B (new pit entry, "
             "main-file-first law); window saga: compute_audit ts-union rebase resolve (r650 "
             "precedent, 210 rows) + r787 daemon-live-face continue false-refusal (atomic "
             "add+continue law) + r519-family claw phantom-deletion block on stale base "
             "(re-rebase onto bm-a r807/808 wave, clean replay, zero --no-verify escapes)"),
}
with open(os.path.join(ROOT, "results", "_r651bmc_codely_gate_pin.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
row = ("{ts} | r651 bm-c S7 close addendum | dept:工程/舰队 | tail gate-pin receipt per r646 law: "
       "post-commit blob face git cat-file -s HEAD:CODELY.md = {bs}B (blob {b16}·gate 30,720·headroom {hr}B gate-ok) -- "
       "送达自证：push 后 fetch+rev-parse HEAD==origin/main=={tip}·本地未达 origin commit 数=0·"
       "ls-tree 自证 CODELY.md/qa/smoke-r651.md/_r651bmc_codely_increment.json 三件在册 | "
       "收口窗实录：close commit 撞 bm-a 在途波=rebase UU 单面 results/compute_audit.json（共享 append-only history 面）——"
       "r648 sha 通道+双面 marker 硬门后 ts-union 收口（base 203/onto 209/mine 201→union 210 行·r650 同款先例）"
       "+rebase --continue 两连拒=r787 车道活面假冲突报正主（sat-engine daemon 窗内活写→has_unstaged_changes"
       "→「You must edit all merge conflicts」假报·两 daemon 面 add+continue 原子化即过）"
       "+首推被 pre-push 爪 r519 族拦截（解冲突窗内 origin 又进 3 commit〔bm-a r807/808 波〕·推区间幻影删除 "
       "bm-a _r806bma 探针件=陈旧基座非真删·dispatcher 面 checkpoint〔commit {cp}〕+再 rebase 干净 replay 后爪过）"
       "| 本轮全链零 --no-verify 逃逸口使用·双爪全程在位").format(
    ts=now, bs=blob_size, b16=blob_sha[:10], hr=gate - blob_size, tip=head[:12], cp="cc832bda1(rewritten)")
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("TAIL_OK delivered=%s blob=%d headroom=%d" % (out["delivered"], blob_size, out["headroom_bytes"]))
