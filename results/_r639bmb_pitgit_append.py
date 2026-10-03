import hashlib, io

entry = (
"- [2026-10-03 23:5x r639 bm-b] push-race 双活 daemon 态 merge 整合尾步两坑（r630 律③姊妹面·实弹=本窗 r638 四 commit 链 vs bm-c r434×2+bm-a r647+churn 撞车·隔离 worktree merge f95419e5 收口窗）："
"①git checkout 的 --pathspec-from-file=<f> 参数前若前置 `--`=选项解析被终结·文件参数被当 pathspec（rc1 pathspec did not match）——正确形态=无 `--` 直传（B795 pathspec-from-file 与显式参数互斥律的姊妹面）；"
"②r630 隔离 worktree merge 完成后主树同步尾步=先 `git reset --mixed origin/main`（分支+索引移动·工作树保留）→变更集（oldHEAD..newHEAD diff name-only）减活 daemon 面（轮首脏集逐件+mtime<15min 守卫 crash_fuse/x2_watch_log/gate_attrition 类 ambiguous 共享池面）定向 `checkout --` 刷新=daemon 追加行零丢失（reset --hard 必丢上次 commit 后至同步点的烧录 append）；"
"③同窗 autofill keepalive 会自主 commit+push（本窗 23:40:17 实弹·只带 pool claim 三件）——push 后必 ls-remote 复核拓扑·勿以本地 origin/main ref 推断送达。"
)
acc_tmpl = (
"> 直写行：r639 bm-b（post-split convention direct-write）+1 条（merge 尾步同步 recipe·活 daemon 面定向 checkout 律·--pathspec-from-file 参数序坑）"
"——同窗自产自扫无跨机比对窗；追加 {n} B·LF blob 桁·md5={md5}；件尾直追加·第二形态为准。"
)

path = r"research\pit-git.md"
raw = open(path, "rb").read()
lead = ("\n" if not raw.endswith(b"\n") else "")
blob = (entry + "\n").encode("utf-8")
n = len(blob)
md5 = hashlib.md5(blob).hexdigest()
acc = acc_tmpl.format(n=n, md5=md5)
blob = (lead + entry + "\n").encode("utf-8")
assert len(blob) == lead.encode("utf-8").__len__() + n and hashlib.md5(blob[len(lead.encode("utf-8")):]).hexdigest() == md5
with open(path, "ab") as f:
    f.write((lead + entry + "\n" + acc + "\n").encode("utf-8"))
new = open(path, "rb").read()
assert new.startswith(raw) and hashlib.md5(new[len(raw):len(raw) + len(blob) - len(lead.encode("utf-8"))]).hexdigest() == md5
print("appended entry", n, "bytes md5", md5, "| new total", len(new))
