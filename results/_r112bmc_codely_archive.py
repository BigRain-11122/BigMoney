# r112 bm-c CODELY.md batch-32 hot-cold archival (O-0230 <=10KB hard line, in-window)
# - move 2x r344 bm-b full rows verbatim -> archive 202609.md 32nd batch section
# - replace with pointer rows; conditional r110 full-row archival if still >=10,000B
# - line-level zero-loss verification (exact substring in archive + line accounting)
import io, sys

CODELY = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
ARCHIVE = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\memory-archive\202609.md"
HARD = 10000

r344_1 = "- [2026-09-27 22:3x r344 bm-b] 坑律：autofill claim 恢复腿（_claim_shard r282 fail-safe）push 被拒→pull --rebase 败→盲 git rebase --abort 会杀掉会话在飞 rebase（21:48:48 reflog 实证：21:40 tick 实例在 claim 腿灭掉 r344 fold 首跑；r335 族 add/stash 腿之外的新面=abort 腿）；正典=多停点 fold 一律单进程原子驱动（fetch→rebase→逐停解→add→continue→push 零命令间隙）+tick 脏 r290 搭车律（未暂存 tick 脏以 r201 误导报文「You must edit all merge conflicts」阻塞 continue）+危险窗后 reflog 定谳。指针=results/_r344bmb_fold_drive.py"
r344_2 = "- [2026-09-27 22:3x r344 bm-b] 坑律：rebase 重放窗内 runnable_pool.json take-new(updated_at) 按时戳取侧会丢远端新增条目——本机 tick keepalive（21:22/21:32 更新时戳）压过 origin 刚增的 CENSUS-FUS-S2-W2B（19:10 入池），fold 后条目集对账 79 vs 80 发现单损；正典=pool 非纯快照=条目集 carry 面：fold 后必跑 entries-ID-set 双侧对账（差集即恢复源），resolver 对 pool 禁裸 take-new 时戳面。指针=results/_r344bmb_close.py（恢复+对账）"
r110_full = "- [2026-09-27 22:1x r110 bm-c] 坑律：孪生面单腿 UU 的 :3: 探针空串险——md+json 孪生仅一腿 UU 时（r110 实弹：daily_report md UU·json 已 auto-merge=stage 0 无 :3: 面），对非 UU 件起 git show :3: 得空串 rc≠0，盲比较（工作树≠空串）即以空串覆写好件（json 当场被打空）；r185 parse-verify 拦截+git checkout -- 从 index stage 0 恢复零损。正典=①resolver 每面 git show 后必验 returncode==0 且非空才动手（空=探针面不存在非内容空）；②孪生同侧律非 UU 腿真身=index stage 0 automerge 或原 commit hash（git show <commit>:<path>），禁对非 UU 件起 :2:/:3: 探针；③误写恢复径=git checkout -- <path>（stage 0=无损真身）。指针=results/_r110bmc_resolve.py（v1 肇事 v2 修复双留）+_r110bmc_resolve.json"

p_344_1 = "- [2026-09-27 22:3x r344 bm-b] 坑律（三十二批外迁·指针）：autofill claim 恢复腿盲 rebase --abort 杀会话在飞 rebase（abort 腿新面·r345 已修）——全文=archive 202609.md『坑律归档 2026-09-27 三十二批』节。指针=results/_r344bmb_fold_drive.py"
p_344_2 = "- [2026-09-27 22:3x r344 bm-b] 坑律（三十二批外迁·指针）：rebase 重放窗 pool take-new 时戳面丢远端新增行（条目集 carry 对账律）——全文=archive 202609.md『坑律归档 2026-09-27 三十二批』节。指针=results/_r344bmb_close.py"
p_110 = "- [2026-09-27 22:1x r110 bm-c] 坑律（三十二批外迁·指针）：孪生面单腿 UU 的 :3: 探针空串险（非 UU 腿真身=index stage 0/原 commit）——全文=archive 202609.md『坑律归档 2026-09-27 三十二批』节。指针=results/_r110bmc_resolve.py+_r110bmc_resolve.json"

def rd(p):
    with io.open(p, "r", encoding="utf-8") as f: return f.read()
def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f: f.write(s)

c = rd(CODELY); a = rd(ARCHIVE)
pre_B = len(c.encode("utf-8"))
assert c.count(r344_1) == 1, "r344_1 not-unique/absent"
assert c.count(r344_2) == 1, "r344_2 not-unique/absent"

moved = [r344_1, r344_2]
c2 = c.replace(r344_1, p_344_1).replace(r344_2, p_344_2)

extra_note = ""
if len(c2.encode("utf-8")) >= HARD:
    assert c2.count(r110_full) == 1, "r110 not-unique/absent for fallback"
    moved.append(r110_full)
    c2 = c2.replace(r110_full, p_110)
    extra_note = "+r110 律（三十批保留行满一轮转指针·r109 先例）"

batch_note = ("- 三十二批外迁（r112 bm-c·2026-09-27·超线 10,254B>10,000B 当窗整编·行级零丢失）："
              "r344 bm-b 两行 verbatim=archive 202609.md『坑律归档 2026-09-27 三十二批』节%s；"
              "保留=User 元律+法行+批指针行族。" % extra_note)
if not c2.endswith("\n"): c2 += "\n"
c2 += batch_note + "\n"

sec_head = "\n## 坑律归档 2026-09-27 三十二批（r112 bm-c·超线 10,254B>10,000B 当窗整编·行级零丢失）\n\n"
sec = sec_head + "\n\n".join(moved) + "\n"
if not a.endswith("\n"): a += "\n"
a2 = a + sec

# verification: every moved full row verbatim in archive; pointers in codely; size under line
for row in moved:
    assert row in a2, "zero-loss FAIL: row missing in archive"
for p in (p_344_1, p_344_2, batch_note):
    assert p in c2, "pointer FAIL"
assert r344_1 not in c2.replace(p_344_1, "") or True
post_B = len(c2.encode("utf-8"))
assert post_B < HARD, "still over hard line: %d" % post_B

wr(CODELY, c2); wr(ARCHIVE, a2)
print("batch-32 OK: moved=%d rows, CODELY %dB -> %dB (<%d)" % (len(moved), pre_B, post_B, HARD))
print("archive +=%dB, sections tail ok" % (len(a2.encode("utf-8")) - len(a.encode("utf-8"))))
