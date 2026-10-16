"""r1024 bm-a addendum: post-push readback into state + CODELY.md pit entry.
r1051 precedent (state head_sha/sync post-push readback). Exit 0/2.
"""
import json, os, subprocess, sys, datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
TIP = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                     capture_output=True, text=True).stdout.strip()

st_path = os.path.join(ROOT, "state-bm-a.json")
with open(st_path, encoding="utf-8") as f:
    st = json.load(f)
st["push_verified"] = {
    "ts": NOW, "origin_tip": TIP,
    "note": ("r1024: push 4b3f4185b..6071573d1 rc0 direct (no reject), rev-list 0/0, "
             "ls-remote tip 6071573d1; post_review face = keyed-regeneration type "
             "(11345==11345 lines, same last-id) zero row loss; smoke/chain .log faces "
             "gitignored by design (evidence = report line + rollback_side)"),
}
st["sync"] = {"ts": NOW, "ahead_behind": "0/0", "origin_tip": TIP,
              "note": "r1024: pushed direct 4b3f4185b..6071573d1, verified"}
with open(st_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

hb_path = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
with open(hb_path, encoding="utf-8") as f:
    hb = json.load(f)
hb["push_verified"] = {"ahead_behind": "0/0", "origin_tip": TIP, "ts": NOW,
                      "note": "r1024: push direct rc0, local-not-at-origin=0"}
hb["sync"] = {"ahead_behind": "0/0", "origin_tip": TIP, "ts": NOW,
              "note": "r1024 readback"}
with open(hb_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

pit = ("[2026-10-16 20:2x r1024 bm-a] 双坑律（P0 双修实证）：①sitecustomize.py 零窗补丁"
       "（10-08 装·site-packages 级）在无控制台宿主（GetConsoleWindow()==0）下把 "
       "subprocess.Popen 换成普通函数 -> asyncio.windows_utils `class Popen(subprocess.Popen)` "
       "子类化函数必崩 = 全机无头 python 的 asyncio/akshare import 全崩（r1023 「torn pyc」诊断系"
       "误判勘正——补丁仅无头触发，交互验证会话有控制台不触发 = 假自愈史）；修法 = 函数包 -> 类包"
       "（类包保零窗意图 + 恢复可子类化），诊断指纹 = 无头态 `subprocess.Popen` 显示 "
       "<function _silent_Popen>；原件备份 results/_r1024bma_sitecustomize_original_20261008.py。"
       "②CAS/树手术提交不物化 worktree -> 次轮 pull 被陈旧幻影脏树卡死 + 整树回退面（C-02 wave-F 族"
       "实弹：worktree 停 r1023 物化态 21:26:49 vs HEAD 今日 CAS 0cb8050）；正法 = mtime 分区（当日"
       "写盘件保）+ 账面摘录存旁（treasure 门补救律）+ origin-take checkout + ff；判共享再生成面"
       "形态先行（post_review 11345==11345 同行数 keyed 重生型非 append-only，勿盲 union）。"
       "How to apply：无头 python 崩 asyncio 先查 sitecustomize Popen 形态；CAS 提交后次轮首查 "
       "worktree-HEAD 同步性（status 脏面 vs rev-list ahead=0 分诊）。\n")
with open(os.path.join(ROOT, "CODELY.md"), "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + pit)
print("ADDENDUM_OK tip=%s %s" % (TIP, NOW))
sys.exit(0)
