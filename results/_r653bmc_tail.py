# -*- coding: utf-8 -*-
# r653 bm-c: S7 tail -- delivery verify + codely gate-pin receipt (r646 law:
# post-commit blob face is the sole size authority) + close-addendum ledger
# row (delivery N + window saga for the record). Pattern: _r652bmc_tail.py.
import subprocess, json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git(*args):
    p = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True)
    assert p.returncode == 0, "git %s rc=%d" % (args, p.returncode)
    return p.stdout.decode("utf-8", "replace").strip()

git("fetch", "origin")
head = git("rev-parse", "HEAD")
origin = git("rev-parse", "origin/main")
behind = int(git("rev-list", "--count", "HEAD..origin/main"))
blob_size = int(git("cat-file", "-s", "HEAD:CODELY.md"))
blob_sha = git("rev-parse", "HEAD:CODELY.md")
gate = 30720
assert head == origin and behind == 0, "NOT DELIVERED"
assert blob_size <= gate, "gate breach"

# ls-tree self-proof of round products in-tree
for probe in ("CODELY.md", "qa/smoke-r653.md", "results/_r653bmc_s6_log.txt"):
    assert git("cat-file", "-e", "HEAD:%s" % probe) or True  # cat-file -e prints nothing on hit

out = {
    "asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "round": "r653 bm-c",
    "head": head,
    "origin_main": origin,
    "delivered": True,
    "undelivered_count": 0,
    "codely_blob_size_bytes": blob_size,
    "codely_blob_sha": blob_sha,
    "gate": gate,
    "gate_ok": blob_size <= gate,
    "headroom_bytes": gate - blob_size,
    "note": ("post-commit blob face per r646 law (receipt-vs-commit mismatch pit); r653 zero-append round: main "
             "unchanged 27,396B; window saga: push#1 non-FF (bm-b r794 wave mid-window) -> daemon checkpoint#1 -> "
             "rebase UU single-face _attrition_guard_scan.json (ts-line only, both scans CLEAN, resolved newer-wins) "
             "-> push#2 pre-push claw double-block (pool shard owner_since 04:24:10->04:14:10 backward = my tip "
             "inherited stale 04:14 pool snapshot vs live remote tip carrying bm-b 04:24 claim-refresh, MSG-0612 "
             "ring-replay family + phantom deletion of non-self-owned files, r651 stale-base kin; probe proven my "
             "commits touch zero pool faces) -> origin-integrate rebase (daemon checkpoint#2) 3/3 clean -> push ok; "
             "zero --no-verify escapes; claws in place all window"),
}
with open(os.path.join(ROOT, "results", "_r653bmc_codely_gate_pin.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
row = ("{ts} | r653 bm-c S7 close addendum | dept:工程/舰队 | tail gate-pin receipt per r646 law: "
       "post-commit blob face git cat-file -s HEAD:CODELY.md = {bs}B (blob {b16}·gate 30,720·headroom {hr}B gate-ok·"
       "零 append 轮主件不变) -- 送达自证：push 后 fetch+rev-parse HEAD==origin/main=={tip}·本地未达 origin commit 数=0·"
       "ls-tree 自证 CODELY.md/qa/smoke-r653.md/_r653bmc_s6_log.txt 三件在册 | 收口窗实录：推#1 non-FF（bm-b r794 波"
       "窗中在途）→daemon checkpoint#1→rebase UU 单面 _attrition_guard_scan.json（仅 ts 行·双面全 CLEAN·newer-wins "
       "裁决 04:21:18）→continue 2/2 干净→推#2 被 pre-push 爪双拦：池分片 owner_since 04:24:10→04:14:10 回退=我 tip "
       "继承 04:14 陈旧池快照 vs 推送时刻活远端 tip 带 bm-b 04:24 claim-refresh〔MSG-0612 环重放族〕+非己属主件幻影"
       "删除〔陈旧基座·r651 同源〕——探针实证我两 commit 零触碰共享池面+删除集双形态皆空→正法=先集成 origin（daemon "
       "checkpoint#2）rebase 3/3 干净→池面前向继承爪过推送成 | 本轮全链零 --no-verify 逃逸口使用·双爪全程在位").format(
    ts=now, bs=blob_size, b16=blob_sha[:10], hr=gate - blob_size, tip=head[:12])
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("TAIL_OK delivered=%s blob=%d headroom=%d" % (out["delivered"], blob_size, out["headroom_bytes"]))
