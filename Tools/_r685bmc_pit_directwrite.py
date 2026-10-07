# -*- coding: utf-8 -*-
"""r685 bm-c S4 pit direct-write: append new pit entry to
research/pit-git-resolver-rebase.md (r672/r684postscript direct-write pattern;
main CODELY.md margin 15B cannot host). Receipt -> results/_r685bmc_pit_directwrite.json."""
import json, hashlib, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, "research", "pit-git-resolver-rebase.md")

ENTRY = (
    "- [2026-10-07 15:5x r685 bm-c] **r808 手工 commit 完成 pick 后同窗再 stage 面后 continue=重复 pick 载体坑（ea6662523 实弹·零数据伤害如实披露）**：多环集成窗（r684 遗留 behind9/ahead3 队列）pick2 撞 compute_audit.json diff3 冲突→ls-files -u sha 通道三段 blob 合并（latest newer-wins 15:08:08+history union 207→209 零重零乱序）→手工 commit 734224bf9 完成 pick（r808 律）；随后 daemon tick 面（dispatcher/saturation）worktree 到达→continue 报「You must edit all merge conflicts」（r787 假冲突文案面）→按 r787 原子律 stage 双面后 continue——**sequencer commit_staged_changes 以停机 pick 的 message 把新 staged 面重 commit 成重复载体**（ea6662523=duplicate closeout 消息+仅 2 daemon 面 7+/7- 内容）再推进剩余 picks。正法：①r808 手工 commit 完成 pick 后，churn 面一律留 worktree 禁 stage——continue 若因 unstaged 拒进=quit 后走 r624 收口（branch -f main HEAD+checkout+absorb 独立 commit），勿用「stage 后 continue」解锁；②重复载体已落史时零手术保留（内容=daemon 快照零独占）+续接 commit 消息注记披露；③纯陈旧 daemon 快照 pick（absorb-A 70f2631dc）可有据 drop=live 树面时间戳超集证明（本窗 15:29 面>15:26 面）；④mid-rebase 窗 push origin HEAD:refs/heads/machine/… 分支=部分态交付（集成完成后主分支收敛即无害·续窗勿按分支 tip 当集成终态）。How to apply：r808 三步与 r787 原子律不可同 pick 窗连用；continue 拒进定性先分「已手工 commit 未 stage」vs「未 commit 有 UU」两态，前者走 r624 后者走 add+continue 原子批。\r\n"
)

with open(TARGET, "ab") as fh:
    raw = ENTRY.encode("utf-8")
    fh.write(raw)

size_after = os.path.getsize(TARGET)
receipt = {
    "round": 685,
    "machine": "bm-c",
    "action": "pit direct-write append",
    "target": "research/pit-git-resolver-rebase.md",
    "entry_bytes": len(raw),
    "entry_md5": hashlib.md5(raw).hexdigest(),
    "size_after": size_after,
    "law_refs": ["r808 manual-commit pick completion", "r787 atomic add+continue", "r624 quit+branch-f takeover", "r662 bare-number clone"],
    "main_file_margin_note": "CODELY.md 30705B vs 30720B line = 15B margin -> direct-write to domain file per r672 pattern",
    "ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
}
rp = os.path.join(ROOT, "results", "_r685bmc_pit_directwrite.json")
with open(rp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(receipt, fh, ensure_ascii=False, indent=1)
print("pit appended %dB, file now %dB, receipt saved" % (len(raw), size_after))
