# -*- coding: utf-8 -*-
# r653 bm-c: S7 tail-2 (verify-only, no commit): final delivery verify +
# fresh post-commit blob measurement + gate-pin refresh + addendum-2 ledger
# row (pits corrigendum). Row/receipt stay dirty for next round's S0
# targeted checkpoint (r652 house pattern). Pattern: _r652bmc_tail.py.
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
assert head == origin and behind == 0, "NOT DELIVERED head=%s origin=%s" % (head, origin)
assert blob_size <= gate, "gate breach %d" % blob_size

out = {
    "asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "round": "r653 bm-c (final delivered face)",
    "head": head,
    "origin_main": origin,
    "delivered": True,
    "undelivered_count": 0,
    "codely_blob_size_bytes": blob_size,
    "codely_blob_sha": blob_sha,
    "gate": gate,
    "gate_ok": blob_size <= gate,
    "headroom_bytes": gate - blob_size,
    "note": ("FINAL delivered face per r646 measured-face law: blob %dB @ tip %s (gate-ok headroom %dB). r653 bm-c own "
             "appends = 2 pits (+1,546B); bm-b r794 in-window +1,175B; close-time 27,396B stale claim kanzhu-corrected "
             "(see addendum-1/2 rows). Push saga total: 3 rejections all claw/push-law faces (non-FF wave, claw "
             "pool-owner_since live-remote-base double-block, claw bm-a r807 file deletion stale-base) -- each resolved "
             "by origin-integrate rebase, ZERO --no-verify escapes; claws in place all window. Next wave: main headroom "
             "%dB -> mini-split likely (r651 machinery).") % (blob_size, head[:12], gate - blob_size, gate - blob_size),
}
with open(os.path.join(ROOT, "results", "_r653bmc_codely_gate_pin.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
row = ("{ts} | r653 bm-c S7 close addendum 2（坑律入册勘注） | dept:工程/舰队 | tail gate-pin receipt per r646 law: "
       "收口窗抓获新坑 2 条已 append 主件（close 尺寸陈旧收据假设坑+pre-push 爪活远端比对基座坑〔MSG-0612 环重放族新变体〕"
       "·+1,546B）——主件终态实测 {bs}B（blob {b16}·bm-b r794 窗内 +1,175B+bm-c 坑律 +1,546B·gate 30,720·余量 {hr}B·"
       "下波 mini-split 预警=r651 机器面承接） | 勘注：主行「零新坑零 CODELY append」声明被本行取代——值守面零新坑属实·"
       "收口窗 2 新坑如实入册（W63 律已推主行不回改） | 送达自证：终态 push 后 fetch+rev-parse HEAD==origin/main=="
       "{tip}·本地未达 origin commit 数=0·ls-tree 自证 CODELY.md/qa/smoke-r653.md/results/_r653bmc_s6_log.txt 三件在册 | "
       "收口窗实录补遗：推#3 再被爪拦=bm-a r807 四件真删除面（我基座分叉早于 bm-a r808 波落 origin）→daemon checkpoint#3+"
       "rebase 2/2 干净集成→爪过推送成 | 全窗 3 推拒全按律集成解决·零 --no-verify 逃逸·双爪全程在位").format(
    ts=now, bs=blob_size, b16=blob_sha[:10], hr=gate - blob_size, tip=head[:12])
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("TAIL2_OK delivered=True blob=%d headroom=%d tip=%s" % (blob_size, gate - blob_size, head[:12]))
