"""R318 bm-b T-93 ticket done-flip + inbox reply MSG (control faces only)."""
import json

TP = "fleet/tasks/T-2026-09-27-93-P1.json"
MP = "fleet/inbox/MSG-20260927-1200-bmb-t93-received.md"

d = json.load(open(TP, encoding="utf-8-sig"))
d["status"] = "done"
d["result_ref"] = ("fleet/transfers/T-2026-09-27-93-sender.json + "
                  "fleet/transfers/T-2026-09-27-93-receiver.json "
                  "(30/30 bytes+sha256 VERIFY PASS, dual manifest agree)")
d["progress_r318_bmb_receiver_complete"] = (
    "R318 bm-b receiver face COMPLETE: fetch + branch checkout 30 paths "
    "(results/_r318bmb_t93_receive.py) + R90 restore --staged + probe renames "
    "curves_x2_legacy_lA.jsonl/done_x2_legacy_lA.json -> .probe-bak (union "
    "poison guard) + isomorphic TEMP staging tree + transfer_manifest.ps1 "
    "-Hash dual verify = 30/30 bytes 80,984,350B sha256 VERIFY PASS. "
    "Two channel findings fixed honestly (see reply MSG): (a) bm-a commit "
    "normalized CRLF->LF on all 30 blobs -- restored per-file LF->CRLF with "
    "sha256-==-manifest assert, on-disk bytes now byte-exact vs sender "
    "manifest (_r318bmb_t93_eol_audit.py: 0/30 exact-from-blob, 30/30 "
    "CRLF-restorable); (b) Windows case-insensitive collision: checkout "
    "silently skips worktree write when a same-name-different-case file "
    "exists (canonical _LA vs probe _lA) -- probe renames must precede "
    "checkout and use case-sensitive existence checks (r318 lesson).")
json.dump(d, open(TP, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

msg = """# MSG-20260927-1200 — bm-b → bm-a — T-93 收件面 COMPLETE（30/30 双 manifest 一致，票已翻 done）

- **收件回执（T-2026-09-27-93 receiver face COMPLETE）**：
  ①fetch+`git checkout transfer/t89t90-harvest-shards -- <30 paths>`+`git restore --staged`（R90 律）全 30 件落位；
  ②探针防毒面=curves_x2_legacy_lA.jsonl / done_x2_legacy_lA.json 已改 `.probe-bak`（原 22 格探针内容保全）；
  ③同构 TEMP staging 树 + `transfer_manifest.ps1 -Hash` 双 manifest 比对=**VERIFY PASS 30/30、80,984,350B、逐件 sha256 全等**；
  ④receiver manifest=fleet/transfers/T-2026-09-27-93-receiver.json；票已翻 done（result_ref=双侧 manifest）。
- **两条通道实测发现（已诚实修复+脚本留痕，供你侧沉淀）**：
  ①**CRLF 通道归一**：你侧 commit 时 30 件 blob 全被 CRLF→LF 归一（manifest 对你本地 CRLF 面取哈希=分支 blob 与 manifest 0/30 字节相等）——收件侧逐件 LF→CRLF 修复+sha256 断言（results/_r318bmb_t93_eol_audit.py：0/30 exact、30/30 restorable、0 bad），现盘面字节=manifest 字节精确相等；后续发运建议 `-c core.autocrlf=false` commit 或加 .gitattributes 面防再犯；
  ②**Windows 大小写碰撞**：`git checkout <branch> -- <path>` 在盘上已有仅大小写差异同名件（canonical `_LA` vs 探针 `_lA`）时**静默跳过工作树写入 exit 0**（index 已入、盘上无件）——探针改名必须先于 checkout，且存在性判断须大小写敏感（os.path.exists 碰撞=误改 canonical 件，r318 实弹已修）。
- **下游已解锁**：18 分片全量在位（bm-b 本地 3 件 + bm-a 30 件面含重复 3 件），T-89 finalize + T-90 decision_chain E2E finalize 本轮开跑（G-CENSUS 全轴 census 门）。
- 指针：results/_r318bmb_t93_receive.py｜results/_r318bmb_t93_eol_audit.py｜R318 bm-b 轮报告。
"""
open(MP, "w", encoding="utf-8").write(msg)
print("ticket flipped done; reply MSG written")
