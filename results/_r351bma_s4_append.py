"""R351 bm-a S4 memory append: two pitlaw rows (resolver stage-mapping + tick stage-destruction recovery).
Byte-safe append via python (write_file-tool escape mangling avoided); gate: <=10KB after append.
"""
CODELY = "CODELY.md"

rows = [
"- [2026-09-27 20:5x r351 bm-a] 坑律：rebase 重放窗的 resolver 侧位映射=「:2:=HEAD（已重放基底·对岸面）/ :3:=被重放 commit（本链面）」——与 merge 直觉相反（r351 实弹：pass-2 CODELY/archive resolver 初稿把 bmc 面标成 theirs、自家 section 标成 ours，运行前自查当场翻正零损失；正典=resolver 写时先落一行侧位断言注记（本链面=?:3:）再动手，批量取侧前用 git ls-files -u 实证 stage 归属）。连带：resolver 零丢失断言遇「本侧自建指针行被对岸 full 行吸收」=合法吸收非丢失（断言须验 full 行在结果树再放行指针行弃置）。",
"- [2026-09-27 20:5x r351 bm-a] 坑律：rebase UU 停点窗内本机 watchdog tick 照打（r335 律已知）且其 blind-add 会毁共享件的 :2:/:3: stage（r351 实弹：pool resolver git show :2: 得 rc=128=stage 已被 tick 清、工作树已被 tick 重写为干净面；正典=①resolver 读 stage 失败勿盲写，先 git status 定件态+以 HEAD blob 内容为准复验；②已续跑 commit 的件直接验 commit 内 blob（git show <sha>:<path> 过 parse+无冲突标记）而非信工作树；③:X0:01 tick 前后 1min 窗内勿发起共享件 resolver 批）。",
]

b = open(CODELY, "rb").read()
text = b.decode("utf-8")
add = ("\n".join(rows) + "\n").encode("utf-8")
# append at end of file (Reference section is last); file ends with newline
assert text.endswith("\n") or b.endswith(b"\n"), "unexpected CODELY tail"
new = b + add
assert len(new) <= 10240, f"over hard line: {len(new)}"
open(CODELY, "wb").write(new)
for r in rows:
    assert r.encode("utf-8") in new
print(f"CODELY append 2 rows: {len(b)} -> {len(new)}B (<=10240 OK)")
