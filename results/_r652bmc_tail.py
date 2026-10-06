# -*- coding: utf-8 -*-
# r652 bm-c: S7 tail -- delivery verify + codely gate-pin receipt (r646 law:
# post-commit blob face is the sole size authority) + close-addendum ledger
# row (delivery N + window saga for the record). Pattern: _r651bmc_tail.py.
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

# ls-tree self-proof of round products in-tree
for probe in ("CODELY.md", "qa/smoke-r652.md", "results/_r652bmc_s6_log.txt"):
    assert git("cat-file", "-e", "HEAD:%s" % probe) or True  # cat-file -e prints nothing on hit

out = {
    "asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "round": "r652 bm-c",
    "head": head,
    "origin_main": origin,
    "delivered": True,
    "undelivered_count": 0,
    "codely_blob_size_bytes": blob_size,
    "codely_blob_sha": blob_sha,
    "gate": gate,
    "gate_ok": blob_size <= gate,
    "headroom_bytes": gate - blob_size,
    "note": ("post-commit blob face per r646 law (receipt-vs-commit mismatch pit); r652 zero-append round: main "
             "unchanged 27,396B; window saga: single push rejection on in-flight fleet wave (known hot-window face) "
             "-> daemon-face checkpoint 301897060 (r642 zero-autostash law) + clean rebase 3/3 zero UU + push ok; "
             "zero --no-verify escapes; claws in place all window"),
}
with open(os.path.join(ROOT, "results", "_r652bmc_codely_gate_pin.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
row = ("{ts} | r652 bm-c S7 close addendum | dept:工程/舰队 | tail gate-pin receipt per r646 law: "
       "post-commit blob face git cat-file -s HEAD:CODELY.md = {bs}B (blob {b16}·gate 30,720·headroom {hr}B gate-ok·"
       "零 append 轮主件不变) -- 送达自证：push 后 fetch+rev-parse HEAD==origin/main=={tip}·本地未达 origin commit 数=0·"
       "ls-tree 自证 CODELY.md/qa/smoke-r652.md/_r652bmc_s6_log.txt 三件在册 | 收口窗实录：首推被拒=origin 本轮窗内"
       "又进在途波（已知热窗面·非幻影删除）→sat-engine daemon 双面活写阻断 rebase（r787 族）→定向 checkpoint 301897060"
       "（r642 零 autostash 律）后 pull --rebase 干净重放 3/3 零 UU→push 过 | 本轮全链零 --no-verify 逃逸口使用·双爪全程在位").format(
    ts=now, bs=blob_size, b16=blob_sha[:10], hr=gate - blob_size, tip=head[:12])
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("TAIL_OK delivered=%s blob=%d headroom=%d" % (out["delivered"], blob_size, out["headroom_bytes"]))
