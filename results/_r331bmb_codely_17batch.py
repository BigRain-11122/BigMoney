# r331 bm-b: 17th-batch hot-cold archival append (verbatim r328+r329 entries -> archive 202609.md)
import os
ARCH = r"research\memory-archive\202609.md"
raw = open(ARCH, "rb").read()
eol = "\r\n" if raw.count(b"\r\n") > (raw.count(b"\n") - raw.count(b"\r\n")) else "\n"
section = "\n## 坑律归档 2026-09-27 十七批（r331 bm-b·当窗超线整编：CODELY 9717B+新条将破 ≤10KB 硬线·律触发当窗办）\n\n- [2026-09-27 14:5x r328 bm-a] 坑律：**腾讯双 K 线端点互不互证——数据源选择必做行序守卫+双面仲裁，akshare 包装件≠独立源**——r328 repo 采集器实弹：newfqkline 全 fabric+深史但偶有数字换位坏行（GC001 2021-08-10 close 服务 2.850>high 2.750，真值 2.085）；fqkline 自洽但缺 25 个 2015 崩盘夏日+浅 1.3 年；akshare stock_zh_a_hist_tx=无修复腿的 newfqkline 血统（M0923 缓存同染 2.850=同血非独立证据）。正典=主面+逐行 close∈[low,high] 守卫+守卫败行经修复面补+不可修复隔离禁落地+兄弟期限曲线当日交叉验证判坏行；利率带先验太窄会误杀真值（(0,50) 被 2015-02-10 GC001 close 53.44/真春节前钱荒否决→(0,200) 证据锁定）。指针=scripts/update_repo.py+research/shortline/REPO_PANEL.md v1.1+commit r328。\n- [2026-09-27 15:0x r329 bm-a] 坑律：**继承挂起 rebase 的完成 resolver 三修（r328 死会话 resolve2 代码审获，未及实弹即修）——①CODELY.md memory-union 前缀断言在对侧原地改指针行（r84/r85 批注为追加式内嵌编辑）时必失败，正解≠放弃：条目级双向覆盖核验替代字节直拼（两侧每条 entry 行∈tree∪archive+tree 每行有 blob 源=零幻影零丢失 r327 律+指针行双批注并含）②daily_report .md 孪生非 JSON——take_newer_json 直接 json.loads 当场崩；正解=json 孪生先按 generated_at 取侧、md 从同侧 blob 字节直拷（twin-side coupling）③EOL/indent 镜像探测源=base blob（:1:）禁读带冲突标记的 worktree 件（标记混杂两侧行尾=探测污染，r85 律新面）。指针=results/_r328bma_resolve3.py（16-UU 全解+CODELY 双向核验过+rebase continue 一次通过）。**\n"
if "十七批（r331 bm-b" in raw.decode("utf-8", errors="ignore"):
    print("section already present, no-op")
else:
    with open(ARCH, "wb") as f:
        f.write(raw + section.replace("\n", eol).encode("utf-8"))
    print("appended, eol=%r, new_size=%d" % (eol, os.path.getsize(ARCH)))
# verification: entries verbatim present in archive, zero-loss
arch_txt = open(ARCH, encoding="utf-8").read()
codely = open("CODELY.md", encoding="utf-8").read()
for tag, frag in [("r328", "腾讯双 K 线端点互不互证"), ("r329", "继承挂起 rebase 的完成 resolver 三修")]:
    print(tag, "in_archive=", frag in arch_txt, "pointer_in_codely=", tag in codely)
print("CODELY size =", os.path.getsize("CODELY.md"), "bytes (<10240:", os.path.getsize("CODELY.md") < 10240, ")")
