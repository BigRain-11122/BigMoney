#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""memory-budget-gate.py — 注入面硬预算确定性守门件（2026-10-15 立·CEO 令 O-20261015-1230·memory.md §10 配套）

用法:
  python Tools/memory-budget-gate.py [--path <CODELY.md>] [--budget-bytes 40960] [--budget-entries 60]
       [--fresh-days 3] [--report]   # --report=只报数不执法（≤预算时本来就不动刀）

语义: 注入面（本机全局 CODELY.md·平台每会话全量注入）≤40KB 且 ≤60 条；
      超限=KEEP 白名单与 ≤fresh-days 新条目之外的条目按主题路由表 verbatim 搬迁到
      <home>\.codely-cli\memory\topics\<主题>.md，重建注入面（四节 ### 结构+主题索引）。
      零 LLM 零 token 维护；写前快照（cleanup-gate-<date>\）+ mtime 竞写守卫；零删除保真。
退出码: 0=预算内或执法完成；1=守卫失配/异常（勿盲重试·先核尾）。
"""
import datetime
import os
import re
import sys

SECTIONS = ("User", "Feedback", "Project", "Reference")
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

KEEP_RULES = [
    ("CEO 汇报语言裁决",), ("CEO 迭代式交付裁决",), ("CEO 创作质量三律",),
    ("CEO 交付地址直给裁决",), ("CEO 深研先行律+过目双闸",),
    ("CEO 呈审纪律总令",), ("CEO 音轨禁令",),
    ("CEO 常设授权令", "否决窗已废止"), ("CEO 三车道+零卡点双令",),
    ("CEO 机队 CPU 常设开放令",), ("CEO 常设工作律",), ("CEO 效率方法论令",),
    ("CEO 账号安全令",), ("CEO 令任务快车道令",),
    ("机队硬件档", "RTX 4070 SUPER 12GB+内存 94GB"),
    ("用户申斥实录（全自动化裁决律",), ("交互会话零窗口铁律",),
    ("CEO 用机让路律触发词",), ("会话分工定界",), ("用户规则（2026-09-19 重申",),
    ("大文件红线（U187",),
    ("bm-a 记忆工具坑：append_memory scope=project EEXIST",),
    ("bm-a 工具坑：rg 长多选 CJK pattern 假阴性",),
    ("命令查重律（2026-10-08 立",), ("立法观察期冻结",),
    ("记忆整理归档法（用户令「整理全局记忆",),
    ("云端 token 严管令",), ("活跃产线指针",), ("记忆分层主题索引",),
    ("本次分层重构快照",), ("记忆分层重构快照",),
]

TOPIC_RULES = [
    ("mv-production.md", ["mv0001", "mv-album", "jman", "krea", "h3", "seedance", "i2v", "镜头", "剧本",
                           "选角", "周杰伦", "星晴", "可爱女人", "邝盛", "方文山", "专辑", "mv ",
                           "导演工作流", "改编创作四律", "受众群", "角色设计", "男主", "女主", "whisper 锚点", "歌词"]),
    ("shortvideo-bili.md", ["meme", "短视频", "b站", "bili", "抖音", "切片", "慢慢踩", "法务部", "涨粉", "账号运营", "capcut", "剪映", "神评论"]),
    ("quant-backtest.md", ["回测", "bigmoney", "波链", "w20", "w2", "saturation", "冻结", "席位", "w17", "w18", "纸盘", "量化", "回撤"]),
    ("hardware-procurement.md", ["v100", "t10", "2680v2", "2695", "c602", "ddr", "水冷", "机架", "采购", "3090", "内存条", "散热", "服务器", "电费", "魔改"]),
    ("game-dev.md", ["u360", "吸嘟嘟", "软著", "关卡", "玩法", "steam", "提审", "metis", "tuanjie", "unity",
                     "gui-agent", "硅基", "可视化", "citywatch", "city3d", "minigame", "gimmeall", "游戏"]),
    ("fleet-dispatcher.md", ["fleet", "机队", "dispatcher", "patrol", "巡视", "poke", "tailnet", "心跳", "车道",
                             "fleetlink", "8090", "bm-b", "bm-c", "调度", "自领", "idlewatch", "主agent", "master-agent",
                             "业务法", "让路令", "排满", "满载"]),
    ("git-surgery.md", ["git", "worktree", "原子推", "commit", "push", "pathspec", "refs", "反转闸", "index.lock",
                        "checkout", "blob", "cherry-pick", "竞推", "丢行", "分支"]),
    ("governance-council.md", ["委员会", "council", "法熵", "治理", "正典", "law-registry", "机制总图", "梳理",
                               "否决窗", "cadence", "versioning", "sli", "主脑", "立法", "修法"]),
    ("tool-pitfalls.md", ["powershell", "ps5", "gbk", "编码", "bat", "python", "comfy", "ollama", "whisper", "rg ",
                          "bom", "curl", "下载", "msi", "sdk", "zip", "7z", "进程", "schtasks", "vbs", "工具坑",
                          "坑", "判例", "正法", "探测", "锁", "unity", "取证", "缓存", "音频"]),
]
MISC = "archive-misc.md"


def parse(text):
    sections = {s: [] for s in SECTIONS}
    cur = None
    entries = []
    pend = None
    for ln in text.split("\n"):
        if ln.startswith("### ") and ln[4:].strip() in sections:
            if pend:
                entries.append(pend)
                pend = None
            cur = ln[4:].strip()
            continue
        if ln.startswith("##") or ln.startswith("# "):
            if pend:
                entries.append(pend)
                pend = None
            continue
        if ln.startswith("- ["):
            if pend:
                entries.append(pend)
            pend = [cur, ln]
            continue
        if pend is not None:
            pend[1] += "\n" + ln
    if pend:
        entries.append(pend)
    return entries


def entry_date(body):
    m = DATE_RE.search(body)
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def is_keep(body, fresh_days, today=None):
    today = today or datetime.date.today()
    for rule in KEEP_RULES:
        if all(k in body for k in rule):
            return True
    d = entry_date(body)
    if d and (today - d).days <= fresh_days:
        return True
    return False


def topic_of(body):
    low = body.lower()
    for tf, kws in TOPIC_RULES:
        if any(k in low or k in body for k in kws):
            return tf
    return MISC


def main():
    args = sys.argv[1:]
    path = os.path.join(os.environ.get("USERPROFILE", ""), ".codely-cli", "CODELY.md")
    budget_bytes, budget_entries, fresh_days = 40960, 60, 3
    report_only = False
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--path":
            i += 1
            path = args[i]
        elif a == "--budget-bytes":
            i += 1
            budget_bytes = int(args[i])
        elif a == "--budget-entries":
            i += 1
            budget_entries = int(args[i])
        elif a == "--fresh-days":
            i += 1
            fresh_days = int(args[i])
        elif a == "--report":
            report_only = True
        i += 1

    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    norm = text.replace("\r\n", "\n")
    entries = parse(norm)
    n = len(entries)
    print("GATE-CHECK bytes=%d budget=%d entries=%d budget=%d" % (len(raw), budget_bytes, n, budget_entries))
    if len(raw) <= budget_bytes and n <= budget_entries:
        print("GATE-OK 预算内·零动作")
        return 0
    if report_only:
        print("GATE-OVER 预算超限（--report 只报不执法）")
        return 0

    mtime0 = os.path.getmtime(path)
    snapdir = os.path.join(os.path.dirname(os.path.dirname(path)), "memory",
                           "cleanup-gate-%s" % datetime.date.today().isoformat())
    os.makedirs(snapdir, exist_ok=True)
    with open(os.path.join(snapdir, "CODELY-pre.md"), "wb") as f:
        f.write(raw)

    keep = {s: [] for s in SECTIONS}
    moved = []
    for sec, txt in entries:
        sec = sec or "Reference"
        body = txt.strip()
        if is_keep(body, fresh_days):
            keep[sec].append(body)
        else:
            moved.append((topic_of(body), body))

    topics_dir = os.path.join(os.path.dirname(os.path.dirname(path)), "memory", "topics")
    os.makedirs(topics_dir, exist_ok=True)
    for tf, body in moved:
        with open(os.path.join(topics_dir, tf), "a", encoding="utf-8", newline="\n") as f:
            f.write("\n" + body + "\n")
    idx = []
    for tf in sorted(set([t for t, _ in moved] + os.listdir(topics_dir))):
        if not tf.endswith(".md"):
            continue
        with open(os.path.join(topics_dir, tf), encoding="utf-8") as f:
            cnt = sum(1 for l in f if l.startswith("- ["))
        idx.append((tf, cnt))

    out = ["# CODELY 全局结构记忆 — 分层制 v2（2026-10-15 立·O-20261015-1230）\n"
           "> 机制：注入面硬预算 ≤40KB/≤60 条（夜审 cron 跑 Tools/memory-budget-gate.py 守门·零 LLM）；"
           "长文/状态/领域细节=memory/topics/ 主题文件（按需读·索引见 ### Reference）；"
           "新条目 >300 字=先落主题文件再回写指针行；跨机价值一律走 git 正典（memory.md §8/§10）。\n\n"]
    for sec, title in (("User", "### User"), ("Feedback", "### Feedback"), ("Project", "### Project"), ("Reference", "### Reference")):
        out.append(title + "\n")
        for e in keep[sec]:
            out.append(e + "\n")
        if sec == "Reference":
            out.append("- [memory-gate] 记忆分层主题索引（按需读·verbatim 全量在档）：\n")
            for tf, cnt in idx:
                out.append("- %s（%d 条）=%s\\%s\n" % (tf, cnt, topics_dir, tf))
        out.append("\n")

    if os.path.getmtime(path) != mtime0:
        print("ABORT: mtime 漂移（他窗竞写）——重跑")
        return 1
    new_text = "".join(out)
    if crlf:
        new_text = new_text.replace("\n", "\r\n")
    nb = (b"\xef\xbb\xbf" if bom else b"") + new_text.encode("utf-8")
    with open(path, "wb") as f:
        f.write(nb)
    print("GATE-EXEC %d->%dB %d->%d条 MOVED=%d topics=%d snapshot=%s"
          % (len(raw), len(nb), n, sum(1 for l in new_text.split("\n") if l.startswith("- [")),
             len(moved), len(set(t for t, _ in moved)), snapdir))
    print("LEDGER-LINE | %s | gate | %d->%d B | %d->%d 条 | moved=%d | topics=%d |"
          % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), len(raw), len(nb), n,
             sum(1 for l in new_text.split("\n") if l.startswith("- [")), len(moved),
             len(set(t for t, _ in moved))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
